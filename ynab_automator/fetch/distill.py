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


def month(json: dict) -> dict:
    return json["data"]["month"]


def month_into_categories(json: dict) -> List[dict]:
    return json["data"]["month"]["categories"]


def month_category(json: dict) -> dict:
    return json["data"]["category"]
