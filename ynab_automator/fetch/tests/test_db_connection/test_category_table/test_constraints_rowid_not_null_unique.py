from __future__ import annotations
import sqlite3

import pytest

from ynab_automator.fetch.db_connection import DbConnection


def test_category_id_is_ROWID(
    db: DbConnection, db_category_table, insert_10_budget_rows
):
    sql = "INSERT INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)"
    values = [
        ("ynab_id_1", "name_1", 2),
        ("ynab_id_2", "name_2", 2),
        ("ynab_id_3", "name_3", 2),
    ]
    db.cur.executemany(sql, values)
    db.conn.commit()
    db.cur.execute("SELECT id FROM Category")
    result = db.cur.fetchall()
    expected = [(1,), (2,), (3,)]
    assert result == expected


cases = [
    # ynab_id missing:
    ("name", "budget_id"),
    # name missing:
    ("ynab_id", "budget_id"),
    # budget_id missing:
    ("ynab_id", "name"),
]

cases = [(f"{str_1}, {str_2}", (str_1, str_2)) for (str_1, str_2) in cases]


@pytest.mark.parametrize("columns, values", cases)
def test_category_column_is_NOT_NULL(
    db: DbConnection, db_category_table, columns, values
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql = f"INSERT INTO Category ({columns}) VALUES (?, ?)"
        db.cur.execute(sql, values)
        db.conn.commit()
    assert "NOT NULL constraint failed" in str(excinfo.value)


cases = [
    # id not UNIQUE:
    [
        (1, "ynab_id_1", "name_1", 1, 1),
        (1, "ynab_id_2", "name_2", 2, 1),
    ],
    # (budget_id, ynab_id) not UNIQUE:
    [
        (1, "ynab_id_1", "name_1", 1, 1),
        (2, "ynab_id_1", "name_2", 2, 1),
    ],
    # (budget_id, position) not UNIQUE:
    [
        (1, "ynab_id_1", "name_1", 1, 1),
        (2, "ynab_id_2", "name_2", 1, 1),
    ],
]


@pytest.mark.parametrize("values", cases)
def test_category_UNIQUE(
    db: DbConnection, db_category_table, insert_10_budget_rows, values
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql = "INSERT INTO Category (id, ynab_id, name, position, budget_id) VALUES (?, ?, ?, ?, ?)"
        db.cur.executemany(sql, values)
        db.conn.commit()
    assert "UNIQUE constraint failed" in str(excinfo.value)
