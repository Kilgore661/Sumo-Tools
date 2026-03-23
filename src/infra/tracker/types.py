from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional


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
    """
    DORMANT = auto()
    READY = auto()
    ACTIVE = auto()


class UpdateResult(Enum):
    """
    Outcome of a single update cycle.
    """
    SUCCESS = auto()
    SCRAPE_FAILED = auto()
    NO_NEW_DATA = auto()
    PARSER_FATAL_ERROR = auto()


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
