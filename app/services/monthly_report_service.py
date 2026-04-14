"""Monthly report aggregation service."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, not_, or_, select
from sqlalchemy.orm import Session

from app.models import JobEmail
from app.schemas import MonthCount, PaginationMeta


SORT_FIELDS = {
    "received_at": JobEmail.received_at,
    "created_at": JobEmail.created_at,
    "company": JobEmail.company,
    "status": JobEmail.status,
    "provider": JobEmail.provider,
    "subject": JobEmail.subject,
}

OFFER_ALERT_PATTERNS = (
    "%new job opportunit%",
    "%new%opportunit%",
    "%jobs you may be interested%",
    "%recommended jobs%",
    "%weekly jobs%",
    "%daily jobs%",
    "%discover jobs%",
    "%listing alert%",
    "%[searching]%",
)

OFFER_ALERT_SENDER_PATTERNS = (
    "%jobs-noreply%",
    "%jobalerts%",
    "%job-alert%",
)


def _apply_offer_exclusion(stmt):
    offer_like = or_(
        *[JobEmail.subject.ilike(pattern) for pattern in OFFER_ALERT_PATTERNS],
        *[JobEmail.snippet.ilike(pattern) for pattern in OFFER_ALERT_PATTERNS],
        *[JobEmail.body_text.ilike(pattern) for pattern in OFFER_ALERT_PATTERNS],
        *[JobEmail.sender_email.ilike(pattern) for pattern in OFFER_ALERT_SENDER_PATTERNS],
    )
    return stmt.where(not_(offer_like))


def list_job_emails(
    db: Session,
    months: list[str] | None = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "received_at",
    sort_order: str = "desc",
    provider: str | None = None,
    status: str | None = None,
    company: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = None,
) -> tuple[list[JobEmail], PaginationMeta]:
    """Return paginated, sortable and filterable list of job emails."""

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 1

    field = SORT_FIELDS.get(sort_by, JobEmail.received_at)
    order_expr = field.asc() if sort_order == "asc" else field.desc()

    base_stmt = select(JobEmail)
    base_stmt = _apply_offer_exclusion(base_stmt)
    if months:
        base_stmt = base_stmt.where(JobEmail.month_key.in_(months))
    if provider:
        base_stmt = base_stmt.where(JobEmail.provider == provider)
    if status:
        base_stmt = base_stmt.where(JobEmail.status == status)
    if company:
        base_stmt = base_stmt.where(JobEmail.company.ilike(f"%{company}%"))
    if date_from:
        base_stmt = base_stmt.where(JobEmail.received_at >= date_from)
    if date_to:
        base_stmt = base_stmt.where(JobEmail.received_at <= date_to)
    if q:
        token = f"%{q}%"
        base_stmt = base_stmt.where(
            or_(
                JobEmail.subject.ilike(token),
                JobEmail.snippet.ilike(token),
                JobEmail.company.ilike(token),
                JobEmail.job_title.ilike(token),
            )
        )

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    rows_stmt = base_stmt.order_by(order_expr).offset(offset).limit(page_size)
    rows = db.execute(rows_stmt).scalars().all()

    total_pages = (total + page_size - 1) // page_size if total else 0
    pagination = PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages)
    return rows, pagination


def get_monthly_groups(
    db: Session,
    months: list[str] | None = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "received_at",
    sort_order: str = "desc",
) -> tuple[dict[str, list[JobEmail]], PaginationMeta]:
    """Return job emails grouped by month key."""

    rows, pagination = list_job_emails(
        db=db,
        months=months,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    grouped: dict[str, list[JobEmail]] = defaultdict(list)
    for row in rows:
        grouped[row.month_key].append(row)

    ordered = {month: grouped[month] for month in sorted(grouped.keys(), reverse=True)}
    return ordered, pagination


def get_email_stats(db: Session) -> dict:
    """Return aggregated email statistics: total, by_status, by_provider, by_month (last 12)."""

    base = select(JobEmail)
    base = _apply_offer_exclusion(base).subquery()

    # total
    total = db.execute(select(func.count()).select_from(base)).scalar_one()

    # by_status
    by_status_rows = db.execute(
        select(base.c.status, func.count().label("cnt"))
        .select_from(base)
        .group_by(base.c.status)
    ).all()
    by_status = {row.status: row.cnt for row in by_status_rows}

    # by_provider
    by_provider_rows = db.execute(
        select(base.c.provider, func.count().label("cnt"))
        .select_from(base)
        .group_by(base.c.provider)
    ).all()
    by_provider = {row.provider: row.cnt for row in by_provider_rows}

    # by_month — last 12 months, sorted chronologically
    by_month_rows = db.execute(
        select(base.c.month_key, func.count().label("cnt"))
        .select_from(base)
        .group_by(base.c.month_key)
        .order_by(base.c.month_key.desc())
        .limit(12)
    ).all()
    by_month = [
        MonthCount(month=row.month_key, count=row.cnt)
        for row in sorted(by_month_rows, key=lambda r: r.month_key)
    ]

    return {"total": total, "by_status": by_status, "by_provider": by_provider, "by_month": by_month}
