"""
Input loading contract for the Banzuke Change Report publisher.
"""

from src.infra.live_store.api import get_history
from src.infra.parser.parser2 import get_banzuke
from src.infra.parser.parser2_IntDate import IntDate
from .classes import PublicationRequest, PublicationSource
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.History import Date, History


def load_publication_source(request: PublicationRequest) -> PublicationSource:
    """
    Contract:
        request either names a current banzuke date, or leaves date selection
        to the standalone publisher's latest-date policy.  The selected date
        can be parsed and has a predecessor in project history.

        Returns the live history, separately parsed current banzuke date, and
        previous basho state needed by the standalone BCR calculation pipeline.

    Note:
        This is the standalone-new-banzuke workflow.  For a make_site2 build
        governed by a selected History use load_selected_history_source().
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


def load_selected_history_source(
    request: PublicationRequest,
    history: History,
) -> PublicationSource:
    """Build the BCR source whose current and previous banzukes are in History.

    Contract:
        history is the data instance selected for the containing site build and
        contains at least two basho states.  The final History entry is the
        current banzuke to report; its predecessor supplies comparison and
        previous-result context.

        Returns a PublicationSource wholly governed by that selected History.
        It does not read the live store or parse a later external banzuke.
    """

    dates = sorted(history.keys())
    if len(dates) < 2:
        raise ValueError("Banzuke Changes requires at least two basho in History")

    current_date = dates[-1]
    previous_date = dates[-2]
    current_basho = history(current_date)

    return PublicationSource(
        request=request,
        history=history,
        current_date=current_date,
        current_banzuke=current_basho.banzuke,
        previous_date=previous_date,
        previous_basho=history(previous_date),
    )


def resolve_current_date(history: History, requested_date: Date | None) -> Date:
    """
    Contract:
        history is non-empty.  requested_date is either None or the requested
        current banzuke date.

        Returns the current banzuke date for the standalone publisher run.  If
        no date is requested, the standalone BCR date is the next basho after
        the latest completed basho in History.
    """

    if requested_date is not None:
        return requested_date

    return next_basho_date(sorted(history.keys())[-1])


def next_basho_date(date: Date) -> Date:
    """
    Contract:
        date is a basho date.

        Returns the following basho date.
    """

    if int(date.month) == 11:
        return IntDate(int(date.year) + 1, 1)

    return IntDate(int(date.year), int(date.month) + 2)


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
