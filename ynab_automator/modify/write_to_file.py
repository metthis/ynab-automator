from __future__ import annotations
from typing import List
import textwrap

from ynab_automator.datastructures.ynab_dataclasses import MonthCategory


def create_file_with_overview_of_updated_m_categories() -> None:
    string = get_overview_string()
    create_overview_file(string)


def get_overview_string(m_categories: List[MonthCategory]) -> str:
    blocks = []
    for m_category in m_categories:
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


def create_overview_file(string: str) -> None:
    FILE_NAME = "updated_overview.txt"
    with open(FILE_NAME, "w") as file:
        file.write(string)
