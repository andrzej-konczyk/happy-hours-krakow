import re
from datetime import datetime


# ── Normalization helpers ──────────────────────────────────────────────────────

KEYWORD_MAP = {
    "2 for 1":      "2+1",
    "two for one":  "2+1",
    "buy one get one": "2+1",
    "bogo":         "2+1",
    "drugi gratis": "2+1",
    "happy hours":  "happy hour",
    "happyhour":    "happy hour",
    "znizka":       "zniżka",
    "discount":     "zniżka",
}

TIME_PATTERN = re.compile(r"^\d{2}:\d{2}$")


def normalize_time(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    # akceptuj HH:MM i HH:MM:SS → przytnij do HH:MM
    match = re.match(r"^(\d{2}:\d{2})(:\d{2})?$", value)
    if match:
        return match.group(1)
    return None


def normalize_description(text: str | None) -> str | None:
    if not text:
        return None
    text = text.strip().lower()
    for raw, canonical in KEYWORD_MAP.items():
        text = text.replace(raw, canonical)
    return text


def normalize_days(days: list | None) -> list | None:
    if not days:
        return None
    valid = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    return sorted({d.strip().lower() for d in days if d.strip().lower() in valid})


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_deal(deal: dict, known_venue_ids: set[str]) -> tuple[bool, list[str]]:
    errors = []

    # description
    if not deal.get("description") or len(deal["description"].strip()) < 3:
        errors.append("empty or too short description")

    # venue_id
    if not deal.get("venue_id"):
        errors.append("missing venue_id")
    elif deal["venue_id"] not in known_venue_ids:
        errors.append(f"unknown venue_id: {deal['venue_id']}")

    # times
    start = normalize_time(deal.get("start_time"))
    end   = normalize_time(deal.get("end_time"))

    if not start:
        errors.append("invalid or missing start_time")
    if not end:
        errors.append("invalid or missing end_time")
    if start and end and start >= end:
        errors.append(f"start_time {start} is not before end_time {end}")

    # days
    days = normalize_days(deal.get("days_of_week"))
    if not days:
        errors.append("missing or invalid days_of_week")

    return (len(errors) == 0), errors


# ── Deduplication ──────────────────────────────────────────────────────────────

def dedup_deals(deals: list[dict]) -> tuple[list[dict], int]:
    seen = set()
    unique = []
    dupes = 0

    for deal in deals:
        key = (
            deal.get("venue_id", ""),
            deal.get("start_time", ""),
            deal.get("end_time", ""),
            deal.get("description", "")[:40],
        )
        if key in seen:
            dupes += 1
        else:
            seen.add(key)
            unique.append(deal)

    return unique, dupes


# ── Main entry point ───────────────────────────────────────────────────────────

def clean_deals(raw_deals: list[dict], known_venue_ids: set[str]) -> list[dict]:
    print(f"\n[VALIDATOR] Input: {len(raw_deals)} deal(s)")

    # 1. Normalize
    normalized = []
    for deal in raw_deals:
        deal["description"] = normalize_description(deal.get("description"))
        deal["start_time"]  = normalize_time(deal.get("start_time"))
        deal["end_time"]    = normalize_time(deal.get("end_time"))
        deal["days_of_week"] = normalize_days(deal.get("days_of_week"))
        normalized.append(deal)

    # 2. Validate
    valid = []
    invalid_count = 0
    for deal in normalized:
        ok, errors = validate_deal(deal, known_venue_ids)
        if ok:
            valid.append(deal)
        else:
            invalid_count += 1
            print(f"[VALIDATOR] REJECTED — {errors} | {deal.get('description', '')[:50]}")

    print(f"[VALIDATOR] Validated: {len(valid)} ok, {invalid_count} rejected")

    # 3. Deduplicate
    clean, dupes = dedup_deals(valid)
    print(f"[VALIDATOR] Deduped: {dupes} duplicate(s) removed")
    print(f"[VALIDATOR] Output: {len(clean)} clean deal(s)\n")

    return clean