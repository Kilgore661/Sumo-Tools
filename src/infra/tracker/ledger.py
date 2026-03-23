"""
Tracker successful-run ledger.

This module records which dates have already had a successful tracker run.

In the current draft implementation the ledger is in-memory only. It is
therefore suitable for exercising tracker logic, but not yet for surviving
process restart.

This module defines:
    - InMemoryLedger: a minimal ledger for successful run dates

The ledger contract is:

    has_success_for(run_date: date) -> bool
    record_success_for(run_date: date) -> None
"""

from datetime import date


class InMemoryLedger:
    """
    Minimal in-memory ledger of successful run dates.
    """

    def __init__(self) -> None:
        self._successful_dates: set[date] = set()

    def has_success_for(self, run_date: date) -> bool:
        """
        Return True iff the given date already has a recorded successful run.
        """
        return run_date in self._successful_dates

    def record_success_for(self, run_date: date) -> None:
        """
        Record a successful run for the given date.
        """
        print(f"[ledger] recording successful run for {run_date.isoformat()}")
        self._successful_dates.add(run_date)
