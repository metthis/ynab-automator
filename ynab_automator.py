from __future__ import annotations
from typing import List, Tuple
from dataclasses import dataclass, fields
import urllib.request, urllib.error, urllib.parse
import ssl
import json
from datetime import date
import sqlite3
import re
import textwrap

import access_token
import config
import ignored


def get_current_month() -> str:
    d = date.today().replace(day=1)
    return d.isoformat()


def offset_month(iso_month: str, offset_in_months: int = 0) -> str:
    if not offset_in_months:
        return iso_month

    d = date.fromisoformat(iso_month)

    year = d.year
    month = d.month + offset_in_months

    while month > 12:
        month -= 12
        year += 1

    while month < 1:
        month += 12
        year -= 1

    d = d.replace(year=year, month=month)

    return d.isoformat()


class ApiRequest:
    BASE_URL = "https://api.youneedabudget.com/v1"
    PATH_BUDGETS = "/budgets"
    PATH_CATEGORIES = "/budgets/{0}/categories"
    PATH_MONTH = "/budgets/{0}/months/{1}"
    PATH_MONTH_CATEGORY = "/budgets/{0}/months/{1}/categories/{2}"

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    def retrieve_json(self, path: str, data: dict | None = None) -> dict:
        url = self.BASE_URL + path
        request = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {access_token.ACCESS_TOKEN}"}
        )

        with urllib.request.urlopen(request, data=data, context=self.ctx) as response:
            received = response.read().decode()
            json_object = json.loads(received)
            return json_object

    def retrieve_budgets(self) -> dict:
        path = self.PATH_BUDGETS
        return self.retrieve_json(path)

    def retrieve_categories(self, budget_ynab_id: str) -> dict:
        path = self.PATH_CATEGORIES.format(budget_ynab_id)
        return self.retrieve_json(path)

    def retrieve_month(self, budget_ynab_id: str, month: str) -> dict:
        path = self.PATH_MONTH.format(budget_ynab_id, month)
        return self.retrieve_json(path)

    def retrieve_or_push_month_category(
        self,
        budget_ynab_id: str,
        month: str,
        category_ynab_id: str,
        data: dict | None = None,
    ) -> dict:
        path = self.PATH_MONTH_CATEGORY.format(budget_ynab_id, month, category_ynab_id)
        return self.retrieve_json(path, data)

    def retrieve_month_category(
        self, budget_ynab_id: str, month: str, category_ynab_id: str
    ) -> dict:
        retrieved_json = self.retrieve_or_push_month_category(
            budget_ynab_id, month, category_ynab_id
        )
        return retrieved_json["data"]["category"]

    def push_month_category(
        self, budget_ynab_id: str, month: str, category_ynab_id: str, data: dict
    ) -> dict:
        return self.retrieve_or_push_month_category(
            self, budget_ynab_id, month, category_ynab_id, data
        )

    @staticmethod
    def retrieve_categories_from_month(month_json: dict) -> Tuple[dict]:
        return tuple(month_json["data"]["month"]["categories"])

    def retrieve_month_categories(self, budget_ynab_id: str, month: str) -> Tuple[dict]:
        month_json = self.retrieve_month(budget_ynab_id, month)
        return self.retrieve_categories_from_month(month_json)


