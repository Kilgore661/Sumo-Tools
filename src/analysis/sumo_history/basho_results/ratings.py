"""fixed_v2 Equelo lookup helpers for Basho Results Browser."""

from __future__ import annotations

from dataclasses import dataclass

from src.analysis.equelo.fixed_v2.api import (
    DayEndRatings,
    EntrantInitialRatings,
    load_day_end_ratings,
    load_entrant_initial_ratings,
)
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class RatingLookup:
    day_end_ratings: DayEndRatings
    entrant_initial_ratings: EntrantInitialRatings

    @classmethod
    def load(cls) -> "RatingLookup":
        return cls(
            day_end_ratings=load_day_end_ratings(),
            entrant_initial_ratings=load_entrant_initial_ratings(),
        )

    def rating(self, date: Date, day: int, rikishi_id: RikId) -> float | None:
        return (
            self.day_end_ratings
            .get(str(date), {})
            .get(str(day), {})
            .get(str(int(rikishi_id)))
        )

    def end_rating(self, history: History, date: Date, rikishi_id: RikId) -> float | None:
        last_day = history(date).summary.last_defined()
        if last_day is None:
            return None
        return self.rating(date=date, day=int(last_day), rikishi_id=rikishi_id)

    def entrant_rating(self, chii: Chii) -> float | None:
        return self.entrant_initial_ratings.get(str(chii.ordinal()))

    def start_rating(
        self,
        *,
        history: History,
        previous_date: Date | None,
        rikishi_id: RikId,
        chii: Chii,
    ) -> float | None:
        if previous_date is not None:
            previous_rating = self.end_rating(
                history=history,
                date=previous_date,
                rikishi_id=rikishi_id,
            )
            if previous_rating is not None:
                return previous_rating

        return self.entrant_rating(chii)


def format_rating(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.0f}"


def format_delta(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:+.0f}"

