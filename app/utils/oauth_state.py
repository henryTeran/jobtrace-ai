"""Helpers to generate and validate OAuth state tokens."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from app.config import get_settings


settings = get_settings()


def generate_oauth_state(provider: str) -> str:
    """Create a signed OAuth state token bound to a provider and timestamp."""

    payload = {"provider": provider, "ts": int(time.time())}
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_encoded = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")

    signature = _sign(payload_encoded)
    return f"{payload_encoded}.{signature}"


def validate_oauth_state(provider: str, state: str) -> bool:
    """Validate OAuth state signature, provider and expiration window."""

    try:
        payload_encoded, signature = state.split(".", 1)
    except ValueError:
        return False

    if not hmac.compare_digest(_sign(payload_encoded), signature):
        return False

    try:
        payload_raw = base64.urlsafe_b64decode(_pad_b64(payload_encoded))
        payload = json.loads(payload_raw.decode("utf-8"))
    except Exception:
        return False

    if payload.get("provider") != provider:
        return False

    timestamp = payload.get("ts")
    if not isinstance(timestamp, int):
        return False

    return int(time.time()) - timestamp <= settings.oauth_state_ttl_seconds


def _sign(payload_encoded: str) -> str:
    digest = hmac.new(
        settings.oauth_state_secret.encode("utf-8"),
        payload_encoded.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def _pad_b64(value: str) -> str:
    remainder = len(value) % 4
    if remainder == 0:
        return value
    return value + ("=" * (4 - remainder))
