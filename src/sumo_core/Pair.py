"""
Pair value object for sumo history.

Represents an unordered pair of distinct rikishi IDs.

This is implemented as a tuple subclass.

Notes:
- The two rikishi must be distinct.
- The special tuple-unpacking branch is preserved because it is needed
  for reconstruction in some contexts (notably pickling).
"""

from __future__ import annotations

from RikId import RikId


class Pair(tuple):
    def __new__(cls, r1: RikId, r2: RikId = None):
        """
        Create a canonical pair of distinct rikishi IDs.

        The pair is stored in sorted order so that:
            Pair(a, b) == Pair(b, a)

        The alternate tuple-unpacking branch is preserved for reconstruction.
        """
        if r2 is None:
            r1, r2 = r1

        if r1 == r2:
            raise ValueError(f"Pair members must be distinct, got {r1} and {r2}")

        return super(Pair, cls).__new__(cls, tuple(sorted((r1, r2))))

    def __repr__(self) -> str:
        return f"({self[0]}, {self[1]})"

    def __str__(self) -> str:
        return f"({self[0]}, {self[1]})"
