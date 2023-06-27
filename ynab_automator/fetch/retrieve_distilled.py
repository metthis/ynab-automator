from __future__ import annotations
from typing import List
from ynab_automator.fetch import distill

from ynab_automator.fetch import retrieve


def budgets() -> List[dict]:
    json = retrieve.budgets()
    return distill.budgets(json)


def categories(budget_ynab_id: str) -> List[dict]:
    json = retrieve.categories(budget_ynab_id)
    return distill.categories(json)


def categories_from_group(
    budget_ynab_id: str,
    *,
    group_ynab_id: str | None = None,
    group_name: str | None = None,
) -> list[dict]:
    json = retrieve.categories(budget_ynab_id)
    return distill.categories_from_group(
        json, group_ynab_id=group_ynab_id, group_name=group_name
    )


def month(budget_ynab_id: str, month: str) -> dict:
    json = retrieve.month(budget_ynab_id, month)
    return distill.month(json)


def month_categories(budget_ynab_id: str, month: str) -> List[dict]:
    json = retrieve.month(budget_ynab_id, month)
    return distill.month_into_categories(json)


def month_category(budget_ynab_id: str, month: str, category_ynab_id: str) -> dict:
    json = retrieve.month_category(budget_ynab_id, month, category_ynab_id)
    return distill.month_category(json)
