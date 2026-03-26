"""Monthly report aggregation service."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JobEmail


def get_monthly_groups(db: Session, months: list[str] | None = None) -> dict[str, list[JobEmail]]:
    """Return job emails grouped by month key."""

    stmt = select(JobEmail).order_by(JobEmail.received_at.desc())
    if months:
        stmt = stmt.where(JobEmail.month_key.in_(months))

    rows = db.execute(stmt).scalars().all()
    grouped: dict[str, list[JobEmail]] = defaultdict(list)
    for row in rows:
        grouped[row.month_key].append(row)

    ordered = {month: grouped[month] for month in sorted(grouped.keys())}
    return ordered
