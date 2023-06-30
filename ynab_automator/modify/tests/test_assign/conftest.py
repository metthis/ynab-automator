from __future__ import annotations

import pytest

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory
from ynab_automator.fetch.months import get_current_month


@pytest.fixture
def m_category(request) -> MonthCategory:
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

    print(request.node.funcargs)
    data: dict = DEFAULTS | request.node.funcargs["data"]

    yield MonthCategory(
        data=data,
        budget_ynab_id="budget_ynab_id",
        month=get_current_month(),
    )
