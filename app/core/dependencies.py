"""Centralized dependency injection providers for FastAPI."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.service import AuthService
from app.modules.email.service import EmailService
from app.modules.report.service import ReportService


DbSession = Annotated[Session, Depends(get_db)]


def get_auth_service(db: DbSession) -> AuthService:
    """Provide auth service instance per request."""

    return AuthService(db)


def get_email_service(db: DbSession) -> EmailService:
    """Provide email service instance per request."""

    return EmailService(db)


def get_report_service(db: DbSession) -> ReportService:
    """Provide report service instance per request."""

    return ReportService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
