# This has the original version of Ann

from typing import Union, Literal
from enum import Enum, auto
from .Kimarite import Kimarite
from functools import lru_cache

class Outcome(Enum):
    #! Val: E2.1.2.1
    W = auto()   # Win
    L = auto()   # Loss
    FS = auto()  # Fusensho (win by default)
    FP = auto()  # Fusenpai (loss by default)
    DRAW = auto()

    def to_symbol(self):
        """Convert an Outcome to its corresponding Symbol"""
        return Symbol[self.name]

class Side(Enum):
    #! Val: E2.1.2.5
    EAST = auto()
    WEST = auto()
    NONE = auto()

class Ann(Enum):
    #! Val: E2.1.2.6
    TD = auto()  
    OB = auto() 
    EMPTY = auto()  # Empty annotation (ε)

class Division(Enum):
    #! Val: E2.1.2.1
    MAKUUCHI = auto()
    JURYO = auto()
    MAKUSHITA = auto()
    SANDANME = auto()
    JONIDAN = auto()
    JONOKUCHI = auto()

    # Hack to get around Python bug: _abbrev_map = { ... } should work as the
    # identifier starts with an underscore so should *not* have type Division,
    # but it does.

    # It turns out there is a reason for including Mz: they occasionally appear
    # in bouts against Jk. It was decided not to do this because (a) we are
    # never interested in Mz and (b) Mz would be a 10th rank, messing up the
    # idea of ordinals having a single digit for the rank/division and (c)
    # whilst that's easy enough to handle by allowing two digits, it would add
    # an extra 0 to very non-Mz ordinal when it is not needed in 99.9% of
    # cases.
    #
    # However, the decision to not change it has consequences for the new
    # parser  - see adapt_banzuke_for_daily_parser() in
    # sandpit.GTB.optimisation.others.infrastructure.parser.parser2_utils

    @staticmethod
    @lru_cache(maxsize=None)  # Cache the result indefinitely
    def abbrev_map():
        return {
            Division.JURYO: 'J',
            Division.MAKUSHITA: 'Ms',
            Division.SANDANME: 'Sd',
            Division.JONIDAN: 'Jd',
            Division.JONOKUCHI: 'Jk'
        }

    def as_abbreviation(self):
        # Access the cached map
        return Division.abbrev_map()[self]

class MSD(Enum):
    #! Val: Inconsistent! But E2.1.2.2 is covered implicitly in declaration of Level.
    # Level = Sanyaku + {maegashira} + Division - { makuuchi }
    #       = MSD +  Division - { makuuchi }
    # which is consistent with the implementation of Level
    YOKOZUNA = auto()
    OZEKI = auto()
    SEKIWAKE = auto()
    KOMUSUBI = auto()
    MAEGASHIRA = auto()

    # Hack to get around Python bug: _abbrev_map = { ... } should work as the
    # identifier starts with an underscore so should *not* have type Division,
    # but it does.
    @staticmethod
    @lru_cache(maxsize=None)  # Cache the result indefinitely
    def abbrev_map():
        return {
            MSD.YOKOZUNA: 'Y',
            MSD.OZEKI: 'O',
            MSD.SEKIWAKE: 'S',
            MSD.KOMUSUBI: 'K',
            MSD.MAEGASHIRA: 'M'
        }

    def as_abbreviation(self):
        # Access the cached map
        return MSD.abbrev_map()[self]

class Symbol(Enum):
    # Should be in core-specific and imported for use above
    #! Val: E3.2.2.1
    W = auto()    # Win
    L = auto()    # Loss
    FS = auto()   # Fusensho (win by default)
    FP = auto()   # Fusenpai (loss by default)
    DASH = auto() # –
    DRAW = auto() # △
    
    #! TBD: Infrastructure
    
    def __str__(self):
        """Return the Unicode symbol for display"""
        display_map = {
            Symbol.L: '\u25CF',    # ●
            Symbol.W: '\u25CB',    # ○
            Symbol.FS: '\u25A1',   # □
            Symbol.FP: '\u25A0',   # ■
            Symbol.DASH: '\u2013', # –
            Symbol.DRAW: '\u25B3'  # △
        }
        return display_map[self]

	#! TBD: Move to Scraping



    
    @classmethod 
    def from_unicode(cls, unicode_char):
        """Convert a Unicode character to the corresponding Symbol enum"""
        reverse_map = {
            '\u25CF': cls.L,    # ●
            '\u25CB': cls.W,    # ○
            '\u25A0': cls.FP,   # ■
            '\u25A1': cls.FS,   # □
            '\u2013': cls.DASH, # –
            '\u25B3': cls.DRAW  # △
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

class Decision:
    def __new__(cls, value: Union[Kimarite, Literal["fusen", "blank"]]):
        if not (isinstance(value, Kimarite) or value in ("fusen", "blank")):
            raise TypeError(f"Decision must be Kimarite or special outcome, got {type(value)}")
        return value

class Prize(Enum):
    YUSHO = "Yusho"         # Championship Winner
    DOTEN_YUSHO = "Doten-Yusho" # Runner-up after playoff
    JUN_YUSHO = "Jun-Yusho" # Runner-up
    KANTO = 'Kantosho'      # Fighting Spirit Prize
    SHUKUN = 'Shukunsho'    # Outstanding Performance Prize
    GINO = 'Ginosho'        # Technique Prize

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

class Direction(Enum):
    PROMOTION = '↑'
    DEMOTION = '↓'

    @staticmethod
    @lru_cache(maxsize=None)  # Cache the result indefinitely
    def abbr_to_direction():
        """Returns a cached mapping from abbreviations to Prize enum members."""
        return {
            '↑': Direction.PROMOTION,
            '↓': Direction.DEMOTION
        }

