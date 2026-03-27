from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional, List
from sumo_core.History import Date
from sumo_core.BasicPrimitives import Day

"""
Core types used by the tracker.

RunState:
    High-level lifecycle state of the tracker loop.

UpdateResult:
    Outcome of a single update cycle.

BashoWindow:
    Concrete scheduling window for a basho, including pre-basho period
    and trigger hour.

TrackerRuntime:
    Ephemeral runtime state of the tracker loop, updated each iteration.
"""


class RunState(Enum):
    """
    High-level tracker state.

    RECOVERY means the tracker is still retry-eligible, but a prior update
    failure implies that required maintained state is currently presumed
    missing, stale, or otherwise unresolved.
    """
    DORMANT = auto()
    READY = auto()
    RECOVERY = auto()
    ACTIVE = auto()


class UpdateResult(Enum):
    """
    Outcome of a single update cycle.
    """
    SUCCESS = auto()
    SCRAPE_FAILED = auto()
    NO_NEW_DATA = auto()
    PARSER_FATAL_ERROR = auto()
    CACHE_FAILED = auto()
    ANALYSIS_FAILED = auto()


@dataclass(frozen=True)
class BashoWindow:
    """
    Concrete scheduling window for a basho.
    """
    pre_basho_start: datetime
    basho_start: datetime
    basho_end: datetime
    trigger_hour: int


@dataclass
class TrackerRuntime:
    """
    Ephemeral runtime state of the tracker loop.
    """
    state: RunState
    current_time: Optional[datetime] = None
    current_window: Optional[BashoWindow] = None
    next_run_time: Optional[datetime] = None


@dataclass(frozen=True)
class BashoDayRef:
    """
    Reference to a specific day within a specific basho.

    A BashoDayRef is the canonical identifier for a unit of work in the
    tracker/scraper/parser pipeline.

    It consists of:
    - date : the basho date (Year, Month)
    - day  : the day number within the basho (1–15)

    This replaces the informal use of (Date, Day) tuples and provides a
    clear, type-safe representation of a basho day.
    """

    date: Date
    day: Day

    def __post_init__(self):
        if not isinstance(self.date, Date):
            raise TypeError(
                f"date must be Date, got {type(self.date)}"
            )

        if not isinstance(self.day, Day):
            raise TypeError(
                f"day must be Day, got {type(self.day)}"
            )

    def __str__(self) -> str:
        return f"{self.date} Day {int(self.day)}"

RequestedDateDays = List[BashoDayRef]
