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


expected_results = [
    10_000,
    20_000,
    30_000,
    3_000_000_000,
    float("inf"),
]


cases = list(zip(notes, expected_results, strict=True))


@pytest.mark.parametrize("note, expected", cases)
def test_extract_TB_limit(note: str, expected: int | float):
    result = assign.extract_TB_limit(note)
    assert result == expected


# cases is a list made up of tuples, with each tuple made up of 2 identical dictionaries.
# The dictionaries have to be doubled like this because it seems to be the only way
# to pass each dictionary both to the fixture (called: m_category)
# and as a variable to the test itself (called: data).
# This approach will be used in other tests as well.
