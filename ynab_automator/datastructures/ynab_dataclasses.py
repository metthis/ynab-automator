from __future__ import annotations
from dataclasses import dataclass, fields
import json
import sqlite3
import textwrap

from ynab_automator.fetch import db_connection


@dataclass(order=True)
class _AutocompletingDataclass:
    # WIP: Allow for more or even all fields to be provided.
    def find_provided_field_name(self) -> str:
        for f in fields(self):
            value = getattr(self, f.name)
            if not value:
                continue
            return value

    _NO_AUTOCOMPLETE = tuple()

    def create_list_of_field_names_to_autocomplete(
        self, provided_field_name: str
    ) -> list[str]:
        field_names_to_autocomplete = []
        for f in fields(self):
            field_name = f.name
            if field_name in self._NO_AUTOCOMPLETE:
                continue
            if field_name == provided_field_name:
                continue
            field_names_to_autocomplete.append(field_name)
        return field_names_to_autocomplete

    def retrieve_autocomplete_data_from_db(
        self, provided_field_name: str, field_names_to_autocomplete: list[str]
    ) -> tuple[int | str]:
        class_name = self.__class__.__name__
        provided_field_value = getattr(self, provided_field_name)

        qmarks = ", ".join("?" for _ in field_names_to_autocomplete)
        sql = "SELECT (%s) FROM ? WHERE ? = ?" % qmarks
        data = (
            *field_names_to_autocomplete,
            class_name,
            provided_field_name,
            provided_field_value,
        )

        reader = db_connection.DbConnection()
        reader.loud_execute(sql, data)
        return reader.cur.fetchone()

    def set_fields_waiting_for_autocomplete(
        self, remaining_field_names: list[str], remaining_data: tuple[int | str]
    ) -> None:
        for name, value in zip(remaining_field_names, remaining_data, strict=True):
            setattr(self, name, value)

    def autocomplete_fields(self) -> None:
        provided_field_name = self.find_provided_field_name()
        field_names_to_autocomplete = self.create_list_of_field_names_to_autocomplete(
            provided_field_name
        )
        autocomplete_data = self.retrieve_autocomplete_data_from_db(
            provided_field_name, field_names_to_autocomplete
        )
        self.set_fields_waiting_for_autocomplete(
            field_names_to_autocomplete, autocomplete_data
        )

    def __post_init__(self) -> None:
        self.autocomplete_fields()


@dataclass
class Budget(_AutocompletingDataclass):
    name: str = ""
    id: int = 0
    ynab_id: str = ""


# @dataclass
# class Category(AutocompletingDataclass):
@dataclass(order=True)
class Category:
    position: int | None = None
    name: str = ""
    drain_into: int | None = None
    overflow: int | None = None
    budget_id: int = 0
    id: int = 0
    category_ynab_id: str = ""


@dataclass
class MonthCategory:
    data: dict
    budget_ynab_id: str
    month: str
    position: int | None = None
    name: str | None = None
    category_id: int | None = None
    category_ynab_id: str = ""
    drain_into: int | None = None
    old_budgeted: int | None = None
    new_budgeted: int | None = None

    def delta(self) -> int:
        if self.old_budgeted is None or self.new_budgeted is None:
            error_string = """\
                    Expected old_budgeted and new_budgeted to be int but at least one is None:
                    old.budgeted = {0}
                    new_budgeted = {1}
            """
            error_string = textwrap.dedent(error_string)
            raise ValueError(error_string.format(self.old_budgeted, self.new_budgeted))

        return self.new_budgeted - self.old_budgeted

    def update_data(self) -> str:
        if self.new_budgeted is None:
            raise ValueError("Expected new_budgeted to be int but is None.")

        python_object = {"category": {"budgeted": self.new_budgeted}}
        serialised = json.dumps(python_object)
        return serialised

    def set_name(self) -> None:
        if self.name:
            return
        self.name = self.data["name"]

    def set_category_ynab_id(self) -> None:
        if self.category_ynab_id:
            return
        self.category_ynab_id = self.data["id"]

    def set_old_budgeted(self) -> None:
        if self.old_budgeted is not None:
            return
        self.old_budgeted = self.data["budgeted"]

    def __post_init__(self) -> None:
        self.set_name()
        self.set_category_ynab_id()
        self.set_old_budgeted()
