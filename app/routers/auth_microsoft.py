"""Microsoft OAuth endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.connectors.outlook_connector import OutlookConnector
from app.database import get_db


router = APIRouter(prefix="/auth/microsoft", tags=["auth-microsoft"])


@router.get("/login")
def microsoft_login(db: Session = Depends(get_db)) -> dict[str, str]:
    """Return Microsoft OAuth2 login URL."""

    connector = OutlookConnector(db)
    return {"auth_url": connector.login()}


@router.get("/callback")
def microsoft_callback(code: str = Query(...), db: Session = Depends(get_db)) -> dict[str, str]:
    """Handle Microsoft callback and store tokens."""

    connector = OutlookConnector(db)
    try:
        connector.callback(code=code)
        return {"message": "Microsoft account connected"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
