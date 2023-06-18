from __future__ import annotations
from typing import List

from ynab_automator.fetch import retrieve_distilled
from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.modify import prepare
from ynab_automator.modify import assign, drain


def update_m_categories(budget_ynab_id: str, month: str) -> List[MonthCategory]:
    categories_data = retrieve_distilled.month_categories(budget_ynab_id, month)
    categories_config = prepare.get_sorted_categories_config_from_db(budget_ynab_id)
    ynab_ids = prepare.get_ynab_ids_from_categories_config(categories_config)
    m_categories = prepare.get_initialised_m_categories(
        budget_ynab_id, month, categories_data, ynab_ids, categories_config
    )
    m_categories = drain.get_m_categories_after_draining(
        m_categories, categories_config
    )
    m_categories = prepare.sort_m_categories_by_position(m_categories)
    return assign.get_updated_m_categories(m_categories, categories_config)
