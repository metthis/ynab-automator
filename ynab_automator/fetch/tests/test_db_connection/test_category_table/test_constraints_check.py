from __future__ import annotations
import sqlite3

import pytest

from ynab_automator.fetch.db_connection import DbConnection
from ynab_automator.fetch.tests.test_db_connection.test_category_table.random_sequences import (
    random_sample,
)


def test_category_CHECK_drain_into_and_overflow_WITH_exception(
    db: DbConnection, db_category_table, insert_10_budget_rows
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql = "INSERT INTO Category (ynab_id, name, drain_into, overflow, budget_id) VALUES (?, ?, ?, ?, ?)"
        values = ("ynab_id", "name", 1, 1, 9)
        db.cur.execute(sql, values)
        db.conn.commit()
    assert "CHECK constraint failed: drain_into IS NULL OR overflow = 0" in str(
        excinfo.value
    )


cases = [
    # drain_into is NULL and overflow == 0:
    ("ynab_id", "name", None, 0, 7),
    # drain_into is not NULL but overflow == 0:
    ("ynab_id", "name", 1, 0, 7),
    # overflow == 1 but drain_into is NULL:
    ("ynab_id", "name", None, 1, 7),
]


@pytest.mark.parametrize("values", cases)
def test_category_CHECK_drain_into_and_overflow_WITHOUT_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    values,
):
    sql = "INSERT INTO Category (ynab_id, name, drain_into, overflow, budget_id) VALUES (?, ?, ?, ?, ?)"
    db.cur.execute(sql, values)
    db.conn.commit()


cases = random_sample(start=1, end=11, size=5)


@pytest.mark.parametrize("category_id", cases)
def test_category_CHECK_drain_into_is_does_not_equal_id_WITH_exception(
    db: DbConnection, db_category_table, insert_10_budget_rows, category_id
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql = "INSERT INTO Category (id, ynab_id, name, drain_into, budget_id) VALUES (?, ?, ?, ?, ?)"
        values = (category_id, "ynab_id", "name", category_id, 3)
        db.cur.execute(sql, values)
        db.conn.commit()
    assert "CHECK constraint failed: drain_into != id" in str(excinfo.value)


def test_category_CHECK_drain_into_is_does_not_equal_id_WITHOUT_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
):
    sql = "INSERT INTO Category (ynab_id, name, drain_into, budget_id) VALUES (?, ?, ?, ?)"
    category_ids = random_sample(start=101, end=300, size=5)
    values = [
        (f"ynab_id_{category_id}", f"name_{category_id}", 5, 3)
        for category_id in category_ids
    ]
    db.cur.executemany(sql, values)
    db.conn.commit()
