from __future__ import annotations

import pytest

from ynab_automator.fetch.db_connection import DbConnection


# Used in test_save_categories_old_and_new test_save_categories_deleted:
def get_upserted_category_column(
    db_conn: DbConnection, categories: list[dict], column: str
) -> list:
    sql = "SELECT ({0}) FROM Category WHERE ynab_id IN ({1}) ORDER BY (id)"
    qmarks = ", ".join("?" for _ in categories)
    sql = sql.format(column, qmarks)
    values = [x["id"] for x in categories]

    db_conn.cur.execute(sql, values)
    return db_conn.cur.fetchall()


@pytest.fixture
def test_categories() -> list[dict]:
    yield [
        # The categories must be in the order of their correspondings ids in the database (for the test purposes).
        {
            # Should update the appropriate row with the exact same values, leaving it "unchanged":
            "id": "ynab_id_1",
            "name": "name_1",
            "deleted": False,
        },
        {
            # Should update the old name (name_2) with the new name (name_2_new):
            "id": "ynab_id_2",
            "name": "name_2_new",
            "deleted": False,
        },
        {
            # Should just insert the values because there's no UNIQUE constraint violation:
            "id": "ynab_id_101",
            "name": "name_101",
            "deleted": False,
        },
    ]


def test_save_categories_old_and_new(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    test_categories: list[dict],
):
    # budget_id=4 is the same value as used in insert_10_category_rows
    db.save_categories(test_categories, budget_id=4)

    upserted_names = get_upserted_category_column(db, test_categories, "name")
    expected_names = [(x["name"],) for x in test_categories]
    assert upserted_names == expected_names

    upserted_ids = get_upserted_category_column(db, test_categories, "id")
    expected_ids = [(1,), (2,), (11,)]
    assert upserted_ids == expected_ids


@pytest.fixture
def test_categories_deleted() -> list[dict]:
    yield [
        {
            # Should get skipped because the category is deleted:
            "id": "ynab_id_deleted",
            "name": "name_deleted",
            "deleted": True,
        },
    ]


def test_save_categories_deleted(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    test_categories_deleted: list[dict],
):
    # budget_id=4 is the same value as used in insert_10_category_rows
    db.save_categories(test_categories_deleted, budget_id=4)

    upserted_names = get_upserted_category_column(db, test_categories_deleted, "name")
    expected_names = []
    assert upserted_names == expected_names
