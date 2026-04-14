"""HTTP routes for email module."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import EmailServiceDep
from app.modules.email.schemas import EmailListResponse, EmailStats, JobEmailOut, StatusType, StatusUpdateRequest, SyncRequest, SyncResponse


router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/stats", response_model=EmailStats)
def email_stats(service: EmailServiceDep) -> EmailStats:
    """Return aggregated statistics: total, by status, by provider, monthly trend."""
    return service.get_stats()


@router.get("", response_model=EmailListResponse)
def list_emails(
    service: EmailServiceDep,
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
) -> EmailListResponse:
    """Return paginated, sortable and filterable list of stored job emails."""

    return service.list_emails(
        month=month,
        provider=provider,
        status=status,
        company=company,
        date_from=date_from,
        date_to=date_to,
        q=q,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.patch("/{email_id}/status", response_model=JobEmailOut)
def update_email_status(email_id: int, payload: StatusUpdateRequest, service: EmailServiceDep) -> JobEmailOut:
    """Manually update the status of a stored email."""

    result = service.update_status(email_id, payload.status)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Email {email_id} not found")
    return result


@router.post("/sync", response_model=SyncResponse)
def sync_endpoint(service: EmailServiceDep, payload: SyncRequest) -> SyncResponse:
    """Sync Gmail/Outlook messages, filter job emails and persist them."""

    try:
        return service.sync(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
