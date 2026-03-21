from dataclasses import dataclass
from typing import Dict, Optional

# --- Import the custom rank object that this model is built to hold ---
from .parser_UrChii import NewFoo

# --- Import core data model classes that do not need to be changed ---
from core.model.common.Banzuke import Riks, RikShikona
from core.model.common.Summary import Summary
from core.model.common.History import Date
from core.model.common.BasicPrimitives import RikId

class RikNewFoo(dict):
    """
    A dictionary-based mapping from a Rikishi's ID to their rank (NewFoo).

    This is a direct replacement for the core model's `RikChii` class.
    Instead of mapping RikId -> Chii, it maps RikId -> NewFoo, allowing it
    to store the extended annotation data from the new parser.
    """
    def __new__(cls, mapping: Optional[Dict[RikId, NewFoo]] = None):
        instance = super().__new__(cls)
        if mapping is not None:
            for rid, foo in mapping.items():
                if not isinstance(rid, RikId):
                    raise TypeError(f"Keys in RikNewFoo must be RikId objects, but got {type(rid)}")
                if not isinstance(foo, NewFoo):
                    raise TypeError(f"Values in RikNewFoo must be NewFoo objects, but got {type(foo)}")
                instance[rid] = foo
        return instance

    def __call__(self, rid: RikId) -> Optional[NewFoo]:
        """Implements function-like behavior to retrieve a NewFoo object by RikId."""
        return self.get(rid)

@dataclass(frozen=True)
class BanzukeWithAnnotations:
    """
    Represents a complete sumo tournament banzuke using the extended `NewFoo` rank object.

    This is a direct replacement for the core model's `Banzuke` class.
    Its structure is identical, but its `rikchii` attribute holds the richer
    rank data required by the new parser.
    """
    riks: Riks
    rikchii: RikNewFoo
    rikshik: RikShikona

    def __post_init__(self):
        """Validates the structure after initialization."""
        if not isinstance(self.riks, Riks):
            raise TypeError(f"banzuke.riks must be a Riks object, got {type(self.riks)}")
        if not isinstance(self.rikchii, RikNewFoo):
            raise TypeError(f"banzuke.rikchii must be a RikNewFoo object, got {type(self.rikchii)}")
        if not isinstance(self.rikshik, RikShikona):
            raise TypeError(f"banzuke.rikshik must be a RikShikona object, got {type(self.rikshik)}")
        if not (self.riks == set(self.rikchii.keys()) == set(self.rikshik.keys())):
            raise ValueError("The domains of riks, rikchii, and rikshik must be identical.")

@dataclass(frozen=True)
class BashoStateWithAnnotations:
    """
    Represents the complete state of a basho using the new, annotation-rich data model.

    This is a direct replacement for the core model's `BashoState` class.
    """
    banzuke: BanzukeWithAnnotations
    summary: Summary  # The Summary structure is unchanged and can be reused directly.

    def __post_init__(self):
        """Validates the structure after initialization."""
        if not isinstance(self.banzuke, BanzukeWithAnnotations):
            raise TypeError(f"basho_state.banzuke must be a BanzukeWithAnnotations object, got {type(self.banzuke)}")
        if not isinstance(self.summary, Summary):
            raise TypeError(f"basho_state.summary must be a Summary object, got {type(self.summary)}")

class HistoryWithAnnotations(dict):
    """
    A dictionary-based mapping from a Date to a `BashoStateWithAnnotations`.

    This is a direct replacement for the core model's `History` class, designed
    to hold the results of the new parser.
    """
    def __new__(cls, mapping: Optional[Dict[Date, BashoStateWithAnnotations]] = None):
        instance = super().__new__(cls)
        if mapping is not None:
            for date, bs in mapping.items():
                if not isinstance(date, Date):
                    raise TypeError(f"Keys in HistoryWithAnnotations must be Date objects, got {type(date)}")
                if not isinstance(bs, BashoStateWithAnnotations):
                    raise TypeError(f"Values must be BashoStateWithAnnotations objects, got {type(bs)}")
                instance[date] = bs
        return instance
    
    def __call__(self, date: Date) -> Optional[BashoStateWithAnnotations]:
        """Implements function-like behavior to retrieve a BashoState by Date."""
        return self.get(date)
