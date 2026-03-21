"""
Direction enum for sumo history.

Represents a direction of rank movement.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache


class Direction(Enum):
    PROMOTION = "↑"
    DEMOTION = "↓"

    @staticmethod
    @lru_cache(maxsize=None)
    def abbr_to_direction():
        """
        Return a cached mapping from abbreviation to Direction.
        """
        return {
            "↑": Direction.PROMOTION,
            "↓": Direction.DEMOTION,
        }
