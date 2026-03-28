"""
Tracker planning logic.

This module determines the ordered list of requested BashoDayRefs
for a tracker update cycle.

Current policy (deliberately simple):

- ignore ledger coverage information for now
- determine the latest basho day for which results should have been published
- request every BashoDayRef from the epoch up to that point

This gives a complete, deterministic request list and keeps the contract
clear while the tracker/parser/scraper boundaries are being established.

Later versions may use the ledger and/or canonical state to reduce this to
only the missing suffix or isolated missing days.
"""

from datetime import datetime, timedelta

from infra.tracker.config import TrackerConfig
from infra.tracker.ledger import InMemoryLedger
from infra.tracker.schedule import add_months, second_sunday
from sumo_core.BasicPrimitives import Day, Month, Year
from sumo_core.History import Date
from .types import BashoDayRef, RequestedDateDays

EPOCH = Date(Year(1958), Month(1))


def get_requested_date_days(
    now: datetime,
    ledger: InMemoryLedger,
    config: TrackerConfig,
) -> RequestedDateDays:
    """
    Return the ordered list of requested BashoDayRefs that should
    exist as of `now`.

    Parameters
    ----------
    now:
        Current real-world time.
    ledger:
        Present for contract stability. Not yet used by this draft planner.
    config:
        Tracker configuration. Currently used for publication-time modelling.

    Returns
    -------
    list[BashoDayRef]
        Chronologically ordered requested BashoDayRefs.
    """
    _ = ledger  # Reserved for future coverage-aware planning.
    # The planner is deliberately coverage-blind: it returns the full set of
    # BashoDayRefs that should exist as of `now`, from the epoch up to the
    # latest expected day.
    #
    # A possible future refinement is to make the planner coverage-aware,
    # using a ledger or similar record to return only missing data
    # (e.g. a suffix or isolated gaps) rather than the full prefix.
    #
    # This is an optimisation only. Correctness does not depend on it,
    # because the downloader already handles existing files efficiently.

    latest_ref = _latest_published_date_day(now, config)
    return _enumerate_from_epoch_to(latest_ref.date, latest_ref.day)


def _latest_published_date_day(
    now: datetime,
    config: TrackerConfig,
) -> BashoDayRef:
    """
    Return the latest BashoDayRef for which results should have been
    published as of `now`.

    Rules used here:

    - bashos are in odd months
    - day 1 begins on the second Sunday of the basho month
    - results for basho day N are published at config.trigger_hour on the
      calendar day corresponding to basho day N
    - if no results for the current/most-recent basho should yet exist,
      the answer is day 15 of the previous basho
    """
    current_year, current_month = _most_recent_basho_year_month(now)
    current_start = second_sunday(current_year, current_month)

    published_day = _last_published_day_in_basho(now, current_start, config)

    if published_day is not None:
        return BashoDayRef(
            Date(Year(current_year), Month(current_month)),
            published_day,
        )

    previous_year, previous_month = add_months(current_year, current_month, -2)
    return BashoDayRef(
        Date(Year(previous_year), Month(previous_month)),
        Day(15),
    )


def _most_recent_basho_year_month(now: datetime) -> tuple[int, int]:
    """
    Return the year/month of the current odd-month basho if `now` is in an
    odd month, otherwise the immediately preceding odd month.
    """
    if now.month % 2 == 1:
        return now.year, now.month
    return add_months(now.year, now.month, -1)


def _last_published_day_in_basho(
    now: datetime,
    basho_start: datetime,
    config: TrackerConfig,
) -> Day | None:
    """
    Return the last day whose results should have been published for the
    basho that starts at `basho_start`, or None if day 1 results should not
    yet exist.
    """
    for day_number in range(config.basho_length_days, 0, -1):
        publication_time = _publication_time_for_day(
            basho_start,
            day_number,
            config,
        )
        if now >= publication_time:
            return Day(day_number)

    return None


def _publication_time_for_day(
    basho_start: datetime,
    day_number: int,
    config: TrackerConfig,
) -> datetime:
    """
    Return the publication datetime for the given basho day.

    This uses the tracker contract that results for each day are available
    at `trigger_hour` UK time.
    """
    calendar_day = basho_start + timedelta(days=day_number - 1)
    return calendar_day.replace(
        hour=config.trigger_hour,
        minute=0,
        second=0,
        microsecond=0,
    )


def _enumerate_from_epoch_to(
    last_date: Date,
    last_day: Day,
) -> RequestedDateDays:
    """
    Enumerate all requested BashoDayRefs from the epoch through
    (last_date, last_day), inclusive, in chronological order.
    """
    requested: RequestedDateDays = []

    year = int(EPOCH.year)
    month = int(EPOCH.month)

    while True:
        date = Date(Year(year), Month(month))
        max_day = int(last_day) if date == last_date else 15

        for day_number in range(1, max_day + 1):
            requested.append(BashoDayRef(date, Day(day_number)))

        if date == last_date:
            break

        year, month = add_months(year, month, 2)

    return requested
