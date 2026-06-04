"""Rating formatting helpers for Basho Results Browser."""

from __future__ import annotations


def format_rating(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.0f}"


def format_delta(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:+.0f}"
