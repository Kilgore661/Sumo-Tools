"""
Level value object for sumo history.

Represents the formal level of a rank.

A Level is either:
- an MSD, or
- a Division other than MAKUUCHI

That is:

    Level = MSD + Division - {MAKUUCHI}

This implementation deliberately preserves the established
factory-style behaviour of the model.
"""

from __future__ import annotations

from typing import Union

from Division import Division
from MSD import MSD


class Level:
    def __new__(cls, value: Union[MSD, Division]):
        if not isinstance(value, (MSD, Division)):
            raise TypeError("Level must be an MSD or Division")

        if isinstance(value, Division) and value == Division.MAKUUCHI:
            raise ValueError(
                "Use MSD values for Makuuchi levels instead of Division.MAKUUCHI"
            )

        result = value
        result.as_string = lambda: result.name.capitalize()

        def get_abbreviation():
            abbrev_map = {
                MSD.YOKOZUNA: "Y",
                MSD.OZEKI: "O",
                MSD.SEKIWAKE: "S",
                MSD.KOMUSUBI: "K",
                MSD.MAEGASHIRA: "M",
                Division.JURYO: "J",
                Division.MAKUSHITA: "Ms",
                Division.SANDANME: "Sd",
                Division.JONIDAN: "Jd",
                Division.JONOKUCHI: "Jk",
            }
            return abbrev_map[result]

        result.as_abbreviation = get_abbreviation
        return result
