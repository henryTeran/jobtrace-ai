"""Pydantic schemas for API payloads and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


StatusType = Literal[
    "candidature",
    "accuse_reception",
    "entretien",
    "refus",
    "recruteur_contact",
    "suivi",
    "inconnu",
]

SyncModeType = Literal["strict", "full"]


class EmailNormalized(BaseModel):
    """Canonical email shape used internally across providers."""

    provider: Literal["gmail", "outlook"]
    message_id: str
    thread_id: str | None = None
    subject: str = ""
    from_email: str | None = None
    from_name: str | None = None
    received_at: datetime
    snippet: str | None = None
    body_text: str | None = None


class SyncRequest(BaseModel):
    """Manual synchronization request options."""

    providers: list[Literal["gmail", "outlook"]] = Field(default_factory=lambda: ["gmail", "outlook"])
    limit_per_provider: int = Field(default=50, ge=1, le=5000)
    mode: SyncModeType = "strict"
    from_date: datetime | None = None
    to_date: datetime | None = None


class SyncResponse(BaseModel):
    """Synchronization result summary."""

    fetched: int
    filtered: int
    inserted: int
    duplicates: int


class JobEmailOut(BaseModel):
    """Public representation of a stored job email."""

    id: int
    provider: str
    message_id: str
    thread_id: str | None = None
    subject: str
    sender_email: str | None = None
    sender_name: str | None = None
    received_at: datetime
    month_key: str
    company: str | None = None
    job_title: str | None = None
    status: StatusType
    snippet: str | None = None
    body_text: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MonthlyReportResponse(BaseModel):
    """Monthly grouped report response."""

    data: dict[str, list[JobEmailOut]]
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    """Pagination metadata for list endpoints."""

    page: int
    page_size: int
    total: int
    total_pages: int


class EmailListResponse(BaseModel):
    """Paginated list of stored emails."""

    items: list[JobEmailOut]
    pagination: PaginationMeta


class OAuthProviderStatus(BaseModel):
    """OAuth connectivity status for one provider."""

    provider: str
    connected: bool
    updated_at: datetime | None = None


class OAuthStatusResponse(BaseModel):
    """OAuth connectivity status for all providers."""

    providers: list[OAuthProviderStatus]


class PdfRequest(BaseModel):
    """PDF generation request."""

    months: list[str] | None = None
    output_filename: str | None = None


class PdfFilteredRequest(BaseModel):
    """Filtered PDF generation request."""

    provider: Literal["gmail", "outlook"] | None = None
    status: StatusType | None = None
    q: str | None = Field(default=None, max_length=100)
    date_from: datetime | None = None
    date_to: datetime | None = None
    sort_by: Literal["received_at", "created_at", "company", "status", "provider", "subject"] = "received_at"
    sort_order: Literal["asc", "desc"] = "desc"
    output_filename: str | None = None


class PdfResponse(BaseModel):
    """PDF generation response."""

    file_path: str
    months: list[str]
    rows: int


class StatusUpdateRequest(BaseModel):
    """Request body for manually updating an email status."""

    status: StatusType


class MonthCount(BaseModel):
    """Email count for one month."""

    month: str
    count: int


class EmailStats(BaseModel):
    """Aggregated email statistics for the dashboard."""

    total: int
    by_status: dict[str, int]
    by_provider: dict[str, int]
    by_month: list[MonthCount]
