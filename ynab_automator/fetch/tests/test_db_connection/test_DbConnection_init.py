from __future__ import annotations
import sqlite3
import os

import pytest

from ynab_automator.db import path
from ynab_automator.fetch.db_connection import DbConnection


cases = [path.get_custom_db_path(f"test{i}.db") for i in range(10)]


@pytest.mark.parametrize("db_path", cases)
def test_DbConnection_init(db_path: str):
    db = DbConnection(db_path)
    assert os.path.isfile(db_path)
    assert isinstance(db.conn, sqlite3.Connection)
    assert isinstance(db.cur, sqlite3.Cursor)
    db.cur.execute("PRAGMA foreign_keys")
    foreign_keys_setting = db.cur.fetchone()[0]
    assert foreign_keys_setting == 1
    db.close()
    os.remove(db_path)
