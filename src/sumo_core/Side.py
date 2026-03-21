"""
Side enum for sumo history.

Represents the side of a rank position.
"""

from __future__ import annotations

from enum import Enum, auto


class Side(Enum):
    EAST = auto()
    WEST = auto()
    NONE = auto()
