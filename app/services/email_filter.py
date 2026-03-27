"""Rule-based filtering for job application related emails."""

from __future__ import annotations

from app.schemas import EmailNormalized


APPLICATION_FLOW_KEYWORDS = {
    "application",
    "application for",
    "candidature",
    "candidature pour",
    "applied",
    "i am applying",
    "je postule",
    "thank you for applying",
    "application received",
    "application submitted",
    "votre candidature",
    "accuse de reception",
    "interview",
    "entretien",
    "recruiter",
    "talent acquisition",
    "next steps",
    "follow up",
    "we are pleased",
    "congratulations",
    "offer stage",
    "unfortunately",
    "not selected",
    "regret to inform",
}

DOMAINS = {
    "greenhouse.io",
    "lever.co",
    "workday.com",
    "smartrecruiters.com",
    "ashbyhq.com",
}

OFFER_ALERT_KEYWORDS = {
    "job alert",
    "new job",
    "new jobs",
    "jobs you may be interested",
    "offres d'emploi",
    "offre d'emploi",
    "suggestions d'offres",
    "recommended jobs",
    "weekly jobs",
    "daily jobs",
    "emplois pour vous",
    "discover jobs",
    "new opportunity posted",
}


def is_job_related(email: EmailNormalized) -> bool:
    """Return True for application lifecycle emails and False for generic offers/alerts."""

    text = " ".join(
        [
            email.subject or "",
            email.snippet or "",
            email.body_text or "",
            email.from_email or "",
        ]
    ).lower()

    has_application_signal = any(keyword in text for keyword in APPLICATION_FLOW_KEYWORDS)
    has_tracking_domain = any(domain in text for domain in DOMAINS)
    is_offer_alert = any(keyword in text for keyword in OFFER_ALERT_KEYWORDS)

    # Drop broad job alerts/newsletters unless they clearly contain application-flow signals.
    if is_offer_alert and not (has_application_signal or has_tracking_domain):
        return False

    return has_application_signal or has_tracking_domain
