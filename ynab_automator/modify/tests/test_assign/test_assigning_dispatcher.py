from __future__ import annotations
import itertools

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory, Category
from ynab_automator.modify import assign


goal_types = ("NEED", "MF", "TB")
pieces_of_data = ({"goal_type": x} for x in goal_types)


overflows = (None, 0, 1)
category_configs = (Category(overflow=x) for x in overflows)


permutations = itertools.product(pieces_of_data, category_configs)


tupled_results = [
    (assign.new_month_NEED_without_overflow,) * 2,
    (assign.new_month_NEED_with_overflow,),
    (assign.new_month_savings_builder_MF,) * 3,
    (assign.new_month_savings_balance_TB,) * 3,
]
results = itertools.chain(*tupled_results)


cases = [
    (data, category_config, result)
    for ((data, category_config), result) in zip(permutations, results, strict=True)
]


@pytest.mark.parametrize("data, category_config, expected_result", cases)
def test_assigning_dispatcher(
    data: dict,
    m_category: MonthCategory,
    category_config: Category,
    expected_result: function,
):
    result = assign.assigning_dispatcher(m_category, category_config)
    assert result == expected_result


overflows = (-12, -1.1, 1.1, 2, 12, "", "string", (), [], {})
category_configs = (Category(overflow=x) for x in overflows)


@pytest.mark.parametrize("category_config", category_configs)
def test_assigning_dispatcher_with_overflow_ValueError(
    m_category: MonthCategory,
    category_config: Category,
):
    with pytest.raises(ValueError) as excinfo:
        assign.assigning_dispatcher(m_category, category_config)
    assert (
        f"Category.overflow should be 0, 1 or None but is: {category_config.overflow}"
        in str(excinfo.value)
    )


goal_types = ("", "_", "foo", "BAR", "123")
pieces_of_data = ({"goal_type": x} for x in goal_types)
category_configs = (Category(overflow=None),)


@pytest.mark.parametrize("data", pieces_of_data)
@pytest.mark.parametrize("category_config", category_configs)
def test_assigning_dispatcher_with_goal_type_ValueError(
    data: dict,
    m_category: MonthCategory,
    category_config: Category,
):
    with pytest.raises(ValueError) as excinfo:
        assign.assigning_dispatcher(m_category, category_config)
    assert f"Unexpected goal_type: {m_category.data['goal_type']}" in str(excinfo.value)


goal_types = (0, 1.1, (), [], {}, None)
pieces_of_data = ({"goal_type": x} for x in goal_types)
category_configs = (Category(overflow=None),)


@pytest.mark.parametrize("data", pieces_of_data)
@pytest.mark.parametrize("category_config", category_configs)
def test_assigning_dispatcher_with_goal_type_TypeError(
    data: dict,
    m_category: MonthCategory,
    category_config: Category,
):
    with pytest.raises(TypeError) as excinfo:
        assign.assigning_dispatcher(m_category, category_config)
    assert (
        f"goal_type should be str but is: {type(m_category.data['goal_type']).__name__}"
        in str(excinfo.value)
    )


if __name__ == "__main__":
    pytest.main([__file__])
