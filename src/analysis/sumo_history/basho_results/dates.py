"""Date helpers for Basho Results Browser producer outputs."""

from __future__ import annotations

from calendar import month_name

from src.sumo_core.History import Date, History


def represented_dates(history: History) -> tuple[Date, ...]:
    """Return dates with at least Day 1 results, sorted in chronological order."""

    return tuple(
        date
        for date in sorted(history.keys())
        if history(date).summary.last_defined() is not None
    )


def next_history_date(history: History, date: Date) -> Date | None:
    """Return the next known banzuke date after date, whether or not it has results."""

    later_dates = [candidate for candidate in sorted(history.keys()) if candidate > date]
    if not later_dates:
        return None
    return later_dates[0]


def previous_represented_date(dates: tuple[Date, ...], date: Date) -> Date | None:
    """Return the previous represented basho date before date."""

    previous_dates = [candidate for candidate in dates if candidate < date]
    if not previous_dates:
        return None
    return previous_dates[-1]


def status_for_date(history: History, represented: tuple[Date, ...], date: Date) -> str:
    """Return the static publication status for a represented basho date."""

    latest_day = int(history(date).summary.last_defined())
    if date != represented[-1]:
        next_date = next_history_date(history, date)
        if next_date == sorted(history.keys())[-1] and history(next_date).summary.last_defined() is None:
            return "post_banzuke_pre_basho"
        return "completed"

    if latest_day < 15:
        return "in_basho"

    if next_history_date(history, date) is None:
        return "post_basho_pre_banzuke"

    return "post_banzuke_pre_basho"


def payload_file_name(date: Date) -> str:
    return f"{int(date.year):04d}-{int(date.month):02d}.csv"


def basho_label(date: Date) -> str:
    return f"{month_name[int(date.month)]} {int(date.year)}"

