from __future__ import annotations
import json

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.datastructures.enums import ResetMode
from ynab_automator.fetch import retrieve_distilled, months
from ynab_automator.fetch.months import get_current_month


def m_category_func(override: dict = None) -> MonthCategory:
    if override is None:
        override = {}

    DEFAULTS = {
        "id": "ynab_id",
        "name": "name",
        "goal_type": "",
        "budgeted": 0,
        "goal_target": 0,
        "goal_under_funded": 0,
        "goal_overall_left": 0,
        "note": "",
    }

    data: dict = DEFAULTS | override

    return MonthCategory(
        data=data,
        budget_ynab_id="budget_ynab_id",
        month=get_current_month(),
    )


@pytest.fixture
def m_category(request) -> MonthCategory:
    try:
        override = request.node.funcargs["data"]
    except KeyError:
        override = {}

    yield m_category_func(override)


@pytest.fixture
def m_categories(request) -> list[MonthCategory]:
    try:
        overrides = request.node.funcargs["data"]
    except KeyError:
        overrides = ({},)

    yield [m_category_func(x) for x in overrides]


# All of the following is used only by:
#  - test_NEED_with_overflow.py
#  - test_overflow_loop.py
#  - test_get_updated_m_categories.py


def _data_func(new_budgeted) -> str:
    # Same code as in MonthCategory.update_data:
    python_object = {"category": {"budgeted": new_budgeted}}
    serialised = json.dumps(python_object)
    return serialised


def reset_cycle(
    budget_ynab_id: str, month: str, category_ynab_id: str, new_budgeted: int
) -> dict:
    result = retrieve_distilled.push_month_category(
        budget_ynab_id=budget_ynab_id,
        month=month,
        category_ynab_id=category_ynab_id,
        data=_data_func(new_budgeted),
    )
    assert result["id"] == category_ynab_id
    assert result["budgeted"] == new_budgeted

    return result


# reset functions reset live categories to an initial state expected by a test:


def reset_empty(
    budget_ynab_id: str, first_month: str, category_ynab_id: str
) -> tuple[dict]:
    result = reset_cycle(
        new_budgeted=0,
        budget_ynab_id=budget_ynab_id,
        month=first_month,
        category_ynab_id=category_ynab_id,
    )
    return (result,)


def reset_partially_full(
    budget_ynab_id: str, first_month: str, category_ynab_id: str
) -> tuple[dict]:
    result = reset_cycle(
        new_budgeted=4_000,
        budget_ynab_id=budget_ynab_id,
        month=first_month,
        category_ynab_id=category_ynab_id,
    )
    assert result["budgeted"] == 0.4 * result["goal_target"]
    return (result,)


def reset_full(
    budget_ynab_id: str, first_month: str, category_ynab_id: str
) -> tuple[dict]:
    result = reset_cycle(
        new_budgeted=10_000,
        budget_ynab_id=budget_ynab_id,
        month=first_month,
        category_ynab_id=category_ynab_id,
    )
    assert result["budgeted"] == result["goal_target"]
    return (result,)


def reset_overflown_partially(
    budget_ynab_id: str, first_month: str, category_ynab_id: str
) -> tuple[dict, dict]:
    result_1 = reset_cycle(
        new_budgeted=10_000,
        budget_ynab_id=budget_ynab_id,
        month=first_month,
        category_ynab_id=category_ynab_id,
    )
    result_2 = reset_cycle(
        new_budgeted=4_000,
        budget_ynab_id=budget_ynab_id,
        month=months.offset_month(first_month, 1),
        category_ynab_id=category_ynab_id,
    )
    assert result_1["budgeted"] == result_1["goal_target"]
    assert result_2["budgeted"] == 0.4 * result_2["goal_target"]
    return result_1, result_2


def reset_overflown_fully(
    budget_ynab_id: str, first_month: str, category_ynab_id: str
) -> tuple[dict, dict]:
    result_1 = reset_cycle(
        new_budgeted=10_000,
        budget_ynab_id=budget_ynab_id,
        month=first_month,
        category_ynab_id=category_ynab_id,
    )
    result_2 = reset_cycle(
        new_budgeted=10_000,
        budget_ynab_id=budget_ynab_id,
        month=months.offset_month(first_month, 1),
        category_ynab_id=category_ynab_id,
    )
    assert result_1["budgeted"] == result_1["goal_target"]
    assert result_2["budgeted"] == result_2["goal_target"]
    return result_1, result_2


