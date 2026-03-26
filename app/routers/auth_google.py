"""Google OAuth endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.connectors.gmail_connector import GmailConnector
from app.database import get_db


router = APIRouter(prefix="/auth/google", tags=["auth-google"])


@router.get("/login")
def google_login(db: Session = Depends(get_db)) -> dict[str, str]:
    """Return Google OAuth2 login URL."""

    connector = GmailConnector(db)
    return {"auth_url": connector.login()}


@router.get("/callback")
def google_callback(code: str = Query(...), db: Session = Depends(get_db)) -> dict[str, str]:
    """Handle Google OAuth2 callback and store tokens."""

    connector = GmailConnector(db)
    try:
        connector.callback(code=code)
        return {"message": "Google account connected"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
