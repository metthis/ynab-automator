from __future__ import annotations
import os

import pytest

from ynab_automator.db import path
from ynab_automator.fetch.db_connection import DbConnection


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


@pytest.fixture
def db_category_table(db: DbConnection, db_budget_table):
    db.create_category_table()
    yield


@pytest.fixture
def insert_10_budget_rows(db: DbConnection):
    sql = "INSERT INTO Budget (ynab_id, name) VALUES (?, ?)"
    values = [(f"ynab_id_{i}", f"name_{i}") for i in range(10)]
    db.cur.executemany(sql, values)
    db.conn.commit()
    yield


@pytest.fixture
def insert_10_category_rows(db: DbConnection):
    sql = "INSERT INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)"
    values = [(f"ynab_id_{i}", f"name_{i}", 4) for i in range(10)]
    db.cur.executemany(sql, values)
    db.conn.commit()
    yield
