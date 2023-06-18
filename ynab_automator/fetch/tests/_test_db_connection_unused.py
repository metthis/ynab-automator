from __future__ import annotations
import sqlite3
import os

import pytest

from ynab_automator.db import path
from ynab_automator.fetch.db_connection import DbConnection, LoudSqliteError


# Tests for code in _db_connection_unused


@pytest.fixture
def db():
    db_path = path.get_custom_db_path("test.db")
    assert not os.path.isfile(db_path)
    db = DbConnection(db_path)
    yield db

    db.close()
    os.remove(db_path)


@pytest.fixture
def db_budget_table(db: DbConnection):
    db.create_budget_table()
    yield


cases = [
    (
        sqlite3.Cursor.execute,
        "INSERT INTO Budget (ynab_id, name) VALUES (?, ?)",
        ("abcd", "some_name"),
        sqlite3.Cursor.execute,
        "SELECT (name) FROM Budget WHERE (ynab_id) = ?",
        ("abcd",),
        [("some_name",)],
     ),
    (
        sqlite3.Cursor.executemany,
        "INSERT INTO Budget (ynab_id, name) VALUES (?, ?)",
        [("one", "name_one"), ("two", "name_two"), ("three", "name_three"), ("four", "name_four")],
        sqlite3.Cursor.execute,
        "SELECT (name) FROM Budget WHERE (ynab_id) IN (?, ?, ?, ?) ORDER BY (ynab_id)",
        ("two", "four", "three", "one",),
       [("name_four",), ("name_one",), ("name_three",), ("name_two",)],
    ),
    (
        sqlite3.Cursor.executescript,
        """
            BEGIN;
            INSERT INTO Budget (ynab_id, name) VALUES ("ten", "name_ten");
            INSERT INTO Budget (ynab_id, name) VALUES ("eleven", "name_eleven");
            COMMIT;
        """,
        (),
        sqlite3.Cursor.execute,
        "SELECT (name) FROM Budget WHERE (ynab_id) IN (?, ?) ORDER BY (ynab_id)",
        ("eleven", "ten"),
        [("name_eleven",), ("name_ten",)]
    ),
]


@pytest.mark.parametrize("func, sql, data, check_func, check_sql, check_data, expected", cases)
def test_loud_without_errors(db: DbConnection, db_budget_table, func, sql, data, check_func, check_sql, check_data, expected):
    db.loud_execute_and_commit(func, sql, data)
    db.loud_execute_and_commit(check_func, check_sql, check_data)
    fetched = db.cur.fetchall()
    assert fetched == expected


cases = [
    sqlite3.Cursor.fetchall,
    print,
    isinstance,
    all
]


@pytest.mark.parametrize("func", cases)
def test_loud_wrong_execute_func_error(db: DbConnection, func: function, sql="", data=()):
    with pytest.raises(TypeError) as excinfo:
        db.loud_execute_and_commit(func, sql, data)
    assert "Wrong execute_func: " in str(excinfo.value)
    assert func.__name__ in str(excinfo.value)


# Missing: Test of loud_execute_and_commit with errors.