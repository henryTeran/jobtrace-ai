"""Extract structured entities from normalized job emails."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas import EmailNormalized, StatusType
from app.services.subject_normalizer import normalize_subject


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
    re.compile(
        r"votre\s+candidature\s+en\s+tant\s+que\s+(.+?)\s+a\s+(?:ete|été)\s+envoy(?:ee|ée)",
        re.IGNORECASE,
    ),
    re.compile(r"votre\s+candidature\s*[:\-]\s*(.+?)(?:\s+chez\s+.+)?$", re.IGNORECASE),
    re.compile(r"candidature\s*[:\-]\s*(.+)$", re.IGNORECASE),
    re.compile(r"application\s+for\s+(.+)$", re.IGNORECASE),
    re.compile(r"for\s+the\s+(.+?)\s+(role|position)", re.IGNORECASE),
    re.compile(r"candidature\s+pour\s+(.+)$", re.IGNORECASE),
    re.compile(r"postule\s+pour\s+(.+)$", re.IGNORECASE),
    re.compile(r"poste\s+de\s+(.+?)(?:\s+a\s+(?:ete|été)\s+re(?:c|ç)u[ea]?|$)", re.IGNORECASE),
]

BODY_JOB_TITLE_PATTERNS = [
    re.compile(r"votre\s+candidature\s+pour\s+le\s+poste\s+de\s+(.+?)\s+a\s+(?:ete|été)\s+re(?:c|ç)u[ea]?", re.IGNORECASE),
    re.compile(r"application\s+for\s+the\s+position\s+of\s+(.+?)(?:\.|\n|$)", re.IGNORECASE),
]

ROLE_HINT_PATTERN = re.compile(
    r"\b("
    r"developer|engineer|software|backend|frontend|full\s*stack|devops|data|"
    r"developpeur|développeur|ingenieur|ingénieur|informat|technicien|"
    r"service\s*desk|administrateur|apprentissage|dessinateur|architect|"
    r"intern|stage|stagiaire|analyst"
    r")\b",
    re.IGNORECASE,
)


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
    job_title = _extract_job_title(email)

    return ExtractedEmailData(company=company, job_title=job_title, status=status)


def _extract_company(email: EmailNormalized) -> str | None:
    subject = normalize_subject(email.subject)
    subject_company_match = re.search(r"(?:at|chez)\s+([A-Za-z0-9&\-\s]{2,})", subject, re.IGNORECASE)
    if subject_company_match:
        company_from_subject = _cleanup_company(subject_company_match.group(1))
        if company_from_subject:
            return company_from_subject

    sender = (email.from_email or "").lower()
    if "@" in sender:
        domain = sender.split("@", 1)[1]
        root = domain.split(".")[0]
        if root not in {"gmail", "outlook", "hotmail", "noreply", "no-reply", "jobs"}:
            return root.replace("-", " ").title()
    return None


def _extract_job_title(email: EmailNormalized) -> str | None:
    clean_subject = normalize_subject(email.subject)
    for pattern in JOB_TITLE_PATTERNS:
        match = pattern.search(clean_subject)
        if match:
            return _cleanup_job_title(match.group(1))

    text_blob = " ".join([email.snippet or "", email.body_text or ""])
    text_blob = re.sub(r"\s+", " ", text_blob).strip()
    for pattern in BODY_JOB_TITLE_PATTERNS:
        match = pattern.search(text_blob)
        if match:
            return _cleanup_job_title(match.group(1))

    # Fallback: try common separators in recruitment emails.
    split_candidates = re.split(r"[-|:]", clean_subject)
    if len(split_candidates) >= 2:
        candidate = split_candidates[-1].strip()
        if 2 <= len(candidate) <= 120:
            cleaned = _cleanup_job_title(candidate)
            if cleaned:
                return cleaned

    # Fallback for bare role subjects (e.g. "Apprentissage Dessinateur en architecture CFC 2026").
    if 6 <= len(clean_subject) <= 140 and ROLE_HINT_PATTERN.search(clean_subject):
        cleaned_subject = _cleanup_job_title(clean_subject)
        if cleaned_subject:
            return cleaned_subject
    return None


def _cleanup_job_title(value: str) -> str | None:
    title = re.sub(r"\s+", " ", value).strip(" .:-")
    title = re.sub(r"\s+chez\s+.+$", "", title, flags=re.IGNORECASE).strip(" .:-")
    title = re.sub(r"\s+a\s+(?:ete|été)\s+envoy(?:ee|ée).*$", "", title, flags=re.IGNORECASE).strip(" .:-")
    title = re.sub(r"(\d+)\s-\s(\d+%?)", r"\1-\2", title)
    if len(title) < 2:
        return None
    return title


def _cleanup_company(value: str) -> str | None:
    company = re.sub(r"\s+", " ", value).strip(" .:-")
    company = re.sub(r"\s+(?:pourrait\s+vous\s+convenir|a\s+ete\s+re(?:c|ç)u[ea]?).*$", "", company, flags=re.IGNORECASE).strip(" .:-")
    if len(company) < 2:
        return None
    return company.title()
