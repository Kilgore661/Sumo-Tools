"""
Input loading contract for the Banzuke Change Report publisher.
"""

from src.infra.live_store.api import get_history
from src.infra.parser.parser2 import get_banzuke
from src.analysis.news.classes import PublicationRequest, PublicationSource
from src.sumo_core.Banzuke import Banzuke
from src.sumo_core.History import Date, History


def load_publication_source(request: PublicationRequest) -> PublicationSource:
    """
    Contract:
        request names a current banzuke date that can be parsed and has a
        predecessor in project history.

        Returns the live history, current banzuke, previous banzuke date, and
        previous basho state needed by the BCR calculation pipeline.
    """

    history = get_history()
    current_banzuke = load_current_banzuke(request.current_date)
    previous_date = resolve_previous_date(history, request.current_date)

    return PublicationSource(
        request=request,
        history=history,
        current_banzuke=current_banzuke,
        previous_date=previous_date,
        previous_basho=history(previous_date),
    )


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
