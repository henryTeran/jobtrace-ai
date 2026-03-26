"""Normalize provider-specific emails into a common schema."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from app.connectors.gmail_connector import GmailConnector
from app.schemas import EmailNormalized


logger = logging.getLogger(__name__)


def _parse_gmail_headers(message: dict[str, Any]) -> dict[str, str]:
    headers = {}
    for item in message.get("payload", {}).get("headers", []) or []:
        name = item.get("name")
        value = item.get("value")
        if name and value:
            headers[name.lower()] = value
    return headers


def normalize_gmail_message(raw: dict[str, Any], connector: GmailConnector) -> EmailNormalized:
    """Normalize a Gmail API message payload."""

    headers = _parse_gmail_headers(raw)
    from_raw = headers.get("from", "")
    from_name = None
    from_email = from_raw
    if "<" in from_raw and ">" in from_raw:
        from_name = from_raw.split("<", 1)[0].strip().strip('"')
        from_email = from_raw.split("<", 1)[1].split(">", 1)[0].strip()

    received_at = datetime.now(timezone.utc)
    if raw.get("internalDate"):
        try:
            received_at = datetime.fromtimestamp(int(raw["internalDate"]) / 1000, tz=timezone.utc)
        except Exception:
            logger.warning("Invalid Gmail internalDate for id=%s", raw.get("id"))
    elif headers.get("date"):
        try:
            parsed = parsedate_to_datetime(headers["date"])
            received_at = parsed.astimezone(timezone.utc)
        except Exception:
            logger.warning("Invalid Gmail date header for id=%s", raw.get("id"))

    body_text = connector.extract_body_text(raw.get("payload", {}))

    return EmailNormalized(
        provider="gmail",
        message_id=raw.get("id", ""),
        thread_id=raw.get("threadId"),
        subject=headers.get("subject", ""),
        from_email=from_email,
        from_name=from_name,
        received_at=received_at,
        snippet=raw.get("snippet"),
        body_text=body_text,
    )


def normalize_outlook_message(raw: dict[str, Any]) -> EmailNormalized:
    """Normalize a Microsoft Graph message payload."""

    sender = (raw.get("from") or {}).get("emailAddress") or {}
    received_raw = raw.get("receivedDateTime")
    received_at = datetime.now(timezone.utc)
    if received_raw:
        try:
            received_at = datetime.fromisoformat(received_raw.replace("Z", "+00:00")).astimezone(timezone.utc)
        except Exception:
            logger.warning("Invalid Outlook receivedDateTime for id=%s", raw.get("id"))

    body = (raw.get("body") or {}).get("content") or ""
    body_preview = raw.get("bodyPreview") or ""

    return EmailNormalized(
        provider="outlook",
        message_id=raw.get("id", ""),
        thread_id=raw.get("conversationId"),
        subject=raw.get("subject") or "",
        from_email=sender.get("address"),
        from_name=sender.get("name"),
        received_at=received_at,
        snippet=body_preview,
        body_text=body or body_preview,
    )
