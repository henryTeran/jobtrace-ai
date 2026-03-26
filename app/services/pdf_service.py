"""PDF generation service for monthly application reports."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import JobEmail
from app.services.monthly_report_service import get_monthly_groups
from app.utils.dates import french_month_title


settings = get_settings()


def generate_monthly_pdf(
    db: Session,
    months: list[str] | None = None,
    output_filename: str | None = None,
) -> tuple[str, list[str], int]:
    """Generate the monthly PDF report and return file path, months and row count."""

    grouped = get_monthly_groups(db=db, months=months)
    resolved_months = list(grouped.keys())
    total_rows = sum(len(rows) for rows in grouped.values())

    reports_dir = Path(settings.report_output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if output_filename:
        filename = output_filename
    else:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"jobtrace_report_{timestamp}.pdf"

    output_path = reports_dir / filename
    _build_pdf(output_path=output_path, grouped=grouped)

    return str(output_path), resolved_months, total_rows


def _build_pdf(output_path: Path, grouped: dict[str, list[JobEmail]]) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "MonthTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=8,
    )

    story = []
    for month_key, rows in grouped.items():
        story.append(Paragraph(french_month_title(month_key), title_style))
        story.append(Spacer(1, 4 * mm))

        table_data = [
            ["Date", "Entreprise", "Poste", "Expediteur", "Sujet", "Statut", "Source"]
        ]

        for row in rows:
            table_data.append(
                [
                    row.received_at.strftime("%Y-%m-%d"),
                    row.company or "-",
                    row.job_title or "-",
                    row.sender_email or row.sender_name or "-",
                    _truncate(row.subject, 80),
                    row.status,
                    row.provider,
                ]
            )

        col_widths = [24 * mm, 40 * mm, 40 * mm, 48 * mm, 85 * mm, 28 * mm, 20 * mm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#94a3b8")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 8 * mm))

    if not grouped:
        story.append(Paragraph("Aucune donnee disponible.", styles["BodyText"]))

    doc.build(story)


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."
