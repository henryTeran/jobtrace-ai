"""HTTP routes for authentication module."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import AuthServiceDep
from app.modules.auth.schemas import OAuthCallbackResponse, OAuthLoginResponse, OAuthStatusResponse
from app.shared.exceptions import DomainError


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login", response_model=OAuthLoginResponse)
def google_login(service: AuthServiceDep) -> OAuthLoginResponse:
    """Return Google OAuth login URL."""

    auth_url, state = service.build_google_login()
    return OAuthLoginResponse(auth_url=auth_url, state=state)


@router.get("/google/callback", response_model=OAuthCallbackResponse)
def google_callback(
    service: AuthServiceDep,
    code: str = Query(...),
    state: str = Query(...),
) -> OAuthCallbackResponse:
    """Handle Google OAuth callback."""

    try:
        message = service.handle_google_callback(code=code, state=state)
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return OAuthCallbackResponse(message=message)


@router.get("/microsoft/login", response_model=OAuthLoginResponse)
def microsoft_login(service: AuthServiceDep) -> OAuthLoginResponse:
    """Return Microsoft OAuth login URL."""

    auth_url, state = service.build_microsoft_login()
    return OAuthLoginResponse(auth_url=auth_url, state=state)


@router.get("/microsoft/callback", response_model=OAuthCallbackResponse)
def microsoft_callback(
    service: AuthServiceDep,
    code: str = Query(...),
    state: str = Query(...),
) -> OAuthCallbackResponse:
    """Handle Microsoft OAuth callback."""

    try:
        message = service.handle_microsoft_callback(code=code, state=state)
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return OAuthCallbackResponse(message=message)


@router.get("/status", response_model=OAuthStatusResponse)
def auth_status(service: AuthServiceDep) -> OAuthStatusResponse:
    """Return OAuth provider connection status."""

    return service.get_status()


@router.delete("/{provider}/disconnect", status_code=200)
def disconnect_provider(provider: str, service: AuthServiceDep) -> dict:
    """Remove stored OAuth token for a provider (gmail or outlook)."""

    try:
        removed = service.disconnect(provider)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"removed": removed, "provider": provider}
