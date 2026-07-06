"""
Input loading contract for the Banzuke Change Report publisher.
"""

from src.infra.new_banzuke.api import load_new_banzuke
from src.infra.live_store.api import get_history
from .classes import PublicationRequest, PublicationSource
from src.sumo_core.History import Date, History


def load_publication_source(request: PublicationRequest) -> PublicationSource:
    """
    Contract:
        request either names a current banzuke date, or leaves date selection
        to the latest-date policy.  The selected date can be parsed and has a
        predecessor in project history.

        Returns the live history, current banzuke, previous banzuke date, and
        previous basho state needed by the BCR calculation pipeline.
    """

    new_banzuke = load_new_banzuke()
    history = get_history()
    current_date = resolve_current_date(request.requested_date, new_banzuke.date)
    previous_date = resolve_previous_date(history, current_date)

    return PublicationSource(
        request=request,
        history=history,
        current_date=current_date,
        current_banzuke=new_banzuke.to_banzuke(),
        previous_date=previous_date,
        previous_basho=history(previous_date),
    )


def resolve_current_date(requested_date: Date | None, new_banzuke_date: Date) -> Date:
    """
    Return the requested current date when it names the New Banzuke date.
    """

    if requested_date is not None:
        if date_key(requested_date) != date_key(new_banzuke_date):
            raise ValueError(
                f"Requested BCR date {requested_date} does not match "
                f"New Banzuke date {new_banzuke_date}"
            )
        return requested_date

    return new_banzuke_date


def date_key(date: Date) -> tuple[int, int]:
    """Return the value identity of a basho date."""
    return int(date.year), int(date.month)


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
