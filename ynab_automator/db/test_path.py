from __future__ import annotations
import os

import pytest

from ynab_automator.db import path
from ynab_automator.config import local

cases = [
    "dwojhwcd",
    "s7sd_dgw9.lol",
    "sifgdsijhvgodsjvhosdjhvsdkvjbsdv.db",
    "a.d",
    "bbbbbbbbb.pdf",
]


@pytest.mark.parametrize("filename", cases)
def test_get_custom_db_path(filename):
    root, _ = os.path.splitext(filename)
    filename = f"{root}.db"
    expected = os.path.abspath(os.path.join(__file__, os.pardir, filename))
    result = path.get_custom_db_path(filename)
    print(result)
    assert result == expected

    # Needs to be changed manually, works in macOS:
    manual_expected = (
        f"{local.DB_DIR_PATH}{filename}"
    )
    assert result == manual_expected