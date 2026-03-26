"""OAuth providers connectivity status endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OAuthToken
from app.schemas import OAuthProviderStatus, OAuthStatusResponse


router = APIRouter(prefix="/auth", tags=["auth-status"])


@router.get("/status", response_model=OAuthStatusResponse)
def auth_status(db: Session = Depends(get_db)) -> OAuthStatusResponse:
    """Return OAuth connectivity status for Gmail and Outlook."""

    rows = db.execute(select(OAuthToken)).scalars().all()
    by_provider = {row.provider: row for row in rows}

    providers = [
        OAuthProviderStatus(
            provider="gmail",
            connected="gmail" in by_provider,
            updated_at=by_provider.get("gmail").updated_at if by_provider.get("gmail") else None,
        ),
        OAuthProviderStatus(
            provider="outlook",
            connected="outlook" in by_provider,
            updated_at=by_provider.get("outlook").updated_at if by_provider.get("outlook") else None,
        ),
    ]

    return OAuthStatusResponse(providers=providers)
