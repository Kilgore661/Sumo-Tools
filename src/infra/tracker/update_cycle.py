"""
Tracker update cycle.

This module orchestrates a single tracker update attempt.

An update cycle is:

    scrape requested (Date, Day) pairs
    -> parse requested (Date, Day) pairs
    -> confirm canonical zip written

The tracker uses the result of this cycle to decide whether to:
- record a successful run
- retry later
- do nothing
- terminate

This module defines:
    - run_update_cycle(): execute one update cycle
    - set_scraper(): inject scraper implementation
    - set_parser(): inject parser implementation
    - set_zip_probe(): inject canonical zip probe

Contract summary:

- The tracker owns planning. It supplies an ordered list of requested
  (Date, Day) pairs.
- The scraper owns acquisition. It fetches raw files for those requests.
- The parser owns construction/validation. It attempts to build canonical
  History from the fetched raw files.
"""

from pathlib import Path
from typing import Callable, List, Optional

from infra.tracker.types import UpdateResult
from sumo_core.BasicPrimitives import Day
from sumo_core.History import Date

RequestedDateDays = List[tuple[Date, Day]]

_scraper: Optional[Callable[[RequestedDateDays], bool]] = None
_parser: Optional[Callable[[RequestedDateDays], str]] = None
_zip_probe: Optional[Callable[[], Optional[Path]]] = None


def set_scraper(scraper: Callable[[RequestedDateDays], bool]) -> None:
    """
    Set the scraper implementation.

    Contract:
        scraper(requested_date_days) -> bool

    The ordered list `requested_date_days` is computed by the tracker.

    Returns True iff scraping succeeded for all requested (Date, Day) pairs.
    """
    global _scraper
    _scraper = scraper


def set_parser(parser: Callable[[RequestedDateDays], str]) -> None:
    """
    Set the parser implementation.

    Contract:
        parser(requested_date_days) -> str

    Expected return values:
        "success"       parser succeeded and wrote a new canonical zip
        "provisional"   parser found provisional / unusable data
        "fatal"         parser encountered a fatal error
    """
    global _parser
    _parser = parser


def set_zip_probe(zip_probe: Callable[[], Optional[Path]]) -> None:
    """
    Set the canonical zip probe implementation.

    Contract:
        zip_probe() -> Optional[Path]

    Returns the path of the most recently written canonical zip, or None if
    no such zip exists.
    """
    global _zip_probe
    _zip_probe = zip_probe


def run_update_cycle(requested_date_days: RequestedDateDays) -> UpdateResult:
    """
    Execute one tracker update cycle.

    The cycle is:

        1. if no requests exist, do nothing
        2. run scraper on the requested (Date, Day) pairs
        3. run parser on the requested (Date, Day) pairs
        4. confirm that a canonical zip exists

    Returns:
        UpdateResult.SUCCESS
        UpdateResult.SCRAPE_FAILED
        UpdateResult.NO_NEW_DATA
        UpdateResult.PARSER_FATAL_ERROR
    """
    if len(requested_date_days) == 0:
        return UpdateResult.NO_NEW_DATA

    scrape_result = _scrape(requested_date_days)
    if not scrape_result:
        return UpdateResult.SCRAPE_FAILED

    parse_result = _parse(requested_date_days)
    if parse_result == "provisional":
        return UpdateResult.NO_NEW_DATA

    if parse_result == "fatal":
        return UpdateResult.PARSER_FATAL_ERROR

    latest_zip = _latest_zip()
    if latest_zip is None:
        return UpdateResult.PARSER_FATAL_ERROR

    return UpdateResult.SUCCESS


def _scrape(requested_date_days: RequestedDateDays) -> bool:
    """
    Run the configured scraper.
    """
    if _scraper is None:
        raise RuntimeError("No scraper has been configured")
    return _scraper(requested_date_days)


def _parse(requested_date_days: RequestedDateDays) -> str:
    """
    Run the configured parser.
    """
    if _parser is None:
        raise RuntimeError("No parser has been configured")
    return _parser(requested_date_days)


def _latest_zip() -> Optional[Path]:
    """
    Return the latest canonical zip path.
    """
    if _zip_probe is None:
        raise RuntimeError("No zip probe has been configured")
    return _zip_probe()
