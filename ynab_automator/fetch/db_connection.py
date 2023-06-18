from __future__ import annotations
import sqlite3

from ynab_automator.config import ignored
from ynab_automator.db import path


class DbConnection:
    def __init__(self, db_path: str = path.DEFAULT_DB_PATH) -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.cur = self.conn.cursor()

    def close(self) -> None:
        self.conn.close()

    def __del__(self) -> None:
        self.close()

    def create_budget_table(self) -> None:
        SQL = """\
            CREATE TABLE IF NOT EXISTS Budget (
                id      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                ynab_id TEXT    NOT NULL UNIQUE,
                name    TEXT    NOT NULL UNIQUE
            )
            """
        self.cur.execute(SQL)
        self.conn.commit()

    def create_category_table(self) -> None:
        SQL = """\
            CREATE TABLE IF NOT EXISTS Category (
                id          INTEGER         NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                ynab_id     TEXT            NOT NULL,
                name        TEXT            NOT NULL UNIQUE,
                position    INTEGER,
                drain_into  INTEGER,
                overflow    INTEGER,
                budget_id   INTEGER         NOT NULL,
                FOREIGN KEY (budget_id)     REFERENCES Budget (id),
                FOREIGN KEY (drain_into)    REFERENCES Category (id),
                UNIQUE      (budget_id, ynab_id),
                UNIQUE      (budget_id, position),
                CHECK       (typeof(position) IN ("integer", "null")),
                CHECK       (typeof(drain_into) IN ("integer", "null")),
                CHECK       (typeof(overflow) IN ("integer", "null")),
                CHECK       (typeof(budget_id) = "integer"),
                CHECK       (drain_into IS NULL OR overflow = 0),
                CHECK       (drain_into != id)
            )
            """
        self.cur.execute(SQL)
        self.conn.commit()

    def save_budgets(self, json_object: dict) -> None:
        for item in json_object["data"]["budgets"]:
            ynab_id = item["id"]
            if ynab_id in ignored.BUDGETS:
                continue
            name = item["name"]
            sql = "INSERT OR REPLACE INTO Budget (ynab_id, name) VALUES (?, ?)"
            self.cur.execute(sql, (ynab_id, name))
            self.conn.commit()

    def save_categories(self, json_object: dict, budget_id: int) -> None:
        for group in json_object["data"]["category_groups"]:
            for category in group["categories"]:
                if category["deleted"]:
                    continue
                ynab_id = category["id"]
                name = category["name"]
                sql = "INSERT OR REPLACE INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)"
                self.cur.execute(sql, (ynab_id, name, budget_id))
                self.conn.commit()
