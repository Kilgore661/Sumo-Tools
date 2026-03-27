"""
Tracker update-cycle orchestration.

This module coordinates one tracker update cycle.

Current implementation:

1. asks the scraper to ensure the required raw artifacts exist
2. calls the analysis stage as a first-class required downstream step

Future versions will also:

3. ask the parser to construct / validate canonical History
4. refresh the cache from the canonical zip
5. verify the canonical zip was published

It returns an UpdateResult describing the outcome.

This module owns the concrete sequencing of tracker sub-steps.
It does not expose dependency-injection hooks because there is only one
scraper, one parser, one cache publisher, and one analysis entry point in
this system.
"""

from .types import RequestedDateDays, UpdateResult
from .scraper.scraper import scrape
from analysis.main import analyse
# from .zip_probe import canonical_zip_exists
# from .parser import parse
# from .cache import refresh_cache


def run_update_cycle(requested_date_days: RequestedDateDays) -> UpdateResult:
    """
    Run one update cycle for the requested BashoDayRefs.

    Current behaviour:
    - run the scraper for the requested BashoDayRefs
    - run the required downstream analysis stage
    - return SCRAPE_FAILED on scrape failure
    - return ANALYSIS_FAILED on analysis failure
    - return SUCCESS only if every required implemented stage succeeds

    Future versions will extend this with parser, cache, and persistence
    checks between scraping and analysis.
    """

    if not requested_date_days:
        return UpdateResult.NO_NEW_DATA

    print(f"[update_cycle] checking {len(requested_date_days)} previous results")

    if not scrape(requested_date_days):
        print("[update_cycle] scrape failed")
        return UpdateResult.SCRAPE_FAILED

    # parse_result = parse(requested_date_days)
    #
    # if parse_result == "fatal":
    #     print("[update_cycle] parser reported fatal error")
    #     return UpdateResult.PARSER_FATAL_ERROR
    #
    # if parse_result == "provisional":
    #     print("[update_cycle] parser produced no new canonical state")
    #     return UpdateResult.NO_NEW_DATA
    #
    # if parse_result != "success":
    #     raise RuntimeError(f"Unexpected parser result: {parse_result!r}")
    #
    # if not canonical_zip_exists():
    #     print("[update_cycle] parser reported success but canonical zip is missing")
    #     return UpdateResult.PARSER_FATAL_ERROR
    #
    # if not refresh_cache():
    #     print("[update_cycle] cache refresh failed")
    #     return UpdateResult.CACHE_FAILED

    if not analyse():
        print("[update_cycle] required analysis failed")
        return UpdateResult.ANALYSIS_FAILED

    print("[update_cycle] update cycle succeeded")
    return UpdateResult.SUCCESS
