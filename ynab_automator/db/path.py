import os


_DEFAULT_DB_FILENAME = "categories.db"


# Depends on the this file remaining in the same folder as the databases.
_DB_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
DEFAULT_DB_PATH = os.path.join(_DB_DIR, _DEFAULT_DB_FILENAME)


def get_custom_db_path(custom_db_filename: str) -> str:
    root, _ = os.path.splitext(custom_db_filename)
    custom_db_filename = f"{root}.db"
    return os.path.join(_DB_DIR, custom_db_filename)