def reset_overflown_fully_plus_partially(
    budget_ynab_id: str, first_month: str, category_ynab_id: str
) -> tuple[dict, dict, dict]:
    result_1 = reset_cycle(
        new_budgeted=10_000,
        budget_ynab_id=budget_ynab_id,
        month=first_month,
        category_ynab_id=category_ynab_id,
    )
    result_2 = reset_cycle(
        new_budgeted=10_000,
        budget_ynab_id=budget_ynab_id,
        month=months.offset_month(first_month, 1),
        category_ynab_id=category_ynab_id,
    )
    result_3 = reset_cycle(
        new_budgeted=4_000,
        budget_ynab_id=budget_ynab_id,
        month=months.offset_month(first_month, 2),
        category_ynab_id=category_ynab_id,
    )
    assert result_1["budgeted"] == result_1["goal_target"]
    assert result_2["budgeted"] == result_2["goal_target"]
    assert result_3["budgeted"] == 0.4 * result_3["goal_target"]
    return result_1, result_2, result_3


def reset(
    budget_ynab_id: str, first_month: str, category_ynab_id: str, mode: ResetMode
) -> tuple[dict] | tuple[dict, dict] | tuple[dict, dict, dict]:
    match mode:
        case ResetMode.EMPTY:
            return reset_empty(budget_ynab_id, first_month, category_ynab_id)
        case ResetMode.PARTIALLY_FULL:
            return reset_partially_full(budget_ynab_id, first_month, category_ynab_id)
        case ResetMode.FULL:
            return reset_full(budget_ynab_id, first_month, category_ynab_id)
        case ResetMode.OVERFLOWN_PARTIALLY:
            return reset_overflown_partially(
                budget_ynab_id, first_month, category_ynab_id
            )
        case ResetMode.OVERFLOWN_FULLY:
            return reset_overflown_fully(budget_ynab_id, first_month, category_ynab_id)
        case ResetMode.OVERFLOWN_FULLY_PLUS_PARTIALLY:
            return reset_overflown_fully_plus_partially(
                budget_ynab_id, first_month, category_ynab_id
            )
        case _:
            raise TypeError(
                f"mode must be a ResetMode enum but it is {type(mode).__name__}"
            )


def reset_before_func(
    mode, budget_ynab_id, first_month, category_ynab_id
) -> tuple[dict] | tuple[dict, dict] | tuple[dict, dict, dict]:
    parametrised_reset = lambda: reset(
        mode=mode,
        budget_ynab_id=budget_ynab_id,
        first_month=first_month,
        category_ynab_id=category_ynab_id,
    )

    return parametrised_reset()


def get_mode_budget_ynab_id_and_first_month_from_request(
    request,
) -> tuple[ResetMode, str, str]:
    mode = request.node.funcargs["mode"]
    budget_ynab_id = request.node.funcargs["budget_ynab_id"]
    first_month = request.node.funcargs["first_month"]

    return mode, budget_ynab_id, first_month


@pytest.fixture
def reset_before(request) -> tuple[dict] | tuple[dict, dict] | tuple[dict, dict, dict]:
    (
        mode,
        budget_ynab_id,
        first_month,
    ) = get_mode_budget_ynab_id_and_first_month_from_request(request)
    category_ynab_id = request.node.funcargs["category_ynab_id"]
    yield reset_before_func(mode, budget_ynab_id, first_month, category_ynab_id)


@pytest.fixture
def reset_before_all(request) -> list[dict]:
    (
        mode,
        budget_ynab_id,
        first_month,
    ) = get_mode_budget_ynab_id_and_first_month_from_request(request)
    category_ynab_ids = request.node.funcargs["category_ynab_ids"]

    all_data = []
    for category_ynab_id in category_ynab_ids:
        set_of_data = reset_before_func(
            mode, budget_ynab_id, first_month, category_ynab_id
        )
        all_data.append(*set_of_data)
    yield all_data


@pytest.fixture
def reset_before_all_and_init_m_categories(
    reset_before_all, request
) -> list[MonthCategory]:
    all_data = reset_before_all
    _, budget_ynab_id, month = get_mode_budget_ynab_id_and_first_month_from_request(
        request
    )
    yield [MonthCategory(data, budget_ynab_id, month) for data in all_data]
