"""
ResultLookup mapping for sumo history.

Represents a partial function:

    Pair -> BoutResult

Implemented as a dictionary with function-call syntax.
"""

from __future__ import annotations

from Pair import Pair
from BoutResult import BoutResult


class ResultLookup(dict):
    DEMOTION = "↓"

    def __call__(self, pair: Pair):
        """
        Return the BoutResult for the given Pair, or None if undefined.
        """
        return self.get(pair)
