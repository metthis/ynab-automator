from __future__ import annotations
import sqlite3

import pytest

from ynab_automator.fetch.db_connection import DbConnection


# The following tests (testing sqlite exceptions) need more test cases.
# However, as long as I thoroughly test my SQL-related code,
# all, should be fine.


cases = [
    (
        "INSERT INTO Budget (ynab_id) VALUES (?)",
        ("abcd",),
        sqlite3.IntegrityError,
        "NOT NULL constraint failed",
    ),
    (
        "INSERT INTO Budget (id, ynab_id, name) VALUES (?, ?, ?)",
        ("text_instead_of_integer", "abcd", "abcd_name"),
        sqlite3.IntegrityError,
        "datatype mismatch",
    ),
]


@pytest.mark.parametrize("sql, values, expected_error, expected_str", cases)
def test_sqlite_errors_execute(
    db: DbConnection, db_budget_table, sql, values, expected_error, expected_str
):
    with pytest.raises(expected_error) as excinfo:
        db.cur.execute(sql, values)
        db.conn.commit()
    assert expected_str in str(excinfo.value)
    print(str(excinfo.value))


cases = [
    (
        "INSERT INTO Budget (ynab_id, name) VALUES (?, ?)",
        [("one_id", "one_name")] * 2,
        sqlite3.IntegrityError,
        "UNIQUE constraint failed",
    ),
]


@pytest.mark.parametrize("sql, values, expected_error, expected_str", cases)
def test_sqlite_errors_executemany(
    db: DbConnection, db_budget_table, sql, values, expected_error, expected_str
):
    with pytest.raises(expected_error) as excinfo:
        db.cur.executemany(sql, values)
        db.conn.commit()
    assert expected_str in str(excinfo.value)
    print(str(excinfo.value))
