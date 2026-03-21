"""
Division enum for sumo history.

Represents the main divisions in professional sumo.

Includes MAKUUCHI, but note:
- MAKUUCHI is not used directly as a Level
- makuuchi ranks are represented via MSD instead
"""

from __future__ import annotations

from enum import Enum, auto


class Division(Enum):
    MAKUUCHI = auto()
    JURYO = auto()
    MAKUSHITA = auto()
    SANDANME = auto()
    JONIDAN = auto()
    JONOKUCHI = auto()

    def as_abbreviation(self) -> str:
        if self == Division.JURYO:
            return "J"
        elif self == Division.MAKUSHITA:
            return "Ms"
        elif self == Division.SANDANME:
            return "Sd"
        elif self == Division.JONIDAN:
            return "Jd"
        elif self == Division.JONOKUCHI:
            return "Jk"
        else:
            raise ValueError(f"Invalid Division: {self}")
