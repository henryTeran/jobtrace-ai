"""Rule-based filtering for job application related emails."""

from __future__ import annotations

import re

from app.schemas import EmailNormalized


STRICT_LIFECYCLE_KEYWORDS = {
    "application for",
    "candidature pour",
    "i am applying",
    "je postule",
    "your application",
    "votre candidature",
    "thank you for applying",
    "application received",
    "application submitted",
    "we received your application",
    "accuse de reception",
    "interview invitation",
    "invitation entretien",
    "schedule interview",
    "screening call",
    "technical interview",
    "next steps",
    "follow up on your application",
    "we are pleased to",
    "congratulations",
    "offer stage",
    "offer letter",
    "unfortunately",
    "not selected",
    "regret to inform",
    "application rejected",
    "rejected",
    "declined",
    "recruiter reached out",
    "talent acquisition",
}

STRICT_LIFECYCLE_REGEX = [
    re.compile(r"\b(application|candidature)\s+(for|pour)\b", re.IGNORECASE),
    re.compile(r"\b(your|votre)\s+(application|candidature)\b", re.IGNORECASE),
    re.compile(r"\b(interview|entretien)\b", re.IGNORECASE),
    re.compile(r"\b(not selected|regret to inform|rejected|declined)\b", re.IGNORECASE),
]

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
    "job applications sent, but no replies",
    "you might be interested",
    "might interest you",
    "votre salaire mensuel pourrait augmenter",
    "repos updates",
}

NOISE_KEYWORDS = {
    "your code",
    "code a usage unique",
    "one-time code",
    "account security",
    "new app connected",
    "connected to your microsoft account",
    "privacy statement",
    "newsletter",
    "notifications@github.com",
    "github",
    "repos updates",
}

NOISE_SENDER_PATTERNS = {
    "account-security-noreply@",
    "@accountprotection.microsoft.com",
    "notifications@github.com",
    "noreply@notifications.freelancer.com",
}


def is_job_related(email: EmailNormalized) -> bool:
    """Backward-compatible wrapper using strict mode by default."""

    return is_job_related_with_mode(email=email, mode="strict")


def is_job_related_with_mode(email: EmailNormalized, mode: str = "strict") -> bool:
    """Return True when an email matches job flow according to the selected mode."""

    text = " ".join(
        [
            email.subject or "",
            email.snippet or "",
            email.body_text or "",
            email.from_email or "",
        ]
    ).lower()
    sender = (email.from_email or "").lower()

    has_application_signal = any(keyword in text for keyword in STRICT_LIFECYCLE_KEYWORDS) or any(
        pattern.search(text) for pattern in STRICT_LIFECYCLE_REGEX
    )
    has_tracking_domain = any(domain in text for domain in DOMAINS)
    is_offer_alert = any(keyword in text for keyword in OFFER_ALERT_KEYWORDS)
    has_noise_keyword = any(keyword in text for keyword in NOISE_KEYWORDS)
    is_noise_sender = any(pattern in sender for pattern in NOISE_SENDER_PATTERNS)

    if has_noise_keyword or is_noise_sender:
        return False

    if mode == "full":
        # Full mode keeps a wider net for pipeline visibility but still drops noisy alerts.
        if is_offer_alert and not (has_application_signal or has_tracking_domain):
            return False
        return has_application_signal or has_tracking_domain

    # Strict mode (default): focus on concrete application lifecycle emails only.
    if is_offer_alert:
        return False
    return has_application_signal
