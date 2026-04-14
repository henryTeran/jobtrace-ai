"""Tests for filtering and extraction refinements."""

from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import EmailNormalized
from app.services.email_extractor import extract_email_data
from app.services.email_filter import is_job_related, is_job_related_with_mode
from app.services.subject_normalizer import normalize_subject


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
    assert is_job_related_with_mode(email, mode="full") is False
    assert is_job_related(email) is False


def test_full_includes_ats_email_with_application_context() -> None:
    email = _email(
        subject="Update on your application via Greenhouse",
        snippet="Your application has moved to next stage",
        body_text="Open this link: https://boards.greenhouse.io/...",
        sender="no-reply@greenhouse.io",
    )
    assert is_job_related_with_mode(email, mode="full") is True


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


def test_strict_excludes_match_jobgether_newsletters() -> None:
    email = _email(
        subject="She applied for months. Nothing. Then one thing changed.",
        snippet="What we're seeing in the data",
        body_text="The #1 reason senior CVs get auto-rejected",
        sender="support@match.jobgether.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_strict_excludes_linkedin_groups_digest() -> None:
    email = _email(
        subject="Ne manquez pas les discussions dans Artificial Intelligence Investors",
        snippet="groups digest",
        body_text="Machine Learning, NLP & Computer Vision",
        sender="groups-noreply@linkedin.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_subject_normalizer_removes_re_and_fwd_prefixes() -> None:
    subject = "Re: Fwd: FW:   Votre candidature : Développeur Full Stack  "
    assert normalize_subject(subject) == "Votre candidature : Développeur Full Stack"


def test_extract_job_title_from_votre_candidature_en_tant_que() -> None:
    email = _email(
        subject="Votre candidature en tant que Full Stack Developer & Database Specialist a été envoyée",
        snippet="",
        body_text="",
        sender="application_no_reply@jobup.ch",
    )
    extracted = extract_email_data(email)
    assert extracted.job_title == "Full Stack Developer & Database Specialist"


def test_extract_job_title_and_company_from_colon_chez_format() -> None:
    email = _email(
        subject="Votre candidature : Développeur Full Stack (h/f) 50-80% chez Board Management Systems SA",
        snippet="",
        body_text="",
        sender="application_no_reply@jobup.ch",
    )
    extracted = extract_email_data(email)
    assert extracted.job_title == "Développeur Full Stack (h/f) 50-80%"
    assert extracted.company == "Board Management Systems Sa"


def test_extract_job_title_from_candidature_dash_format() -> None:
    email = _email(
        subject="Candidature – Apprentissage Dessinateur en architecture CFC 2026",
        snippet="",
        body_text="",
        sender="noreply@example.com",
    )
    extracted = extract_email_data(email)
    assert extracted.job_title == "Apprentissage Dessinateur en architecture CFC 2026"


def test_extract_job_title_from_application_for_format() -> None:
    email = _email(
        subject="Application for Senior Backend Engineer",
        snippet="",
        body_text="",
        sender="noreply@example.com",
    )
    extracted = extract_email_data(email)
    assert extracted.job_title == "Senior Backend Engineer"


def test_extract_job_title_from_bare_role_subject() -> None:
    email = _email(
        subject="Apprentissage Dessinateur en architecture CFC 2026",
        snippet="",
        body_text="",
        sender="someone@example.com",
    )
    extracted = extract_email_data(email)
    assert extracted.job_title == "Apprentissage Dessinateur en architecture CFC 2026"


def test_strict_excludes_academia_mail_updates() -> None:
    email = _email(
        subject='Are you the HENRY TERAN who wrote "Efficacy of three greenhouse screening methods for the..."?',
        snippet="research digest",
        body_text="updates newsletter",
        sender="updates@academia-mail.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_strict_excludes_architecture_related_opportunities() -> None:
    email = _email(
        subject="Candidature – Apprentissage Dessinateur en architecture CFC 2026",
        snippet="",
        body_text="",
        sender="jesus.rodriguez.pesantez@gmail.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_strict_excludes_new_job_opportunities_posted_subject() -> None:
    email = _email(
        subject="New job opportunities posted",
        snippet="Fresh openings this week",
        body_text="Recommended jobs for your profile",
        sender="jobs-noreply@linkedin.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False


def test_strict_excludes_new_full_stack_developer_opportunity_subject() -> None:
    email = _email(
        subject="New Full Stack Developer Opportunity",
        snippet="A new opportunity matches your profile",
        body_text="Apply now to discover this role",
        sender="jobalerts@example.com",
    )
    assert is_job_related_with_mode(email, mode="strict") is False
