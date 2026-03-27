from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional

from sumo_core.BasicPrimitives import Day
from sumo_core.History import Date

"""
Core types used by the tracker.

RunState:
    High-level lifecycle state of the tracker loop.

UpdateResult:
    Outcome of a single update cycle.

RetrievalResult:
    Outcome of the retrieval stage within an update cycle.

BashoWindow:
    Concrete scheduling window for a basho, including pre-basho period
    and trigger hour.

TrackerRuntime:
    Ephemeral runtime state of the tracker loop, updated each iteration.
"""


class RunState(Enum):
    """
    High-level tracker state.

    RECOVERY means the tracker is still retry-eligible, but a prior
    retrieval failure implies that required source data is currently
    presumed missing.
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
    NO_NEW_DATA = auto()
    RETRIEVAL_FAILED = auto()
    REBUILD_FAILED = auto()
    PUBLISH_FAILED = auto()
    CACHE_FAILED = auto()
    ANALYSIS_FAILED = auto()
    DERIVED_ARTIFACTS_MISSING = auto()


class RetrievalResult(Enum):
    """
    Outcome of the retrieval stage within an update cycle.
    """

    FAILURE = auto()
    SUCCESS_UNCHANGED = auto()
    SUCCESS_CHANGED = auto()


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
    current_time: datetime
    current_window: BashoWindow
    next_run_time: Optional[datetime] = None # Hack
    # Strictly speaking, there are two TrackerRuntimes. One is for during a
    # basho, when there is no next time after Day 15. The other is outside the
    # window when there is always a next basho.


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
            raise TypeError(f"date must be Date, got {type(self.date)}")

        if not isinstance(self.day, Day):
            raise TypeError(f"day must be Day, got {type(self.day)}")

    def __str__(self) -> str:
        return f"{self.date} Day {int(self.day)}"


RequestedDateDays = List[BashoDayRef]
