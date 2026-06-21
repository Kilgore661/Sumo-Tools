"""Data model for the rising-rikishi producer."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


DEFAULT_WINDOWS = (3, 4, 5, 6, 12, 18)


@dataclass(frozen=True)
class RisingWindow:
    """One n-basho movement window ending at one basho."""

    end_basho: Date
    movement_basho: tuple[Date, ...]

    @property
    def size(self) -> int:
        return len(self.movement_basho)

    @property
    def first_basho(self) -> Date:
        return self.movement_basho[0]


@dataclass(frozen=True)
class BoutCounts:
    """Bout counts for one rikishi across a movement window."""

    rating_bouts: int


@dataclass(frozen=True)
class RisingRow:
    """CSV row for one rikishi in one rising-rikishi window."""

    rik_id: int
    shikona: str
    chii: str
    chii_ordinal: int
    delta: str
    basho_norm: str
    num_bouts: int
    bout_norm: str


@dataclass(frozen=True)
class RatingEndpoints:
    """Start and end ratings for a rikishi movement window."""

    rikid: RikId
    chii: Chii
    start_rating: float
    end_rating: float
