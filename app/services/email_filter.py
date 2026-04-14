"""Rule-based filtering for job application related emails."""

from __future__ import annotations

import re

from app.schemas import EmailNormalized


STRICT_LIFECYCLE_KEYWORDS = {
    "application for",
    "candidature pour",
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
    "your profile",
    "your candidacy",
    "not selected for",
    "regret to inform you",
    "your application was rejected",
}

APPLICATION_SUBMISSION_KEYWORDS = {
    "thank you for applying",
    "application received",
    "application submitted",
    "we received your application",
    "your application",
    "votre candidature",
    "candidature pour",
    "application for",
    "je postule",
    "i am applying",
    "you applied",
}

PIPELINE_FOLLOWUP_KEYWORDS = {
    "interview invitation",
    "invitation entretien",
    "schedule interview",
    "screening call",
    "technical interview",
    "next steps",
    "follow up on your application",
    "we are pleased to",
    "congratulations",
    "not selected for",
    "regret to inform you",
    "your application was rejected",
}

STRICT_LIFECYCLE_REGEX = [
    re.compile(r"\b(application|candidature)\s+(for|pour)\b", re.IGNORECASE),
    re.compile(r"\b(your|votre)\s+(application|candidature)\b", re.IGNORECASE),
    re.compile(r"\b(interview invitation|schedule interview|invitation entretien)\b", re.IGNORECASE),
    re.compile(r"\b(regret to inform you|not selected for|your application was rejected)\b", re.IGNORECASE),
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
    "new job opportunity posted",
}

OFFER_ALERT_REGEX = [
    re.compile(r"\bnew\s+job\s+opportunit(?:y|ies)\s+posted\b", re.IGNORECASE),
    re.compile(r"\bnew\s+[\w\s\-/+]{0,80}\s+opportunit(?:y|ies)\b", re.IGNORECASE),
    re.compile(r"\bopportunit(?:y|ies)\s+posted\b", re.IGNORECASE),
    re.compile(r"\brecommended\s+jobs?\b", re.IGNORECASE),
    re.compile(r"\bjobs?\s+you\s+may\s+be\s+interested\b", re.IGNORECASE),
]

JOB_ALERT_SENDER_PATTERNS = {
    "jobs-noreply@",
    "jobalerts@",
    "job-alert@",
    "alerts-noreply@",
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
    "what we're seeing in the data",
    "she applied for months",
    "why experienced professionals get ignored",
    "the #1 reason senior cvs get auto-rejected",
    "ne manquez pas les discussions",
    "artificial intelligence investors",
    "are you the",
    "who wrote",
    "screening methods for the",
    "dessinateur en architecture",
    "architecture cfc",
    "apprentissage dessinateur",
    "architecte",
    "architecture",
}

NOISE_SENDER_PATTERNS = {
    "account-security-noreply@",
    "@accountprotection.microsoft.com",
    "notifications@github.com",
    "noreply@notifications.freelancer.com",
    "support@match.jobgether.com",
    "groups-noreply@linkedin.com",
    "updates@academia-mail.com",
}

NOISE_DOMAIN_PATTERNS = {
    "match.jobgether.com",
    "academia-mail.com",
}


def is_job_related(email: EmailNormalized) -> bool:
    """Backward-compatible wrapper using strict mode by default."""

    return is_job_related_with_mode(email=email, mode="strict")


def is_job_related_with_mode(email: EmailNormalized, mode: str = "strict") -> bool:
    """Return True when an email matches job flow according to the selected mode."""

    subject = (email.subject or "").lower()
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
    has_submission_signal = any(keyword in text for keyword in APPLICATION_SUBMISSION_KEYWORDS)
    has_followup_signal = any(keyword in text for keyword in PIPELINE_FOLLOWUP_KEYWORDS)
    has_application_reference = re.search(r"\b(your|votre)\s+(application|candidature)\b", text) is not None
    has_tracking_domain = any(domain in text for domain in DOMAINS)
    is_offer_alert = any(keyword in text for keyword in OFFER_ALERT_KEYWORDS) or any(
        pattern.search(subject) for pattern in OFFER_ALERT_REGEX
    )
    has_noise_keyword = any(keyword in text for keyword in NOISE_KEYWORDS)
    is_noise_sender = any(pattern in sender for pattern in NOISE_SENDER_PATTERNS)
    is_noise_domain = any(domain in sender for domain in NOISE_DOMAIN_PATTERNS)
    is_job_alert_sender = any(pattern in sender for pattern in JOB_ALERT_SENDER_PATTERNS)

    if has_noise_keyword or is_noise_sender or is_noise_domain:
        return False

    if is_offer_alert or is_job_alert_sender:
        return False

    if has_submission_signal:
        return True

    if has_followup_signal and has_application_reference:
        return True

    if mode == "full":
        # Full mode is broader than strict, but still rejects pure offer/job alert traffic.
        # Keep ATS-platform traffic only when linked to an explicit application context.
        return has_application_signal and (has_application_reference or has_tracking_domain)

    # Strict mode (default): focus on concrete application lifecycle emails only.
    return has_application_signal and has_application_reference
