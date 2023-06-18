from __future__ import annotations

import pytest

from ynab_automator.modify import prepare
from ynab_automator.fetch import retrieve_distilled, months
from ynab_automator.datastructures.ynab_dataclasses import Category, MonthCategory


def get_test_cases():
    budget_ynab_id = "c1e0ea99-5668-483b-b01e-25b348fe3437"
    month = months.get_current_month()
    categories_data = retrieve_distilled.month_categories(budget_ynab_id, month)
    categories_config = prepare.get_sorted_categories_config_from_db(budget_ynab_id)
    category_ynab_ids = prepare.get_ynab_ids_from_categories_config(categories_config)
    return [
        (budget_ynab_id, month, categories_data, category_ynab_ids, categories_config)
    ]


@pytest.mark.parametrize(
    "budget_ynab_id, month, categories_data, category_ynab_ids, categories_config",
    get_test_cases(),
)
def test_get_initialised_m_categories(
    budget_ynab_id: str,
    month: str,
    categories_data: tuple[dict],
    category_ynab_ids: tuple[str],
    categories_config: list[Category],
):
    result = prepare.get_initialised_m_categories(
        budget_ynab_id, month, categories_data, category_ynab_ids, categories_config
    )
    assert isinstance(result, list)
    assert len(result) == len(category_ynab_ids)
    result_ynab_ids = (x.category_ynab_id for x in result)
    assert set(result_ynab_ids) == set(category_ynab_ids)
    for m_category in result:
        assert isinstance(m_category, MonthCategory)
        assert isinstance(m_category.budget_ynab_id, str)
        assert m_category.budget_ynab_id == budget_ynab_id
        assert isinstance(m_category.month, str)
        assert m_category.month == month
        assert isinstance(m_category.data, dict)
        assert len(m_category.data) == 23
        assert isinstance(m_category.name, str)
        assert m_category.name == m_category.data["name"]
        assert isinstance(m_category.category_ynab_id, str)
        assert m_category.category_ynab_id in category_ynab_ids
        assert m_category.category_ynab_id == m_category.data["id"]
        assert isinstance(m_category.old_budgeted, int)
        assert m_category.old_budgeted == m_category.data["budgeted"]
        assert m_category.new_budgeted is None
        category_config = prepare.get_matching_category_config(
            categories_config, m_category
        )
        assert isinstance(m_category.position, int)
        assert m_category.position == category_config.position
        assert isinstance(m_category.category_id, int)
        assert m_category.category_id == category_config.id
        assert isinstance(m_category.drain_into, (int, type(None)))
        assert m_category.drain_into == category_config.drain_into
