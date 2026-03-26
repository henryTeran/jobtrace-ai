"""Rule-based filtering for job application related emails."""

from __future__ import annotations

from app.schemas import EmailNormalized


KEYWORDS = {
    "application",
    "candidature",
    "interview",
    "entretien",
    "recruiter",
    "job",
    "position",
    "thank you for applying",
    "unfortunately",
    "next steps",
}

DOMAINS = {
    "greenhouse.io",
    "lever.co",
    "workday.com",
    "smartrecruiters.com",
    "ashbyhq.com",
}


def is_job_related(email: EmailNormalized) -> bool:
    """Return True if email appears related to a job application flow."""

    text = " ".join(
        [
            email.subject or "",
            email.snippet or "",
            email.body_text or "",
            email.from_email or "",
        ]
    ).lower()

    if any(keyword in text for keyword in KEYWORDS):
        return True
    if any(domain in text for domain in DOMAINS):
        return True
    return False
