"""
Canonical transitional rank model.

NOTE:
- The file name is Chii.py
- The class name remains NewFoo for now
- When the migration is complete, NewFoo will be renamed to Chii

NewFoo is the authoritative rank object in the model.

Its authoritative value is:

    NewFoo.ordinal()

This means that:

- all comparison
- all sorting
- all grouping
- all indexing
- all matrix axes

must use the ordinal (or NewFoo objects whose comparison is defined by ordinal),
never the display string.

A NewFoo consists of:

- level      : Level = MSD + Division - {MAKUUCHI}
- number     : positive integer
- side       : Side
- ann        : NewAnn

String form is presentation only.
It must never be used to drive logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import re

from Division import Division
from MSD import MSD
from Side import Side
from Level import Level
from Annotation import NewAnn


@dataclass(frozen=True, eq=False)
class NewFoo:
    """
    Immutable, hashable, intrinsically sortable representation of a sumo rank.

    Equality, ordering, and hashing are defined by ordinal().
    """
    level: Level
    number: int
    side: Side
    ann: NewAnn

    _sort_key_level: int = field(init=False, repr=False, compare=False)
    _sort_key_number: int = field(init=False, repr=False, compare=False)
    _sort_key_side: int = field(init=False, repr=False, compare=False)
    _sort_key_ann: int = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        """
        Enforce the one real invariant at this level.

        The rest is trusted by contract.
        """
        if self.number <= 0:
            raise ValueError(f"NewFoo.number must be positive, got {self.number}")

        core_level_enum = self.level

        # Levels are made comparable only in the context of NewFoo.
        # MSD values come first; lower divisions follow after an offset.
        if isinstance(core_level_enum, MSD):
            level_val_for_sort = core_level_enum.value
        elif isinstance(core_level_enum, Division):
            if core_level_enum == Division.MAKUUCHI:
                raise ValueError("NewFoo cannot be formed with Division.MAKUUCHI as level.")
            level_val_for_sort = len(MSD.__members__) + (core_level_enum.value - 1)
        else:
            raise TypeError(f"Unexpected level type: {type(core_level_enum)}")

        object.__setattr__(self, "_sort_key_level", level_val_for_sort)
        object.__setattr__(self, "_sort_key_number", self.number)
        object.__setattr__(self, "_sort_key_side", self.side.value)
        object.__setattr__(self, "_sort_key_ann", self.ann.value)

    @classmethod
    def from_str(cls, chii_str: str) -> "NewFoo":
        """
        Parse a display-form rank string.

        Examples:
            M1e
            Y1wTD
            Ms13wHD

        The display string is accepted here as an input format,
        but it is not the authoritative representation of rank.
        """
        if not chii_str:
            raise ValueError("Cannot parse empty chii string.")

        level_map = {
            "Y": MSD.YOKOZUNA,
            "O": MSD.OZEKI,
            "S": MSD.SEKIWAKE,
            "K": MSD.KOMUSUBI,
            "M": MSD.MAEGASHIRA,
            "J": Division.JURYO,
            "Ms": Division.MAKUSHITA,
            "Sd": Division.SANDANME,
            "Jd": Division.JONIDAN,
            "Jk": Division.JONOKUCHI,
        }

        level_num_pat = re.compile(r"(Y|O|S|K|M|J|Ms|Sd|Jd|Jk)(\d+)(.*)")
        match = level_num_pat.fullmatch(chii_str)
        if not match:
            raise ValueError(f"Invalid chii string: '{chii_str}'")

        level_str = match.group(1)
        level = Level(level_map[level_str])
        number = int(match.group(2))

        side = Side.NONE
        ann = NewAnn.EMPTY

        suffix = match.group(3)
        if suffix.startswith("e"):
            side = Side.EAST
            suffix = suffix[1:]
        elif suffix.startswith("w"):
            side = Side.WEST
            suffix = suffix[1:]

        if suffix:
            try:
                ann = NewAnn[suffix]
            except KeyError:
                raise ValueError(f"Invalid annotation part '{suffix}' in chii string '{chii_str}'")

        return NewFoo(level=level, number=number, side=side, ann=ann)

    def ordinal(self) -> int:
        """
        Return the authoritative machine rank.

        Encoding is effectively:

            lnnnas

        where:
        - l     = level code
        - nnn   = rank number
        - a     = annotation code
        - s     = side code

        Lower ordinal means stronger rank.

        This imposes an artificial ordering among non-empty annotations.
        The important semantic guarantee is that an unannotated rank
        outranks an annotated one at the same underlying level/number/side.
        """
        ord_val = (
            (self._sort_key_level - 1) * 100000
            + self._sort_key_number * 100
            + (5 - self._sort_key_ann) * 10
            + (self._sort_key_side - 1)
        )
        return int(ord_val)

    @classmethod
    def from_ordinal(cls, ordinal: int) -> "NewFoo":
        """
        Reconstruct a NewFoo from its ordinal.

        This is the inverse of ordinal().
        """
        if not hasattr(cls, "_from_ordinal_maps"):
            level_key_map = {}
            for msd_member in MSD:
                level_key_map[msd_member.value] = Level(msd_member)

            div_offset = len(MSD.__members__)
            for div_member in Division:
                if div_member != Division.MAKUUCHI:
                    key = div_offset + (div_member.value - 1)
                    level_key_map[key] = Level(div_member)

            side_key_map = {s.value: s for s in Side}

            ann_from_inverted_key = {}
            for ann_member in NewAnn:
                inverted_key = 5 - ann_member.value
                ann_from_inverted_key[inverted_key] = ann_member

            cls._from_ordinal_maps = {
                "level": level_key_map,
                "side": side_key_map,
                "ann": ann_from_inverted_key,
            }

        try:
            side_enc = ordinal % 10
            ann_enc = (ordinal // 10) % 10
            number_val = (ordinal // 100) % 1000
            level_enc = ordinal // 100000

            level_key = level_enc + 1
            side_key = side_enc + 1

            level = cls._from_ordinal_maps["level"][level_key]
            side = cls._from_ordinal_maps["side"][side_key]
            ann = cls._from_ordinal_maps["ann"][ann_enc]

            if number_val == 0 and level_key <= 5:
                raise ValueError("Ordinal implies rank number 0, which is invalid for this rank.")

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

    def __hash__(self) -> int:
        return hash(self.ordinal())

    def __str__(self) -> str:
        """
        Human-readable display form.

        This is presentation only and must not be used for logic.
        """
        level_abbr = self.level.as_abbreviation()

        side_char = ""
        if self.side == Side.EAST:
            side_char = "e"
        elif self.side == Side.WEST:
            side_char = "w"

        ann_str = ""
        if self.ann != NewAnn.EMPTY:
            ann_str = self.ann.name

        return f"{level_abbr}{self.number}{side_char}{ann_str}".strip()
