"""
Tracker scheduling logic.

This module contains the pure time- and calendar-based logic used by the
tracker.

It is responsible for:

1. Identifying the relevant basho for a given datetime
2. Constructing the corresponding scheduling window
3. Deriving the tracker run state from that window
4. Computing the next scheduled run time
5. Deciding whether new data may exist now and a run should be attempted

The scheduling model is inherited from the existing tracker design:

- bashos occur in odd-numbered months
- a basho starts on the second Sunday of its month
- the tracker becomes active a configurable number of days before basho
- the tracker may run once per day, at or after the configured trigger hour

This module does not inspect the repository and does not perform I/O.
"""

import calendar
from datetime import datetime, timedelta
from typing import Optional

from infra.tracker.config import TrackerConfig
from infra.tracker.types import BashoWindow, RunState


def second_sunday(year: int, month: int, hour: int = 8) -> datetime:
    """
    Return the datetime of the second Sunday in the given month.

    The default hour is 08:00, matching the existing tracker logic.
    """
    cal = calendar.monthcalendar(year, month)
    sundays = [week[6] for week in cal if week[6] != 0]
    day = sundays[1]
    return datetime(year, month, day, hour, 0, 0)


def add_months(year: int, month: int, months_to_add: int) -> tuple[int, int]:
    """
    Add a number of months to a year/month pair.
    """
    raw_month = month + months_to_add
    new_year = year + (raw_month - 1) // 12
    new_month = ((raw_month - 1) % 12) + 1
    return new_year, new_month


def get_basho_window(now: datetime, config: TrackerConfig) -> BashoWindow:
    """
    Return the relevant basho window for the given datetime.

    The relevant basho is:
    - the current odd-month basho if we are before or during it
    - otherwise the next basho
    """
    year = now.year
    month = now.month

    if month % 2 == 1:
        basho_start = second_sunday(year, month)
        basho_end = basho_start + timedelta(days=config.basho_length_days)

        if now > basho_end:
            year, month = add_months(year, month, 2)
            basho_start = second_sunday(year, month)
            basho_end = basho_start + timedelta(days=config.basho_length_days)
    else:
        year, month = add_months(year, month, 1)
        basho_start = second_sunday(year, month)
        basho_end = basho_start + timedelta(days=config.basho_length_days)

    pre_basho_start = basho_start - timedelta(days=config.pre_basho_days)

    return BashoWindow(
        pre_basho_start=pre_basho_start,
        basho_start=basho_start,
        basho_end=basho_end,
        trigger_hour=config.trigger_hour,
    )


def within_window(now: datetime, window: BashoWindow) -> bool:
    """
    Return True iff now is within the relevant scheduling window.
    """
    return window.pre_basho_start <= now <= window.basho_end


def state_for(now: datetime, window: BashoWindow) -> RunState:
    """
    Derive the tracker run state from the current time and basho window.

    ACTIVE is not produced here; it is a transient execution state set by
    the main loop when work actually begins.
    """
    if within_window(now, window):
        return RunState.READY
    return RunState.DORMANT


def next_run_time(
    now: datetime,
    window: BashoWindow,
    config: TrackerConfig,
) -> Optional[datetime]:
    """
    Return the next scheduled run time after now, or None if there is none
    within the current window.
    """
    day = window.pre_basho_start
    for _ in range(config.pre_basho_days):
        candidate = day.replace(
            hour=window.trigger_hour,
            minute=0,
            second=0,
            microsecond=0,
        )
        if candidate > now:
            return candidate
        day += timedelta(days=1)

    day = window.basho_start
    for _ in range(config.basho_length_days):
        candidate = day.replace(
            hour=window.trigger_hour,
            minute=0,
            second=0,
            microsecond=0,
        )
        if candidate > now:
            return candidate
        day += timedelta(days=1)

    return None


def time_when_new_data_may_exist(
    now: datetime,
    state: RunState,
    window: BashoWindow,
    ledger,
) -> bool:
    """
    Return True iff the tracker should attempt an update now.

    Conditions:
    - the tracker is in READY state
    - the current time is at or after the trigger hour for today
    - there has not yet been a successful run today
    """
    if state != RunState.READY:
        return False

    trigger_time = now.replace(
        hour=window.trigger_hour,
        minute=0,
        second=0,
        microsecond=0,
    )

    if now < trigger_time:
        return False

    if ledger.has_success_for(now.date()):
        return False

    return True
