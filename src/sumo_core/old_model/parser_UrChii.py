'''
Rule for rank handling

The authoritative rank object is NewFoo, and operationally its authoritative value is:

NewFoo.ordinal

That is the model rank.

So:

all computation,

all comparisons,

all sorting,

all grouping,

all indexing,

all matrix axes,

must use ordinals / NewFoo, never the display string.

Therefore

The string form (str(NewFoo) / chii) is:

display only

It must never drive logic.

Practical consequence

Inside code:

✔ use:

rank.ordinal

or NewFoo directly if hashing/comparison is defined consistently.

✘ do not use:

str(rank)

for any logical operation.

Because strings are human-readable labels, not model values.

Output rule

When a rank appears in output as a row/column identifier:

write both:

ordinal

string form

for example:

400200,M2e

or separate columns:

rank_ordinal,rank_chii
400200,M2e

This preserves:

machine-sortability by ordinal

human readability by chii

Why this matters

Because ordinals encode rank order formally:

if a.ordinal < b.ordinal, then rank a is stronger than rank b

That property must never be lost by accidental string handling.

So the canonical hierarchy is

Model layer: NewFoo.ordinal
Presentation layer: str(NewFoo)

and never the other way round.
'''

# This started as main_8_UrChii.py but has been co-opted to form the "NewUrChii
# class": i.e. UrChii + extended annotations which is needed for a new version
# of the parse that writes a History with annotations (sadly missing from the
# core parser). The actual UrChii class was called "Foo" for historical
# reasons. We will use "NewFoo" not "NewUrChii".


from dataclasses import dataclass, field
from typing import Union, Any, TYPE_CHECKING
from pdb import set_trace
import re

from core.model.common.BasicEnums import MSD, Division, Side
from core.model.common.Banzuke import Level, Chii, Annotation
from core.model.common.BasicEnums import Ann as CoreAnn
from .parser_NewAnn import NewAnn


