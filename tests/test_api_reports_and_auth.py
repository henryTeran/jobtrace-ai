"""API tests for reports pagination and OAuth status."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import JobEmail, OAuthToken


def _seed_job_emails(db_session: Session) -> None:
    rows = [
        JobEmail(
            provider="gmail",
            message_id="g1",
            thread_id="t1",
            subject="Application received",
            sender_email="jobs@acme.com",
            sender_name="Acme",
            received_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
            month_key="2026-03",
            company="Acme",
            job_title="Backend Engineer",
            status="accuse_reception",
            snippet="thank you for applying",
            body_text="body",
        ),
        JobEmail(
            provider="outlook",
            message_id="o1",
            thread_id="t2",
            subject="Interview invitation",
            sender_email="talent@globex.com",
            sender_name="Globex",
            received_at=datetime(2026, 3, 5, 13, 0, tzinfo=timezone.utc),
            month_key="2026-03",
            company="Globex",
            job_title="Python Developer",
            status="entretien",
            snippet="interview",
            body_text="body",
        ),
        JobEmail(
            provider="gmail",
            message_id="g2",
            thread_id="t3",
            subject="Unfortunately",
            sender_email="noreply@initech.com",
            sender_name="Initech",
            received_at=datetime(2026, 2, 20, 8, 0, tzinfo=timezone.utc),
            month_key="2026-02",
            company="Initech",
            job_title="Data Engineer",
            status="refus",
            snippet="unfortunately",
            body_text="body",
        ),
    ]
    db_session.add_all(rows)
    db_session.commit()


def test_auth_status_endpoint(client, db_session: Session) -> None:
    db_session.add(OAuthToken(provider="gmail", token_json='{"access_token":"x"}'))
    db_session.commit()

    response = client.get("/auth/status")

    assert response.status_code == 200
    body = response.json()
    status_by_provider = {item["provider"]: item for item in body["providers"]}
    assert status_by_provider["gmail"]["connected"] is True
    assert status_by_provider["outlook"]["connected"] is False


def test_reports_monthly_pagination_and_sorting(client, db_session: Session) -> None:
    _seed_job_emails(db_session)

    response = client.get(
        "/reports/monthly",
        params={
            "page": 1,
            "page_size": 2,
            "sort_by": "received_at",
            "sort_order": "desc",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] == 3
    assert payload["pagination"]["total_pages"] == 2

    flattened = []
    for _, month_rows in payload["data"].items():
        flattened.extend(month_rows)
    assert len(flattened) == 2
    assert flattened[0]["message_id"] == "g1"


def test_emails_list_endpoint_pagination(client, db_session: Session) -> None:
    _seed_job_emails(db_session)

    response = client.get(
        "/emails",
        params={
            "page": 2,
            "page_size": 2,
            "sort_by": "received_at",
            "sort_order": "desc",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["page"] == 2
    assert payload["pagination"]["total"] == 3
    assert len(payload["items"]) == 1
    assert payload["items"][0]["message_id"] == "g2"
