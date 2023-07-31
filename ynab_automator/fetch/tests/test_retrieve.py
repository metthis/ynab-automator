from __future__ import annotations

import pytest

from ynab_automator.fetch import retrieve, distill, retrieve_distilled


def test_budgets():
    json = retrieve.budgets()
    assert isinstance(json, dict)
    assert "data" in json

    # Current number of budgets, including those shared with me.
    assert len(json["data"]["budgets"]) == 5


cases = [
    "c1e0ea99-5668-483b-b01e-25b348fe3437",  # Common budget
    "f8017349-fb67-4db6-b02c-bf212e6bb438",  # MV EUR
    "b236bcc3-2a34-46a0-8c63-67b11d4201e1",  # MV CZK
]


@pytest.mark.parametrize("budget_ynab_id", cases)
def test_categories(budget_ynab_id):
    json = retrieve.categories(budget_ynab_id)
    assert isinstance(json, dict)
    assert "data" in json
    active_category_group_names = [
        x["name"] for x in json["data"]["category_groups"] if not x["deleted"]
    ]
    print(f"Category groups: {len(active_category_group_names)}")
    print(f"Category group names: {active_category_group_names}")


cases = [
    ("c1e0ea99-5668-483b-b01e-25b348fe3437", "2023-05-01"),
    ("c1e0ea99-5668-483b-b01e-25b348fe3437", "2023-06-01"),
    ("c1e0ea99-5668-483b-b01e-25b348fe3437", "2023-02-01"),
    ("c1e0ea99-5668-483b-b01e-25b348fe3437", "2022-12-01"),
    ("f8017349-fb67-4db6-b02c-bf212e6bb438", "2023-05-01"),
    ("f8017349-fb67-4db6-b02c-bf212e6bb438", "2023-03-01"),
    ("f8017349-fb67-4db6-b02c-bf212e6bb438", "2023-01-01"),
    ("b236bcc3-2a34-46a0-8c63-67b11d4201e1", "2023-05-01"),
    ("b236bcc3-2a34-46a0-8c63-67b11d4201e1", "2023-04-01"),
    ("b236bcc3-2a34-46a0-8c63-67b11d4201e1", "2023-02-01"),
]


@pytest.mark.parametrize("budget_ynab_id, month", cases)
def test_month(budget_ynab_id, month):
    json = retrieve.month(budget_ynab_id, month)
    assert isinstance(json, dict)
    assert "data" in json
    assert len(json["data"]["month"]) == 9


cases = [
    "567fd3f3-0d59-43c8-9edb-c5371896d8d0",
    "7d3c38fa-1bd3-4471-9d39-d0342cac0d42",
    "1be05b77-b871-43f9-a756-8afea9ccdce2",
    "76ad6fcf-9ae8-4282-b6a2-ceaeb5534fee",
    "c33c49b3-e6f9-4192-88e7-4da7368aff4d",
    "465ad8ab-f4b2-4190-8636-ab25d420aca6",
    "59923e4e-dc0d-4003-9ff9-aa4b6b5a506b",
    "33b5155c-7744-46c3-a0e6-1c85970ddc29",
    "1393d143-deb1-4afe-a745-624851d8a7bd",
    "3c6c19f7-9e95-44e0-8468-9a099395e1b8",
]


cases = [
    ("c1e0ea99-5668-483b-b01e-25b348fe3437", "2023-05-01", category_ynab_id)
    for category_ynab_id in cases
]


@pytest.mark.parametrize("budget_ynab_id, month, category_ynab_id", cases)
def test_month_category(budget_ynab_id, month, category_ynab_id):
    json = retrieve.month_category(budget_ynab_id, month, category_ynab_id)
    assert isinstance(json, dict)
    assert "data" in json
    assert len(json["data"]["category"]) == 23


test_budget_ynab_id = "7aadfdf9-ee55-40f1-b26b-09ffc4563085"  # Belongs to "Test budget"
categories = retrieve_distilled.categories_from_group(
    test_budget_ynab_id, group_name="All used goal types"
)


@pytest.mark.parametrize("test_budget_ynab_id", [test_budget_ynab_id])
@pytest.mark.parametrize("test_category_ynab_id", [x["id"] for x in categories])
def test_push_month_category(
    test_budget_ynab_id: str,
    test_category_ynab_id: str,
    current_month: str,
    new_budgeted: int,
    data: str,
    empty_before: None,
):
    result = retrieve.push_month_category(
        budget_ynab_id=test_budget_ynab_id,
        month=current_month,
        category_ynab_id=test_category_ynab_id,
        data=data,
    )
    assert isinstance(result, dict)
    distilled = distill.month_category(result)
    assert len(distilled) == 23
    assert distilled["id"] == test_category_ynab_id
    assert distilled["budgeted"] == new_budgeted


if __name__ == "__main__":
    pytest.main([__file__])
