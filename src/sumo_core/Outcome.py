"""
Outcome enum for sumo history.

Represents the result outcome for one rikishi in a bout.

Members:
- W    : win
- L    : loss
- FS   : fusensho (win by default)
- FP   : fusenpai (loss by default)
- DRAW : draw

The name mapping to Symbol is intentional:
    Outcome.W    -> Symbol.W
    Outcome.L    -> Symbol.L
    Outcome.FS   -> Symbol.FS
    Outcome.FP   -> Symbol.FP
    Outcome.DRAW -> Symbol.DRAW
"""

from __future__ import annotations

from enum import Enum, auto

from Symbol import Symbol


class Outcome(Enum):
    W = auto()
    L = auto()
    FS = auto()
    FP = auto()
    DRAW = auto()

    def to_symbol(self):
        """
        Convert an Outcome to its corresponding Symbol.
        """
        return Symbol[self.name]
