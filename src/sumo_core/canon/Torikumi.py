"""
Torikumi value object for sumo history.

Represents a set of Pair.

This class does not currently enforce the stronger tournament-level
constraint that the same rikishi cannot appear twice. That belongs
to a higher-level validation step if and when it is implemented.
"""

from __future__ import annotations

from Pair import Pair


class Torikumi(set):
    def __new__(cls, pairs=None):
        if pairs is not None:
            return super().__new__(cls, pairs)
        return super().__new__(cls)
