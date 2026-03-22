from dataclasses import dataclass

from .Banzuke import Banzuke
from .Summary import Summary


@dataclass(frozen=True)
class BashoState:
    """
    Canonical transitional basho state model.

    NOTE:
    - File name: BashoState.py
    - Class name: BashoState
    - Will be renamed to BashoState once migration is complete

    Represents the state of a basho.

    A BashoState consists of:
    - banzuke : the set of rikishi and their ranks
    - summary : the recorded results and performances
    """


    banzuke: Banzuke
    summary: Summary

    def __post_init__(self):
        if not isinstance(self.banzuke, Banzuke):
            raise TypeError(
                f"banzuke must be Banzuke, got {type(self.banzuke)}"
            )

        if not isinstance(self.summary, Summary):
            raise TypeError(
                f"summary must be Summary, got {type(self.summary)}"
            )
