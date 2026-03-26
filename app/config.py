"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the JobTrace AI backend."""

    app_name: str = os.getenv("APP_NAME", "JobTrace AI")
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/jobtrace.db")

    report_output_dir: str = os.getenv("REPORT_OUTPUT_DIR", "reports")

    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    google_scope: str = os.getenv(
        "GOOGLE_SCOPE", "https://www.googleapis.com/auth/gmail.readonly"
    )

    microsoft_client_id: str = os.getenv("MICROSOFT_CLIENT_ID", "")
    microsoft_client_secret: str = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    microsoft_tenant_id: str = os.getenv("MICROSOFT_TENANT_ID", "common")
    microsoft_redirect_uri: str = os.getenv(
        "MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback"
    )
    microsoft_scope: str = os.getenv("MICROSOFT_SCOPE", "Mail.Read")

    oauth_state_secret: str = os.getenv("OAUTH_STATE_SECRET", "jobtrace-state")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached immutable Settings instance."""

    return Settings()
