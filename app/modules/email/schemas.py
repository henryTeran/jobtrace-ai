"""Schemas dedicated to the email module.

For the first migration lot, schemas are re-exported from the existing module to
avoid behavior changes while introducing the new architecture.
"""

from __future__ import annotations

from app.schemas import EmailListResponse, EmailStats, JobEmailOut, StatusType, StatusUpdateRequest, SyncRequest, SyncResponse

__all__ = [
    "StatusType",
    "StatusUpdateRequest",
    "SyncRequest",
    "SyncResponse",
    "JobEmailOut",
    "EmailListResponse",
    "EmailStats",
]