@dataclass(frozen=True, eq=False) # eq=False because we implement our own __eq__ (and __lt__)
class NewFoo:
    """
    An immutable, serializable, hashable, and intrinsically sortable representation
    of a sumo rank (chii), derived from the core model's Chii concept.

    It internalizes sorting logic based on sumo hierarchy, removing the need
    for external ordering maps for its own comparison.
    """
    level: 'Level'  # Stores the Level object from Banzuke.py (which wraps MSD/Division)
    number: int
    side: 'Side'    # Stores the Side enum from BasicEnums.py
    ann: 'NewAnn'   # Stores the NewAnn enum from .parser_NewAnn

    # Pre-calculated sort keys for efficient comparison and hashing.
    _sort_key_level: int = field(init=False, repr=False, compare=False)
    _sort_key_number: int = field(init=False, repr=False, compare=False)
    _sort_key_side: int = field(init=False, repr=False, compare=False)
    _sort_key_ann: int = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        """
        Calculates and sets the internal sort keys after initialization.
        Uses object.__setattr__ because the dataclass is frozen.
        """
        # Validate inputs first (optional, but good practice if not done elsewhere)
        if not isinstance(self.level, (MSD, Division)):
            raise TypeError(f"NewFoo.level must be a Level object wrapping MSD/Division, got {type(self.level)}")
        if not isinstance(self.number, int) or self.number <= 0:
            #set_trace()
            raise ValueError(f"NewFoo.number must be a positive integer not <{self.number}>.")
        if not isinstance(self.side, Side):
            raise TypeError(f"NewFoo.side must be a Side enum, got {type(self.side)}")
        if not isinstance(self.ann, NewAnn):
            raise TypeError(f"NewFoo.ann must be an NewAnn enum, got {type(self.ann)}")

        # --- Level Sort Key Derivation ---
        # Access the underlying MSD/Division enum from the Level object
        core_level_enum: Union[MSD, Division] = self.level # Assuming Level object IS the enum
                                                           # or self.level.value if Level is a wrapper class
                                                           # Based on Banzuke.py Level.__new__, self.level IS the enum.

        # What follows looks like we are defining < on Levels and so it would
        # make sense to subclass Level and add the definition. Unforunately you
        # cant to this becuase Levels are created with new(). To get around
        # that you'd have to write a new Level class and at this point it
        # doesn't seem worth it. The key takeaway: Levels are comparable in the
        # "obvious" sense, but only in the context of an NewFoo.
        #
        # Or, to be more precise, the *underlying MSD/Division enums* (which
        # are what NewFoo.level holds) are *made comparable* through the
        # mechanism implemented within NewFoo.

        level_val_for_sort: int
        if isinstance(core_level_enum, MSD):
            level_val_for_sort = core_level_enum.value
        elif isinstance(core_level_enum, Division):
            if core_level_enum == Division.MAKUUCHI:
                # This case should ideally be prevented by Chii/Level validation
                # or how NewFoo is constructed (e.g., from_chii).
                raise ValueError("NewFoo cannot be formed with Division.MAKUUCHI as level.")
            # Derivation: offset by number of MSD ranks, adjust for Division enum's own .value
            level_val_for_sort = len(MSD.__members__) + (core_level_enum.value - 1)
        else:
            # This should not be reached if the initial type check for self.level passes
            raise TypeError(f"Unexpected type for NewFoo's core level enum: {type(core_level_enum)}")
        
        object.__setattr__(self, '_sort_key_level', level_val_for_sort)

        # --- Number Sort Key ---
        object.__setattr__(self, '_sort_key_number', self.number)

        # --- Side Sort Key ---
        # Assumes Side enum values (from auto()) align with desired sort order
        # e.g., EAST.value (1) < WEST.value (2) < NONE.value (3)
        object.__setattr__(self, '_sort_key_side', self.side.value)

        # --- Annotation Sort Key ---
        # Assumes NewAnn enum values (from auto()) align with desired sort order
        # e.g., TD.value (1) < OB.value (2) < EMPTY.value (3)
        object.__setattr__(self, '_sort_key_ann', self.ann.value)

    @classmethod
    def from_chii(cls, chii_instance: 'Chii') -> 'NewFoo':
        """
        Factory method to create an NewFoo instance from a core model Chii object.
        """

        # Chii.level is a Level object (which is an MSD/Division enum per Banzuke.py)
        # Chii.ann is an NewAnn enum (result of Annotation factory class)
        return cls(
            level=chii_instance.level,
            number=chii_instance.number,
            side=chii_instance.side,
            ann=NewAnn[chii_instance.ann.name]
        )

    @classmethod
    def from_str(cls, chii_str: str) -> 'NewFoo':
        """
        Parses a raw chii string (e.g., "M1e", "Y1wTD") and creates a NewFoo object.
        This is the modern replacement for the old `_get_chii` logic.
        """
        if not chii_str:
            raise ValueError("Cannot parse empty chii string.")

        s = chii_str
        
        level_map = {
            'Y': MSD.YOKOZUNA, 'O': MSD.OZEKI, 'S': MSD.SEKIWAKE, 
            'K': MSD.KOMUSUBI, 'M': MSD.MAEGASHIRA, 'J': Division.JURYO, 
            'Ms': Division.MAKUSHITA, 'Sd': Division.SANDANME, 'Jd': Division.JONIDAN, 
            'Jk': Division.JONOKUCHI
        }
        level_num_pat = re.compile(r"(Y|O|S|K|M|J|Ms|Sd|Jd|Jk)(\d+)(.*)")
        match = level_num_pat.fullmatch(s)
        if not match:
            set_trace()
            raise ValueError(f"Invalid level/number part in chii string '{chii_str}'")
        level_str = match.group(1)
        level = Level(level_map[level_str])

        num = int(match.group(2))

        side = Side.NONE
        ann = NewAnn.EMPTY
        
        s = match.group(3)
        if s.startswith('e'):
            side = Side.EAST
            s = s[1:]
        elif s.startswith('w'):
            side = Side.WEST
            s = s[1:]
        
        if s:
            try:
                ann = NewAnn[s]
            except KeyError:
                raise ValueError(f"Invalid annotation part '{s}' in chii string '{chii_str}'")

        return NewFoo(level=level, number=num, side=side, ann=ann)


    def old_ordinal(self) -> int:
        # Buggy: there are 5 enum values, and 'Yes' we really do need YO as a
        # bonafide annotation (for reasons I forget; treating it as a synonym
        # for Y did not work out.)
        """
        Calculates a single integer ordinal for this NewFoo, suitable for
        cases where a single sort key is preferred over rich comparison.
        Lower value means better rank.

        # There is a subtlety that LLMs miss regarding Chii "codes" which are
        # sometimes unhelpfully called Chii "ordinals". In general a chii is
        # (Division, Level, Side, Annotation ). These tuples are cast into 6
        # digit decimal integers dlllsa wherein supremacy is indicated by lower
        # numbers eg. 0 for yokozuna, 1 for ozeki etc, 1 is the highest level,
        # 0 (east) is the highest side. Annotations are coded for completeness
        # but (iirc) generally ignored. Thus the highest possible rank Y1e is
        # 00010x i.e 10. 40121x would be M12w. This has the advantage that
        # chii1 <= chii2 iff code(chi1) <= code(chii2). This is the sense in
        # which they are "ordinals". However "code(chi1) <= code(chii2)" is
        # meaningless. 
        """
        # This formula provides a unique integer per chii, weighted.
        # Adjust weights if necessary based on max number, side count, ann count.
        # Max number typically < 100 for Maegashira/Juryo.
        # Sides = 3, Anns = 4.
        # Ordinal = LevelKey * 10000 + NumberKey * 100 + SideKey * 10 + AnnKey
        # For NumberKey, lower is better rank, so use self._sort_key_number directly if that's raw num.
        # But __lt__ logic for number is "higher number is worse", so for ordinal,
        # we want lower number to contribute less.
        # Let's stick to the pattern used in auto_4.py's ordinal for consistency,
        # adapting it to use the internal sort keys.

        # self._sort_key_level: 1 (Yokozuna) is best.
        # self._sort_key_number: 1 (M1) is best.
        # self._sort_key_side: 1 (EAST) is best.
        # self._sort_key_ann: 1 (TD) is best.

        # Multipliers ensure distinctness.
        # Max number of ranks ~10 (Y,O,S,K,M,J,Ms,Sd,Jd,Jk) for level_key.
        # Max rank number ~60 (Ms).
        # Max side_key ~3.
        # Max ann_key ~3.
        # ord_val = 100000 * (level_ord - 1) + 100 * chii_obj.number + 10 * side_val + ann_val (from auto_4.py)

        # Using the pre-calculated sort keys:
        # _sort_key_level already starts at 1 for best.
        # _sort_key_number is the rank number (1 is best).
        # _sort_key_side is side.value (1 for EAST is best).
        # _sort_key_ann is ann.value (1 for TD is best).
        ord_val = ( (self._sort_key_level -1) * 10000 + # Scale level
                    (self._sort_key_number) * 10 +    # Scale number
                    (self._sort_key_side -1) * 1 +      # Scale side
                    2*(5-self._sort_key_ann )              # 
                  )
        return ord_val

    def ordinal(self) -> int:
        """
        Calculates a single integer ordinal for this NewFoo, suitable for
        cases where a single sort key is preferred over rich comparison.
        Lower value means better rank.

        In essence, a chii with level l, number nnn, side s and annotation a,
        where l, nnn, a and s are the obvious enumeration values has code
        lnnnas. Eg, Ms13wHD is 6,013,1,5-3=2 so 601321 whereas Ms13w is 601301.

        NOTE: This formula imposes a specific, artificial ranking among the
        different non-empty annotation types (e.g., TD vs. OB). This is a
        necessary side-effect of creating a unique integer key and does not
        reflect a formal rule in sumo. The only guaranteed ranking is that
        an un-annotated rikishi is ranked higher than any annotated one.
        """
        ord_val = ( (self._sort_key_level -1) * 100000 + # Scale level
                    (self._sort_key_number) * 100 +      # Scale number
                    (5-self._sort_key_ann ) * 10 +       # Scale annotation
                    (self._sort_key_side -1)             # Scale side
                  )
        return int(ord_val)


    @classmethod
    def from_ordinal(cls, ordinal: int) -> 'NewFoo':
        """
        Reconstructs an NewFoo object from its unique integer ordinal,
        which is based on the 'lnnnas' encoding scheme. This is the
        direct inverse of the ordinal() method.
        """
        # --- Pre-calculate Reverse Lookups (if not already cached) ---
        if not hasattr(cls, '_from_ordinal_maps'):
            # Level Key (1-based) to Level Enum
            level_key_map = {}
            for msd_member in MSD:
                level_key_map[msd_member.value] = Level(msd_member)
            div_offset = len(MSD.__members__)
            for div_member in Division:
                if div_member != Division.MAKUUCHI:
                    key = div_offset + (div_member.value - 1)
                    level_key_map[key] = Level(div_member)

            # Side Key (1-based) to Side Enum
            side_key_map = {s.value: s for s in Side}
            
            # Ann Key to Ann Enum. We need the inverse of `5 - key`.
            # inverted_key = 5 - key -> key = 5 - inverted_key
            ann_from_inverted_key = {}
            for ann_member in NewAnn:
                inverted_key = 5 - ann_member.value
                ann_from_inverted_key[inverted_key] = ann_member

            cls._from_ordinal_maps = {
                'level': level_key_map,
                'side': side_key_map,
                'ann': ann_from_inverted_key
            }

        try:
            # --- Deconstruct the ordinal using integer and modulo arithmetic ---
            side_enc   = ordinal % 10
            ann_enc    = (ordinal // 10) % 10
            number_val = (ordinal // 100) % 1000
            level_enc  = ordinal // 100000

            # Convert 0-based encoding keys back to 1-based sort keys for lookup
            level_key = level_enc + 1
            side_key = side_enc + 1

            # --- Convert keys back to their original types ---
            level = cls._from_ordinal_maps['level'][level_key]
            side  = cls._from_ordinal_maps['side'][side_key]
            ann   = cls._from_ordinal_maps['ann'][ann_enc]

            if number_val == 0 and level_key <= 5: # Sanyaku/Makuuchi ranks must have num > 0
                raise ValueError("Ordinal implies a rank number of 0, which is invalid for this rank.")

        except KeyError as e:
            raise ValueError(f"Could not decode ordinal {ordinal}. Invalid component key: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse ordinal {ordinal}: {e}")
            
        return NewFoo(level=level, number=number_val, side=side, ann=ann)

    def __gt__(self, other: Any) -> bool:
        return self.ordinal() > other.ordinal()  

    def __lt__(self, other: Any) -> bool:
        return self.ordinal() < other.ordinal()  

    def __eq__(self, other: Any) -> bool:
        return self.ordinal() == other.ordinal()  

    def to_chii(self) -> 'Chii':
        """
        Converts this NewFoo instance back to a core model Chii object.
        This handles the managed information loss for new annotations.
        """
        # Chii's 'ann' attribute expects an NewAnn enum.
        # NewFoo.ann is already an NewAnn enum.

        # Check if our NewAnn value is one of the new, unsupported ones
        if self.ann in (NewAnn.HD, NewAnn.YO):
            # If so, downgrade it to a safe default value
            safe_ann_for_core = CoreAnn.EMPTY
        else:
            # Otherwise, the name exists in the old enum, so we can convert it
            safe_ann_for_core = CoreAnn[self.ann.name]

        return Chii(
            level=self.level,  # self.level is already MSD/Division enum
            number=self.number,
            side=self.side,
            ann=safe_ann_for_core 
        )

    def __hash__(self) -> int:
        return hash(self.ordinal())

    def __str__(self) -> str:
        """Provides a human-readable string representation like 'M1e', 'S1 TD'."""
        # Uses as_abbreviation from the Level object (which is MSD/Division enum)
        level_abbr = self.level.as_abbreviation() 
        side_char = ''
        if self.side == Side.EAST: side_char = 'e'
        elif self.side == Side.WEST: side_char = 'w'
        # Side.NONE results in no side character.
        
        ann_str = ''
        if self.ann != NewAnn.EMPTY:
            ann_str = f"{self.ann.name}" # e.g., " TD", " OB"

        # Special Sanyaku+ formatting: if number is 1, side is East, and ann is Empty,
        # traditionally the '1e' is omitted for Y, O, S, K.
        # However, for a generic NewFoo string, being explicit might be better.
        # The old auto_4.py NewFoo.__str__ had this logic:
        #if self.side == Side.EAST and self.ann == Ann.EMPTY and \
        #   isinstance(self.level, MSD) and \
        #   self.level in (MSD.YOKOZUNA, MSD.OZEKI, MSD.SEKIWAKE, MSD.KOMUSUBI) and \
        #   self.number == 1:
        #    return f"{level_abbr}{ann_str}".strip() # Omits number and side for Y1e, O1e, S1e, K1e
        
        return f"{level_abbr}{self.number}{side_char}{ann_str}".strip()

# --- Self-Test Block (Optional) ---
if __name__ == '__main__':
    print("--- NewFoo.py Self-Test ---")

    # Mock core model Chii for testing from_chii (if Chii itself is not too complex to mock)
    # For a real test, you'd import and use actual Chii, Level, Side, NewAnn.
    # This requires BasicEnums.py and Banzuke.py to be importable and functional.
    
    # Create some Level, Side, NewAnn instances (assuming imports work)
    try:
        level_Y1 = Level(MSD.YOKOZUNA)
        level_M1 = Level(MSD.MAEGASHIRA)
        level_M5 = Level(MSD.MAEGASHIRA)
        level_J10 = Level(Division.JURYO)

        # Test NewFoo creation directly
        y1e = NewFoo(level_Y1, 1, Side.EAST, NewAnn.EMPTY)
        o1w = NewFoo(Level(MSD.OZEKI), 1, Side.WEST, NewAnn.EMPTY)
        s1e_td = NewFoo(Level(MSD.SEKIWAKE), 1, Side.EAST, NewAnn.TD)
        k1w = NewFoo(Level(MSD.KOMUSUBI), 1, Side.WEST, NewAnn.EMPTY)
        m1e = NewFoo(level_M1, 1, Side.EAST, NewAnn.EMPTY)
        m1w = NewFoo(level_M1, 1, Side.WEST, NewAnn.EMPTY)
        m5e = NewFoo(level_M5, 5, Side.EAST, NewAnn.EMPTY)
        m5w = NewFoo(level_M5, 5, Side.WEST, NewAnn.EMPTY)
        j10e = NewFoo(level_J10, 10, Side.EAST, NewAnn.EMPTY)
        j10w_yo = NewFoo(level_J10, 10, Side.WEST, NewAnn.YO)
        j10w_ob = NewFoo(level_J10, 10, Side.WEST, NewAnn.OB)

        test_urchiis = [m5e, y1e, m1w, s1e_td, k1w, o1w, m1e, j10w_yo, j10w_ob, m5w, j10e]

        print("\nOriginal NewFoo list:")
        for u in test_urchiis:
            print(f"  {str(u):<10} (LevelKey: {u._sort_key_level}, NumKey: {u._sort_key_number}, SideKey: {u._sort_key_side}, AnnKey: {u._sort_key_ann}, Ordinal: {u.ordinal()})")

        print("\nSorted NewFoo list (should be by rank):")
        test_urchiis.sort() # Uses NewFoo.__lt__
        for u in test_urchiis:
            print(f"  {str(u):<10} (Ordinal: {u.ordinal()})")

        # Test equality and hashing
        m1e_copy = NewFoo(level_M1, 1, Side.EAST, NewAnn.EMPTY)
        print(f"\nm1e == m1e_copy: {m1e == m1e_copy} (Expected: True)")
        print(f"m1e == m1w: {m1e == m1w} (Expected: False)")
        
        urchii_set = {m1e, m1w, m1e_copy}
        print(f"Set size: {len(urchii_set)} (Expected: 2 if hash/eq work)")
        for item in urchii_set:
            print(f"  In set: {str(item)}")

        # Test from_chii if Chii can be instantiated
        # This requires Chii from Banzuke.py to be importable and usable
        try:
            # Create components for Chii
            chii_level_component = Level(MSD.MAEGASHIRA) # This is MSD.MAEGASHIRA
            chii_number_component = 3
            chii_side_component = Side.EAST
            # Chii's 'ann' attribute expects an NewAnn enum (due to its __post_init__).
            # The Annotation class is a factory that PRODUCES an NewAnn enum.
            # So, when constructing Chii, you pass what Annotation(...) returns.
            chii_ann_component = Annotation("") # This returns NewAnn.EMPTY

            # Instantiate Chii
            core_chii_m3e = Chii(
                level=chii_level_component,
                number=chii_number_component,
                side=chii_side_component,
                ann=chii_ann_component # Pass the NewAnn.EMPTY enum member
            )

            # Now test NewFoo.from_chii()
            urchii_from_core = NewFoo.from_chii(core_chii_m3e)
            print(f"\nFoo from Chii object representing 'M3e': {str(urchii_from_core)}")
            print(f"  Its Ordinal: {urchii_from_core.ordinal()}")
        except ImportError:
            print("\nSkipping from_chii test due to Chii import issues in standalone mode.")
        except Exception as e_chii:
            print(f"\nError during from_chii test setup: {e_chii}")


        print("\nTest __str__ special Sanyaku cases:")
        print(f"  Y1e (Num 1, E, Empty): {NewFoo(Level(MSD.YOKOZUNA), 1, Side.EAST, NewAnn.EMPTY)}") # Exp: Y
        print(f"  Y2e (Num 2, E, Empty): {NewFoo(Level(MSD.YOKOZUNA), 2, Side.EAST, NewAnn.EMPTY)}") # Exp: Y2e
        print(f"  S1w (Num 1, W, Empty): {NewFoo(Level(MSD.SEKIWAKE), 1, Side.WEST, NewAnn.EMPTY)}") # Exp: S1w
        print(f"  K1e TD (Num 1, E, TD): {NewFoo(Level(MSD.KOMUSUBI), 1, Side.EAST, NewAnn.TD)}")   # Exp: K TD (as K1e TD) -> K TD if number is 1. 

    except ImportError as e:
        print(f"\nSELF-TEST SKIPPED for NewFoo.py: Failed to import core model components.")
        print(f"Error: {e}")
    except Exception as e_main_test:
        print(f"\nAn error occurred during NewFoo.py self-test: {e_main_test}")
        import traceback
        traceback.print_exc()

    print("\n--- End NewFoo.py Self-Test ---")
