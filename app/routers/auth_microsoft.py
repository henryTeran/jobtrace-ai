"""Microsoft OAuth endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.connectors.outlook_connector import OutlookConnector
from app.database import get_db
from app.utils.oauth_state import generate_oauth_state, validate_oauth_state


router = APIRouter(prefix="/auth/microsoft", tags=["auth-microsoft"])


@router.get("/login")
def microsoft_login(db: Session = Depends(get_db)) -> dict[str, str]:
    """Return Microsoft OAuth2 login URL."""

    connector = OutlookConnector(db)
    state = generate_oauth_state("outlook")
    return {"auth_url": connector.login(state=state), "state": state}


@router.get("/callback")
def microsoft_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Handle Microsoft callback and store tokens."""

    if not validate_oauth_state(provider="outlook", state=state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    connector = OutlookConnector(db)
    try:
        connector.callback(code=code)
        return {"message": "Microsoft account connected"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
