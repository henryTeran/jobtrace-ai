"""FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from app.config import get_settings
from app.database import Base, engine
from app.routers import auth_google, auth_microsoft, auth_status, emails, reports
from app.utils.logger import configure_logging


configure_logging()
settings = get_settings()


def initialize_runtime() -> None:
    """Create runtime folders and database schema."""

    Path(settings.report_output_dir).mkdir(parents=True, exist_ok=True)

    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.replace("sqlite:///", "", 1)
        db_dir = Path(db_path).parent
        if str(db_dir) not in {"", "."}:
            db_dir.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)


initialize_runtime()

app = FastAPI(title="JobTrace AI", version="1.0.0")

app.include_router(auth_google.router)
app.include_router(auth_microsoft.router)
app.include_router(auth_status.router)
app.include_router(emails.router)
app.include_router(reports.router)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Return API health status."""

    return {"status": "ok"}
