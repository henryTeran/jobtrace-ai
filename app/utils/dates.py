"""Date helper utilities."""

from __future__ import annotations

from datetime import datetime


FRENCH_MONTHS = {
    1: "Janvier",
    2: "Fevrier",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Aout",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Decembre",
}


def month_key_from_datetime(value: datetime) -> str:
    """Return YYYY-MM month key from datetime."""

    return value.strftime("%Y-%m")


def french_month_title(month_key: str) -> str:
    """Return month title like 'Fevrier 2026' from YYYY-MM key."""

    year_str, month_str = month_key.split("-", 1)
    month_num = int(month_str)
    return f"{FRENCH_MONTHS.get(month_num, month_str)} {year_str}"
