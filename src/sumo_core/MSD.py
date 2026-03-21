"""
MSD (Makuuchi SubDivision) enum for sumo history.

Represents subdivisions within makuuchi:

- Yokozuna
- Ozeki
- Sekiwake
- Komusubi
- Maegashira

Used in place of Division.MAKUUCHI for rank modelling.
"""

from __future__ import annotations

from enum import Enum, auto


class MSD(Enum):
    YOKOZUNA = auto()
    OZEKI = auto()
    SEKIWAKE = auto()
    KOMUSUBI = auto()
    MAEGASHIRA = auto()

    def as_abbreviation(self) -> str:
        if self == MSD.YOKOZUNA:
            return "Y"
        elif self == MSD.OZEKI:
            return "O"
        elif self == MSD.SEKIWAKE:
            return "S"
        elif self == MSD.KOMUSUBI:
            return "K"
        elif self == MSD.MAEGASHIRA:
            return "M"
        else:
            raise ValueError(f"Invalid MSD: {self}")
