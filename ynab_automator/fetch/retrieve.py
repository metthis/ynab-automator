from __future__ import annotations
import textwrap

import requests

from ynab_automator.config import access_token


_BASE_URL = "https://api.youneedabudget.com/v1"
_PATH_BUDGETS = "/budgets"
_PATH_CATEGORIES = "/budgets/{0}/categories"
_PATH_MONTH = "/budgets/{0}/months/{1}"
_PATH_MONTH_CATEGORY = "/budgets/{0}/months/{1}/categories/{2}"

_HEADERS = {"Authorization": f"Bearer {access_token.ACCESS_TOKEN}"}


def _retrieve_or_push_json(path: str, data: dict | None = None) -> dict:
    url = _BASE_URL + path
    if data is None:
        response = requests.get(url, headers=_HEADERS)
    else:
        response = requests.patch(url, headers=_HEADERS, data=data)
    json = response.json()
    check_json_for_errors(json)
    return json


def check_json_for_errors(json: dict) -> None:
    if not isinstance(json, dict):
        err_string = f"""\
                    Expected to retrieve json as dict, is not dict.
                    Retrieved: {repr(json)}
                    """
        err_string = textwrap.dedent(err_string)
        raise TypeError(err_string)
    if "error" in json:
        err_string = f"""\
                    Retrieved json communicates an error.
                    Retrieved: {repr(json)}
                    """
        err_string = textwrap.dedent(err_string)
        raise ValueError(err_string)


def budgets() -> dict:
    path = _PATH_BUDGETS
    return _retrieve_or_push_json(path)


def categories(budget_ynab_id: str) -> dict:
    path = _PATH_CATEGORIES.format(budget_ynab_id)
    return _retrieve_or_push_json(path)


def month(budget_ynab_id: str, month: str) -> dict:
    path = _PATH_MONTH.format(budget_ynab_id, month)
    return _retrieve_or_push_json(path)


def month_category(budget_ynab_id: str, month: str, category_ynab_id: str) -> dict:
    path = _PATH_MONTH_CATEGORY.format(budget_ynab_id, month, category_ynab_id)
    return _retrieve_or_push_json(path)


def push_month_category(
    budget_ynab_id: str, month: str, category_ynab_id: str, data: str
) -> dict:
    path = _PATH_MONTH_CATEGORY.format(budget_ynab_id, month, category_ynab_id)
    return _retrieve_or_push_json(path, data)
