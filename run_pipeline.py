import json
import os
from datetime import datetime
from dotenv import load_dotenv

from scraper.scraper import scrape_html, scrape_pdfs
from scraper.parser import parse_deal
from db.client import get_client
from scraper.validator import clean_deals
from scraper.enricher import enrich_deals
from scraper.scraper_config import ALL_HTML_URLS, ALL_PDF_URLS

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
USE_MOCK = not API_KEY  # automatycznie mock jeśli brak klucza


# ── Config ─────────────────────────────────────────────────────────────────────

# Puby z potwierdzonymi stronami www i happy hours
HTML_URLS = ALL_HTML_URLS
PDF_URLS  = ALL_PDF_URLS

# venue_id musi istnieć w tabeli venues w Supabase
# tymczasowo hardcode — później będzie z bazy
VENUE_MAP = {
    "https://alchemia.com.pl/":                                                "WSTAW-UUID-ALCHEMIA",
    "https://ckbrowar.pl/wp-content/uploads/2026/02/menu-web-01.2026.pdf":    "82755228-76bb-4187-a167-f45ec077322d",
}


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ── Pipeline steps ────────────────────────────────────────────────────────────

def step_scrape() -> list[dict]:
    log("STEP 1 — Scraping started")
    results = scrape_html(HTML_URLS) + scrape_pdfs(PDF_URLS)
    total_snippets = sum(len(r["snippets"]) for r in results)
    log(f"STEP 1 — Done. {len(results)} URLs scraped, {total_snippets} snippet(s) found")
    return results


def step_parse(scrape_results: list[dict]) -> list[dict]:
    log("STEP 2 — Parsing started")
    parsed = []

    for result in scrape_results:
        if result["status"] == "error" or not result["snippets"]:
            log(f"  SKIP {result['url']} — no snippets")
            continue

        venue_id = VENUE_MAP.get(result["url"])
        if not venue_id or "WSTAW" in venue_id:
            log(f"  SKIP {result['url']} — no venue_id configured")
            continue

        for snippet in result["snippets"]:
            log(f"  Parsing snippet from {result['url']} (keyword: {snippet['keyword']})")
            deal = parse_deal(snippet["snippet"], api_key=API_KEY, use_mock=USE_MOCK)

            if "error" in deal:
                log(f"  ERROR parsing: {deal['error']}")
                continue

            deal["venue_id"] = venue_id
            deal["source_url"] = result["url"]
            parsed.append(deal)
            log(f"  → {deal['description'][:60]} | {deal['start_time']}–{deal['end_time']} | confidence: {deal['confidence']}")

    log(f"STEP 2 — Done. {len(parsed)} deal(s) parsed")
    return parsed


def step_save(parsed_deals: list[dict]) -> int:
    log("STEP 3 — Enriching, validating & saving")

    if not parsed_deals:
        log("STEP 3 — Nothing to save")
        return 0

    client = get_client()
    venues = client.table("venues").select("id").execute()
    known_ids = {v["id"] for v in venues.data}

    # enrich → validate → save
    enriched = enrich_deals(parsed_deals)
    clean    = clean_deals(enriched, known_venue_ids=known_ids)

    saved = 0
    for deal in clean:
        row = {
            "venue_id":     deal["venue_id"],
            "description":  deal["description"],
            "start_time":   deal["start_time"],
            "end_time":     deal["end_time"],
            "days_of_week": deal["days_of_week"],
            "type":         deal.get("type", "mixed"),
            "tags":         deal.get("tags", []),
            "value_score":  deal.get("value_score", 1),
        }
        try:
            client.table("deals").insert(row).execute()
            saved += 1
            log(f"  SAVED [{row['type']} | score:{row['value_score']} | tags:{row['tags']}] {row['description'][:50]}")
        except Exception as e:
            log(f"  ERROR: {e}")

    log(f"STEP 3 — Done. {saved}/{len(clean)} saved")
    return saved


def step_dump(parsed_deals: list[dict]):
    """Zapisz parsed deals do pliku — przydatne do debugowania bez Supabase."""
    path = "scraper/pipeline_output.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(parsed_deals, f, ensure_ascii=False, indent=2)
    log(f"DEBUG dump saved to {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log("=" * 50)
    log("Happy Hours Kraków — Pipeline START")
    log(f"Mode: {'MOCK' if USE_MOCK else 'Claude API'}")
    log("=" * 50)

    scraped = step_scrape()
    parsed  = step_parse(scraped)
    step_dump(parsed)   # zawsze zapisz lokalnie do debugowania

    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        step_save(parsed)
    else:
        log("STEP 3 — SKIPPED (no Supabase credentials in .env)")

    log("=" * 50)
    log("Pipeline DONE")
    log("=" * 50)