"""Email synchronization endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SyncRequest, SyncResponse
from app.services.sync_service import sync_emails


router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/sync", response_model=SyncResponse)
def sync_endpoint(payload: SyncRequest, db: Session = Depends(get_db)) -> SyncResponse:
    """Sync Gmail/Outlook messages, filter job emails and persist them."""

    try:
        stats = sync_emails(
            db=db,
            providers=payload.providers,
            limit_per_provider=payload.limit_per_provider,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SyncResponse(
        fetched=stats.fetched,
        filtered=stats.filtered,
        inserted=stats.inserted,
        duplicates=stats.duplicates,
    )
