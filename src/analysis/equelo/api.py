"""Public Equelo rating API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from src.analysis.equelo.fixed_v2.api import (
    DayEndRatings,
    EntrantInitialRatings,
    load_day_end_ratings,
    load_entrant_initial_ratings,
)
from src.sumo_core.BasicEnums import Annotation, Division, Side
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


class EqueloTiming(Enum):
    BEFORE = auto()
    AFTER = auto()


@dataclass(frozen=True)
class EntrantRatingDomain:
    entrant_initial_ratings: EntrantInitialRatings

    @classmethod
    def from_ratings(
        cls,
        entrant_initial_ratings: EntrantInitialRatings,
    ) -> "EntrantRatingDomain":
        return cls(entrant_initial_ratings=entrant_initial_ratings)

    def rating_for(self, chii: Chii) -> float | None:
        if no_rating(chii):
            return None

        ordinal = annotation_free_chii(chii).ordinal()
        return self.entrant_initial_ratings[str(ordinal)]


@dataclass(frozen=True)
class EqueloLookup:
    """Cached fixed_v2 Equelo lookup for one selected History."""

    history: History
    before_ratings: dict[Date, dict[RikId, float | None]]
    after_ratings: dict[Date, dict[RikId, float | None]]

    @classmethod
    def load(cls, history: History) -> "EqueloLookup":
        return cls.build(
            history=history,
            day_end_ratings=load_day_end_ratings(),
            entrant_initial_ratings=load_entrant_initial_ratings(),
        )

    @classmethod
    def build(
        cls,
        *,
        history: History,
        day_end_ratings: DayEndRatings,
        entrant_initial_ratings: EntrantInitialRatings,
    ) -> "EqueloLookup":
        entrant_rating_domain = EntrantRatingDomain.from_ratings(
            entrant_initial_ratings
        )
        before_ratings: dict[Date, dict[RikId, float | None]] = {}
        after_ratings: dict[Date, dict[RikId, float | None]] = {}
        last_known: dict[RikId, float] = {}

        for date in sorted(history.keys()):
            basho = history(date)
            before_ratings[date] = {
                rikid: rating_before(
                    rikid=rikid,
                    chii=basho.banzuke.get_chii(rikid),
                    last_known=last_known,
                    entrant_rating_domain=entrant_rating_domain,
                )
                for rikid in basho.banzuke.riks
            }
            after_ratings[date] = ratings_after_basho(
                date=date,
                history=history,
                before_ratings=before_ratings[date],
                day_end_ratings=day_end_ratings,
            )
            last_known.update(
                {
                    rikid: rating
                    for rikid, rating in after_ratings[date].items()
                    if rating is not None
                }
            )

        return cls(
            history=history,
            before_ratings=before_ratings,
            after_ratings=after_ratings,
        )

    def get_equelo(
        self,
        rikid: RikId,
        date: Date,
        when: EqueloTiming = EqueloTiming.AFTER,
    ) -> float | None:
        if when == EqueloTiming.BEFORE:
            return self.before_ratings[date][rikid]
        if when == EqueloTiming.AFTER:
            return self.after_ratings[date][rikid]
        raise ValueError(f"Unsupported EqueloTiming: {when!r}")


_LOOKUPS_BY_HISTORY: dict[int, EqueloLookup] = {}


def get_equelo(
    rikid: RikId,
    date: Date,
    h: History,
    when: EqueloTiming = EqueloTiming.AFTER,
) -> float | None:
    """Return the fixed_v2 Equelo rating for a represented rikishi."""

    key = id(h)
    if key not in _LOOKUPS_BY_HISTORY:
        _LOOKUPS_BY_HISTORY[key] = EqueloLookup.load(h)
    return _LOOKUPS_BY_HISTORY[key].get_equelo(rikid=rikid, date=date, when=when)


def rating_before(
    *,
    rikid: RikId,
    chii: Chii,
    last_known: dict[RikId, float],
    entrant_rating_domain: EntrantRatingDomain,
) -> float | None:
    if rikid in last_known:
        return last_known[rikid]
    return entrant_rating_domain.rating_for(chii)


def ratings_after_basho(
    *,
    date: Date,
    history: History,
    before_ratings: dict[RikId, float | None],
    day_end_ratings: DayEndRatings,
) -> dict[RikId, float | None]:
    basho = history(date)
    last_day = basho.summary.last_defined()
    persisted = (
        day_end_ratings.get(str(date), {}).get(str(int(last_day)), {})
        if last_day is not None
        else {}
    )
    result: dict[RikId, float | None] = {}
    for rikid in basho.banzuke.riks:
        key = str(int(rikid))
        result[rikid] = float(persisted[key]) if key in persisted else before_ratings[rikid]
    return result


def annotation_free_chii(chii: Chii) -> Chii:
    return Chii(
        level=chii.level,
        number=chii.number,
        side=chii.side,
        ann=Annotation.EMPTY,
    )


def no_rating(chii: Chii) -> bool:
    """Rikishi with these chii never appear in SumoDB *bout* data. See validate.py."""

    chii = annotation_free_chii(chii)

    if chii.level == Division.MAKUSHITA and 61 <= chii.number <= 101:
        return True

    if chii.level == Division.SANDANME:
        if chii.number == 101 and chii.side == Side.WEST:
            return True
        if 102 <= chii.number <= 119:
            return True
        if chii.number == 120 and chii.side == Side.EAST:
            return True

    return False
