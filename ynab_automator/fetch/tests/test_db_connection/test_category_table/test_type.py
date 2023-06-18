from __future__ import annotations
import sqlite3

import pytest

from ynab_automator.fetch.db_connection import DbConnection


cases = [
    (
        "id",
        ("not_int", "ynab_id", "name", 1, 1, 0, 1000),
    ),
    ("position", (1, "ynab_id", "name", "not_int", 1, 0, 1000)),
    ("drain_into", (1, "ynab_id", "name", 1, "not_int", 0, 1000)),
    ("overflow", (1, "ynab_id", "name", 1, 1, "not_int", 1000)),
    ("budget_id", (1, "ynab_id", "name", 1, 1, 0, "not_int")),
]


@pytest.mark.parametrize("column, values", cases)
def test_category_column_is_INTEGER(
    db: DbConnection, db_category_table, column, values
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql = "INSERT INTO Category (id, ynab_id, name, position, drain_into, overflow, budget_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.cur.execute(sql, values)
        db.conn.commit()
    assert "datatype mismatch" in str(
        excinfo.value
    ) or f"CHECK constraint failed: typeof({column})" in str(excinfo.value)


def test_category_columns_are_TEXT(
    db: DbConnection, db_category_table, insert_10_budget_rows
):
    sql = """\
            INSERT INTO Category (id, ynab_id, name, position, drain_into, overflow, budget_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
    values = (1, "ynab_id", "name", 1, None, 0, 5)
    db.cur.execute(sql, values)
    db.conn.commit()
    # No exception should be raised
