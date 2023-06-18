from __future__ import annotations
from dataclasses import astuple
from typing import Any
import random
from copy import copy, deepcopy

import pytest

from ynab_automator.modify import prepare
from ynab_automator.fetch import retrieve_distilled, months
from ynab_automator.datastructures.ynab_dataclasses import Category, MonthCategory


def get_m_category_init_vars():
    budget_ynab_id = "c1e0ea99-5668-483b-b01e-25b348fe3437"
    month = months.get_current_month()
    categories_data = retrieve_distilled.month_categories(budget_ynab_id, month)
    categories_config = prepare.get_sorted_categories_config_from_db(budget_ynab_id)
    category_ynab_ids = prepare.get_ynab_ids_from_categories_config(categories_config)

    return budget_ynab_id, month, categories_data, category_ynab_ids, categories_config


def get_test_cases():
    m_categories = prepare.get_initialised_m_categories(*get_m_category_init_vars())
    categories_config = get_m_category_init_vars()[-1]
    return [(categories_config, x) for x in m_categories]


@pytest.mark.parametrize("categories_config, m_category", get_test_cases())
def test_get_matching_category_config(
    categories_config: list[Category], m_category: MonthCategory
):
    result = prepare.get_matching_category_config(categories_config, m_category)
    assert isinstance(result, Category)
    assert result.category_ynab_id == m_category.category_ynab_id


def get_test_cases():
    m_categories = prepare.get_initialised_m_categories(*get_m_category_init_vars())
    cases = [copy(m_categories) for _ in range(10)]
    for m_categories in cases:
        random.shuffle(m_categories)
    return cases


# Sets data to None because a dict isn't hashable and conversions to a string
# are expensive and take exponentially more time with each test case
# for some reason:
def turn_elements_into_tuples(
    m_categories: list[MonthCategory],
) -> list[tuple[Any, ...]]:
    m_categories = deepcopy(m_categories)
    m_categories = remove_data(m_categories)
    m_categories_tup = [astuple(x) for x in m_categories]
    return m_categories_tup


def remove_data(m_categories: list[MonthCategory]) -> list[MonthCategory]:
    new_m_categories = []
    for x in m_categories:
        new_x = deepcopy(x)
        new_x.data = None
        new_m_categories.append(new_x)
    return new_m_categories


# Tests whether the cases above indeed contain shuffled lists of MonthCategory:
@pytest.mark.parametrize("ten_lists_of_m_categories", [get_test_cases()])
def test_shuffling_of_m_categories(
    ten_lists_of_m_categories: list[list[MonthCategory]],
):
    # Tests whether all the shuffled lists are made up of the same elements:
    ten_lists_of_m_categories = [
        turn_elements_into_tuples(m_categories)
        for m_categories in ten_lists_of_m_categories
    ]
    set_of_sets = {frozenset(shuffled) for shuffled in ten_lists_of_m_categories}
    assert len(set_of_sets) == 1

    # Tests whether the shuffled lists are distinct from each other.
    # 0.7 allows some slack in case a permutation occurs more than once.
    ten_tups_of_m_categories = tuple(
        tuple(m_categories) for m_categories in ten_lists_of_m_categories
    )
    assert len(set(ten_tups_of_m_categories)) > (len(ten_lists_of_m_categories) * 0.7)


@pytest.mark.parametrize("m_categories", get_test_cases())
def test_sort_m_categories_by_position(m_categories: list[MonthCategory]):
    result = prepare.sort_m_categories_by_position(m_categories)
    assert isinstance(result, list)
    assert len(result) == len(m_categories)

    positions = (x.position for x in result)
    for position, i in zip(positions, range(1, len(m_categories) + 1), strict=True):
        assert position == i

    # Sets data to None because a dict isn't hashable and conversions to a string
    # are expensive and take exponentially more time with each test case
    # for some reason:
    def turn_elements_into_tuples(lst: list[MonthCategory]) -> list[tuple[Any, ...]]:
        lst = deepcopy(lst)
        lst = remove_data(lst)
        lst_tup = [astuple(x) for x in lst]
        return lst_tup

    def remove_data(lst: list[MonthCategory]) -> list[MonthCategory]:
        new_lst = []
        for x in lst:
            new_x = deepcopy(x)
            new_x.data = None
            new_lst.append(new_x)
        return new_lst

    result_tups = turn_elements_into_tuples(result)
    m_categories_tups = turn_elements_into_tuples(m_categories)
    assert set(result_tups) == set(m_categories_tups)
