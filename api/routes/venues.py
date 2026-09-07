from fastapi import APIRouter, HTTPException
from models.venue import Venue
from services.deals import get_all_deals, get_all_venues, get_venue

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/", response_model=list[Venue])
def list_venues():
    return get_all_venues()


@router.get("/{venue_id}")
def venue_detail(venue_id: str):
    venue = get_venue(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    deals = [
        deal for deal in get_all_deals(venue_id=venue_id)
        if deal.get("status", "verified") != "expired"
    ]
    return {"venue": venue, "deals": deals}