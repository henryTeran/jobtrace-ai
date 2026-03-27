"""Email synchronization endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EmailListResponse, JobEmailOut, SyncRequest, SyncResponse, StatusType
from app.services.monthly_report_service import list_job_emails
from app.services.sync_service import sync_emails


router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("", response_model=EmailListResponse)
def list_emails(
    month: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
    provider: Literal["gmail", "outlook"] | None = Query(default=None),
    status: StatusType | None = Query(default=None),
    company: str | None = Query(default=None, max_length=100),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    q: str | None = Query(default=None, max_length=100, description="Recherche dans sujet, snippet, entreprise, poste"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: Literal["received_at", "created_at", "company", "status", "provider", "subject"] = Query(
        default="received_at"
    ),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    db: Session = Depends(get_db),
) -> EmailListResponse:
    """Return paginated, sortable and filterable list of stored job emails."""

    rows, pagination = list_job_emails(
        db=db,
        months=[month] if month else None,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        provider=provider,
        status=status,
        company=company,
        date_from=date_from,
        date_to=date_to,
        q=q,
    )
    return EmailListResponse(items=[JobEmailOut.model_validate(row) for row in rows], pagination=pagination)


@router.post("/sync", response_model=SyncResponse)
def sync_endpoint(payload: SyncRequest, db: Session = Depends(get_db)) -> SyncResponse:
    """Sync Gmail/Outlook messages, filter job emails and persist them."""

    try:
        stats = sync_emails(
            db=db,
            providers=payload.providers,
            limit_per_provider=payload.limit_per_provider,
            mode=payload.mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SyncResponse(
        fetched=stats.fetched,
        filtered=stats.filtered,
        inserted=stats.inserted,
        duplicates=stats.duplicates,
    )
