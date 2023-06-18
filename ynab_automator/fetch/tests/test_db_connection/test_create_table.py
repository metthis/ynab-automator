from __future__ import annotations

from ynab_automator.fetch.db_connection import DbConnection
from ynab_automator.fetch.tests.test_db_connection.expected_schema import (
    normalise_sql,
    resulted_table_schema,
    EXPECTED_BUDGET_TABLE_SCHEMA,
    EXPECTED_CATEGORY_TABLE_SCHEMA,
)


def test_create_budget_table(db: DbConnection):
    db.create_budget_table()
    result = resulted_table_schema(db, "Budget")
    expected = normalise_sql(EXPECTED_BUDGET_TABLE_SCHEMA)
    assert result == expected


def test_create_category_table(db: DbConnection):
    db.create_budget_table()
    db.create_category_table()
    result = resulted_table_schema(db, "Category")
    expected = normalise_sql(EXPECTED_CATEGORY_TABLE_SCHEMA)
    assert result == expected
