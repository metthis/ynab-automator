from __future__ import annotations
import sqlite3

import pytest

from ynab_automator.fetch.db_connection import DbConnection


# I could automate the below test cases depending on the tested SQL query:


def test_budget_id_is_INTEGER(db: DbConnection, db_budget_table):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db.cur.execute(
            "INSERT INTO Budget (id, ynab_id, name) VALUES (?, ?, ?)",
            ("not_int", "ynab_id", "name"),
        )
        db.conn.commit()
    assert "datatype mismatch" in str(excinfo.value)


def test_budget_columns_are_TEXT(db: DbConnection, db_budget_table):
    values = (1, "ynab_id_xy", "name_xy")
    db.cur.execute("INSERT INTO Budget (id, ynab_id, name) VALUES (?, ?, ?)", values)
    db.conn.commit()
    # No exception should be raised


def test_budget_id_is_AUTOINCREMENT(db: DbConnection, db_budget_table):
    db.cur.executemany(
        "INSERT INTO Budget (ynab_id, name) VALUES (?, ?)",
        [("id_one", "one"), ("id_two", "two"), ("id_three", "three")],
    )
    db.conn.commit()
    db.cur.execute("SELECT id FROM Budget")
    result = db.cur.fetchall()
    expected = [(1,), (2,), (3,)]
    assert result == expected


cases = [
    ("name",) * 2,
    ("ynab_id",) * 2,
]


@pytest.mark.parametrize("column, value", cases)
def test_budget_column_is_NOT_NULL(db: DbConnection, db_budget_table, column, value):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        # An f-string isn't safe (SQL injection) but inserting a column name
        # via placeholders doesn't work. This repates in some tests below as well.
        db.cur.execute(f"INSERT INTO Budget ({column}) VALUES (?)", (value,))
        db.conn.commit()
    assert "NOT NULL constraint failed" in str(excinfo.value)


cases = [
    # id not UNIQUE:
    [(1, "ynab_id_1", "name_1"), (1, "ynab_id_2", "name_2")],
    # ynab_id not UNIQUE:
    [(1, "ynab_id_1", "name_1"), (2, "ynab_id_1", "name_2")],
]


@pytest.mark.parametrize("values", cases)
def test_budget_column_is_UNIQUE(db: DbConnection, db_budget_table, values):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        db.cur.executemany(
            f"INSERT INTO Budget (id, ynab_id, name) VALUES (?, ?, ?)", values
        )
        db.conn.commit()
    assert "UNIQUE constraint failed" in str(excinfo.value)
