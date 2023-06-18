from __future__ import annotations
from typing import List, Tuple

from ynab_automator.fetch import db_connection
from ynab_automator.datastructures.ynab_dataclasses import Category, MonthCategory


def get_sorted_categories_config_from_db(budget_ynab_id: str) -> List[Category]:
    SQL = """\
        SELECT Category.position, Category.name, Category.drain_into,
            Category.overflow, Category.budget_id, Category.id,
            Category.ynab_id
        FROM Category JOIN Budget ON Category.budget_id = Budget.id
        WHERE Budget.ynab_id = ?
        AND Category.position IS NOT NULL
        ORDER BY Category.position
    """
    db_reader = db_connection.DbConnection()
    db_reader.cur.execute(SQL, (budget_ynab_id,))
    rows = db_reader.cur.fetchall()

    categories_config = []
    for row in rows:
        category_config = Category(*row)
        categories_config.append(category_config)

    categories_config.sort()  # Obsolete because of ORDER BY Category.position in the SQL query
    return categories_config


def get_ynab_ids_from_categories_config(
    categories_config: List[Category],
) -> Tuple[str]:
    return tuple(x.category_ynab_id for x in categories_config)


def get_initialised_m_categories(
    budget_ynab_id: str,
    month: str,
    categories_data: Tuple[dict],
    category_ynab_ids: Tuple[str],
    categories_config: List[Category],
) -> List[MonthCategory]:
    m_categories = []
    for category_data in categories_data:
        ynab_id = category_data["id"]
        if ynab_id not in category_ynab_ids:
            continue
        m_category = MonthCategory(
            data=category_data,
            budget_ynab_id=budget_ynab_id,
            month=month,
            category_ynab_id=ynab_id,
        )
        category_config = get_matching_category_config(categories_config, m_category)
        m_category.position = category_config.position
        m_category.category_id = category_config.id
        m_category.drain_into = category_config.drain_into
        m_categories.append(m_category)
    return m_categories


def get_matching_category_config(
    categories_config: List[Category], m_category: MonthCategory
) -> Category:
    for category_config in categories_config:
        if category_config.category_ynab_id == m_category.category_ynab_id:
            return category_config


def sort_m_categories_by_position(
    m_categories: List[MonthCategory],
) -> List[MonthCategory]:
    return sorted(m_categories, key=lambda m_category: m_category.position)
