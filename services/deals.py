from datetime import date, datetime
from db.client import get_client


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def is_active_now(deal: dict) -> bool:
    if not is_visible(deal):
        return False
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_day  = DAYS[now.weekday()]

    days = deal.get("days_of_week") or []
    if current_day not in days:
        return False

    start = deal.get("start_time", "")[:5]  # HH:MM:SS → HH:MM
    end   = deal.get("end_time",   "")[:5]

    if not start or not end:
        return False

    # overnight deal (np. 22:00 → 02:00)
    if start > end:
        return current_time >= start or current_time <= end
    else:
        return start <= current_time <= end


def is_visible(deal: dict, today: date | None = None) -> bool:
    """Keep expired deals out while remaining compatible with legacy rows."""
    if deal.get("status") == "expired":
        return False
    valid_until = deal.get("valid_until")
    if not valid_until:
        return True
    if isinstance(valid_until, str):
        valid_until = date.fromisoformat(valid_until[:10])
    return valid_until >= (today or date.today())


def get_all_venues():
    client = get_client()
    return client.table("venues").select("*").execute().data


def get_all_deals(
    *,
    active_now: bool = False,
    deal_type: str | None = None,
    tag: str | None = None,
    venue_id: str | None = None,
    day: str | None = None,
    status: str | None = None,
):
    client = get_client()
    deals = [
        deal for deal in client.table("deals").select("*").execute().data
        if is_visible(deal)
    ]
    if status:
        deals = [deal for deal in deals if deal.get("status", "verified") == status]
    if deal_type:
        deals = [deal for deal in deals if deal.get("type") == deal_type]
    if tag:
        deals = [deal for deal in deals if tag in (deal.get("tags") or [])]
    if venue_id:
        deals = [deal for deal in deals if str(deal.get("venue_id")) == venue_id]
    if day:
        deals = [deal for deal in deals if day in (deal.get("days_of_week") or [])]
    if active_now:
        deals = [deal for deal in deals if is_active_now(deal)]
    return deals


def get_active_deals():
    return get_all_deals(active_now=True)