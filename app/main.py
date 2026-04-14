"""FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logger import configure_logging
from app.modules.auth.router import router as auth_router
from app.modules.email.router import router as email_router
from app.modules.report.router import router as report_router


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allow_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(email_router)
app.include_router(report_router)
app.mount("/reports/files", StaticFiles(directory=settings.report_output_dir), name="report-files")


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Return API health status."""

    return {"status": "ok"}
