from __future__ import annotations
import sqlite3

import pytest

from ynab_automator.fetch.db_connection import DbConnection
from ynab_automator.fetch.tests.test_db_connection.test_category_table.random_sequences import (
    random_sample,
    get_complementary_randomised_seqs_of_ints,
)


def get_case_for_test_category_FOREIGN_KEYs_removing_budget_id_WITHOUT_exception() -> (
    list[list[str, str, int], list[tuple[int]]]
):
    suffixes = range(1, 6)
    referenced_ids, non_referenced_ids = get_complementary_randomised_seqs_of_ints(
        start=1, end=11
    )
    values_1 = []
    for suffix, referenced in zip(suffixes, referenced_ids, strict=True):
        value_1 = (f"ynab_id_{suffix}", f"name_{suffix}", referenced)
        values_1.append(value_1)
    values_2 = [(x,) for x in non_referenced_ids]
    return values_1, values_2


cases = [
    # Points to non-existent budget_id:
    ("ynab_id", "name", 1, 1000),
    # Points to non-existent category_id:
    ("ynab_id", "name", 1000, 1),
]


@pytest.mark.parametrize("values", cases)
def test_category_FOREIGN_KEYs_inserting_WITH_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    values,
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql = "INSERT INTO Category (ynab_id, name, drain_into, budget_id) VALUES (?, ?, ?, ?)"
        db.cur.execute(sql, values)
        db.conn.commit()
    assert "FOREIGN KEY constraint failed" in str(excinfo.value)


suffixes = range(11, 16)
drain_intos = random_sample(start=1, end=11, size=5)
budget_ids = random_sample(start=1, end=11, size=5)
cases = []
for suffix, drain_into, budget_id in zip(
    suffixes, drain_intos, budget_ids, strict=True
):
    case = (f"ynab_id_{suffix}", f"name_{suffix}", drain_into, budget_id)
    cases.append(case)


@pytest.mark.parametrize("values", cases)
def test_category_FOREIGN_KEYs_inserting_WITHOUT_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    values,
):
    sql = "INSERT INTO Category (ynab_id, name, drain_into, budget_id) VALUES (?, ?, ?, ?)"
    db.cur.execute(sql, values)
    db.conn.commit()


cases = random_sample(start=1, end=11, size=5)


@pytest.mark.parametrize("budget_id", cases)
def test_category_FOREIGN_KEYs_removing_budget_id_WITH_exception(
    db: DbConnection, db_category_table, insert_10_budget_rows, budget_id
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql_1 = "INSERT INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)"
        values_1 = ("ynab_id_1", "name_1", budget_id)
        sql_2 = "DELETE FROM Budget WHERE id = ?"
        values_2 = (budget_id,)
        db.cur.execute(sql_1, values_1)
        db.cur.execute(sql_2, values_2)
        db.conn.commit()
    assert "FOREIGN KEY constraint failed" in str(excinfo.value)


cases = [
    get_case_for_test_category_FOREIGN_KEYs_removing_budget_id_WITHOUT_exception()
    for _ in range(5)
]


@pytest.mark.parametrize("values_1, values_2", cases)
def test_category_FOREIGN_KEYs_removing_budget_id_WITHOUT_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    values_1,
    values_2,
):
    sql_1 = "INSERT INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)"
    sql_2 = "DELETE FROM Budget WHERE id = ?"
    db.cur.executemany(sql_1, values_1)
    db.cur.executemany(sql_2, values_2)
    db.conn.commit()


cases = random_sample(start=1, end=11, size=5)


@pytest.mark.parametrize("category_id", cases)
def test_category_FOREIGN_KEYs_removing_category_id_WITH_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    category_id,
):
    with pytest.raises(sqlite3.IntegrityError) as excinfo:
        sql_1 = "INSERT INTO Category (ynab_id, name, drain_into, budget_id) VALUES (?, ?, ?, ?)"
        values_1 = ("ynab_id", "name", category_id, 8)
        sql_2 = "DELETE FROM Category WHERE id = ?"
        values_2 = (category_id,)
        db.cur.execute(sql_1, values_1)
        db.cur.execute(sql_2, values_2)
        db.conn.commit()
    assert "FOREIGN KEY constraint failed" in str(excinfo.value)


cases = [get_complementary_randomised_seqs_of_ints(start=1, end=11) for _ in range(5)]


@pytest.mark.parametrize("ids_1, ids_2", cases)
def test_category_FOREIGN_KEYs_removing_category_id_WITHOUT_exception(
    db: DbConnection,
    db_category_table,
    insert_10_budget_rows,
    insert_10_category_rows,
    ids_1,
    ids_2,
):
    sql_1 = "INSERT INTO Category (ynab_id, name, drain_into, budget_id) VALUES (?, ?, ?, ?)"
    values_1 = [
        (f"ynab_id_ref_{category_id}", f"name_ref_{category_id}", category_id, 8)
        for category_id in ids_1
    ]
    sql_2 = "DELETE FROM Category WHERE id = ?"
    values_2 = [(category_id,) for category_id in ids_2]
    db.cur.executemany(sql_1, values_1)
    db.cur.executemany(sql_2, values_2)
    db.conn.commit()
