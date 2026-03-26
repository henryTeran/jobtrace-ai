"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth_google, auth_microsoft, emails, reports
from app.utils.logger import configure_logging


configure_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobTrace AI", version="1.0.0")

app.include_router(auth_google.router)
app.include_router(auth_microsoft.router)
app.include_router(emails.router)
app.include_router(reports.router)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Return API health status."""

    return {"status": "ok"}
