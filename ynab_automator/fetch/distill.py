from __future__ import annotations
from typing import List


def budgets(json: dict) -> List[dict]:
    return json["data"]["budgets"]


def categories(json: dict) -> List[dict]:
    categories = []
    for group in json["data"]["category_groups"]:
        for category in group["categories"]:
            categories.append(category)
    return categories


def categories_from_group(
    json: dict,
    *,
    group_ynab_id: str | None = None,
    group_name: str | None = None,
) -> list[dict]:
    if group_ynab_id is None and group_name is None:
        raise TypeError(
            "Need to supply group_name and/or group_ynab_id as str but both are None"
        )

    categories = []
    for group in json["data"]["category_groups"]:
        if group_ynab_id is not None and group["id"] not in group_ynab_id:
            continue
        elif group_ynab_id is None and group["name"] not in group_name:
            # If only group_name is provided and more groups have the same name,
            # categories from all such groups will be included.
            continue
        for category in group["categories"]:
            categories.append(category)
    return categories


def month(json: dict) -> dict:
    return json["data"]["month"]


def month_into_categories(json: dict) -> List[dict]:
    return json["data"]["month"]["categories"]


def month_category(json: dict) -> dict:
    return json["data"]["category"]
