"""Monthly report and PDF endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import JobEmailOut, MonthlyReportResponse, PdfRequest, PdfResponse
from app.services.monthly_report_service import get_monthly_groups
from app.services.pdf_service import generate_monthly_pdf


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReportResponse)
def monthly_report(db: Session = Depends(get_db)) -> MonthlyReportResponse:
    """Return job emails grouped by month."""

    grouped = get_monthly_groups(db=db)
    serialized = {
        month: [JobEmailOut.model_validate(row) for row in rows] for month, rows in grouped.items()
    }
    return MonthlyReportResponse(data=serialized)


@router.post("/pdf", response_model=PdfResponse)
def monthly_pdf(payload: PdfRequest, db: Session = Depends(get_db)) -> PdfResponse:
    """Generate monthly PDF report in the reports directory."""

    try:
        file_path, months, rows = generate_monthly_pdf(
            db=db,
            months=payload.months,
            output_filename=payload.output_filename,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PdfResponse(file_path=file_path, months=months, rows=rows)
