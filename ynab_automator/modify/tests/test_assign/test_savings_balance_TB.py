from __future__ import annotations
import textwrap
from random import randint

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.modify import assign


notes = [
    """\
    Limit: 10 EUR
    """,
    """\
    Line 1
    LIMIT:         2_ _ 0 gbp
    Line 3    
    """,
    """\
    Line 1
    line 2
    lImIT:3________0 usdfgvd hellod 34 beep
    liNE 4
    last line
    """,
    """\
    LIMIT: 3_000_000 blurps and 1_000_000_000_000 3403 beeps
    """,
    # No match on this one because "limit" isn't at the beginning of a line:
    """\
    Line 1
    Line 2
    Line 3 limit: 40 eur
    Line 4
    """,
]


notes = [textwrap.dedent(x) for x in notes]


expected_limits = [
    10_000,
    20_000,
    30_000,
    3_000_000_000,
    float("inf"),
]


cases = list(zip(notes, expected_limits, strict=True))


@pytest.mark.parametrize("note, expected", cases)
def test_extract_TB_limit(note: str, expected: int | float):
    result = assign.extract_TB_limit(note)
    assert result == expected


# cases is a list made up of tuples, with each tuple made up of (among other things) 2 identical dictionaries.
# The dictionaries have to be doubled like this because it seems to be the only way
# to pass each dictionary both to the fixture (called: m_category)
# and as a variable to the test itself (called: data).
# This approach will be used in other tests as well.


cases = [
    {
        "budgeted": randint(0, 100_000),
        "goal_overall_left": randint(0, 100_000),
    }
    for _ in range(5)
]


for data, note in zip(cases, notes, strict=True):
    data["note"] = note


cases = [
    (data, data, limit) for data, limit in zip(cases, expected_limits, strict=True)
]


@pytest.mark.parametrize(
    "m_category, data, expected_limit", cases, indirect=["m_category"]
)
def test_new_month_savings_balance_TB(
    m_category: MonthCategory, data: dict, expected_limit: int | float
):
    result = assign.new_month_savings_balance_TB(m_category)
    assert isinstance(result, tuple)
    assert len(result) == 1

    resulted_m_category = result[0]
    assert isinstance(resulted_m_category, MonthCategory)
    assert resulted_m_category.new_budgeted == data["budgeted"] + min(
        data["goal_overall_left"], expected_limit
    )
    assert 0 <= resulted_m_category.delta() <= expected_limit
    if data["goal_overall_left"] >= expected_limit:
        assert resulted_m_category.delta() == expected_limit
    else:
        assert resulted_m_category.delta() == data["goal_overall_left"]
