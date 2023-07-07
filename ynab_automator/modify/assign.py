from __future__ import annotations
import re
from ynab_automator.fetch import months

from ynab_automator.fetch import retrieve_distilled
from ynab_automator.datastructures.ynab_dataclasses import Category, MonthCategory
from ynab_automator.modify import prepare


def get_updated_m_categories(
    m_categories: list[MonthCategory], categories_config: list[Category]
) -> list[MonthCategory]:
    all_updated_m_categories = []

    for m_category in m_categories:
        category_config = prepare.get_matching_category_config(
            categories_config, m_category
        )
        sequence_of_updated_m_categories = m_category_dispatcher(
            m_category, category_config
        )
        all_updated_m_categories.extend(sequence_of_updated_m_categories)

    return all_updated_m_categories


def m_category_dispatcher(
    m_category: MonthCategory, category_config: Category
) -> tuple[MonthCategory]:
    goal_type = m_category.data["goal_type"]
    if goal_type == "NEED":
        if category_config.overflow:
            return new_month_NEED_with_overflow(m_category)
        else:
            return new_month_NEED_without_overflow(m_category)
    elif goal_type == "MF":
        return new_month_savings_builder_MF(m_category)
    elif goal_type == "TB":
        return new_month_savings_balance_TB(m_category)
    else:
        raise ValueError(f"Unexpected goal_type: {m_category.data['goal_type']}")


def new_month_NEED_without_overflow(
    m_category: MonthCategory,
) -> tuple[MonthCategory]:
    to_add = m_category.data["goal_under_funded"]
    m_category.new_budgeted = m_category.old_budgeted + to_add
    return (m_category,)


def new_month_NEED_with_overflow(m_category: MonthCategory) -> list[MonthCategory]:
    left_to_add = m_category.data["goal_target"]
    return overflow_loop(m_category, left_to_add)


def overflow_loop(m_category: MonthCategory, left_to_add: int) -> list[MonthCategory]:
    updated_m_categories = []
    cycle = 0
    while left_to_add > 0:
        left_to_add, updated_m_category = overflow_cycle(m_category, cycle, left_to_add)
        updated_m_categories.append(updated_m_category)
        cycle += 1

    return updated_m_categories


def overflow_cycle(
    m_category: MonthCategory, overflow_cycle: int, left_to_add: int
) -> tuple[int, MonthCategory]:
    budget_ynab_id = m_category.budget_ynab_id
    category_ynab_id = m_category.category_ynab_id
    month = months.offset_month(m_category.month, overflow_cycle)

    if overflow_cycle == 0:
        month_celing = m_category.data["goal_under_funded"]
    elif overflow_cycle > 0:
        category_data = retrieve_distilled.month_category(
            budget_ynab_id, month, category_ynab_id
        )
        m_category = MonthCategory(
            data=category_data,
            budget_ynab_id=budget_ynab_id,
            month=month,
            category_ynab_id=category_ynab_id,
        )
        month_celing = m_category.data["goal_target"] - m_category.old_budgeted
    else:
        raise ValueError(f"overflow_cycle is {overflow_cycle}, should be 0 or larger")

    to_add_this_month = min(left_to_add, month_celing)

    if m_category.old_budgeted is None:
        raise ValueError("Expected old_budgeted to be int but is None.")
    m_category.new_budgeted = m_category.old_budgeted + to_add_this_month

    left_to_add -= to_add_this_month
    return left_to_add, m_category


def new_month_savings_builder_MF(m_category: MonthCategory) -> tuple[MonthCategory]:
    to_add = m_category.data["goal_overall_left"]
    m_category.new_budgeted = m_category.old_budgeted + to_add
    return (m_category,)


def new_month_savings_balance_TB(m_category: MonthCategory) -> tuple[MonthCategory]:
    limit = extract_TB_limit(m_category.data["note"])
    to_add = min(m_category.data["goal_overall_left"], limit)
    m_category.new_budgeted = m_category.old_budgeted + to_add
    return (m_category,)


def extract_TB_limit(note: str) -> int | float:
    PATTERN = "^limit: *((?:[0-9]+[ _]*)+)"
    note = note.lower()

    re_match = re.search(PATTERN, note, flags=re.MULTILINE)
    if not re_match:
        return float("inf")

    number_str: str = re_match[1]
    number_str: str = re.sub(" +", "", number_str)
    number_str: str = re.sub("_+", "_", number_str)
    number_int: int = int(number_str) * 1000

    return number_int
