"""
Tracker update cycle.

This module contains the orchestration of a single tracker update attempt.

An update cycle is:

    scrape -> parse -> confirm canonical zip written

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

The current version is intentionally minimal. Scraper, parser, and zip
confirmation are supplied by injected callables so that tracker control flow
can be developed before the concrete implementations are written.
"""

from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from infra.tracker.types import UpdateResult


_scraper: Optional[Callable[[datetime], bool]] = None
_parser: Optional[Callable[[datetime], str]] = None
_zip_probe: Optional[Callable[[], Optional[Path]]] = None


def set_scraper(scraper: Callable[[datetime], bool]) -> None:
    """
    Set the scraper implementation.

    Contract:
        scraper(now) -> bool

    Returns True iff scraping succeeded.
    """
    global _scraper
    _scraper = scraper


def set_parser(parser: Callable[[datetime], str]) -> None:
    """
    Set the parser implementation.

    Contract:
        parser(now) -> str

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


def run_update_cycle(now: datetime) -> UpdateResult:
    """
    Execute one tracker update cycle.

    The cycle is:

        1. run scraper
        2. run parser
        3. confirm that a canonical zip exists

    Returns:
        UpdateResult.SUCCESS
        UpdateResult.SCRAPE_FAILED
        UpdateResult.NO_NEW_DATA
        UpdateResult.PARSER_FATAL_ERROR
    """
    scrape_result = _scrape(now)
    if not scrape_result:
        return UpdateResult.SCRAPE_FAILED

    parse_result = _parse(now)
    if parse_result == "provisional":
        return UpdateResult.NO_NEW_DATA

    if parse_result == "fatal":
        return UpdateResult.PARSER_FATAL_ERROR

    latest_zip = _latest_zip()
    if latest_zip is None:
        return UpdateResult.PARSER_FATAL_ERROR

    return UpdateResult.SUCCESS


def _scrape(now: datetime) -> bool:
    """
    Run the configured scraper.
    """
    if _scraper is None:
        raise RuntimeError("No scraper has been configured")
    return _scraper(now)


def _parse(now: datetime) -> str:
    """
    Run the configured parser.
    """
    if _parser is None:
        raise RuntimeError("No parser has been configured")
    return _parser(now)


def _latest_zip() -> Optional[Path]:
    """
    Return the latest canonical zip path.
    """
    if _zip_probe is None:
        raise RuntimeError("No zip probe has been configured")
    return _zip_probe()
