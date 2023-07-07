from enum import Enum, auto


# Used by test.assign/conftest.py:
class ResetMode(Enum):
    EMPTY = auto()
    PARTIALLY_FULL = auto()
    FULL = auto()
    OVERFLOWN_PARTIALLY = auto()
    OVERFLOWN_FULLY = auto()
    OVERFLOWN_FULLY_PLUS_PARTIALLY = auto()
