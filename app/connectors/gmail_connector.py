"""Google OAuth2 and Gmail API connector."""

from __future__ import annotations

import base64
import json
import logging
import secrets
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import OAuthToken


logger = logging.getLogger(__name__)
settings = get_settings()


class GmailConnector:
    """Connector for OAuth2 login and Gmail message retrieval."""

    provider = "gmail"
    auth_base = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    api_base = "https://gmail.googleapis.com/gmail/v1"

    def __init__(self, db: Session):
        self.db = db

    def login(self) -> str:
        """Return the Google OAuth login URL."""

        state = secrets.token_urlsafe(24)
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": settings.google_scope,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
            "state": state,
        }
        return f"{self.auth_base}?{urlencode(params)}"

    def callback(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for access token and persist it."""

        data = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(self.token_url, data=data)
            response.raise_for_status()
            token_payload = response.json()

        token_payload["expires_at"] = int(time.time()) + int(token_payload.get("expires_in", 0))
        self._save_token(token_payload)
        return token_payload

    def get_messages(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch message details from Gmail API."""

        access_token = self._get_valid_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        with httpx.Client(timeout=30) as client:
            list_response = client.get(
                f"{self.api_base}/users/me/messages",
                headers=headers,
                params={"maxResults": limit},
            )
            list_response.raise_for_status()
            ids = list_response.json().get("messages", [])

            messages: list[dict[str, Any]] = []
            for item in ids:
                message_id = item.get("id")
                if not message_id:
                    continue
                detail_response = client.get(
                    f"{self.api_base}/users/me/messages/{message_id}",
                    headers=headers,
                    params={"format": "full"},
                )
                if detail_response.status_code >= 400:
                    logger.warning("Gmail message fetch failed for id=%s", message_id)
                    continue
                messages.append(detail_response.json())
        return messages

    def extract_body_text(self, payload: dict[str, Any]) -> str:
        """Extract plain text body from Gmail payload recursively."""

        def decode_body(data: str) -> str:
            try:
                raw = base64.urlsafe_b64decode(data + "==")
                return raw.decode("utf-8", errors="replace")
            except Exception:
                return ""

        if payload.get("body", {}).get("data"):
            return decode_body(payload["body"]["data"])

        for part in payload.get("parts", []) or []:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain" and part.get("body", {}).get("data"):
                return decode_body(part["body"]["data"])
            if part.get("parts"):
                nested = self.extract_body_text(part)
                if nested:
                    return nested
        return ""

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
            logger.error("Invalid Gmail token payload in storage")
            return None

    def _refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(self.token_url, data=data)
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
            raise RuntimeError("Google account not connected")

        expires_at = int(token_payload.get("expires_at", 0))
        if expires_at > int(time.time()) + 60:
            return token_payload["access_token"]

        refresh_token = token_payload.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("Google token expired and no refresh token available")

        refreshed = self._refresh_access_token(refresh_token)
        return refreshed["access_token"]
