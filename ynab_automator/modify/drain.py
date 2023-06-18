from __future__ import annotations
from typing import Set
import textwrap

from ynab_automator.datastructures.ynab_dataclasses import Category, MonthCategory
from ynab_automator.modify import prepare
from ynab_automator.modify import assign


def get_m_categories_after_draining(
    m_categories_before_draining: list[MonthCategory],
    categories_config: list[Category],
) -> list[MonthCategory]:
    (
        donors_after_draining,
        recipients_ids_and_amounts,
    ) = drain_from_m_categories(m_categories_before_draining)

    recipients_ids_and_amounts = consolidate_ids_and_amounts(
        recipients_ids_and_amounts
    )

    recipients_after_draining = drain_into_m_categories(
        m_categories_before_draining,
        categories_config,
        recipients_ids_and_amounts,
    )

    all_m_categories_after_draining = (
        donors_after_draining + recipients_after_draining
    )

    assert_that_no_m_category_was_lost(
        m_categories_before_draining, all_m_categories_after_draining
    )

    return all_m_categories_after_draining


def consolidate_ids_and_amounts(
    recipients_ids_and_amounts: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    consolidated_dict = {}
    for id, amount in recipients_ids_and_amounts:
        consolidated_dict[id] = consolidated_dict.get(id, 0) + amount
    consolidated_list = [consolidated_dict.items()]
    return consolidated_list


def drain_from_m_categories(
    m_categories: list[MonthCategory],
) -> tuple[list[MonthCategory], list[tuple[int, int]]]:
    donors_after_draining: list[MonthCategory] = []
    recipients_ids_and_amounts: list[tuple[int, int]] = []

    for m_category in m_categories:
        if not m_category.drain_into:
            continue
        (
            m_category,
            drain_recipient_id,
            drain_amount,
        ) = drain_from_a_single_m_category(m_category)
        donors_after_draining.append(m_category)
        recipients_ids_and_amounts.append(drain_recipient_id, drain_amount)

    return donors_after_draining, recipients_ids_and_amounts


def drain_from_a_single_m_category(
    m_category: MonthCategory,
) -> tuple[MonthCategory, int, int]:
    drain_recipient_id = m_category.drain_into
    drain_amount = m_category.data["balance"]
    m_category.new_budgeted = m_category.old_budgeted - drain_amount
    return (m_category, drain_recipient_id, drain_amount)


def drain_into_m_categories(
    m_categories_before_draining: list[MonthCategory],
    categories_config: list[Category],
    recipients_ids_and_amounts: list[tuple[int, int]],
) -> list[MonthCategory]:
    m_categories_after_draining = []

    for id, amount in recipients_ids_and_amounts:
        m_category = tuple(
            x for x in m_categories_before_draining if id == x.category_id
        )[0]
        if m_category.drain_into:
            continue
        category_config = prepare.get_matching_category_config(
            categories_config, m_category
        )
        if category_config.overflow:
            recipient_m_categories_after_draining = assign.overflow_loop(
                m_category, amount
            )
            m_categories_after_draining.extend(recipient_m_categories_after_draining)
        else:
            m_category.new_budgeted = m_category.old_budgeted + amount
            m_categories_after_draining.append(m_category)

    return m_categories_after_draining


def assert_that_no_m_category_was_lost(
    before_draining: list[MonthCategory], after_draining: list[MonthCategory]
) -> None:
    def get_set_of_m_category_identifiers(
        m_categories: list[MonthCategory],
    ) -> Set[tuple[str, str]]:
        identifiers = {(x.category_ynab_id, x.month) for x in m_categories}
        return identifiers

    identifiers_before_draining = get_set_of_m_category_identifiers(before_draining)
    identifiers_after_draining = get_set_of_m_category_identifiers(after_draining)

    if difference := identifiers_before_draining ^ identifiers_after_draining:
        string = f"""\
                The lists before and after draining don't contain the same MonthCategories.
                Difference: {difference}
                Amount before: {len(identifiers_before_draining)}
                Amount after:  {len(identifiers_after_draining)}
                """
        string = textwrap.dedent(string)
        raise ValueError(string)
    else:
        return None
