from __future__ import annotations

import pytest

from ynab_automator.config import ignored
from ynab_automator.fetch.db_connection import DbConnection


# Used in test_save_budgets_old_and_new and test_save_budgets_ignored:
def get_upserted_budget_column(
    db_conn: DbConnection, list_of_budgets: list[dict], column: str
) -> list:
    sql = "SELECT ({0}) FROM Budget WHERE ynab_id IN ({1}) ORDER BY (id)"
    qmarks = ", ".join("?" for _ in list_of_budgets)
    sql = sql.format(column, qmarks)
    values = [x["id"] for x in list_of_budgets]

    db_conn.cur.execute(sql, values)
    return db_conn.cur.fetchall()


@pytest.fixture
def test_budgets() -> list[dict]:
    return [
        # The dictionaries must be in the order of their correspondings ids in the database (for the test purposes).
        {
            # Should update the appropriate row with the exact same values, leaving it "unchanged":
            "id": "ynab_id_1",
            "name": "name_1",
        },
        {
            # Should update the old name (name_2) with the new name (name_2_new):
            "id": "ynab_id_2",
            "name": "name_2_new",
        },
        {
            # Should just insert the values because there's no UNIQUE constraint violation:
            "id": "ynab_id_101",
            "name": "name_101",
        },
    ]


def test_save_budgets_old_and_new(
    db: DbConnection,
    db_budget_table,
    insert_10_budget_rows,
    test_budgets: list[dict],
):
    db.save_budgets(test_budgets)

    upserted_names = get_upserted_budget_column(db, test_budgets, "name")
    expected_names = [(x["name"],) for x in test_budgets]
    assert upserted_names == expected_names

    upserted_ids = get_upserted_budget_column(db, test_budgets, "id")
    expected_ids = [(1,), (2,), (11,)]
    assert upserted_ids == expected_ids


@pytest.fixture
def test_budget_ignored() -> list[dict]:
    if not ignored.BUDGETS:
        ignored.BUDGETS.append("ignored_ynab_id")

    return [
        {
            # Should get skipped because the id is in ignored.BUDGETS:
            "id": ignored.BUDGETS[0],
            "name": "ignored_name",
        },
    ]


def test_save_budgets_ignored(
    db: DbConnection,
    db_budget_table,
    insert_10_budget_rows,
    test_budget_ignored: list[dict],
):
    db.save_budgets(test_budget_ignored)
    upserted_names = get_upserted_budget_column(db, test_budget_ignored, "name")
    expected_names = []
    assert upserted_names == expected_names
