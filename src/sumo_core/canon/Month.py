"""
Month value object for sumo history.

Represents a basho month.

Invariants:
- Month must be in range 1..12
- Month must be odd (sumo tournaments occur in odd months only)

This is an immutable, hashable value object.
"""

from __future__ import annotations


class Month(int):
    MIN_MONTH = 1
    MAX_MONTH = 12

    def __new__(cls, value: int) -> "Month":
        if not (cls.MIN_MONTH <= value <= cls.MAX_MONTH):
            raise ValueError(f"Month must be in range {cls.MIN_MONTH}..{cls.MAX_MONTH}, got {value}")

        if value % 2 == 0:
            raise ValueError(f"Month must be odd, got {value}")

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))
