"""Business services for authentication and OAuth connectivity."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.connectors.gmail import GmailConnector
from app.connectors.outlook import OutlookConnector
from app.modules.auth.repository import OAuthTokenRepository
from app.modules.auth.schemas import OAuthProviderStatus, OAuthStatusResponse
from app.shared.exceptions import IntegrationError, ValidationError
from app.shared.oauth_state import generate_oauth_state, validate_oauth_state


class AuthService:
    """Application service encapsulating OAuth use cases."""

    def __init__(self, db: Session):
        self.db = db
        self.tokens = OAuthTokenRepository(db)

    def build_google_login(self) -> tuple[str, str]:
        """Return Google authorization URL and generated state."""

        state = generate_oauth_state("gmail")
        auth_url = GmailConnector(self.db).login(state=state)
        return auth_url, state

    def handle_google_callback(self, code: str, state: str) -> str:
        """Validate callback state and persist Google tokens."""

        if not validate_oauth_state(provider="gmail", state=state):
            raise ValidationError("Invalid OAuth state")
        try:
            GmailConnector(self.db).callback(code=code)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise IntegrationError(str(exc)) from exc
        return "Google account connected"

    def build_microsoft_login(self) -> tuple[str, str]:
        """Return Microsoft authorization URL and generated state."""

        state = generate_oauth_state("outlook")
        auth_url = OutlookConnector(self.db).login(state=state)
        return auth_url, state

    def handle_microsoft_callback(self, code: str, state: str) -> str:
        """Validate callback state and persist Microsoft tokens."""

        if not validate_oauth_state(provider="outlook", state=state):
            raise ValidationError("Invalid OAuth state")
        try:
            OutlookConnector(self.db).callback(code=code)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise IntegrationError(str(exc)) from exc
        return "Microsoft account connected"

    def get_status(self) -> OAuthStatusResponse:
        """Return OAuth connectivity status for both providers."""

        rows = self.tokens.list_all()
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

    def disconnect(self, provider: str) -> bool:
        """Remove stored token for the given provider. Returns True if a token existed."""

        if provider not in {"gmail", "outlook"}:
            raise ValidationError(f"Unknown provider: {provider}")
        return self.tokens.delete_by_provider(provider)
