"""
Symbol enum for sumo history.

Represents the display symbol associated with a rikishi's outcome in a bout.

Members:
- W    : win
- L    : loss
- FS   : fusensho (win by default)
- FP   : fusenpai (loss by default)
- DASH : no bout / no symbol
- DRAW : draw

String conversion returns the corresponding Unicode display symbol.

The method inconsistent(out) encodes the established consistency check
between Symbol and Outcome.
"""

from __future__ import annotations

from enum import Enum, auto


class Symbol(Enum):
    W = auto()
    L = auto()
    FS = auto()
    FP = auto()
    DASH = auto()
    DRAW = auto()

    def __str__(self):
        """
        Return the Unicode symbol for display.
        """
        display_map = {
            Symbol.L: "\u25CF",    # ●
            Symbol.W: "\u25CB",    # ○
            Symbol.FS: "\u25A1",   # □
            Symbol.FP: "\u25A0",   # ■
            Symbol.DASH: "\u2013", # –
            Symbol.DRAW: "\u25B3", # △
        }
        return display_map[self]

    @classmethod
    def from_unicode(cls, unicode_char):
        """
        Convert a Unicode character to the corresponding Symbol enum.
        """
        reverse_map = {
            "\u25CF": cls.L,    # ●
            "\u25CB": cls.W,    # ○
            "\u25A0": cls.FP,   # ■
            "\u25A1": cls.FS,   # □
            "\u2013": cls.DASH, # –
            "\u25B3": cls.DRAW, # △
        }
        return reverse_map.get(unicode_char, None)
