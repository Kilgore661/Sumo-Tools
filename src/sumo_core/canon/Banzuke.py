"""
Canonical banzuke model.

NOTE:
- File name: Banzuke.py
- Class name: BanzukeWithAnnotations (temporary)
- Will be renamed to Banzuke once migration is complete

A Banzuke consists of:

- riks     : the set of rikishi IDs present in the banzuke
- rikchii  : a partial function from RikId to NewFoo
- rikshik  : a partial function from RikId to Shikona

The defining structural constraint is that these three objects have
the same domain.
"""

from __future__ import annotations

from dataclasses import dataclass

from Riks import Riks
from RikChii import RikNewFoo
from RikShikona import RikShikona
from RikId import RikId


@dataclass(frozen=True)
class BanzukeWithAnnotations:
    """
    Immutable aggregate representing a complete banzuke
    in the annotated rank model.
    """
    riks: Riks
    rikchii: RikNewFoo
    rikshik: RikShikona

    def __post_init__(self):
        """
        Validate structural correctness of the aggregate.

        At this level, validation belongs in the class.
        """
        if not isinstance(self.riks, Riks):
            raise TypeError(f"banzuke.riks must be a Riks object, got {type(self.riks)}")

        if not isinstance(self.rikchii, RikNewFoo):
            raise TypeError(f"banzuke.rikchii must be a RikNewFoo object, got {type(self.rikchii)}")

        if not isinstance(self.rikshik, RikShikona):
            raise TypeError(f"banzuke.rikshik must be a RikShikona object, got {type(self.rikshik)}")

        if not (self.riks == set(self.rikchii.keys()) == set(self.rikshik.keys())):
            raise ValueError("The domains of riks, rikchii, and rikshik must be identical.")

    def get_chii(self, rid: RikId):
        return self.rikchii(rid)

    def get_shik(self, rid: RikId):
        return self.rikshik(rid)

    def __contains__(self, rid: RikId) -> bool:
        return rid in self.riks

    def __len__(self) -> int:
        return len(self.riks)
