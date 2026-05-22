from dataclasses import dataclass

from .BasicPrimitives import RikId, Riks, Shikona
from .Chii import Chii


################################################################################

"""
Mapping from RikId to Shikona.

Represents a partial function:

    RikId -> Shikona
"""

class RikShikona(dict):
    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for rid, shik in mapping.items():
                instance[rid] = shik

        return instance

    def __call__(self, rid: RikId):
        return self.get(rid)

"""
Canonical transitional mapping from RikId to Chii.

Represents a partial function:

    RikId → Chii

This is implemented as a dictionary with function-call syntax.
"""



class RikChii(dict):
    def __new__(cls, mapping=None):
        instance = super().__new__(cls)

        if mapping is not None:
            for rid, foo in mapping.items():
                instance[rid] = foo

        return instance

    def __call__(self, rid: RikId):
        return self.get(rid)

################################################################################

"""
Canonical banzuke model.

A Banzuke consists of:

- riks     : the set of rikishi IDs present in the banzuke
- rikchii  : a partial function from RikId to Chii
- rikshik  : a partial function from RikId to Shikona

The defining structural constraint is that these three objects have
the same domain.
"""


@dataclass(frozen=True)
class Banzuke:
    """
    Immutable aggregate representing a complete banzuke
    in the annotated rank model.
    """
    riks: Riks
    rikchii: RikChii
    rikshik: RikShikona

    def __post_init__(self):
        """
        Validate structural correctness of the aggregate.

        At this level, validation belongs in the class.
        """
        if not isinstance(self.riks, Riks):
            raise TypeError(f"banzuke.riks must be a Riks object, got {type(self.riks)}")

        if not isinstance(self.rikchii, RikChii):
            raise TypeError(f"banzuke.rikchii must be a RikChii object, got {type(self.rikchii)}")

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
