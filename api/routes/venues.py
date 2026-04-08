from fastapi import APIRouter
from models.venue import Venue
from services.deals import get_all_venues

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/", response_model=list[Venue])
def list_venues():
    return get_all_venues()