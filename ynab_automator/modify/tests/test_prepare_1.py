from __future__ import annotations
from dataclasses import fields

import pytest

from ynab_automator.modify import prepare
from ynab_automator.fetch import db_connection
from ynab_automator.datastructures.ynab_dataclasses import Category


def get_test_cases():
    return [
        ("c1e0ea99-5668-483b-b01e-25b348fe3437", 20),
    ]


@pytest.mark.parametrize("budget_ynab_id, category_count", get_test_cases())
def test_get_sorted_categories_config_from_db(budget_ynab_id, category_count):
    result = prepare.get_sorted_categories_config_from_db(budget_ynab_id)
    assert isinstance(result, list)
    assert len(result) == category_count

    for category_config in result:
        assert isinstance(category_config, Category)
        sql = """\
            SELECT position, name, drain_into, overflow, budget_id, id, ynab_id
            FROM Category WHERE ynab_id = ?"""
        reader = db_connection.DbConnection()
        # reader.conn.set_trace_callback(print)
        reader.cur.execute(sql, (category_config.category_ynab_id,))
        expected_values = reader.cur.fetchone()

        zipped = zip(fields(category_config), expected_values, strict=True)
        for f, expected_value in zipped:
            value = getattr(category_config, f.name)
            assert value == expected_value

    positions = (x.position for x in result)
    for position, i in zip(positions, range(1, category_count + 1), strict=True):
        assert position == i


def get_test_cases():
    sorted_categories_config = prepare.get_sorted_categories_config_from_db(
        "c1e0ea99-5668-483b-b01e-25b348fe3437"
    )
    selectors = [
        {1, 3, 4, 7, 13, 18, 19},
        {4, 5, 6, 7, 8, 12, 17, 20},
        {2, 9, 19, 10},
        {1, 11, 13, 15, 17},
        {2, 8, 14, 16},
    ]
    cases = []
    for selector in selectors:
        cases.append([x for x in sorted_categories_config if x.position in selector])
    return cases


@pytest.mark.parametrize("categories_config", get_test_cases())
def test_get_ynab_ids_from_categories_config(categories_config: list[Category]):
    result = prepare.get_ynab_ids_from_categories_config(categories_config)
    assert isinstance(result, tuple)
    assert len(result) == len(categories_config)
    for ynab_id, category_config in zip(result, categories_config, strict=True):
        assert isinstance(ynab_id, str)
        assert ynab_id == category_config.category_ynab_id
