"""
Tracker update-cycle orchestration.

This module coordinates one tracker update cycle.

Current implementation:

1. asks the scraper to ensure the required raw artifacts exist

Future versions will also:

2. ask the parser to construct / validate canonical History
3. check that the canonical zip was published

It returns an UpdateResult describing the outcome.

This module owns the concrete sequencing of tracker sub-steps.
It does not expose dependency-injection hooks because there is only one
scraper, one parser, and one zip probe in this system.
"""

from .types import RequestedDateDays, UpdateResult
from .scraper import scraper
#from .zip_probe import canonical_zip_exists
#from .parser import parse


def run_update_cycle(requested_date_days: RequestedDateDays) -> UpdateResult:
    """
    Run one update cycle for the requested BashoDayRefs.

    Current behaviour:
    - run the scraper for the requested BashoDayRefs
    - return SCRAPE_FAILED on scrape failure
    - return SUCCESS on scrape success

    Future versions will extend this with parser and persistence checks.
    """

    if not requested_date_days:
        return UpdateResult.NO_NEW_DATA

    print(
        f"[update_cycle] running update cycle for "
        f"{len(requested_date_days)} requested BashoDayRefs"
    )

    if not scrape(requested_date_days):
        print("[update_cycle] scrape failed")
        return UpdateResult.SCRAPE_FAILED

#    parse_result = parse(requested_date_days)
#
#    if parse_result == "fatal":
#        print("[update_cycle] parser reported fatal error")
#        return UpdateResult.PARSER_FATAL_ERROR
#
#    if parse_result == "provisional":
#        print("[update_cycle] parser produced no new canonical state")
#        return UpdateResult.NO_NEW_DATA
#
#    if parse_result != "success":
#        raise RuntimeError(f"Unexpected parser result: {parse_result!r}")
#
#    if not canonical_zip_exists():
#        print("[update_cycle] parser reported success but canonical zip is missing")
#        return UpdateResult.PARSER_FATAL_ERROR

    print("[update_cycle] update cycle succeeded")
    return UpdateResult.SUCCESS
