"""Business services for monthly reports and PDF generation."""

from __future__ import annotations

from typing import Literal

from sqlalchemy.orm import Session

from app.modules.report.schemas import JobEmailOut, MonthlyReportResponse, PdfFilteredRequest, PdfRequest, PdfResponse
from app.services.monthly_report_service import get_monthly_groups
from app.services.pdf_service import generate_filtered_pdf, generate_monthly_pdf


class ReportService:
    """Application service for reporting use cases."""

    def __init__(self, db: Session):
        self.db = db

    def monthly_report(
        self,
        months: list[str] | None,
        page: int,
        page_size: int,
        sort_by: Literal["received_at", "created_at", "company", "status", "provider", "subject"],
        sort_order: Literal["asc", "desc"],
    ) -> MonthlyReportResponse:
        """Return rows grouped by month with pagination metadata."""

        grouped, pagination = get_monthly_groups(
            db=self.db,
            months=months,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        serialized = {
            month: [JobEmailOut.model_validate(row) for row in rows]
            for month, rows in grouped.items()
        }
        return MonthlyReportResponse(data=serialized, pagination=pagination)

    def generate_pdf(self, payload: PdfRequest) -> PdfResponse:
        """Generate PDF report for selected months."""

        file_path, months, rows = generate_monthly_pdf(
            db=self.db,
            months=payload.months,
            output_filename=payload.output_filename,
        )
        return PdfResponse(file_path=file_path, months=months, rows=rows)

    def generate_filtered_pdf(self, payload: PdfFilteredRequest) -> PdfResponse:
        """Generate PDF report for the current filtered emails selection."""

        file_path, months, rows = generate_filtered_pdf(
            db=self.db,
            provider=payload.provider,
            status=payload.status,
            q=payload.q,
            date_from=payload.date_from,
            date_to=payload.date_to,
            sort_by=payload.sort_by,
            sort_order=payload.sort_order,
            output_filename=payload.output_filename,
        )
        return PdfResponse(file_path=file_path, months=months, rows=rows)
