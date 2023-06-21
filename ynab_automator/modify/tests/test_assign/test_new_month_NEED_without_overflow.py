from __future__ import annotations
from random import randint

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.modify import assign


# cases is a list made up of tuples, with each tuple made up of 2 identical dictionaries.
# The dictionaries have to be doubled like this because it seems to be the only way
# to pass each dictionary both to the fixture (called: m_category)
# and as a variable to the test itself (called: data).
# This approach will be used in other tests as well.


cases = (
    {
        "budgeted": randint(0, 499) * 1000,
        "goal_under_funded": randint(0, 499) * 1000,
    }
    for _ in range(5)
)
cases = [(x, x) for x in cases]


@pytest.mark.parametrize("m_category, data", cases, indirect=["m_category"])
def test_new_month_NEED_without_overflow(m_category: MonthCategory, data: dict):
    result = assign.new_month_NEED_without_overflow(m_category)
    assert isinstance(result, tuple)
    assert len(result) == 1

    resulted_m_category = result[0]
    assert isinstance(resulted_m_category, MonthCategory)
    assert (
        resulted_m_category.new_budgeted == data["budgeted"] + data["goal_under_funded"]
    )
