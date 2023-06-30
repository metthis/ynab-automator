from __future__ import annotations

import pytest

from ynab_automator.fetch import retrieve_distilled


def test_budgets():
    foo = retrieve_distilled.budgets()
    assert isinstance(foo, list)
    assert len(foo) == 5


cases = [
    "c1e0ea99-5668-483b-b01e-25b348fe3437",  # Common budget
    "f8017349-fb67-4db6-b02c-bf212e6bb438",  # MV EUR
    "b236bcc3-2a34-46a0-8c63-67b11d4201e1",  # MV CZK
]


@pytest.mark.parametrize("budget_ynab_id", cases)
def test_categories(budget_ynab_id):
    foo = retrieve_distilled.categories(budget_ynab_id)
    assert isinstance(foo, list)
    active_category_names = [x["name"] for x in foo if not x["deleted"]]
    print(f"Categories: {len(active_category_names)}")
    print(f"Category names: {active_category_names}")


cases = [
    (
        "5f228e6f-fabe-40d7-bf67-6fc09350e241",  # All used goal types
        None,
        [
            "f976f06c-53fa-4f3f-bfd5-f52cb32493df",  # NEED
            "d132450f-62cf-4879-a094-810466c4c90a",  # TB savings balance
            "3dc19598-d1c2-4f89-ad3c-2b8b4d86258c",  # MF savings builder
        ],
    ),
    (
        None,
        "NEED monthly",
        [
            "7bc6c91b-a130-4ec3-aaca-aa72673d78a7",  # Empty
            "6cfc508d-a311-4e0b-bacb-5a67488c059f",  # Partially full
            "24610eb9-82ce-444e-8be1-a57feab1df6e",  # Full
            "df83267a-7d61-4c22-8c22-2dd54f01b440",  # Overflown +0,4
            "41d54a43-694e-42e0-b776-ca831d266a5f",  # Overflown +1
            "df4c2bcb-7bd1-42d3-bfa0-aeef4b59cc11",  # Overflown +1,4
        ],
    ),
    (
        "5f228e6f-fabe-40d7-bf67-6fc09350e241",  # All used goal types
        "NEED monthly",
        [
            # A conflicting ynab_id and name are provided, ynab_id takes precedence:
            "f976f06c-53fa-4f3f-bfd5-f52cb32493df",  # NEED
            "d132450f-62cf-4879-a094-810466c4c90a",  # TB savings balance
            "3dc19598-d1c2-4f89-ad3c-2b8b4d86258c",  # MF savings builder
        ],
    ),
]


@pytest.mark.parametrize("group_ynab_id, group_name, category_ynab_ids", cases)
def test_categories_from_groups_without_exception(
    group_ynab_id: str | None, group_name: str | None, category_ynab_ids: list[str]
):
    result = retrieve_distilled.categories_from_group(
        budget_ynab_id="7aadfdf9-ee55-40f1-b26b-09ffc4563085",  # Belongs to "Test budget"
        group_ynab_id=group_ynab_id,
        group_name=group_name,
    )
    assert isinstance(result, list)
    for category in result:
        assert isinstance(category, dict)
    assert len(result) == len(category_ynab_ids)
    result_category_ynab_ids = [x["id"] for x in result]
    result_category_ynab_ids.sort()
    category_ynab_ids.sort()
    assert result_category_ynab_ids == category_ynab_ids


def test_categories_from_groups_with_exception():
    with pytest.raises(TypeError) as excinfo:
        result = retrieve_distilled.categories_from_group(
            budget_ynab_id="7aadfdf9-ee55-40f1-b26b-09ffc4563085",  # Belongs to "Test budget"
            group_ynab_id=None,
            group_name=None,
        )
    assert (
        "Need to supply group_name and/or group_ynab_id as str but both are None"
        in str(excinfo.value)
    )


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
    foo = retrieve_distilled.month(budget_ynab_id, month)
    assert isinstance(foo, dict)
    assert len(foo) == 9


@pytest.mark.parametrize("budget_ynab_id, month", cases)
def test_month_categories(budget_ynab_id, month):
    foo = retrieve_distilled.month_categories(budget_ynab_id, month)
    assert isinstance(foo, list)
    active_category_names = [x["name"] for x in foo if not x["deleted"]]
    print(f"Categories (in month): {len(active_category_names)}")
    print(f"Category names (in month): {active_category_names}")


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
    foo = retrieve_distilled.month_category(budget_ynab_id, month, category_ynab_id)
    assert isinstance(foo, dict)
    assert len(foo) == 23


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
    check_emptiness_then_teardown,
):
    result = retrieve_distilled.push_month_category(
        budget_ynab_id=test_budget_ynab_id,
        month=current_month,
        category_ynab_id=test_category_ynab_id,
        data=data,
    )
    assert isinstance(result, dict)
    assert len(result) == 23
    assert result["id"] == test_category_ynab_id
    assert result["budgeted"] == new_budgeted


if __name__ == "__main__":
    pytest.main([__file__])
