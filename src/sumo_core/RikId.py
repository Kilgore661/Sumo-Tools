"""
RikId value object for sumo history.

Represents the unique identifier of a rikishi.

Invariant:
- RikId must be a positive integer

This is an immutable, hashable value object.
"""

from __future__ import annotations


class RikId(int):
    def __new__(cls, value: int) -> "RikId":
        if value <= 0:
            raise ValueError(f"RikId must be positive, got {value}")

        return int.__new__(cls, value)

    def __repr__(self) -> str:
        return f"{int(self)}"

    def __str__(self) -> str:
        return str(int(self))
