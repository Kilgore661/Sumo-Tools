"""Shared policies for derived serialized History artifacts."""

from __future__ import annotations

from src.sumo_core.History import History


POST_1988_START_YEAR = 1989


def history_from_year(history: History, start_year: int) -> History:
    """Return a date slice containing basho from ``start_year`` onward."""

    result = History()
    for date, basho in history.items():
        if int(date.year) >= start_year:
            result[date] = basho
    return result
