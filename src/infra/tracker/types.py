from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional

from ...sumo_core.BasicPrimitives import Day
from ...sumo_core.History import Date

"""
Core runtime and scheduling types used by the Tracker.

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

    READY:
        Tracker is eligible to run when new data may exist.

    ACTIVE:
        An update cycle is currently in progress.

    RECOVERY:
        A prior retrieval failure implies required source data is
        presumed missing. The tracker will continue to attempt update
        cycles while the current window remains open. If the window
        closes before recovery completes, this is a fatal condition.

    DORMANT:
        Outside any active basho window; no runs will be attempted.
    """

    DORMANT = auto()
    READY = auto()
    RECOVERY = auto()
    ACTIVE = auto()


class UpdateResult(Enum):
    """
    Outcome of a single update cycle of the maintained data store.
    """

    SUCCESS = auto()
    NO_NEW_DATA = auto()
    RETRIEVAL_FAILED = auto()
    REBUILD_FAILED = auto()
    PUBLISH_FAILED = auto()
    LIVE_STORE_FAILED = auto()


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
    next_run_time: Optional[datetime] = None


@dataclass(frozen=True)
class BashoDayRef:
    """
    Reference to a specific day within a specific basho.

    A BashoDayRef is the canonical identifier for a unit of work in the
    tracker/downloader/parser pipeline.

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


@dataclass(frozen=True)
class RetrievalPlan:
    """
    Source artifacts required for one tracker update cycle.

    banzuke_dates:
        Basho dates for which the current-standings/banzuke page must exist.

    daily_results:
        Specific basho days for which daily Results pages must exist.
    """

    banzuke_dates: List[Date]
    daily_results: RequestedDateDays

from datetime import datetime, timedelta
import time

class RealClock:
    """
    Real wall-clock time source.
    """

    def now(self) -> datetime:
        return datetime.now()


class ScaledClock:
    """
    Simulated clock.

    Time starts at `simulated_start` and then advances according to
    `real_seconds_per_simulated_day`.

    Example:
        real_seconds_per_simulated_day = 20.0
    means one simulated day passes in twenty real seconds.
    """

    def __init__(
        self,
        simulated_start: datetime,
        real_seconds_per_simulated_day: float,
    ) -> None:
        if real_seconds_per_simulated_day <= 0.0:
            raise ValueError(
                "real_seconds_per_simulated_day must be > 0"
            )

        self._simulated_start = simulated_start
        self._real_start = time.monotonic()
        self._real_seconds_per_simulated_day = real_seconds_per_simulated_day

    def now(self) -> datetime:
        real_elapsed_seconds = time.monotonic() - self._real_start
        simulated_days = real_elapsed_seconds / self._real_seconds_per_simulated_day
        return self._simulated_start + timedelta(days=simulated_days)
