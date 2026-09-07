"""
scraper_config.py — central config for all URLs to scrape.
Used by scraper.py in batch mode.
"""

# ── HTML pages ────────────────────────────────────────────────────────────────
# Bars with static HTML — requests + BeautifulSoup works

HTML_SOURCES = [
    {"venue": "Alchemia",              "url": "https://alchemia.com.pl/"},
    {"venue": "Stara Zajezdnia",       "url": "https://starazajezdniakrakow.pl/restauracja/"},
    {"venue": "C.K. Browar",           "url": "https://ckbrowar.pl/menu/"},
    {"venue": "Omerta Pub",            "url": "https://omerta.ontap.pl/"},
    {"venue": "Spoko Pub",             "url": "https://spokopub.pl/"},
]

# ── PDF menus ─────────────────────────────────────────────────────────────────
# Bars that publish menus/promotions as PDFs

PDF_SOURCES = [
    {"venue": "C.K. Browar", "url": "https://ckbrowar.pl/wp-content/uploads/2026/02/menu-web-01.2026.pdf"},
]

# ── Combined (used by batch scraper) ─────────────────────────────────────────

ALL_HTML_URLS = [s["url"] for s in HTML_SOURCES]
ALL_PDF_URLS  = [s["url"] for s in PDF_SOURCES]