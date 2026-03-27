"""Tests for /emails/sync with mocked Gmail and Outlook connectors."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session


# 2026-03-10T00:00:00Z  →  1773100800000 ms
# 2026-03-05T00:00:00Z  →  1772668800000 ms
# 2026-03-01T00:00:00Z  →  1772323200000 ms
RAW_GMAIL_MESSAGES = [
    {
        "id": "gmock1",
        "threadId": "thread1",
        "internalDate": "1773100800000",
        "snippet": "thank you for applying to the Backend Engineer position",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Application received - Backend Engineer at Acme Corp"},
                {"name": "From", "value": "jobs@acme.com"},
            ],
            "body": {},
            "parts": [],
        },
    },
    {
        "id": "gmock2",
        "threadId": "thread2",
        "internalDate": "1772668800000",
        "snippet": "We regret to inform you",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Unfortunately - Data Engineer role"},
                {"name": "From", "value": "noreply@initech.com"},
            ],
            "body": {},
            "parts": [],
        },
    },
    {
        "id": "gmock3",
        "threadId": "thread3",
        "internalDate": "1772323200000",
        "snippet": "Weekend BBQ invite",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "BBQ this Saturday !"},
                {"name": "From", "value": "friend@example.com"},
            ],
            "body": {},
            "parts": [],
        },
    },
]

RAW_OUTLOOK_MESSAGES = [
    {
        "id": "omock1",
        "conversationId": "conv1",
        "subject": "Interview invitation - Python Developer at Globex",
        "from": {"emailAddress": {"name": "Globex HR", "address": "talent@globex.com"}},
        "receivedDateTime": "2026-03-06T10:00:00Z",
        "bodyPreview": "We would like to schedule an interview",
        "body": {"content": "interview schedule"},
    }
]


def _mock_gmail_connector(db: Session) -> MagicMock:
    mock = MagicMock()
    mock.get_messages.return_value = RAW_GMAIL_MESSAGES
    mock.extract_body_text.return_value = ""
    return mock


def _mock_outlook_connector(db: Session) -> MagicMock:
    mock = MagicMock()
    mock.get_messages.return_value = RAW_OUTLOOK_MESSAGES
    return mock


def test_sync_gmail_filters_and_inserts(client, db_session: Session) -> None:
    """Only job-related Gmail emails should be persisted; social emails dropped."""

    with (
        patch("app.services.sync_service.GmailConnector", side_effect=_mock_gmail_connector),
        patch("app.services.sync_service.OutlookConnector", side_effect=_mock_outlook_connector),
    ):
        response = client.post(
            "/emails/sync",
            json={"providers": ["gmail"], "limit_per_provider": 50},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["fetched"] == 3
    assert body["filtered"] == 2
    assert body["inserted"] == 2
    assert body["duplicates"] == 0


def test_sync_outlook_inserts(client, db_session: Session) -> None:
    with (
        patch("app.services.sync_service.GmailConnector", side_effect=_mock_gmail_connector),
        patch("app.services.sync_service.OutlookConnector", side_effect=_mock_outlook_connector),
    ):
        response = client.post(
            "/emails/sync",
            json={"providers": ["outlook"], "limit_per_provider": 50},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["fetched"] == 1
    assert body["filtered"] == 1
    assert body["inserted"] == 1


def test_sync_deduplication(client, db_session: Session) -> None:
    """Second sync of the same messages must count as duplicates."""

    with (
        patch("app.services.sync_service.GmailConnector", side_effect=_mock_gmail_connector),
        patch("app.services.sync_service.OutlookConnector", side_effect=_mock_outlook_connector),
    ):
        client.post("/emails/sync", json={"providers": ["gmail"], "limit_per_provider": 50})
        response2 = client.post("/emails/sync", json={"providers": ["gmail"], "limit_per_provider": 50})

    body = response2.json()
    assert body["inserted"] == 0
    assert body["duplicates"] == 2


def test_sync_then_list_with_filters(client, db_session: Session) -> None:
    """After syncing, advanced filters must narrow results correctly."""

    with (
        patch("app.services.sync_service.GmailConnector", side_effect=_mock_gmail_connector),
        patch("app.services.sync_service.OutlookConnector", side_effect=_mock_outlook_connector),
    ):
        client.post(
            "/emails/sync",
            json={"providers": ["gmail", "outlook"], "limit_per_provider": 50},
        )

    # Filter by provider
    resp_gmail = client.get("/emails", params={"provider": "gmail"})
    assert resp_gmail.status_code == 200
    assert all(item["provider"] == "gmail" for item in resp_gmail.json()["items"])

    # Filter by status
    resp_refus = client.get("/emails", params={"status": "refus"})
    assert resp_refus.status_code == 200
    assert all(item["status"] == "refus" for item in resp_refus.json()["items"])

    # Full-text search
    resp_q = client.get("/emails", params={"q": "Interview"})
    assert resp_q.status_code == 200
    assert resp_q.json()["pagination"]["total"] >= 1

    # Date range that includes all inserted rows
    resp_date = client.get(
        "/emails",
        params={"date_from": "2026-01-01T00:00:00", "date_to": "2026-12-31T23:59:59"},
    )
    assert resp_date.status_code == 200
    assert resp_date.json()["pagination"]["total"] == 3
