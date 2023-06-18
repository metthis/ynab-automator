from __future__ import annotations
from datetime import date


def get_current_month() -> str:
    d = date.today().replace(day=1)
    return d.isoformat()


def offset_month(iso_month: str, offset_in_months: int = 0) -> str:
    if not offset_in_months:
        return iso_month

    d = date.fromisoformat(iso_month)

    year = d.year
    month = d.month + offset_in_months

    while month > 12:
        month -= 12
        year += 1

    while month < 1:
        month += 12
        year -= 1

    d = d.replace(year=year, month=month)

    return d.isoformat()
