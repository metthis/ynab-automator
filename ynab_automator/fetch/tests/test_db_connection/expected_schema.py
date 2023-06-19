from __future__ import annotations
import re

from ynab_automator.fetch.db_connection import DbConnection


def normalise_sql(sql: str) -> str:
    # Returns lowercase str unless str is capitalised word, then returns str:
    def lower_if_not_capitalised_word(matchobj: re.Match) -> str:
        word: str = matchobj.group(0)
        is_capitalised_word = re.match(r"[A-Z][a-z]+", word)
        if is_capitalised_word:
            return word
        else:
            return word.lower()

    # Applies the function above to the first and last word.
    # I need to handle it separately because ^ and $ are zero-lenght characters.
    sql = re.sub(r"(?:^\w+)|(?:\w+$)", lower_if_not_capitalised_word, sql)
    # Applies the function above to all the other words:
    sql = re.sub(
        r"(?<=\s|,|[(]|[)]|^.)\w+(?=\s|,|[(]|[)]|.$)",
        lower_if_not_capitalised_word,
        sql,
    )

    # Removes "if not exists", as this command doesn't get
    # reflected in the resulting schema:
    sql = sql.replace("if not exists", "")

    # Collapses white spaces:
    sql = re.sub(r"\s+", " ", sql)
    sql = sql.strip()

    return sql


def resulted_table_schema(db: DbConnection, table_name: str) -> str:
    sql = "SELECT sql FROM sqlite_master WHERE name = ? AND tbl_name = ?"
    values = (table_name,) * 2
    db.cur.execute(sql, values)
    schema = db.cur.fetchone()[0]
    return normalise_sql(schema)


EXPECTED_BUDGET_TABLE_SCHEMA = """\
                                CREATE TABLE IF NOT EXISTS Budget (
                                    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                                    ynab_id TEXT NOT NULL UNIQUE,
                                    name TEXT NOT NULL
                                )
                                """


EXPECTED_CATEGORY_TABLE_SCHEMA = """\
                                    CREATE TABLE IF NOT EXISTS Category (
                                        id          INTEGER         NOT NULL PRIMARY KEY UNIQUE,
                                        ynab_id     TEXT            NOT NULL,
                                        name        TEXT            NOT NULL,
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
