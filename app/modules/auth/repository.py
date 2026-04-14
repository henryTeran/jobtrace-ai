"""Repositories for auth domain persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import OAuthToken


class OAuthTokenRepository:
    """Data access layer for OAuth token records."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[OAuthToken]:
        """Return all OAuth token records."""

        return self.db.execute(select(OAuthToken)).scalars().all()

    def delete_by_provider(self, provider: str) -> bool:
        """Delete token for given provider. Returns True if a row was deleted."""

        row = self.db.execute(
            select(OAuthToken).where(OAuthToken.provider == provider)
        ).scalar_one_or_none()
        if row is None:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
