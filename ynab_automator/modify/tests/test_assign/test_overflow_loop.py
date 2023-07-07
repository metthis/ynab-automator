from __future__ import annotations
from itertools import product

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.datastructures.enums import ResetMode
from ynab_automator.fetch import retrieve_distilled, months
from ynab_automator.modify import assign


# I don't test overflow_cycle because it's only ever used by overflow_loop which I test here.


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


# I want to cover partially filling, full topping up, and overflowing each of the test categories:
to_add_empty_or_full = (3_000, 10_000, 13_000)
to_add_partial = (3_000, 6_000, 13_000)


ids_modes_and_amounts_empty_or_full = list(
    product(ids_and_modes_empty_or_full, to_add_empty_or_full)
)
ids_modes_and_amounts_partial = list(product(ids_and_modes_partial, to_add_partial))
ids_modes_and_amounts = (
    ids_modes_and_amounts_empty_or_full + ids_modes_and_amounts_partial
)


expected_budgeted = {}
expected_budgeted["empty"] = ((3_000,), (10_000,), (10_000, 3_000))
expected_budgeted["full"] = tuple(
    (10_000, *amounts) for amounts in expected_budgeted["empty"]
)
expected_budgeted["overflown_fully"] = tuple(
    (10_000, 10_000, *amounts) for amounts in expected_budgeted["empty"]
)
expected_budgeted["partially_full"] = ((7_000,), (10_000,), (10_000, 7_000))
expected_budgeted["overflown_partially"] = tuple(
    (10_000, *amounts) for amounts in expected_budgeted["partially_full"]
)
expected_budgeted["overflown_fully_plus_partially"] = tuple(
    (10_000, 10_000, *amounts) for amounts in expected_budgeted["partially_full"]
)
unpacked_expected_budgeted = []
for tup in expected_budgeted.values():
    unpacked_expected_budgeted.extend(tup)


cases = (
    (id, mode, to_add, budgeted)
    for (((id, mode), to_add), budgeted) in zip(
        ids_modes_and_amounts, unpacked_expected_budgeted, strict=True
    )
)
cases = tuple(cases)


@pytest.mark.parametrize("budget_ynab_id", (budget_ynab_id,))
@pytest.mark.parametrize("first_month", (current_month,))
@pytest.mark.parametrize("category_ynab_id, mode, to_add, expected_budgeted", cases)
def test_overflow_loop(
    budget_ynab_id: str,
    first_month: str,
    category_ynab_id: str,
    mode: ResetMode,
    to_add: int,
    expected_budgeted: tuple[int],
    reset_before,
):
    data = retrieve_distilled.month_category(
        budget_ynab_id, first_month, category_ynab_id
    )
    m_category = MonthCategory(
        data=data, budget_ynab_id=budget_ynab_id, month=first_month
    )
    result = assign.overflow_loop(m_category, to_add)

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
