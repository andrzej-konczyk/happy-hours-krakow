from datetime import datetime
from db.client import get_client


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def is_active_now(deal: dict) -> bool:
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


def get_all_venues():
    client = get_client()
    return client.table("venues").select("*").execute().data


def get_all_deals():
    client = get_client()
    return client.table("deals").select("*").execute().data


def get_active_deals():
    all_deals = get_all_deals()
    return [deal for deal in all_deals if is_active_now(deal)]