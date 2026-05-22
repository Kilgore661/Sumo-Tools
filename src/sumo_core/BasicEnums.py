from enum import Enum, auto
from functools import lru_cache

################################################################################

class Outcome(Enum):
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

################################################################################

class Symbol(Enum):
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

    def inconsistent( self, out: Outcome ) -> bool:
        #! Val: E3.2.11
        if self == Symbol.W and out == Outcome.W:
            return False
        if self == Symbol.L and out == Outcome.L:
            return False
        if self == Symbol.FS and out == Outcome.FS:
            return False
        if self == Symbol.FP and out == Outcome.FP:
            return False
        if self == Symbol.DRAW and out == Outcome.DRAW:
            return False
        return True

################################################################################

class Annotation(Enum):
    """
    Annotation enum for sumo history.

    Represents the extended annotation set used by the new Chii model.
    """

    TD = auto()
    OB = auto()
    HD = auto()
    YO = auto()
    EMPTY = auto()

################################################################################

class Division(Enum):
    """
    Division enum for sumo history.

    Represents the main divisions in professional sumo.

    Includes MAKUUCHI, but note:
    - MAKUUCHI is not used directly as a Level
    - makuuchi ranks are represented via MSD instead
    """

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

################################################################################

class MSD(Enum):
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

################################################################################

class Prize(Enum):
    """
    Prize enum for sumo history.

    Represents special prizes awarded in a basho.
    """

    YUSHO = "Yusho"             # Championship Winner
    DOTEN_YUSHO = "Doten-Yusho" # Runner-up after playoff
    JUN_YUSHO = "Jun-Yusho"     # Runner-up
    KANTO = 'Kantosho'          # Fighting Spirit Prize
    SHUKUN = 'Shukunsho'        # Outstanding Performance Prize
    GINO = 'Ginosho'            # Technique Prize

    @staticmethod
    @lru_cache(maxsize=None)

    def abbr_to_prize():
        """Returns a cached mapping from abbreviations to Prize enum members."""
        return {
            'Y': Prize.YUSHO,
            'J': Prize.JUN_YUSHO,
            'D': Prize.DOTEN_YUSHO, # YUSHO_DOTEN would break my assumption
                                    # about initial letters being different :(
            'K': Prize.KANTO,    
            'S': Prize.SHUKUN,  
            'G': Prize.GINO    
        }

    def prize_to_abbr( p ):
        """Returns a cached mapping from abbreviations to Prize enum members."""
        return p.name[0]

################################################################################

class Direction(Enum):
    """
    Direction enum for sumo history.

    Represents a direction of rank movement.
    """

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
################################################################################

class Side(Enum):
    """
    Side enum for sumo history.

    Represents the side of a rank position.
    """
    EAST = auto()
    WEST = auto()
    NONE = auto()
