"""
Day value object for sumo history.

Represents a day within a basho.

Invariant:
- Day must be in range 1..15
"""

from __future__ import annotations


class Day(int):
    MIN_DAY = 1
    MAX_DAY = 15

    def __new__(cls, value: int) -> "Day":
        if not (cls.MIN_DAY <= value <= cls.MAX_DAY):
            raise ValueError(
                f"Day must be in range {cls.MIN_DAY}..{cls.MAX_DAY}, got {value}"
            )

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))
