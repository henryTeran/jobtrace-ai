"""Synchronization service orchestrating providers and persistence."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.connectors.gmail_connector import GmailConnector
from app.connectors.outlook_connector import OutlookConnector
from app.models import JobEmail
from app.schemas import EmailNormalized
from app.services.email_extractor import extract_email_data
from app.services.email_filter import is_job_related_with_mode
from app.services.email_normalizer import normalize_gmail_message, normalize_outlook_message
from app.utils.dates import month_key_from_datetime


logger = logging.getLogger(__name__)


@dataclass
class SyncStats:
    """Summary of one synchronization run."""

    fetched: int = 0
    filtered: int = 0
    inserted: int = 0
    duplicates: int = 0


def sync_emails(
    db: Session,
    providers: list[str],
    limit_per_provider: int = 50,
    mode: str = "strict",
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> SyncStats:
    """Synchronize emails for selected providers and persist job-related rows."""

    stats = SyncStats()

    if "gmail" in providers:
        stats = _sync_gmail(
            db=db,
            limit=limit_per_provider,
            stats=stats,
            mode=mode,
            from_date=from_date,
            to_date=to_date,
        )
    if "outlook" in providers:
        stats = _sync_outlook(
            db=db,
            limit=limit_per_provider,
            stats=stats,
            mode=mode,
            from_date=from_date,
            to_date=to_date,
        )

    return stats


def _sync_gmail(
    db: Session,
    limit: int,
    stats: SyncStats,
    mode: str,
    from_date: datetime | None,
    to_date: datetime | None,
) -> SyncStats:
    connector = GmailConnector(db)
    raw_messages = connector.get_messages(limit=limit, from_date=from_date, to_date=to_date)
    stats.fetched += len(raw_messages)

    for raw in raw_messages:
        normalized = normalize_gmail_message(raw, connector)
        _process_one_email(db=db, normalized=normalized, stats=stats, mode=mode)

    return stats


def _sync_outlook(
    db: Session,
    limit: int,
    stats: SyncStats,
    mode: str,
    from_date: datetime | None,
    to_date: datetime | None,
) -> SyncStats:
    connector = OutlookConnector(db)
    raw_messages = connector.get_messages(limit=limit, from_date=from_date, to_date=to_date)
    stats.fetched += len(raw_messages)

    for raw in raw_messages:
        normalized = normalize_outlook_message(raw)
        _process_one_email(db=db, normalized=normalized, stats=stats, mode=mode)

    return stats


def _process_one_email(db: Session, normalized: EmailNormalized, stats: SyncStats, mode: str) -> None:
    if not normalized.message_id:
        return

    if not is_job_related_with_mode(normalized, mode=mode):
        return

    stats.filtered += 1
    extracted = extract_email_data(normalized)

    row = JobEmail(
        provider=normalized.provider,
        message_id=normalized.message_id,
        thread_id=normalized.thread_id,
        subject=normalized.subject,
        sender_email=normalized.from_email,
        sender_name=normalized.from_name,
        received_at=normalized.received_at,
        month_key=month_key_from_datetime(normalized.received_at),
        company=extracted.company,
        job_title=extracted.job_title,
        status=extracted.status,
        snippet=normalized.snippet,
        body_text=normalized.body_text,
    )

    db.add(row)
    try:
        db.commit()
        stats.inserted += 1
    except IntegrityError:
        db.rollback()
        stats.duplicates += 1
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to persist email %s: %s", normalized.message_id, exc)
