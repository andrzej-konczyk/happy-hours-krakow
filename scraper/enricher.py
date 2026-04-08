# ── Keyword maps ───────────────────────────────────────────────────────────────

TYPE_KEYWORDS = {
    "beer": [
        "piwo", "beer", "draft", "lager", "ipa", "stout", "craft",
        "browar", "kran", "kufel", "pint", "piwa",
    ],
    "cocktails": [
        "cocktail", "koktajl", "drink", "gin", "vodka", "wódka",
        "rum", "whisky", "whiskey", "martini", "mojito",
    ],
    "food": [
        "food", "jedzenie", "lunch", "obiad", "przekąska", "snack",
        "pizza", "burger", "zupa", "soup", "pierogi", "danie",
    ],
    "shots": [
        "shot", "szot", "wściekły pies", "kamikaze", "probówka",
    ],
}

TAG_KEYWORDS = {
    "cheap": [
        "-30%", "-40%", "-50%", "gratis", "free", "2+1", "za darmo",
        "taniej", "tańsze", "promocja", "1 zł", "6 zł", "8 zł",
    ],
    "group": [
        "group", "grupa", "groups", "grupow", "powyżej", "osoby",
        "team", "firma", "corporate", "bankiet",
    ],
    "student": [
        "student", "studenci", "studencka", "akademik", "uczelnia",
        "isic", "legitymacja",
    ],
    "date": [
        "romantyczny", "romantic", "dla dwojga", "dla par", "intimate",
        "kameralny", "świece", "candle",
    ],
    "craft": [
        "craft", "kraftowe", "rzemieślnicze", "artisanal", "browar",
        "brewery", "microbrewery",
    ],
}

VALUE_RULES = [
    # (score, keywords) — sprawdzamy od najwyższego
    (5, ["2+1", "drugi gratis", "free beer", "gratis piwo", "-50%", "za darmo"]),
    (4, ["-40%", "-30%", "happy hour", "2 for 1"]),
    (3, ["-20%", "-15%", "promo", "promocja", "tańsze"]),
    (2, ["lunch", "obiad", "zniżka", "discount"]),
    (1, []),  # default
]


# ── Core logic ─────────────────────────────────────────────────────────────────

def detect_type(text: str) -> str:
    text_lower = text.lower()
    scores = {t: 0 for t in TYPE_KEYWORDS}

    for deal_type, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[deal_type] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "mixed"


def detect_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags or ["general"]


def detect_value_score(text: str) -> int:
    text_lower = text.lower()
    for score, keywords in VALUE_RULES:
        if any(kw in text_lower for kw in keywords):
            return score
    return 1


def enrich_deal(deal: dict) -> dict:
    text = f"{deal.get('description', '')} {' '.join(deal.get('days_of_week') or [])}"

    deal["type"]        = detect_type(text)
    deal["tags"]        = detect_tags(text)
    deal["value_score"] = detect_value_score(text)

    return deal


def enrich_deals(deals: list[dict]) -> list[dict]:
    return [enrich_deal(deal) for deal in deals]