"""Utilities for normalizing email subjects before extraction."""

from __future__ import annotations

import re


SUBJECT_PREFIX_PATTERN = re.compile(r"^(?:\s*(?:re|fw|fwd)\s*:\s*)+", re.IGNORECASE)


def normalize_subject(subject: str | None) -> str:
    """Normalize subject by removing reply/forward prefixes and harmonizing spaces/dashes."""

    text = (subject or "").strip()
    text = SUBJECT_PREFIX_PATTERN.sub("", text)

    # Harmonize common dash characters, then collapse spaces.
    text = text.replace("—", "-").replace("–", "-").replace("−", "-")
    text = re.sub(r"\s*-\s*", " - ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
