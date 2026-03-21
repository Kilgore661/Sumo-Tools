"""
Summary aggregate for sumo history.

Represents the recorded summary of a basho.

A Summary consists of:
- a partial function from Day to DailyResults
- a partial function from RikId to Performance

The established structural invariant is that, if any days are recorded,
they must begin at day 1 and be contiguous with no gaps.
"""

from __future__ import annotations

from Day import Day
from DailyResults import DailyResults
from Performances import Performances


class Summary(dict):
    def __init__(self, daily_results_dict, performances=None):
        super().__init__(daily_results_dict)
        self.performances = performances if performances is not None else Performances()

        days = sorted(self.keys())
        if days and days[0] != 1:
            raise ValueError(
                f"Tournament must start with day 1, found: {days[0]}"
            )

        for i in range(1, len(days)):
            if days[i] != days[i - 1] + 1:
                raise ValueError(
                    f"Gap in daily records between days {days[i - 1]} and {days[i]}"
                )

    def __call__(self, day: Day):
        """
        Return the DailyResults for the given day, or None if undefined.
        """
        return self.get(day)

    def last_defined(self):
        """
        Return the last day with defined results, or None if the summary is empty.
        """
        return Day(max(self.keys())) if self else None
