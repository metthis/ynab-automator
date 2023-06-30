from __future__ import annotations
from random import randint

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.modify import assign


pieces_of_data = (
    {
        "budgeted": randint(0, 499),
        "goal_overall_left": randint(0, 499),
    }
    for _ in range(5)
)


@pytest.mark.parametrize("data", pieces_of_data)
def test_new_month_savings_builder_MF(data: dict, m_category: MonthCategory):
    result = assign.new_month_savings_builder_MF(m_category)
    assert isinstance(result, tuple)
    assert len(result) == 1

    resulted_m_category = result[0]
    assert isinstance(resulted_m_category, MonthCategory)
    assert (
        resulted_m_category.new_budgeted == data["budgeted"] + data["goal_overall_left"]
    )


if __name__ == "__main__":
    pytest.main([__file__])
