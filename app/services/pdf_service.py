"""PDF generation service for monthly application reports."""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from collections import defaultdict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import JobEmail
from app.schemas import StatusType
from app.services.monthly_report_service import list_job_emails
from app.services.monthly_report_service import get_monthly_groups
from app.utils.dates import french_month_title


settings = get_settings()


def generate_monthly_pdf(
    db: Session,
    months: list[str] | None = None,
    output_filename: str | None = None,
) -> tuple[str, list[str], int]:
    """Generate the monthly PDF report and return file path, months and row count."""

    grouped, _ = get_monthly_groups(
        db=db,
        months=months,
        page=1,
        page_size=100000,
        sort_by="received_at",
        sort_order="desc",
    )
    resolved_months = list(grouped.keys())
    total_rows = sum(len(rows) for rows in grouped.values())

    reports_dir = Path(settings.report_output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if output_filename:
        filename = output_filename
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"jobtrace_report_{timestamp}.pdf"

    output_path = reports_dir / filename
    _build_pdf(output_path=output_path, grouped=grouped)

    return str(output_path), resolved_months, total_rows


def generate_filtered_pdf(
    db: Session,
    provider: str | None = None,
    status: StatusType | None = None,
    q: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "received_at",
    sort_order: str = "desc",
    output_filename: str | None = None,
) -> tuple[str, list[str], int]:
    """Generate PDF from the filtered email list shown in the emails screen."""

    rows, _ = list_job_emails(
        db=db,
        months=None,
        page=1,
        page_size=100000,
        sort_by=sort_by,
        sort_order=sort_order,
        provider=provider,
        status=status,
        company=None,
        date_from=date_from,
        date_to=date_to,
        q=q,
    )

    grouped: dict[str, list[JobEmail]] = defaultdict(list)
    for row in rows:
        grouped[row.month_key].append(row)

    ordered_grouped = {month: grouped[month] for month in sorted(grouped.keys(), reverse=True)}
    resolved_months = list(ordered_grouped.keys())
    total_rows = len(rows)

    reports_dir = Path(settings.report_output_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if output_filename:
        filename = output_filename
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"jobtrace_filtered_{timestamp}.pdf"

    output_path = reports_dir / filename
    _build_pdf(output_path=output_path, grouped=ordered_grouped)

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
    header_cell_style = ParagraphStyle(
        "HeaderCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,
    )
    body_cell_style = ParagraphStyle(
        "BodyCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#111827"),
    )

    story = []
    for month_key, rows in grouped.items():
        story.append(Paragraph(french_month_title(month_key), title_style))
        story.append(Spacer(1, 4 * mm))

        table_data = [[
            Paragraph("Date", header_cell_style),
            Paragraph("Entreprise", header_cell_style),
            Paragraph("Poste", header_cell_style),
            Paragraph("Expediteur", header_cell_style),
            Paragraph("Sujet", header_cell_style),
            Paragraph("Statut", header_cell_style),
            Paragraph("Source", header_cell_style),
        ]]

        for row in rows:
            table_data.append(
                [
                    Paragraph(_cell_text(row.received_at.strftime("%Y-%m-%d"), 20), body_cell_style),
                    Paragraph(_cell_text(row.company or "-", 60), body_cell_style),
                    Paragraph(_cell_text(row.job_title or "-", 90), body_cell_style),
                    Paragraph(_cell_text(row.sender_email or row.sender_name or "-", 100), body_cell_style),
                    Paragraph(_cell_text(row.subject, 150), body_cell_style),
                    Paragraph(_cell_text(row.status, 30), body_cell_style),
                    Paragraph(_cell_text(row.provider, 20), body_cell_style),
                ]
            )

        col_widths = [20 * mm, 32 * mm, 38 * mm, 44 * mm, 96 * mm, 24 * mm, 16 * mm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#94a3b8")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("TOPPADDING", (0, 1), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
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


def _cell_text(value: str | None, limit: int) -> str:
    text = (value or "-").replace("\r", " ").replace("\n", " ").strip()
    return escape(_truncate(text, limit))
