"""
Input loading contract for the Banzuke Change Report publisher.
"""

import re
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.parser.parser2 import get_banzuke
from src.infra.parser.parser2_IntDate import IntDate
from .classes import PublicationRequest, PublicationSource
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.History import Date, History


CURRENT_STANDINGS_ROOT = Path("files/output/current standings")
CURRENT_STANDINGS_FILE_RE = re.compile(r"^(\d{4}) (\d{2})\.html$")


def load_publication_source(request: PublicationRequest) -> PublicationSource:
    """
    Contract:
        request either names a current banzuke date, or leaves date selection
        to the latest-date policy.  The selected date can be parsed and has a
        predecessor in project history.

        Returns the live history, current banzuke, previous banzuke date, and
        previous basho state needed by the BCR calculation pipeline.
    """

    history = get_history()
    current_date = resolve_current_date(history, request.requested_date)
    current_banzuke = load_current_banzuke(current_date)
    previous_date = resolve_previous_date(history, current_date)

    return PublicationSource(
        request=request,
        history=history,
        current_date=current_date,
        current_banzuke=current_banzuke,
        previous_date=previous_date,
        previous_basho=history(previous_date),
    )


def resolve_current_date(history: History, requested_date: Date | None) -> Date:
    """
    Contract:
        history is non-empty.  requested_date is either None or the requested
        current banzuke date.

        Returns the current banzuke date for this publisher run.  If no date is
        requested, the current BCR date is the latest locally available
        current-standings/banzuke source file.
    """

    if requested_date is not None:
        return requested_date

    # This deliberately uses source-file availability as the current-banzuke
    # selector. It is a pragmatic deployment fix, not the ideal model boundary:
    # the same banzuke-calendar concepts also exist in tracker scheduling, and
    # should eventually be factored into a shared calendar/source-availability
    # model. For now, BCR is a source-publication product; the latest banzuke it
    # can honestly publish is the latest banzuke source file it actually has.
    _ = history
    return latest_available_banzuke_date()


def latest_available_banzuke_date(
    source_root: Path = CURRENT_STANDINGS_ROOT,
) -> Date:
    """
    Return the latest banzuke date represented by local source HTML files.
    """

    dates = sorted(
        IntDate(int(match.group(1)), int(match.group(2)))
        for path in source_root.glob("*.html")
        if (match := CURRENT_STANDINGS_FILE_RE.fullmatch(path.name)) is not None
    )

    if not dates:
        raise FileNotFoundError(f"No banzuke source files found in {source_root}")

    return dates[-1]


def load_current_banzuke(current_date: Date) -> Banzuke:
    """
    Contract:
        current_date names a banzuke that the parser can read.

        Returns the parsed current banzuke.
    """

    banzuke = get_banzuke(current_date)

    if banzuke is None:
        raise ValueError(f"No banzuke parsed for {current_date}")

    return banzuke


def resolve_previous_date(history: History, current_date: Date) -> Date:
    """
    Contract:
        history contains at least one basho before current_date.

        Returns the latest history date before current_date.
    """

    previous_dates = [date for date in sorted(history.keys()) if date < current_date]

    if not previous_dates:
        raise ValueError(f"No previous basho found before {current_date}")

    return previous_dates[-1]
