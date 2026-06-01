"""Kyujo continuity fallback for Basho Results Browser Equelo display.

This module is intentionally a local Basho Results Browser workaround. It does
not change fixed_v2 rating artefacts, the Oracle, or the simulator. It resolves
display ratings for rikishi who are present on the displayed banzuke but absent
from persisted day-end ratings.

See make_site2 Outstanding Issues: "BRB kyujo rating continuity".
"""

from dataclasses import dataclass

from src.analysis.sumo_history.basho_results.ratings import RatingLookup
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


@dataclass
class KyujoRatingContext:
    seen_on_banzuke: set[RikId]
    last_known_rating: dict[RikId, float]

    @classmethod
    def empty(cls) -> "KyujoRatingContext":
        return cls(seen_on_banzuke=set(), last_known_rating={})

    def copy(self) -> "KyujoRatingContext":
        return KyujoRatingContext(
            seen_on_banzuke=set(self.seen_on_banzuke),
            last_known_rating=dict(self.last_known_rating),
        )

    def observe_basho(
        self,
        *,
        history: History,
        ratings: RatingLookup,
        date: Date,
    ) -> None:
        basho = history(date)

        for rikishi_id in basho.banzuke.riks:
            self.seen_on_banzuke.add(rikishi_id)

        last_day = basho.summary.last_defined()
        if last_day is None:
            return

        day_ratings = (
            ratings.day_end_ratings
            .get(str(date), {})
            .get(str(int(last_day)), {})
        )

        for rikishi_id_text, rating in day_ratings.items():
            self.last_known_rating[RikId(int(rikishi_id_text))] = float(rating)


_CONTEXTS_BY_HISTORY_AND_RATINGS: dict[
    tuple[int, int, tuple[Date, ...]],
    dict[Date, KyujoRatingContext],
] = {}


def build_context_before(
    *,
    history: History,
    ratings: RatingLookup,
    dates: tuple[Date, ...],
    target_date: Date,
) -> KyujoRatingContext:
    contexts = _contexts_for_dates(history=history, ratings=ratings, dates=dates)
    return contexts[target_date].copy()


def resolve_display_start_rating(
    *,
    ratings: RatingLookup,
    rikishi_id: RikId,
    chii: Chii,
    context: KyujoRatingContext,
) -> float | None:
    if rikishi_id in context.seen_on_banzuke:
        return context.last_known_rating.get(rikishi_id)

    return ratings.entrant_rating(chii)


def resolve_display_end_rating(
    *,
    ratings: RatingLookup,
    history: History,
    date: Date,
    rikishi_id: RikId,
    chii: Chii,
    context: KyujoRatingContext,
) -> float | None:
    direct = ratings.end_rating(
        history=history,
        date=date,
        rikishi_id=rikishi_id,
    )
    if direct is not None:
        return direct

    return resolve_display_start_rating(
        ratings=ratings,
        rikishi_id=rikishi_id,
        chii=chii,
        context=context,
    )


def _contexts_for_dates(
    *,
    history: History,
    ratings: RatingLookup,
    dates: tuple[Date, ...],
) -> dict[Date, KyujoRatingContext]:
    key = (id(history), id(ratings), dates)
    if key not in _CONTEXTS_BY_HISTORY_AND_RATINGS:
        _CONTEXTS_BY_HISTORY_AND_RATINGS[key] = _build_contexts_for_dates(
            history=history,
            ratings=ratings,
            dates=dates,
        )
    return _CONTEXTS_BY_HISTORY_AND_RATINGS[key]


def _build_contexts_for_dates(
    *,
    history: History,
    ratings: RatingLookup,
    dates: tuple[Date, ...],
) -> dict[Date, KyujoRatingContext]:
    contexts: dict[Date, KyujoRatingContext] = {}
    context = KyujoRatingContext.empty()

    for date in dates:
        contexts[date] = context.copy()
        context.observe_basho(
            history=history,
            ratings=ratings,
            date=date,
        )

    return contexts
