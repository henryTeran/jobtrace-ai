"""Schemas dedicated to the auth module."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class OAuthLoginResponse(BaseModel):
    """Response payload for OAuth login URL generation."""

    auth_url: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """Response payload after OAuth callback processing."""

    message: str


class OAuthProviderStatus(BaseModel):
    """OAuth status for one provider."""

    provider: str
    connected: bool
    updated_at: datetime | None = None


class OAuthStatusResponse(BaseModel):
    """OAuth status summary for all providers."""

    providers: list[OAuthProviderStatus]
