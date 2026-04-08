from fastapi import APIRouter, Query
from models.deal import Deal
from services.deals import get_all_deals, get_active_deals

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", response_model=list[Deal])
def list_deals(active_now: bool = Query(default=False)):
    if active_now:
        return get_active_deals()
    return get_all_deals()