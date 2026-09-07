from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from datetime import datetime
from html import escape
from services.deals import get_all_deals, is_active_now
from db.client import get_client

router = APIRouter()

TAG_EMOJI = {
    "cheap":   "💰",
    "group":   "👥",
    "student": "🎓",
    "date":    "❤️",
    "craft":   "🍺",
    "general": "⭐",
}

TYPE_EMOJI = {
    "beer":      "🍺",
    "cocktails": "🍹",
    "food":      "🍔",
    "shots":     "🥃",
    "mixed":     "🎉",
}

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    min-height: 100vh;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: radial-gradient(circle at 50% -10%, #252b52 0, #11131d 42%, #0b0d13 100%);
    color: #e8eaf2;
    padding: 28px 16px 40px;
}
.hero {
    max-width: 1100px;
    margin: 0 auto 26px;
    text-align: center;
}
.logo {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: clamp(1.8rem, 5vw, 3rem);
    letter-spacing: -0.04em;
    color: #ffd43b;
    text-shadow: 0 8px 30px rgba(255, 212, 59, .18);
}
.logo-mark {
    display: grid;
    place-items: center;
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: linear-gradient(145deg, #ffd43b, #ff9f1c);
    color: #1a1720;
    font-size: 1.8rem;
    box-shadow: 0 8px 24px rgba(255, 159, 28, .25);
}
.subtitle {
    text-align: center;
    color: #9da3bb;
    margin: 8px 0 18px;
    font-size: 0.95rem;
}
.filters {
    max-width: 1100px;
    margin: 0 auto 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
}
.filter {
    border: 1px solid #3b4263;
    border-radius: 999px;
    background: rgba(29, 33, 52, .8);
    color: #c1c8df;
    padding: 8px 14px;
    font: inherit;
    font-size: .82rem;
}
.filter:focus { outline: 2px solid #ffd43b; outline-offset: 2px; }
.status {
    max-width: 1100px;
    margin: 0 auto 24px;
    text-align: center;
    padding: 13px 20px;
    border: 1px solid transparent;
    border-radius: 14px;
    font-weight: 600;
    box-shadow: 0 10px 30px rgba(0, 0, 0, .12);
}
.status.active   { background: rgba(34, 126, 66, .28); border-color: rgba(86, 220, 124, .25); color: #76ee9c; }
.status.inactive { background: rgba(157, 116, 22, .24); border-color: rgba(255, 212, 59, .22); color: #ffd95a; }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    max-width: 1100px;
    margin: 0 auto;
}
.card {
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 205px;
    background: rgba(29, 33, 52, .82);
    border: 1px solid #333957;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 18px 45px rgba(0, 0, 0, .2);
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto;
    height: 3px;
    background: linear-gradient(90deg, #ffd43b, #ff8c42);
}
.card:hover { transform: translateY(-4px); border-color: #ffd43b; box-shadow: 0 24px 55px rgba(0, 0, 0, .3); }
.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}
.venue { font-weight: 750; font-size: 1.04rem; flex: 1; color: #ffffff; }
.stars { color: #ffd43b; font-size: 0.82rem; letter-spacing: 1px; white-space: nowrap; }
.badge { font-size: 0.68rem; padding: 4px 9px; border-radius: 99px; font-weight: 800; letter-spacing: .03em; }
.active-badge { background: rgba(55, 174, 83, .22); color: #76ee9c; }
.deal-desc { font-size: 1.05rem; color: #e2e6f5; margin-bottom: 14px; line-height: 1.45; }
.meta { font-size: 0.84rem; color: #aeb5ce; margin-bottom: 7px; }
.address { font-size: 0.82rem; color: #858da8; margin-bottom: 14px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { background: #2b304b; color: #c1c8df; font-size: 0.75rem; padding: 4px 10px; border-radius: 99px; }
.source { margin-top: auto; padding-top: 14px; font-size: .75rem; color: #77809d; }
.source a, .footer a { color: #ffd43b; text-decoration: none; }
.source a:hover, .footer a:hover { text-decoration: underline; }
.venue-link { color: inherit; text-decoration: none; }
.venue-link:hover { color: #ffd43b; }
.map-panel {
    max-width: 1100px;
    margin: 28px auto 0;
    padding: 18px 20px;
    border: 1px solid #333957;
    border-radius: 18px;
    background: rgba(29, 33, 52, .68);
}
.map-title { color: #ffd43b; font-size: 1rem; margin-bottom: 10px; }
.venue-list { display: flex; flex-wrap: wrap; gap: 8px; }
.venue-pill {
    border: 1px solid #3b4263;
    border-radius: 999px;
    padding: 7px 11px;
    color: #c1c8df;
    text-decoration: none;
    font-size: .8rem;
}
.venue-pill:hover { border-color: #ffd43b; color: #ffd43b; }
.footer { text-align: center; margin-top: 34px; color: #69718c; font-size: 0.8rem; }
@media (max-width: 520px) {
    body { padding: 20px 12px 30px; }
    .grid { grid-template-columns: 1fr; }
    .card { min-height: 0; }
}
"""


def format_time(t: str) -> str:
    return t[:5] if t else "?"


def render_stars(score: int) -> str:
    return "★" * score + "☆" * (5 - score)


def get_venue_map() -> dict:
    client = get_client()
    venues = client.table("venues").select("id, name, address, lat, lng, website_url, maps_url").execute()
    return {v["id"]: v for v in venues.data}


def build_card(deal: dict, venue_map: dict) -> str:
    venue    = venue_map.get(str(deal.get("venue_id")), {})
    name     = escape(str(venue.get("name", "Unknown venue")))
    address  = escape(str(venue.get("address", "")))
    desc     = escape(str(deal.get("description", "")).capitalize())
    start    = format_time(deal.get("start_time", ""))
    end      = format_time(deal.get("end_time", ""))
    score    = deal.get("value_score", 1)
    dtype    = str(deal.get("type", "mixed"))
    tags     = deal.get("tags") or []
    days     = deal.get("days_of_week") or []

    type_icon = TYPE_EMOJI.get(dtype, "🎉")
    stars     = render_stars(score)
    days_short = escape(", ".join(d[:3].capitalize() for d in days))

    tags_html = " ".join(
        '<span class="tag">' + TAG_EMOJI.get(t, "•") + " " + escape(str(t)) + "</span>"
        for t in tags
    )

    active_badge = ""
    if is_active_now(deal):
        active_badge = '<span class="badge active-badge">● ACTIVE NOW</span>'

    source_url = deal.get("source_url")
    source_html = (
        '<div class="source"><a href="' + escape(str(source_url), quote=True)
        + '" target="_blank" rel="noopener">View source ↗</a></div>'
        if source_url else ""
    )

    verification_html = (
        '<span class="tag">✓ ' + escape(str(deal.get("status", "verified"))) + "</span>"
        if deal.get("status") else ""
    )

    venue_links = ""
    if venue.get("website_url"):
        venue_links += '<a href="' + escape(str(venue["website_url"]), quote=True) + '" target="_blank" rel="noopener">Website ↗</a> '
    if venue.get("maps_url"):
        venue_links += '<a href="' + escape(str(venue["maps_url"]), quote=True) + '" target="_blank" rel="noopener">Map ↗</a>'
    venue_links_html = '<div class="source">' + venue_links + "</div>" if venue_links else ""

    return (
        '<div class="card">'
        '<div class="card-header">'
        '<a class="venue venue-link" href="/venues/' + escape(str(deal.get("venue_id")), quote=True)
        + '">' + type_icon + " " + name + "</a>"
        + active_badge
        + '<span class="stars" title="Value score ' + str(score) + '/5">' + stars + "</span>"
        "</div>"
        '<div class="deal-desc">' + desc + "</div>"
        '<div class="meta">🕐 ' + start + " – " + end + " &nbsp;|&nbsp; 📅 " + days_short + "</div>"
        '<div class="address">📍 ' + address + "</div>"
        + venue_links_html
        + '<div class="tags">' + tags_html + verification_html + "</div>"
        + source_html
        + "</div>"
    )


@router.get("/deals/preview", response_class=HTMLResponse)
def deals_preview(
    deal_type: str | None = Query(default=None, alias="type"),
    tag: str | None = Query(default=None),
):
    all_deals = get_all_deals(deal_type=deal_type, tag=tag)
    venue_map = get_venue_map()
    now       = datetime.now()

    active = [d for d in all_deals if is_active_now(d)]
    active.sort(key=lambda d: d.get("value_score", 0), reverse=True)
    top10  = active[:10]

    if not top10:
        top10 = sorted(all_deals, key=lambda d: d.get("value_score", 0), reverse=True)[:10]
        status_html = '<div class="status inactive">⏰ No active deals right now — showing top deals by value</div>'
    else:
        status_html = '<div class="status active">🟢 ' + str(len(active)) + " active deal(s) right now in Kraków</div>"

    cards_html = "\n".join(build_card(d, venue_map) for d in top10)
    venue_pills = []
    for venue in sorted(venue_map.values(), key=lambda item: item.get("name", "")):
        venue_name = escape(str(venue.get("name", "")))
        maps_url = venue.get("maps_url") or (
            "https://www.google.com/maps/search/?api=1&query="
            + str(venue.get("lat", "")) + "," + str(venue.get("lng", ""))
        )
        venue_pills.append(
            '<a class="venue-pill" href="' + escape(str(maps_url), quote=True)
            + '" target="_blank" rel="noopener">📍 ' + venue_name + "</a>"
        )

    html = (
        "<!DOCTYPE html><html lang='pl'><head>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        "<title>Happy Hours Kraków</title>"
        "<style>" + CSS + "</style>"
        "</head><body>"
        "<main><header class='hero'><div class='logo'><span class='logo-mark'>🍺</span><span>Happy Hours Kraków</span></div>"
        "<p class='subtitle'>Updated " + now.strftime("%A, %H:%M") + " · Fresh local deals</p>"
        "</header>"
        + status_html
        + '<form class="filters" method="get" action="/deals/preview">'
        + '<select class="filter" name="type"><option value="">All types</option>'
        + '<option value="beer">Beer</option><option value="food">Food</option>'
        + '<option value="cocktails">Cocktails</option><option value="shots">Shots</option>'
        + '</select><select class="filter" name="tag"><option value="">All tags</option>'
        + '<option value="cheap">Cheap</option><option value="student">Student</option>'
        + '<option value="craft">Craft</option><option value="date">Date</option>'
        + '</select><button class="filter" type="submit">Filter deals</button></form>'
        + '<div class="grid">' + cards_html + "</div>"
        + '<section class="map-panel"><div class="map-title">Explore venues on the map</div>'
        + '<div class="venue-list">' + "".join(venue_pills) + "</div></section>"
        "<div class='footer'>Fresh local deals · <a href='/docs'>API docs</a></div></main>"
        "</body></html>"
    )

    return HTMLResponse(content=html)
