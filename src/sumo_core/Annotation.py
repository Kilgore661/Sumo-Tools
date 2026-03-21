"""
Annotation enum for sumo history.

Represents the extended annotation set used by the new Chii model.
"""

from __future__ import annotations

from enum import Enum, auto


class Annotation(Enum):
    TD = auto()
    OB = auto()
    HD = auto()
    YO = auto()
    EMPTY = auto()
