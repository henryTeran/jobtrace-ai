"""Google OAuth endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.connectors.gmail_connector import GmailConnector
from app.database import get_db
from app.utils.oauth_state import generate_oauth_state, validate_oauth_state


router = APIRouter(prefix="/auth/google", tags=["auth-google"])


@router.get("/login")
def google_login(db: Session = Depends(get_db)) -> dict[str, str]:
    """Return Google OAuth2 login URL."""

    connector = GmailConnector(db)
    state = generate_oauth_state("gmail")
    return {"auth_url": connector.login(state=state), "state": state}


@router.get("/callback")
def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Handle Google OAuth2 callback and store tokens."""

    if not validate_oauth_state(provider="gmail", state=state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    connector = GmailConnector(db)
    try:
        connector.callback(code=code)
        return {"message": "Google account connected"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
