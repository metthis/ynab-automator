from __future__ import annotations

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory, Category
from ynab_automator.datastructures.enums import ResetMode
from ynab_automator.fetch import retrieve_distilled, months
from ynab_automator.modify import assign


def verify_m_category(
    m_category: MonthCategory,
    data: dict,
    budget_ynab_id: str = "budget_ynab_id",
    month: str = months.get_current_month(),
):
    assert set(data.items()).issubset(set(m_category.data.items()))
    assert m_category.budget_ynab_id == budget_ynab_id
    assert m_category.month == month


budget_ynab_id = "7aadfdf9-ee55-40f1-b26b-09ffc4563085"
first_month = months.get_current_month()
category_ynab_ids = (
    # NEED with overflow:
    "f976f06c-53fa-4f3f-bfd5-f52cb32493df",
    # NEED without overflow:
    "01b96637-34a8-4394-8b94-e6a3fa7ef0ab",
    # TB savings balance:
    "d132450f-62cf-4879-a094-810466c4c90a",
    # MF savings builder:
    "3dc19598-d1c2-4f89-ad3c-2b8b4d86258c",
)
categories_config = [
    # The following are appropriate for the MonthCategories that'll be created based on the data above:
    Category(
        category_ynab_id=category_ynab_ids[0],
        overflow=1,
    ),
    Category(
        category_ynab_id=category_ynab_ids[1],
        overflow=0,
    ),
    Category(
        category_ynab_id=category_ynab_ids[2],
        overflow=None,
    ),
    Category(
        category_ynab_id=category_ynab_ids[3],
        overflow=None,
    ),
    # The following are extra and meant to be ignored by the tested function:
    Category(
        category_ynab_id="EXTRA_1",
        overflow=None,
    ),
    Category(
        category_ynab_id="EXTRA_2",
        overflow=0,
    ),
    Category(
        category_ynab_id="EXTRA_3",
        overflow=1,
    ),
]
mode = ResetMode.PARTIALLY_FULL
expected_budgeted = (
    # NEED with overflow:
    10_000,
    4_000,
    # NEED without overflow:
    10_000,
    # TB savings balance:
    9_000,
    # MF savings builder:
    10_000,
)
expected_delta = (
    # NEED with overflow:
    6_000,
    4_000,
    # NEED without overflow:
    6_000,
    # TB savings balance:
    5_000,
    # MF savings builder:
    6_000,
)


@pytest.mark.parametrize("budget_ynab_id", (budget_ynab_id,))
@pytest.mark.parametrize("first_month", (first_month,))
@pytest.mark.parametrize("category_ynab_ids", (category_ynab_ids,))
@pytest.mark.parametrize("categories_config", (categories_config,))
@pytest.mark.parametrize("mode", (mode,))
@pytest.mark.parametrize("expected_budgeted", (expected_budgeted,))
@pytest.mark.parametrize("expected_delta", (expected_delta,))
def test_get_updated_m_categories(
    budget_ynab_id: str,
    first_month: str,
    category_ynab_ids: str,
    categories_config: list[Category],
    mode: ResetMode,
    expected_budgeted: tuple[int],
    expected_delta: tuple[int],
    reset_before_all_and_init_m_categories: list[MonthCategory],
):
    m_categories = reset_before_all_and_init_m_categories
    result = assign.get_updated_m_categories(m_categories, categories_config)
    assert len(result) == len(expected_budgeted)
    assert len(result) == len(expected_delta)
    zipped = zip(result, expected_budgeted, expected_delta, strict=True)
    for m_category, budgeted, delta in zipped:
        assert m_category.new_budgeted == budgeted
        assert m_category.delta() == delta


if __name__ == "__main__":
    pytest.main([__file__, "-vs"])
