from __future__ import annotations

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.datastructures.enums import ResetMode
from ynab_automator.fetch import retrieve_distilled, months
from ynab_automator.modify import assign


# Just testing the main function, not its extracted helpers.
# But maybe I should test the helpers as well because they are used in drain?


# test_new_month_NEED_with_overflow tests only NEED with a monthly time frame (goal_cadence == 1),
# as that's the only type of goal I'm willing to let overflow.


budget_ynab_id = "7aadfdf9-ee55-40f1-b26b-09ffc4563085"
current_month = months.get_current_month()
ids_and_modes_empty_or_full = (
    ("7bc6c91b-a130-4ec3-aaca-aa72673d78a7", ResetMode.EMPTY),
    ("24610eb9-82ce-444e-8be1-a57feab1df6e", ResetMode.FULL),
    ("41d54a43-694e-42e0-b776-ca831d266a5f", ResetMode.OVERFLOWN_FULLY),
)
ids_and_modes_partial = (
    ("6cfc508d-a311-4e0b-bacb-5a67488c059f", ResetMode.PARTIALLY_FULL),
    ("df83267a-7d61-4c22-8c22-2dd54f01b440", ResetMode.OVERFLOWN_PARTIALLY),
    ("df4c2bcb-7bd1-42d3-bfa0-aeef4b59cc11", ResetMode.OVERFLOWN_FULLY_PLUS_PARTIALLY),
)

category_ids = (
    "7bc6c91b-a130-4ec3-aaca-aa72673d78a7",
    "24610eb9-82ce-444e-8be1-a57feab1df6e",
    "41d54a43-694e-42e0-b776-ca831d266a5f",
    "6cfc508d-a311-4e0b-bacb-5a67488c059f",
    "df83267a-7d61-4c22-8c22-2dd54f01b440",
    "df4c2bcb-7bd1-42d3-bfa0-aeef4b59cc11",
)
modes = (
    ResetMode.EMPTY,
    ResetMode.FULL,
    ResetMode.OVERFLOWN_FULLY,
    ResetMode.PARTIALLY_FULL,
    ResetMode.OVERFLOWN_PARTIALLY,
    ResetMode.OVERFLOWN_FULLY_PLUS_PARTIALLY,
)
expected_budgeted = (
    (10_000,),
    (10_000,) * 2,
    (10_000,) * 3,
    (10_000, 4_000),
    (10_000, 10_000, 4_000),
    (10_000, 10_000, 10_000, 4_000),
)
cases = tuple(zip(category_ids, modes, expected_budgeted, strict=True))


@pytest.mark.parametrize("budget_ynab_id", (budget_ynab_id,))
@pytest.mark.parametrize("first_month", (current_month,))
@pytest.mark.parametrize("category_ynab_id, mode, expected_budgeted", cases)
def test_new_month_NEED_with_overflow(
    budget_ynab_id: str,
    first_month: str,
    category_ynab_id: str,
    mode: ResetMode,
    expected_budgeted: tuple[int],
    reset_before,
):
    data = retrieve_distilled.month_category(
        budget_ynab_id, first_month, category_ynab_id
    )
    m_category = MonthCategory(
        data=data, budget_ynab_id=budget_ynab_id, month=first_month
    )
    result = assign.new_month_NEED_with_overflow(m_category)

    budgeted = tuple(m_category.new_budgeted for m_category in result)
    assert budgeted == expected_budgeted

    for m_category in result:
        assert m_category.budget_ynab_id == budget_ynab_id
        assert m_category.category_ynab_id == category_ynab_id

    month_offsets = range(len(expected_budgeted))
    expected_months = tuple(
        months.offset_month(first_month, offset) for offset in month_offsets
    )
    result_months = tuple(m_category.month for m_category in result)
    assert result_months == expected_months


if __name__ == "__main__":
    pytest.main([__file__])
