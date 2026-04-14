"""Auth module model exports.

Kept as a separate module-level import path to support gradual migration.
"""

from __future__ import annotations

from app.models import OAuthToken

__all__ = ["OAuthToken"]
