from fastapi import APIRouter, Query
from models.deal import Deal
from services.deals import get_all_deals

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", response_model=list[Deal])
def list_deals(
    active_now: bool = Query(default=False),
    deal_type: str | None = Query(default=None, alias="type"),
    tag: str | None = Query(default=None),
    venue_id: str | None = Query(default=None),
    day: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    return get_all_deals(
        active_now=active_now,
        deal_type=deal_type,
        tag=tag,
        venue_id=venue_id,
        day=day,
        status=status,
    )