from __future__ import annotations
from datetime import date
import time

import pytest

from ynab_automator.fetch import months


@pytest.fixture
def expected_current_month() -> str:
    today = date.fromtimestamp(time.time())
    year = str(today.year)
    month = str(today.month).zfill(2)
    day = "01"
    return f"{year}-{month}-{day}"


def test_get_current_month(expected_current_month: str):
    result = months.get_current_month()
    assert result == expected_current_month


cases = [
    ("2023-07-01", None, "2023-07-01"),
    ("2023-07-01", 0, "2023-07-01"),
    ("2023-02-01", 1, "2023-03-01"),
    ("2026-09-01", -1, "2026-08-01"),
    ("2016-03-01", -4, "2015-11-01"),
    ("2023-09-01", 10, "2024-07-01"),
    ("2021-06-01", 25, "2023-07-01"),
    ("2025-04-01", -30, "2022-10-01"),
]


@pytest.mark.parametrize("iso_month, offset_in_months, expected", cases)
def test_offset_month(iso_month: str, offset_in_months: int, expected: str):
    assert months.offset_month(iso_month, offset_in_months) == expected
