from __future__ import annotations
from collections.abc import Iterable
import sqlite3
import textwrap

from ynab_automator.db import path


# Sqlite sometimes raises silent exceptions (can be caight but no traceback
# and no iterruption) when encountering constraints during query execution.
# Upon testing, the exceptions seemed to be loud as desired.
# The code below serves to make such silent exceptions loud, if ever needed.

class LoudSqliteError(Exception):
    def __init__(self, err: sqlite3.Error, func: function, sql_template: str, sql_parameters: Iterable) -> None:
        self.name = err.__class__.__name__,
        self.orig_message = err,
        self.func = repr(func)
        # self.func = func.__name__,
        self.sql_template = textwrap.dedent(sql_template),
        self.sql_parameters = sql_parameters
        
        self.message = self.create_message()
        super().__init__(self.message)
    
    def create_message(self) -> str:
        message = f"""
                    >>{self.name}<<
                    [ERROR MESSAGE]  {self.orig_message}
                    [FUNCTION]       {self.func}
                    [SLQ TEMPLATE]   {self.sql_template}
                    [SQL PARAMETERS] {self.sql_parameters}
                """
        return textwrap.dedent(message)


class DbConnection:
    def __init__(self, db_path: str = path.DEFAULT_DB_PATH) -> None:
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def close(self) -> None:
        self.conn.close()

    def __del__(self) -> None:
        self.close()

    def loud_execute_and_commit(self, execute_func: function, sql: str, parameters: Iterable | dict = ()) -> None:
        try:
            prepared_func = self._prepare_function(execute_func, sql, parameters)
            prepared_func()
            self.conn.commit()
        except sqlite3.Error as err:
            raise LoudSqliteError(
                                    err=err,
                                    func=execute_func,
                                    sql_template=sql,
                                    sql_parameters=parameters
                                  )

    def _prepare_function(self, execute_func, sql, parameters) -> function:
        match execute_func:
            case self.cur.execute | sqlite3.Cursor.execute:
                return lambda: self.cur.execute(sql, parameters)
            case self.cur.executemany | sqlite3.Cursor.executemany:
                return lambda: self.cur.executemany(sql, parameters)
            case self.cur.executescript | sqlite3.Cursor.executescript:
                return lambda: self.cur.executescript(sql)
            case _:
                raise TypeError(f"Wrong execute_func: {repr(execute_func)}")

    def create_budget_table(self) -> None:
        SQL = """\
            CREATE TABLE IF NOT EXISTS Budget (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                ynab_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL UNIQUE
            )
            """
        self.loud_execute_and_commit(self.cur.execute, SQL)

    def create_category_table(self) -> None:
        SQL = """\
            CREATE TABLE OF NOT EXISTS Category (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                ynab_id TEXT NOT NULL,
                name TEXT NOT NULL UNIQUE,
                position INTEGER,
                drain_into INTEGER,
                overflow INTEGER,
                budget_id INTEGER NOT NULL,
                FOREIGN KEY (budget_id) REFERENCES Budget (id),
                FOREIGN KEY (drain_into) REFERENCES Category (id),
                UNIQUE (budget_id, ynab_id),
                UNIQUE (budget_id, position),
                CHECK (drain_into IS NULL OR overflow == 0)
            )
            """
        self.loud_execute_and_commit(self.cur.execute, SQL)

    def save_budgets(self, json_object: dict) -> None:
        for item in json_object["data"]["budgets"]:
            ynab_id = item["id"]
            if ynab_id in ignored.BUDGETS:
                continue
            name = item["name"]
            sql = "INSERT OR REPLACE INTO Budget (ynab_id, name) VALUES (?, ?)"
            self.loud_execute_and_commit(self.cur.execute, sql, (ynab_id, name))

    def save_categories(self, json_object: dict, budget_id: int) -> None:
        for group in json_object["data"]["category_groups"]:
            for category in group["categories"]:
                if category["deleted"]:
                    continue
                ynab_id = category["id"]
                name = category["name"]
                sql = "INSERT OR REPLACE INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)"
                self.loud_execute_and_commit(self.cur.execute, sql, (ynab_id, name, budget_id))