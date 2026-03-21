"""
Riks value object for sumo history.

Represents a set of RikId.

This is an immutable collection. No constraints are enforced
on the elements beyond the class contract: they are expected
to be RikId.
"""

from __future__ import annotations


class Riks(frozenset):
    def __new__(cls, iterable=()):
        return super().__new__(cls, iterable)

    def __repr__(self) -> str:
        return f"{set(self)}"

    def __str__(self) -> str:
        return str(set(self))
