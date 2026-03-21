"""
Date value object for sumo history.

A Date represents a basho date as a pair (Year, Month).

It is immutable, hashable, and orderable.
Its string form is "YYYY/MM".
"""

from __future__ import annotations

from dataclasses import dataclass

from Year import Year
from Month import Month


@dataclass(frozen=True)
class Date:
    year: Year
    month: Month

    def __str__(self) -> str:
        return f"{self.year}/{self.month:02d}"

    def __lt__(self, other: "Date") -> bool:
        return self.year < other.year or (
            self.year == other.year and self.month < other.month
        )

    def __gt__(self, other: "Date") -> bool:
        return self.year > other.year or (
            self.year == other.year and self.month > other.month
        )

    def __le__(self, other: "Date") -> bool:
        return self < other or self == other

    def __ge__(self, other: "Date") -> bool:
        return self > other or self == other
