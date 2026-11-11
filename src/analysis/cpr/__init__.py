"""Cumulative Performance Rating (CPR) analysis."""

from .model import (
    CPRMetrics,
    CPRRow,
    calculate_metrics,
    cumulative_rows,
    remove_repetitions,
)

__all__ = (
    "CPRMetrics",
    "CPRRow",
    "calculate_metrics",
    "cumulative_rows",
    "remove_repetitions",
)
