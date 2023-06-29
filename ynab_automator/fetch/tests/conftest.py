from __future__ import annotations
import json

import pytest
import requests

from ynab_automator.fetch import months
from ynab_automator.fetch import retrieve, distill, retrieve_distilled


# All the following code is used only by test_push_month_category_...


@pytest.fixture(scope="module")
def current_month() -> str:
    yield months.get_current_month()


@pytest.fixture(scope="module")
def new_budgeted() -> int:
    # 5 EUR
    yield 5000


@pytest.fixture
def data(request):
    yield data_func(request.node.funcargs["new_budgeted"])


def data_func(new_budgeted):
    # Same code as in MonthCategory.update_data:
    python_object = {"category": {"budgeted": new_budgeted}}
    serialised = json.dumps(python_object)
    return serialised


# Made specifically for testing so that I avoid using
# the tested push_month_category() function in a fixture:
def push(budget_ynab_id: str, month: str, category_ynab_id: str, data: str):
    url = retrieve._BASE_URL + retrieve._PATH_MONTH_CATEGORY.format(
        budget_ynab_id, month, category_ynab_id
    )
    response = requests.patch(url, headers=retrieve._HEADERS_PATCH, data=data)
    json = response.json()
    retrieve.check_json_for_errors(json)
    return json


@pytest.fixture
def check_emptiness_then_teardown(request):
    test_budget_ynab_id = request.node.funcargs["test_budget_ynab_id"]
    current_month = request.node.funcargs["current_month"]
    test_category_ynab_id = request.node.funcargs["test_category_ynab_id"]

    result = retrieve_distilled.month_category(
        budget_ynab_id=test_budget_ynab_id,
        month=current_month,
        category_ynab_id=test_category_ynab_id,
    )
    assert result["budgeted"] == 0
    assert result["id"] == test_category_ynab_id

    yield

    result = push(
        budget_ynab_id=test_budget_ynab_id,
        month=current_month,
        category_ynab_id=test_category_ynab_id,
        data=data_func(new_budgeted=0),
    )
    distilled = distill.month_category(result)
    assert distilled["budgeted"] == 0
    assert distilled["id"] == test_category_ynab_id
