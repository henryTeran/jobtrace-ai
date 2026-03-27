"""Extract structured entities from normalized job emails."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas import EmailNormalized, StatusType


@dataclass
class ExtractedEmailData:
    """Result of rule-based extraction."""

    company: str | None
    job_title: str | None
    status: StatusType


STATUS_RULES: list[tuple[StatusType, tuple[str, ...]]] = [
    (
        "refus",
        (
            "unfortunately",
            "regret to inform",
            "not selected",
            "declined",
            "rejected",
            "malheureusement",
            "nous regrettons",
            "pas retenu",
            "no ha sido seleccionado",
        ),
    ),
    (
        "entretien",
        (
            "interview",
            "entretien",
            "schedule",
            "meet with",
            "technical test",
            "assessment",
            "screening call",
        ),
    ),
    (
        "accuse_reception",
        (
            "thank you for applying",
            "application received",
            "we received your application",
            "application submitted",
            "accuse de reception",
            "votre candidature a bien ete envoyee",
            "votre candidature a ete recue",
        ),
    ),
    (
        "suivi",
        (
            "next steps",
            "follow up",
            "suivi",
            "update",
            "we are pleased",
            "congratulations",
            "we are excited",
            "offer",
            "offre",
            "moved forward",
            "shortlisted",
        ),
    ),
    ("recruteur_contact", ("recruiter", "talent acquisition", "reach out", "headhunter", "sourcer")),
    ("candidature", ("application", "application for", "candidature", "candidature pour", "applied", "je postule", "i am applying")),
]

JOB_TITLE_PATTERNS = [
    re.compile(r"for\s+the\s+(.+?)\s+(role|position)", re.IGNORECASE),
    re.compile(r"application\s+for\s+(.+)$", re.IGNORECASE),
    re.compile(r"candidature\s+pour\s+(.+)$", re.IGNORECASE),
    re.compile(r"postule\s+pour\s+(.+)$", re.IGNORECASE),
    re.compile(r"poste\s+de\s+(.+)$", re.IGNORECASE),
]


def extract_email_data(email: EmailNormalized) -> ExtractedEmailData:
    """Extract company, job title and status from normalized email."""

    text = " ".join([email.subject or "", email.snippet or "", email.body_text or ""]).strip()
    lowered = text.lower()

    status: StatusType = "inconnu"
    for candidate_status, needles in STATUS_RULES:
        if any(needle in lowered for needle in needles):
            status = candidate_status
            break

    company = _extract_company(email)
    job_title = _extract_job_title(email.subject or "")

    return ExtractedEmailData(company=company, job_title=job_title, status=status)


def _extract_company(email: EmailNormalized) -> str | None:
    sender = (email.from_email or "").lower()
    if "@" in sender:
        domain = sender.split("@", 1)[1]
        root = domain.split(".")[0]
        if root not in {"gmail", "outlook", "hotmail", "noreply", "no-reply", "jobs"}:
            return root.replace("-", " ").title()

    subject = email.subject or ""
    subject_company_match = re.search(r"(?:at|chez)\s+([A-Za-z0-9&\-\s]{2,})", subject, re.IGNORECASE)
    if subject_company_match:
        return subject_company_match.group(1).strip().title()
    return None


def _extract_job_title(subject: str) -> str | None:
    clean_subject = re.sub(r"\s+", " ", subject).strip()
    for pattern in JOB_TITLE_PATTERNS:
        match = pattern.search(clean_subject)
        if match:
            return match.group(1).strip(" .:-")

    # Fallback: try common separators in recruitment emails.
    split_candidates = re.split(r"[-|:]", clean_subject)
    if len(split_candidates) >= 2:
        candidate = split_candidates[-1].strip()
        if 2 <= len(candidate) <= 120:
            return candidate
    return None
