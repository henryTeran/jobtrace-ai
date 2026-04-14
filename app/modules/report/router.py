"""HTTP routes for reporting module."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import ReportServiceDep
from app.modules.report.schemas import MonthlyReportResponse, PdfFilteredRequest, PdfRequest, PdfResponse


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReportResponse)
def monthly_report(
    service: ReportServiceDep,
    months: list[str] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: Literal["received_at", "created_at", "company", "status", "provider", "subject"] = Query(
        default="received_at"
    ),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
) -> MonthlyReportResponse:
    """Return job emails grouped by month."""

    return service.monthly_report(
        months=months,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("/pdf", response_model=PdfResponse)
def monthly_pdf(service: ReportServiceDep, payload: PdfRequest) -> PdfResponse:
    """Generate monthly PDF report in the reports directory."""

    try:
        return service.generate_pdf(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pdf/filtered", response_model=PdfResponse)
def filtered_pdf(service: ReportServiceDep, payload: PdfFilteredRequest) -> PdfResponse:
    """Generate PDF report for filtered emails."""

    try:
        return service.generate_filtered_pdf(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
