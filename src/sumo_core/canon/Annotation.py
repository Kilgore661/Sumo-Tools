"""
NewAnn enum for sumo history.

Represents the extended annotation set used by the new Chii model.
"""

# NOTE: NewAnn will be renamed to Annotation once legacy model is retired

from __future__ import annotations

from enum import Enum, auto


class NewAnn(Enum):
    TD = auto()
    OB = auto()
    HD = auto()
    YO = auto()
    EMPTY = auto()
