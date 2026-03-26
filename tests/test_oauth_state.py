"""Tests for OAuth state helpers."""

from __future__ import annotations

from app.utils.oauth_state import generate_oauth_state, validate_oauth_state


def test_generate_and_validate_oauth_state() -> None:
    state = generate_oauth_state("gmail")
    assert validate_oauth_state("gmail", state) is True


def test_oauth_state_rejects_provider_mismatch() -> None:
    state = generate_oauth_state("gmail")
    assert validate_oauth_state("outlook", state) is False


def test_oauth_state_rejects_tampered_token() -> None:
    state = generate_oauth_state("gmail") + "tampered"
    assert validate_oauth_state("gmail", state) is False
