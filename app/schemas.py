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
    limit_per_provider: int = Field(default=50, ge=1, le=200)


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


class PdfRequest(BaseModel):
    """PDF generation request."""

    months: list[str] | None = None
    output_filename: str | None = None


class PdfResponse(BaseModel):
    """PDF generation response."""

    file_path: str
    months: list[str]
    rows: int