@dataclass(order=True)
class AutocompletingDataclass:
    # WIP: Allow for more or even all fields to be provided.
    def find_provided_field_name(self) -> str:
        for f in fields(self):
            value = getattr(self, f.name)
            if not value:
                continue
            return value

    no_autocomplete = tuple()

    def create_list_of_field_names_to_autocomplete(
        self, provided_field_name: str
    ) -> List[str]:
        field_names_to_autocomplete = []
        for f in fields(self):
            field_name = f.name
            if field_name in self.no_autocomplete:
                continue
            if field_name == provided_field_name:
                continue
            field_names_to_autocomplete.append(field_name)
        return field_names_to_autocomplete

    def retrieve_autocomplete_data_from_db(
        self, provided_field_name: str, field_names_to_autocomplete: List[str]
    ) -> Tuple[int | str]:
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

        reader = DbConnection()
        try:
            reader.cur.execute(sql, data)
        except sqlite3.Error as e:
            string = f"""\
                == {e.sqlite_errorcode}: {e.sqlite_errorname} ==
                [SLQ TEMPLATE]  {sql}
                [SQL VARIABLES] {data}
            """
            string = textwrap.dedent(string)
            print(string)
            quit()
        return reader.cur.fetchone()

    def set_fields_waiting_for_autocomplete(
        self, remaining_field_names: List[str], remaining_data: Tuple[int | str]
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
class Budget(AutocompletingDataclass):
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


class DbConnection:
    def __init__(self, db_filename: str = config.DEFAULT_DB_FILENAME) -> None:
        self.conn = sqlite3.connect(db_filename)
        self.cur = self.conn.cursor()

    def __del__(self) -> None:
        self.conn.close()


class SaveToDb(DbConnection):
    def save_budgets(self, json_object: dict) -> None:
        for item in json_object["data"]["budgets"]:
            ynab_id = item["id"]
            if ynab_id in ignored.BUDGETS:
                continue
            name = item["name"]
            self.cur.execute(
                "INSERT OR UPDATE INTO Budget (ynab_id, name) VALUES (?, ?)",
                (ynab_id, name),
            )
            self.conn.commit()

    def save_categories(self, json_object: dict, budget_id: int) -> None:
        for group in json_object["data"]["category_groups"]:
            for category in group["categories"]:
                if category["deleted"]:
                    continue
                ynab_id = category["id"]
                name = category["name"]
                self.cur.execute(
                    "INSERT OR UPDATE INTO Category (ynab_id, name, budget_id) VALUES (?, ?, ?)",
                    (ynab_id, name, budget_id),
                )
                self.conn.commit()


@dataclass
class MonthCategory:
    data: dict
    budget_ynab_id: str
    month: str
    position: int | None = None
    name: str | None = None
    category_ynab_id: str = ""
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
            raise ValueError("Expected new_budgeted to be an integer but is None.")

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


# Only works in the new month, not the old month
# Next up: Test main(). Then draining.
class UpdatedMonthCategoriesFactory:
    all_updated_m_categories: List[MonthCategory] = []

    def main(self, budget_ynab_id: str, month: str) -> None:
        requester = ApiRequest()
        categories_data = requester.retrieve_month_categories(budget_ynab_id, month)
        categories_config = self.get_sorted_categories_config_from_db(budget_ynab_id)
        ynab_ids = self.get_ynab_ids_from_categories_config(categories_config)
        m_categories = self.get_initialised_m_categories(
            budget_ynab_id, month, categories_data, ynab_ids, categories_config
        )
        m_categories = self.sort_m_categories_by_position(m_categories)
        self.all_updated_m_categories = self.get_updated_m_categories(
            m_categories, categories_config
        )

    @staticmethod
    def get_sorted_categories_config_from_db(budget_ynab_id: str) -> List[Category]:
        SQL = """
            SELECT Category.position, Category.name, Category.drain_into, Category.overflow, Category.budget_id, Category.id, Category.ynab_id
            FROM Category JOIN Budget ON Category.budget_id = Budget.id
            WHERE Budget.ynab_id = ?
            AND Category.position IS NOT NULL
            ORDER BY Category.position
        """
        db_reader = DbConnection()
        db_reader.cur.execute(SQL, (budget_ynab_id,))
        rows = db_reader.cur.fetchall()

        categories_config = []
        for row in rows:
            category_config = Category(*row)
            categories_config.append(category_config)

        categories_config.sort()  # Obsolete because of ORDER BY Category.position in the SQL query
        return categories_config

    @staticmethod
    def get_ynab_ids_from_categories_config(
        categories_config: List[Category],
    ) -> Tuple[str]:
        return tuple(x.category_ynab_id for x in categories_config)

    @staticmethod
    def get_initialised_m_categories(
        budget_ynab_id: str,
        month: str,
        categories_data: Tuple[dict],
        category_ynab_ids: Tuple[str],
        categories_config: List[Category],
    ) -> List[MonthCategory]:
        m_categories = []
        for category_data in categories_data:
            ynab_id = category_data["id"]
            if ynab_id not in category_ynab_ids:
                continue
            for category_config in categories_config:
                if category_config.category_ynab_id == ynab_id:
                    position = category_config.position
            m_category = MonthCategory(
                data=category_data,
                budget_ynab_id=budget_ynab_id,
                month=month,
                position=position,
                category_ynab_id=ynab_id,
            )
            m_categories.append(m_category)
        return m_categories

    @staticmethod
    def sort_m_categories_by_position(
        m_categories: List[MonthCategory],
    ) -> List[MonthCategory]:
        return sorted(m_categories, key=lambda m_category: m_category.position)

    def get_updated_m_categories(
        self, m_categories: List[MonthCategory], categories_config: List[Category]
    ) -> List[MonthCategory]:
        all_updated_m_categories = []

        for m_category in m_categories:
            category_config = self.get_matching_category_config(
                categories_config, m_category
            )
            sequence_of_updated_m_categories = self.m_category_dispatcher(
                m_category, category_config
            )
            all_updated_m_categories.extend(sequence_of_updated_m_categories)

        return all_updated_m_categories

    @staticmethod
    def get_matching_category_config(
        categories_config: List[Category], m_category: MonthCategory
    ) -> Category:
        for category_config in categories_config:
            if category_config.category_ynab_id == m_category.data["id"]:
                return category_config

    def m_category_dispatcher(
        self, m_category: MonthCategory, category_config: Category
    ) -> Tuple[MonthCategory]:
        goal_type = m_category.data["goal_type"]
        if goal_type == "NEED":
            if category_config.overflow:
                return self.new_month_NEED_with_overflow(m_category)
            else:
                return self.new_month_NEED_without_overflow(m_category)
        elif goal_type == "MF":
            return self.new_month_savings_builder_MF(m_category)
        elif goal_type == "TB":
            return self.new_month_savings_balance_TB(m_category)
        else:
            raise ValueError(f"Unexpected goal_type: {m_category.data['goal_type']}")

    @staticmethod
    def new_month_NEED_without_overflow(
        m_category: MonthCategory,
    ) -> Tuple[MonthCategory]:
        to_add = m_category.data["goal_under_funded"]
        m_category.new_budgeted = m_category.old_budgeted + to_add
        return (m_category,)

    def new_month_NEED_with_overflow(
        self, m_category: MonthCategory
    ) -> List[MonthCategory]:
        updated_m_categories = []
        left_to_add = m_category.data["goal_target"]

        overflow_cycle = 0
        while left_to_add > 0:
            left_to_add, updated_m_category = self.overflow(
                m_category, overflow_cycle, left_to_add
            )
            updated_m_categories.append(updated_m_category)
            overflow_cycle += 1

        return updated_m_categories

    @staticmethod
    def overflow(
        m_category: MonthCategory, overflow_cycle: int, left_to_add: int
    ) -> Tuple[int, MonthCategory]:
        budget_ynab_id = m_category.budget_ynab_id
        category_ynab_id = m_category.category_ynab_id
        month = offset_month(m_category.month, overflow_cycle)

        requester = ApiRequest()
        if overflow_cycle == 0:
            month_celing = m_category.data["goal_under_funded"]
        elif overflow_cycle > 0:
            category_data = requester.retrieve_month_category(
                budget_ynab_id, month, category_ynab_id
            )
            m_category = MonthCategory(
                data=category_data,
                budget_ynab_id=budget_ynab_id,
                month=month,
                category_ynab_id=category_ynab_id,
            )
            month_celing = m_category.data["goal_target"] - m_category.old_budgeted
        else:
            raise ValueError(
                f"overflow_cycle is {overflow_cycle}, should be 0 or larger"
            )

        if left_to_add > month_celing:
            to_add_this_month = month_celing
        else:
            to_add_this_month = left_to_add

        if m_category.old_budgeted is None:
            raise ValueError("Expected old_budgeted to be int but is None.")
        m_category.new_budgeted = m_category.old_budgeted + to_add_this_month

        left_to_add -= to_add_this_month
        return left_to_add, m_category

    @staticmethod
    def new_month_savings_builder_MF(m_category: MonthCategory) -> Tuple[MonthCategory]:
        to_add = m_category.data["goal_overall_left"]
        m_category.new_budgeted = m_category.old_budgeted + to_add
        return (m_category,)

    def new_month_savings_balance_TB(
        self, m_category: MonthCategory
    ) -> Tuple[MonthCategory]:
        to_add = m_category.data["goal_overall_left"]
        limit = self.extract_TB_limit(m_category.data["note"])

        if limit < to_add:
            to_add = limit

        m_category.new_budgeted = m_category.old_budgeted + to_add
        return (m_category,)

    @staticmethod
    def extract_TB_limit(note: str) -> int | float:
        PATTERN = "^limit: *((?:[0-9]+[ _]*)+)"
        note = note.lower()

        re_match = re.search(PATTERN, note, flags=re.MULTILINE)
        if not re_match:
            return float("inf")

        number_str: str = re_match[1]
        number_str: str = number_str.replace(" ", "")
        number_int: int = int(number_str) * 1000

        return number_int

    def create_file_with_overview_of_updated_m_categories(self) -> None:
        string = self.get_overview_string()
        self.create_overview_file(string)

    def get_overview_string(self) -> str:
        blocks = []
        for m_category in self.all_updated_m_categories:
            block = f"""\
                    {m_category.name}
                    {m_category.month}
                    ADDING: {m_category.delta() / 1000} EUR
                    BEFORE: {m_category.old_budgeted / 1000} EUR
                    AFTER:  {m_category.new_budgeted / 1000} EUR
            """
            block = textwrap.dedent(block)
            blocks.append(block)
        return "\n".join(blocks)

    @staticmethod
    def create_overview_file(string: str) -> None:
        FILE_NAME = "updated_overview.txt"
        with open(FILE_NAME, "w") as file:
            file.write(string)
