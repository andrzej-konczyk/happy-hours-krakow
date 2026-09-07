from fastapi import APIRouter, HTTPException
import httpx
from postgrest.exceptions import APIError

from core.config import settings
from db.client import get_client

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/ready")
def readiness_check():
    """Report whether the API can reach its configured database."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise HTTPException(status_code=503, detail="Database is not configured")

    try:
        get_client().table("venues").select("id").limit(1).execute()
    except (APIError, httpx.HTTPError, OSError, TimeoutError, ValueError) as error:
        raise HTTPException(status_code=503, detail="Database is unavailable") from error

    return {"status": "ready", "database": "ok"}