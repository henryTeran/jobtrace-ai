"""Repositories for email domain persistence and querying."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JobEmail
from app.schemas import PaginationMeta
from app.services.monthly_report_service import list_job_emails


class JobEmailRepository:
    """Data access abstraction for job email queries."""

    def __init__(self, db: Session):
        self.db = db

    def list_paginated(
        self,
        months: list[str] | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
        provider: str | None,
        status: str | None,
        company: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        q: str | None,
    ) -> tuple[list[JobEmail], PaginationMeta]:
        """Return paginated emails with filters and sorting."""

        return list_job_emails(
            db=self.db,
            months=months,
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

    def get_by_id(self, email_id: int) -> JobEmail | None:
        """Return a single email by its primary key."""

        return self.db.execute(
            select(JobEmail).where(JobEmail.id == email_id)
        ).scalar_one_or_none()

    def update_status(self, email_id: int, status: str) -> JobEmail | None:
        """Update the status field of an email. Returns the updated row or None if not found."""

        row = self.get_by_id(email_id)
        if row is None:
            return None
        row.status = status
        self.db.commit()
        self.db.refresh(row)
        return row
