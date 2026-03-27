"""Tests for filtering and extraction refinements."""

from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import EmailNormalized
from app.services.email_extractor import extract_email_data
from app.services.email_filter import is_job_related, is_job_related_with_mode


def _email(subject: str, snippet: str = "", body_text: str = "", sender: str = "jobs@example.com") -> EmailNormalized:
    return EmailNormalized(
        provider="gmail",
        message_id="m1",
        thread_id="t1",
        subject=subject,
        from_email=sender,
        from_name="Sender",
        received_at=datetime.now(timezone.utc),
        snippet=snippet,
        body_text=body_text,
    )


def test_offer_alert_is_excluded() -> None:
    email = _email(
        subject="Jobs you may be interested in",
        snippet="Daily jobs for you",
        body_text="New jobs near you",
        sender="jobs-noreply@linkedin.com",
    )
    assert is_job_related(email) is False


def test_sent_application_is_included() -> None:
    email = _email(
        subject="Application for Backend Engineer",
        snippet="I am applying for the Backend Engineer role",
        body_text="Please find attached my resume",
        sender="me@hotmail.com",
    )
    assert is_job_related(email) is True
    extracted = extract_email_data(email)
    assert extracted.status in {"candidature", "accuse_reception"}


def test_negative_outcome_detected_as_refus() -> None:
    email = _email(
        subject="Update on your application",
        snippet="We regret to inform you that you were not selected",
        body_text="Unfortunately we will not proceed",
    )
    extracted = extract_email_data(email)
    assert extracted.status == "refus"


def test_positive_outcome_detected_as_suivi_or_entretien() -> None:
    email = _email(
        subject="Congratulations! Next steps for your application",
        snippet="We are pleased to move forward with your profile",
        body_text="Let's schedule an interview",
    )
    extracted = extract_email_data(email)
    assert extracted.status in {"suivi", "entretien"}


def test_strict_vs_full_mode_domain_only_email() -> None:
    email = _email(
        subject="Action required in Greenhouse",
        snippet="Please review candidate updates",
        body_text="Open this link: https://boards.greenhouse.io/...",
        sender="no-reply@greenhouse.io",
    )
    assert is_job_related_with_mode(email, mode="strict") is False
    assert is_job_related_with_mode(email, mode="full") is True
    assert is_job_related(email) is False


def test_strict_excludes_linkedin_offer_recommendation() -> None:
    email = _email(
        subject="Le poste de Software Engineer (Frontend) chez Lorum pourrait vous convenir",
        snippet="Jobs you may be interested in",
        body_text="recommended jobs for you",
        sender="jobs-listings@linkedin.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_strict_excludes_github_notification() -> None:
    email = _email(
        subject="[repo] chore(deps): bump npm package",
        snippet="PR #10",
        body_text="repos updates",
        sender="notifications@github.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_strict_excludes_account_security_email() -> None:
    email = _email(
        subject="Votre code a usage unique",
        snippet="New app connected to your Microsoft account",
        body_text="account security",
        sender="account-security-noreply@accountprotection.microsoft.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False
