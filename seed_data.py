"""
seed_data.py — inserts real Kraków venues and deals into Supabase.
Run: python seed_data.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from db.client import get_client

# ── Venues ────────────────────────────────────────────────────────────────────

VENUES = [
    # already in DB — will be skipped if name exists
    {"name": "Piwnica Pod Złotą Pipą",   "address": "ul. Floriańska 30, Kraków",       "lat": 50.062500, "lng": 19.938500, "category": "pub"},
    {"name": "Café Szafé",               "address": "ul. Felicjanek 10, Kraków",        "lat": 50.058800, "lng": 19.935200, "category": "cafe"},
    {"name": "C.K. Browar",              "address": "ul. Podwale 6-7, Kraków",          "lat": 50.061500, "lng": 19.936800, "category": "pub"},
    # new venues
    {"name": "Alchemia",                 "address": "ul. Estery 5, Kraków",             "lat": 50.051200, "lng": 19.944600, "category": "pub"},
    {"name": "Omerta Pub",               "address": "ul. Kupa 3, Kraków",               "lat": 50.052100, "lng": 19.945300, "category": "pub"},
    {"name": "Craftownia",               "address": "ul. Św. Wawrzyńca 22, Kraków",    "lat": 50.052800, "lng": 19.946100, "category": "pub"},
    {"name": "House of Beer",            "address": "ul. Św. Tomasza 35, Kraków",       "lat": 50.062100, "lng": 19.937400, "category": "pub"},
    {"name": "Mercy Brown",              "address": "ul. Estery 5, Kraków",             "lat": 50.051500, "lng": 19.944800, "category": "bar"},
    {"name": "Propaganda Pub",           "address": "ul. Miodowa 20, Kraków",           "lat": 50.053400, "lng": 19.947200, "category": "pub"},
    {"name": "Stara Zajezdnia",          "address": "ul. Św. Wawrzyńca 12, Kraków",    "lat": 50.051900, "lng": 19.945700, "category": "pub"},
    {"name": "Weźże Krafta",             "address": "ul. Dajwór 16, Kraków",            "lat": 50.052600, "lng": 19.950100, "category": "pub"},
    {"name": "Szklarnie",                "address": "ul. Jakuba 19, Kraków",            "lat": 50.051800, "lng": 19.944200, "category": "bar"},
    {"name": "Nowy Kraftowy",            "address": "Plac Nowy 8, Kraków",              "lat": 50.051000, "lng": 19.943800, "category": "pub"},
    {"name": "Pijalnia Wódki i Piwa",    "address": "ul. Św. Jana 5, Kraków",           "lat": 50.062800, "lng": 19.937100, "category": "bar"},
    {"name": "Ambasada Śledzia",         "address": "ul. Stolarska 8, Kraków",          "lat": 50.061400, "lng": 19.939200, "category": "bar"},
    {"name": "Forum Przestrzenie",       "address": "ul. Konopnickiej 28, Kraków",      "lat": 50.051700, "lng": 19.927300, "category": "bar"},
    {"name": "Bunkier Cafe",             "address": "Plac Szczepański 3a, Kraków",      "lat": 50.062300, "lng": 19.933600, "category": "cafe"},
    {"name": "Spoko Pub",                "address": "ul. Kalwaryjska 9, Kraków",        "lat": 50.047200, "lng": 19.934800, "category": "pub"},
    {"name": "Ursa Maior",               "address": "ul. Szewska 21, Kraków",           "lat": 50.061700, "lng": 19.936400, "category": "pub"},
    {"name": "TeaTime Brewpub",          "address": "ul. Dietla 1, Kraków",             "lat": 50.058300, "lng": 19.942100, "category": "pub"},
    {"name": "Hard Rock Cafe Kraków",    "address": "Rynek Główny 25, 31-008 Kraków",   "lat": 50.061900, "lng": 19.936800, "category": "bar"},
]

# ── Deals ─────────────────────────────────────────────────────────────────────
# Format: (venue_name, description, start_time, end_time, days, type, tags, value_score)

DEALS_RAW = [
    # Piwnica Pod Złotą Pipą
    ("Piwnica Pod Złotą Pipą",  "Piwo draft -30% — wszystkie krany w happy hour",          "17:00", "19:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap"],          4),
    ("Piwnica Pod Złotą Pipą",  "2+1 na piwa kraftowe w każdy piątek",                      "18:00", "20:00", ["friday"],                                           "beer",      ["cheap","craft"],  5),

    # Café Szafé
    ("Café Szafé",              "Kawa + ciasto za 15 PLN",                                  "14:00", "16:00", ["saturday","sunday"],                                "food",      ["cheap"],          2),
    ("Café Szafé",              "Lunch zestaw dnia od 18 PLN",                              "12:00", "15:00", ["monday","tuesday","wednesday","thursday","friday"], "food",      ["cheap"],          3),

    # C.K. Browar
    ("C.K. Browar",             "Happy hour — piwa własnego wyrobu do 16:00",               "12:00", "16:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "beer", ["cheap"], 4),
    ("C.K. Browar",             "Lunch galicyjski — zupa + danie główne 35 PLN",            "12:00", "15:00", ["monday","tuesday","wednesday","thursday","friday"], "food",      ["cheap"],          3),

    # Alchemia
    ("Alchemia",                "Happy hour na drinki — wybrane koktajle -20%",             "18:00", "20:00", ["monday","tuesday","wednesday","thursday"],          "cocktails", ["cheap"],          3),
    ("Alchemia",                "Piwo 0,5l za 10 PLN w godzinach otwarcia",                 "16:00", "19:00", ["friday","saturday"],                                "beer",      ["cheap","student"], 4),

    # Omerta Pub
    ("Omerta Pub",              "Kraftowe piwa -15% codziennie po południu",                "15:00", "18:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap","craft"],  3),
    ("Omerta Pub",              "2+1 na piwa podczas koncertów",                            "19:00", "21:00", ["friday","saturday"],                                "beer",      ["cheap","group"],  5),

    # Craftownia
    ("Craftownia",              "Happy hours — wszystkie lane piwa -15%",                   "15:00", "18:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "beer", ["cheap","craft"], 3),
    ("Craftownia",              "Degustacja 4 piw kraftowych za 25 PLN",                    "16:00", "20:00", ["thursday","friday"],                                "beer",      ["cheap","craft"],  4),

    # House of Beer
    ("House of Beer",           "Happy hour — piwa lane -15% codziennie",                   "15:00", "18:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "beer", ["cheap","craft"], 3),
    ("House of Beer",           "Piątkowy student night — karta -10% dla studentów",        "17:00", "22:00", ["friday"],                                           "beer",      ["student","cheap"], 3),

    # Propaganda Pub
    ("Propaganda Pub",          "PRL happy hour — piwo Żywiec za 8 PLN",                    "16:00", "18:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap","student"], 4),
    ("Propaganda Pub",          "Sobotni drink night — koktajle -25%",                      "19:00", "21:00", ["saturday"],                                         "cocktails", ["cheap"],          3),

    # Stara Zajezdnia
    ("Stara Zajezdnia",         "Własne piwo browaru -20% w happy hour",                    "15:00", "17:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap","craft"],  3),
    ("Stara Zajezdnia",         "Lunch set — zupa + drugie danie 32 PLN",                   "12:00", "15:00", ["monday","tuesday","wednesday","thursday","friday"], "food",      ["cheap"],          3),
    ("Stara Zajezdnia",         "Wieczór grupowy — przy zamówieniu 10+ piw jedno gratis",   "18:00", "23:00", ["friday","saturday"],                                "beer",      ["group","cheap"],  4),

    # Weźże Krafta
    ("Weźże Krafta",            "Happy hour kraftowe piwa -20%",                            "15:00", "18:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap","craft"],  3),
    ("Weźże Krafta",            "Pizza + piwo 0,5l za 35 PLN",                              "12:00", "16:00", ["monday","tuesday","wednesday","thursday","friday","saturday"], "food", ["cheap"],   3),

    # Pijalnia Wódki i Piwa
    ("Pijalnia Wódki i Piwa",   "Wódka smakowa za 5 PLN — cały dzień",                     "10:00", "23:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "shots", ["cheap","student"], 5),
    ("Pijalnia Wódki i Piwa",   "Piwo 0,5l za 8 PLN non-stop",                             "10:00", "23:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "beer",  ["cheap","student"], 4),

    # Ambasada Śledzia
    ("Ambasada Śledzia",        "Śledź + kieliszek wódki za 12 PLN",                       "12:00", "22:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "food", ["cheap"],          3),
    ("Ambasada Śledzia",        "Happy hour — drinki -30% po 17:00",                        "17:00", "19:00", ["monday","tuesday","wednesday","thursday","friday"], "cocktails", ["cheap"],          4),

    # Forum Przestrzenie
    ("Forum Przestrzenie",      "Sunset happy hour — koktajle -20% z widokiem na Wisłę",   "17:00", "19:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "cocktails", ["cheap","date"], 3),

    # Bunkier Cafe
    ("Bunkier Cafe",            "Kawa + kawałek ciasta 14 PLN do 15:00",                   "10:00", "15:00", ["monday","tuesday","wednesday","thursday","friday"], "food",      ["cheap"],          2),
    ("Bunkier Cafe",            "Artystyczny aperitivo — wino + przekąska 25 PLN",          "17:00", "19:00", ["thursday","friday","saturday"],                     "cocktails", ["cheap","date"],   3),

    # Spoko Pub
    ("Spoko Pub",               "Gin tasting — 3 giny za 30 PLN",                          "16:00", "19:00", ["thursday","friday"],                                "cocktails", ["cheap","craft"],  4),
    ("Spoko Pub",               "Naturalne wina -15% w happy hour",                         "17:00", "20:00", ["monday","tuesday","wednesday"],                     "cocktails", ["cheap"],          3),

    # Ursa Maior
    ("Ursa Maior",              "Craft beer z Bieszczad — 3 piwa za 25 PLN",               "15:00", "18:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap","craft"],  4),

    # TeaTime Brewpub
    ("TeaTime Brewpub",         "Angielskie piwa z pompy — happy hour -20%",                "16:00", "19:00", ["monday","tuesday","wednesday","thursday","friday"], "beer",      ["cheap","craft"],  3),
    ("TeaTime Brewpub",         "Piątek bitter + fish&chips za 40 PLN",                    "17:00", "21:00", ["friday"],                                           "food",      ["cheap"],          3),

    # Mercy Brown
    ("Mercy Brown",             "Speakeasy aperitivo — koktajl powitalny -30%",             "18:00", "20:00", ["wednesday","thursday"],                             "cocktails", ["cheap","date"],   3),

    # Szklarnie
    ("Szklarnie",               "Dach otwarty — piwa kraftowe -15% przy ogródku",           "15:00", "18:00", ["friday","saturday","sunday"],                       "beer",      ["cheap","craft"],  3),

    # Nowy Kraftowy
    ("Nowy Kraftowy",           "Plac Nowy happy hour — piwa -20%",                         "15:00", "18:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "beer", ["cheap","craft"], 3),
    ("Nowy Kraftowy",           "Piątkowy student night — 2+1 na piwa lane",               "19:00", "22:00", ["friday"],                                           "beer",      ["student","cheap","craft"], 5),

    # Hard Rock Cafe Kraków — official breakfast offering
    ("Hard Rock Cafe Kraków",   "Breakfast menu served daily",                              "10:00", "12:00", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"], "food", ["general"], 1),
]

SOURCE_URLS = {
    "Hard Rock Cafe Kraków": "https://cafe.hardrock.com/krakow/",
}


# ── Insert logic ──────────────────────────────────────────────────────────────

def seed():
    client = get_client()
    print("\n" + "=" * 50)
    print("Happy Hours Kraków — Data Seeder")
    print("=" * 50)

    # ── 1. Venues ──
    print(f"\n[VENUES] Inserting {len(VENUES)} venues...")

    existing_venues = client.table("venues").select("name").execute()
    existing_names  = {v["name"] for v in existing_venues.data}

    venue_added = 0
    venue_skipped = 0

    for v in VENUES:
        if v["name"] in existing_names:
            venue_skipped += 1
            continue
        client.table("venues").insert(v).execute()
        print(f"  + {v['name']}")
        venue_added += 1

    print(f"[VENUES] Done — {venue_added} added, {venue_skipped} skipped (already exist)")

    # ── 2. Build venue name → id map ──
    all_venues  = client.table("venues").select("id, name").execute()
    venue_map   = {v["name"]: v["id"] for v in all_venues.data}

    # ── 3. Deals ──
    print(f"\n[DEALS] Inserting {len(DEALS_RAW)} deals...")

    existing_deals = client.table("deals").select("description, venue_id").execute()
    existing_keys  = {(d["venue_id"], d["description"][:40]) for d in existing_deals.data}

    deal_added   = 0
    deal_skipped = 0
    deal_errors  = 0

    for (venue_name, desc, start, end, days, dtype, tags, score) in DEALS_RAW:
        venue_id = venue_map.get(venue_name)
        if not venue_id:
            print(f"  ! SKIP — venue not found: {venue_name}")
            deal_errors += 1
            continue

        key = (venue_id, desc[:40])
        if key in existing_keys:
            deal_skipped += 1
            continue

        row = {
            "venue_id":    venue_id,
            "description": desc,
            "start_time":  start,
            "end_time":    end,
            "days_of_week": days,
            "type":        dtype,
            "tags":        tags,
            "value_score": score,
            "source_url":   SOURCE_URLS.get(venue_name),
            "confidence":   "high" if venue_name in SOURCE_URLS else None,
            "dedupe_key":   f"seed:{venue_id}:{desc[:40]}",
        }

        try:
            client.table("deals").insert(row).execute()
            deal_added += 1
            print(f"  + [{dtype} | score:{score}] {venue_name} — {desc[:50]}")
        except Exception as e:
            print(f"  ! ERROR: {e}")
            deal_errors += 1

    print(f"\n[DEALS] Done — {deal_added} added, {deal_skipped} skipped, {deal_errors} errors")

    # ── 4. Summary ──
    total_venues = client.table("venues").select("id", count="exact").execute()
    total_deals  = client.table("deals").select("id",  count="exact").execute()

    print("\n" + "=" * 50)
    print(f"DATABASE SUMMARY")
    print(f"  Venues: {total_venues.count}")
    print(f"  Deals:  {total_deals.count}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    seed()