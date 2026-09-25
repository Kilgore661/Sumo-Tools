"""Domain objects for published torikumi, independent of bout results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import Date


@dataclass(frozen=True, slots=True)
class FutureBout:
    order: int
    east: RikId
    west: RikId
    east_shikona: str | None = None
    west_shikona: str | None = None

    def __post_init__(self) -> None:
        if self.order < 1:
            raise ValueError("Future bout order must be positive")
        if self.east == self.west:
            raise ValueError("Future bout participants must be distinct")


@dataclass(frozen=True, slots=True)
class FutureDay:
    day: Day
    bouts: tuple[FutureBout, ...]
    source_url: str
    downloaded_at: datetime
    result_count: int = 0

    def __post_init__(self) -> None:
        if not self.bouts:
            raise ValueError("Future day must contain at least one bout")
        if self.result_count < 0 or self.result_count > len(self.bouts):
            raise ValueError("Future day result count is outside its bout range")


@dataclass(frozen=True, slots=True)
class Future:
    date: Date
    completed_through: Day | None
    days: tuple[FutureDay, ...]
    generated_at: datetime

    def __post_init__(self) -> None:
        day_numbers = [int(day.day) for day in self.days]
        if day_numbers != sorted(set(day_numbers)):
            raise ValueError("Future days must be unique and ordered")

