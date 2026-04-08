import json
import re
import requests


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """
You are a data extraction assistant.
Extract happy hour / promotion details from bar or restaurant text snippets.
Always respond with valid JSON only — no markdown, no explanation.

Return this structure:
{
  "description": "short human-readable description of the deal",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "days_of_week": ["monday", "tuesday", ...],
  "confidence": "high | medium | low"
}

Rules:
- Normalize all times to 24h HH:MM format
- days_of_week must use full English lowercase day names
- If a field cannot be determined, use null
- confidence = high if all fields found, medium if some, low if mostly guessing
"""


def _mock_parse(text: str) -> dict:
    """
    Prosty mock — parsuje tekst regexem bez API.
    Wystarczy do testowania pipeline'u.
    """
    text_lower = text.lower()

    # szukaj godzin w formacie 12:00, 16:00, 4pm, 5pm itd.
    times = re.findall(r'\b(\d{1,2}:\d{2}|\d{1,2}(?:am|pm))\b', text_lower)

    def normalize(t: str) -> str | None:
        t = t.strip()
        if "am" in t or "pm" in t:
            hour = int(re.sub(r'[apm]', '', t))
            if "pm" in t and hour != 12:
                hour += 12
            return f"{hour:02d}:00"
        return t if len(t) == 5 else None

    normalized = [normalize(t) for t in times]
    normalized = [t for t in normalized if t]

    # szukaj dni tygodnia
    day_map = {
        "monday": "monday", "poniedziałek": "monday", "poniedziałku": "monday",
        "tuesday": "tuesday", "wtorek": "tuesday", "wtorku": "tuesday",
        "wednesday": "wednesday", "środa": "wednesday", "środy": "wednesday",
        "thursday": "thursday", "czwartek": "thursday", "czwartku": "czwartek",
        "friday": "friday", "piątek": "friday", "piątku": "friday",
        "saturday": "saturday", "sobota": "saturday", "soboty": "saturday",
        "sunday": "sunday", "niedziela": "sunday", "niedzieli": "sunday",
    }

    found_days = [eng for pol, eng in day_map.items() if pol in text_lower]
    found_days = sorted(set(found_days), key=list(day_map.values()).index)

    # jeśli "poniedziałku do piątku" — uzupełnij wszystkie dni robocze
    if "do piątku" in text_lower or "to friday" in text_lower:
        found_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    if "every day" in text_lower or "daily" in text_lower or "codziennie" in text_lower:
        found_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    start = normalized[0] if len(normalized) >= 2 else None
    end = normalized[1] if len(normalized) >= 2 else (normalized[0] if normalized else None)

    confidence = "high" if (start and end and found_days) else "medium" if (end or found_days) else "low"

    return {
        "description": text[:80].strip(),
        "start_time": start,
        "end_time": end,
        "days_of_week": found_days or None,
        "confidence": confidence,
        "source": "mock",
    }


def parse_deal(text: str, api_key: str | None = None, use_mock: bool = False) -> dict:
    if use_mock or not api_key:
        return _mock_parse(text)

    payload = {
        "model": MODEL,
        "max_tokens": 300,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": f"Extract deal info from this text:\n\n{text}"}
        ],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        raw = response.json()["content"][0]["text"].strip()
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": raw}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    examples = [
        "od poniedziałku do piątku w godz. 12:00 - 16:00 Promocja nie dotyczy grup powyżej 10 osób",
        "Happy Hour every day until 4pm, when 5l of light beer costs only $12!",
        "Every Monday and Tuesday from 5pm to 7pm — all draft beers 30% off",
    ]

    for snippet in examples:
        print(f"\n--- INPUT ---\n{snippet}")
        result = parse_deal(snippet, use_mock=True)
        print(f"--- OUTPUT ---\n{json.dumps(result, ensure_ascii=False, indent=2)}")