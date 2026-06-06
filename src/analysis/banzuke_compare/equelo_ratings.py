"""
Equelo rating snapshot adapter for the Banzuke Change Report.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.analysis.equelo.api import EntrantRatingDomain
from src.analysis.equelo.fixed_v2.api import (
    load_day_end_ratings,
    load_entrant_initial_ratings,
)
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


@dataclass(frozen=True)
class EqueloSnapshot:
    """
    Contract:
        ratings contains the fixed_v2 day-end Equelo ratings for the latest
        completed basho before the requested banzuke date.  Rikishi absent
        from that snapshot are new entrants for rating purposes and receive
        the public fixed_v2 entry rating for their current chii.
    """

    date: Date
    day: int
    ratings: dict[RikId, float]
    entrant_rating_domain: EntrantRatingDomain

    def rating_for(self, rikishi_id: RikId, chii: Chii) -> float | None:
        """
        Contract:
            rikishi_id and chii identify a rikishi on the current banzuke.

            Returns the persisted day-end rating when present, otherwise the
            public fixed_v2 entry rating implied by chii.
        """

        if rikishi_id in self.ratings:
            return self.ratings[rikishi_id]

        return self.entrant_rating_domain.rating_for(chii)


def load_latest_equelo_snapshot_before(date: Date) -> EqueloSnapshot:
    """
    Contract:
        date is the banzuke date being published.

        Returns the latest fixed_v2 day-end rating snapshot whose basho date is
        earlier than date. Missing files and missing dates are contract
        violations and are allowed to fail noisily.
    """

    day_end_ratings = load_day_end_ratings()
    date_text = max(
        candidate
        for candidate in day_end_ratings
        if parse_date(candidate) < date
    )
    day_text = max(day_end_ratings[date_text], key=int)

    return EqueloSnapshot(
        date=parse_date(date_text),
        day=int(day_text),
        ratings={
            RikId(int(rikishi_id)): rating
            for rikishi_id, rating in day_end_ratings[date_text][day_text].items()
        },
        entrant_rating_domain=EntrantRatingDomain.from_ratings(
            load_entrant_initial_ratings()
        ),
    )


def parse_date(value: str) -> Date:
    """
    Contract:
        value is the fixed_v2 JSON date key, formatted as YYYY/MM.
    """

    year, month = value.split("/")
    return Date(Year(int(year)), Month(int(month)))
