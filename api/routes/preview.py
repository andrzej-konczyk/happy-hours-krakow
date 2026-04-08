from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
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
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f1117;
    color: #e0e0e0;
    padding: 24px 16px;
}
h1 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 4px;
    color: #f5c518;
}
.subtitle {
    text-align: center;
    color: #888;
    margin-bottom: 20px;
    font-size: 0.9rem;
}
.status {
    text-align: center;
    padding: 10px 20px;
    border-radius: 8px;
    margin-bottom: 24px;
    font-weight: 600;
}
.status.active   { background: #1a3a1a; color: #4caf50; }
.status.inactive { background: #2a2a1a; color: #f5c518; }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    max-width: 1100px;
    margin: 0 auto;
}
.card {
    background: #1e2130;
    border: 1px solid #2e3250;
    border-radius: 12px;
    padding: 18px;
    transition: transform 0.15s;
}
.card:hover { transform: translateY(-2px); border-color: #f5c518; }
.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}
.venue { font-weight: 700; font-size: 1rem; flex: 1; color: #ffffff; }
.stars { color: #f5c518; font-size: 0.85rem; letter-spacing: 1px; }
.badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 99px; font-weight: 700; }
.active-badge { background: #1a3a1a; color: #4caf50; }
.deal-desc { font-size: 1rem; color: #c0c8e0; margin-bottom: 10px; line-height: 1.4; }
.meta { font-size: 0.82rem; color: #888; margin-bottom: 6px; }
.address { font-size: 0.8rem; color: #666; margin-bottom: 10px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { background: #2a2d45; color: #a0aec0; font-size: 0.75rem; padding: 3px 10px; border-radius: 99px; }
.footer { text-align: center; margin-top: 32px; color: #444; font-size: 0.8rem; }
"""


def format_time(t: str) -> str:
    return t[:5] if t else "?"


def render_stars(score: int) -> str:
    return "★" * score + "☆" * (5 - score)


def get_venue_map() -> dict:
    client = get_client()
    venues = client.table("venues").select("id, name, address").execute()
    return {v["id"]: v for v in venues.data}


def build_card(deal: dict, venue_map: dict) -> str:
    venue    = venue_map.get(str(deal.get("venue_id")), {})
    name     = venue.get("name", "Unknown venue")
    address  = venue.get("address", "")
    desc     = deal.get("description", "").capitalize()
    start    = format_time(deal.get("start_time", ""))
    end      = format_time(deal.get("end_time", ""))
    score    = deal.get("value_score", 1)
    dtype    = deal.get("type", "mixed")
    tags     = deal.get("tags") or []
    days     = deal.get("days_of_week") or []

    type_icon = TYPE_EMOJI.get(dtype, "🎉")
    stars     = render_stars(score)
    days_short = ", ".join(d[:3].capitalize() for d in days)

    tags_html = " ".join(
        '<span class="tag">' + TAG_EMOJI.get(t, "•") + " " + t + "</span>"
        for t in tags
    )

    active_badge = ""
    if is_active_now(deal):
        active_badge = '<span class="badge active-badge">● ACTIVE NOW</span>'

    return (
        '<div class="card">'
        '<div class="card-header">'
        '<span class="venue">' + type_icon + " " + name + "</span>"
        + active_badge
        + '<span class="stars" title="Value score ' + str(score) + '/5">' + stars + "</span>"
        "</div>"
        '<div class="deal-desc">' + desc + "</div>"
        '<div class="meta">🕐 ' + start + " – " + end + " &nbsp;|&nbsp; 📅 " + days_short + "</div>"
        '<div class="address">📍 ' + address + "</div>"
        '<div class="tags">' + tags_html + "</div>"
        "</div>"
    )


@router.get("/deals/preview", response_class=HTMLResponse)
def deals_preview():
    all_deals = get_all_deals()
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

    html = (
        "<!DOCTYPE html><html lang='en'><head>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        "<title>Happy Hours Kraków</title>"
        "<style>" + CSS + "</style>"
        "</head><body>"
        "<h1>🍺 Happy Hours Kraków</h1>"
        "<p class='subtitle'>Updated " + now.strftime("%A, %H:%M") + " · Top deals sorted by value</p>"
        + status_html
        + '<div class="grid">' + cards_html + "</div>"
        "<div class='footer'>Happy Hours Kraków MVP · <a href='/docs' style='color:#555'>API docs</a></div>"
        "</body></html>"
    )

    return HTMLResponse(content=html)