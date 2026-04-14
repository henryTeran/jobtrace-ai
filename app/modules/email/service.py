"""Business services for email querying and synchronization."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy.orm import Session

from app.modules.email.repositories.job_email_repository import JobEmailRepository
from app.modules.email.schemas import EmailListResponse, EmailStats, JobEmailOut, StatusType, StatusUpdateRequest, SyncRequest, SyncResponse
from app.services.monthly_report_service import get_email_stats
from app.services.sync_service import sync_emails


class EmailService:
    """Application service for email use cases."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = JobEmailRepository(db)

    def list_emails(
        self,
        month: str | None,
        provider: Literal["gmail", "outlook"] | None,
        status: StatusType | None,
        company: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        q: str | None,
        page: int,
        page_size: int,
        sort_by: Literal["received_at", "created_at", "company", "status", "provider", "subject"],
        sort_order: Literal["asc", "desc"],
    ) -> EmailListResponse:
        """Return paginated and filterable email list."""

        rows, pagination = self.repo.list_paginated(
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
        items = [JobEmailOut.model_validate(row) for row in rows]
        return EmailListResponse(items=items, pagination=pagination)

    def get_stats(self) -> EmailStats:
        """Return aggregated email statistics."""
        result = get_email_stats(self.db)
        return EmailStats(**result)

    def update_status(self, email_id: int, status: StatusType) -> JobEmailOut | None:
        """Manually update the status of a stored email."""

        row = self.repo.update_status(email_id, status)
        if row is None:
            return None
        return JobEmailOut.model_validate(row)

    def sync(self, payload: SyncRequest) -> SyncResponse:
        """Synchronize emails from selected providers."""

        stats = sync_emails(
            db=self.db,
            providers=payload.providers,
            limit_per_provider=payload.limit_per_provider,
            mode=payload.mode,
            from_date=payload.from_date,
            to_date=payload.to_date,
        )
        return SyncResponse(
            fetched=stats.fetched,
            filtered=stats.filtered,
            inserted=stats.inserted,
            duplicates=stats.duplicates,
        )
