"""Microsoft OAuth2 (MSAL) and Graph API connector."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx
import msal
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import OAuthToken


logger = logging.getLogger(__name__)
settings = get_settings()


class OutlookConnector:
    """Connector for Microsoft OAuth and Outlook messages via Graph API."""

    provider = "outlook"

    def __init__(self, db: Session):
        self.db = db
        authority = f"https://login.microsoftonline.com/{settings.microsoft_tenant_id}"
        self._msal_app = msal.ConfidentialClientApplication(
            client_id=settings.microsoft_client_id,
            client_credential=settings.microsoft_client_secret,
            authority=authority,
        )

    def login(self, state: str) -> str:
        """Return Microsoft login URL."""

        return self._msal_app.get_authorization_request_url(
            scopes=[settings.microsoft_scope],
            redirect_uri=settings.microsoft_redirect_uri,
            prompt="select_account",
            state=state,
        )

    def callback(self, code: str) -> dict[str, Any]:
        """Exchange authorization code and persist token payload."""

        result = self._msal_app.acquire_token_by_authorization_code(
            code=code,
            scopes=[settings.microsoft_scope],
            redirect_uri=settings.microsoft_redirect_uri,
        )
        if "access_token" not in result:
            raise RuntimeError(result.get("error_description") or "Failed Microsoft OAuth callback")

        result["expires_at"] = int(time.time()) + int(result.get("expires_in", 0))
        self._save_token(result)
        return result

    def get_messages(
        self,
        limit: int = 50,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch Outlook messages via Microsoft Graph API."""

        access_token = self._get_valid_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "$top": str(limit),
            "$orderby": "receivedDateTime DESC",
            "$select": "id,conversationId,subject,from,receivedDateTime,bodyPreview,body,internetMessageId",
        }
        date_filter = self._build_date_filter(from_date=from_date, to_date=to_date)
        if date_filter:
            params["$filter"] = date_filter

        with httpx.Client(timeout=30) as client:
            response = client.get("https://graph.microsoft.com/v1.0/me/messages", headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
            return payload.get("value", [])

    def _build_date_filter(
        self,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> str | None:
        filters: list[str] = []
        if from_date is not None:
            from_utc = from_date.astimezone(timezone.utc).replace(microsecond=0)
            filters.append(f"receivedDateTime ge {from_utc.isoformat().replace('+00:00', 'Z')}")
        if to_date is not None:
            to_utc = to_date.astimezone(timezone.utc).replace(microsecond=0)
            filters.append(f"receivedDateTime le {to_utc.isoformat().replace('+00:00', 'Z')}")
        if not filters:
            return None
        return " and ".join(filters)

    def _save_token(self, token_payload: dict[str, Any]) -> None:
        existing = self.db.query(OAuthToken).filter(OAuthToken.provider == self.provider).first()
        payload_text = json.dumps(token_payload)

        if existing:
            existing.token_json = payload_text
        else:
            self.db.add(OAuthToken(provider=self.provider, token_json=payload_text))
        self.db.commit()

    def _load_token(self) -> dict[str, Any] | None:
        row = self.db.query(OAuthToken).filter(OAuthToken.provider == self.provider).first()
        if not row:
            return None
        try:
            return json.loads(row.token_json)
        except json.JSONDecodeError:
            logger.error("Invalid Outlook token payload in storage")
            return None

    def _refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        token_url = f"https://login.microsoftonline.com/{settings.microsoft_tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": settings.microsoft_client_id,
            "client_secret": settings.microsoft_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": settings.microsoft_redirect_uri,
            "scope": f"{settings.microsoft_scope} offline_access",
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(token_url, data=data)
            response.raise_for_status()
            refreshed = response.json()

        token_payload = self._load_token() or {}
        token_payload.update(refreshed)
        token_payload["refresh_token"] = token_payload.get("refresh_token", refresh_token)
        token_payload["expires_at"] = int(time.time()) + int(token_payload.get("expires_in", 0))
        self._save_token(token_payload)
        return token_payload

    def _get_valid_access_token(self) -> str:
        token_payload = self._load_token()
        if not token_payload:
            raise RuntimeError("Microsoft account not connected")

        expires_at = int(token_payload.get("expires_at", 0))
        if expires_at > int(time.time()) + 60:
            return token_payload["access_token"]

        refresh_token = token_payload.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("Microsoft token expired and no refresh token available")

        refreshed = self._refresh_access_token(refresh_token)
        return refreshed["access_token"]
