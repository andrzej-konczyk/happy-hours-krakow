import secrets
from datetime import date, datetime, time
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from core.config import settings
from db.client import get_client

router = APIRouter(prefix="/admin", tags=["admin"])


class DealCreate(BaseModel):
    venue_id: UUID
    description: str = Field(min_length=3, max_length=500)
    start_time: time
    end_time: time
    days_of_week: list[str] = Field(min_length=1)
    type: str = "mixed"
    tags: list[str] = Field(default_factory=list)
    value_score: int = Field(default=1, ge=1, le=5)
    source_url: str | None = None
    valid_until: date | None = None


class DealStatusUpdate(BaseModel):
    status: str
    valid_until: date | None = None


def require_admin(x_admin_token: str | None) -> None:
    if not settings.ADMIN_TOKEN or not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API is not configured",
        )
    if not secrets.compare_digest(x_admin_token, settings.ADMIN_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )


@router.post("/deals", status_code=status.HTTP_201_CREATED)
def create_deal(deal: DealCreate, x_admin_token: str | None = Header(default=None)):
    require_admin(x_admin_token)
    if deal.start_time == deal.end_time:
        raise HTTPException(status_code=422, detail="Deal times must differ")
    row = deal.model_dump(mode="json")
    row["venue_id"] = str(deal.venue_id)
    row["status"] = "pending"
    row["verified_at"] = None
    row["confidence"] = "manual"
    row["dedupe_key"] = (
        f"manual:{deal.venue_id}:{deal.description[:40]}:"
        f"{deal.start_time}:{deal.end_time}:{','.join(deal.days_of_week)}"
    )
    result = get_client().table("deals").insert(row).execute()
    return result.data[0]


@router.patch("/deals/{deal_id}/status")
def update_deal_status(
    deal_id: UUID,
    update: DealStatusUpdate,
    x_admin_token: str | None = Header(default=None),
):
    require_admin(x_admin_token)
    if update.status not in {"pending", "verified", "expired"}:
        raise HTTPException(status_code=422, detail="Invalid deal status")
    values = {"status": update.status, "valid_until": update.valid_until.isoformat() if update.valid_until else None}
    if update.status == "verified":
        values["verified_at"] = datetime.now().isoformat()
    result = get_client().table("deals").update(values).eq("id", str(deal_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Deal not found")
    return result.data[0]


@router.post("/deals/{deal_id}/expire")
def expire_deal(deal_id: UUID, x_admin_token: str | None = Header(default=None)):
    require_admin(x_admin_token)
    result = get_client().table("deals").update({
        "status": "expired",
        "valid_until": date.today().isoformat(),
    }).eq("id", str(deal_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Deal not found")
    return result.data[0]
