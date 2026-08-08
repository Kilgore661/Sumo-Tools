"""Run the single chronological Basic Elo pass and retain its forecast ledger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.sumo_core.BasicPrimitives import RikId

from .basic_elo import BasicEloProducer
from .bouts import BoutId, RatedBout
from .definition import Proposal1Definition


@dataclass(frozen=True)
class ForecastRecord:
    """Immutable evidence from one predict-then-update transition."""

    bout_id: BoutId
    rikishi_a: int
    rikishi_b: int
    rating_a_before: float
    rating_b_before: float
    rated_bouts_a_before: int
    rated_bouts_b_before: int
    probability_a_wins: float
    a_won: bool
    delta_a: float
    rating_a_after: float
    rating_b_after: float


def build_forecast_ledger(
    bouts: tuple[RatedBout, ...],
    definition: Proposal1Definition,
    initial_ratings: Mapping[RikId, float] | None = None,
) -> tuple[ForecastRecord, ...]:
    """Predict each bout, reveal its outcome, then update persistent ratings."""

    producer = BasicEloProducer(definition, initial_ratings)
    rows: list[ForecastRecord] = []
    for bout in bouts:
        prediction = producer.predict(bout.contest)
        transition = producer.update(prediction, a_won=bout.a_won)
        rows.append(
            ForecastRecord(
                bout_id=bout.contest.id,
                rikishi_a=int(bout.contest.rikishi_a),
                rikishi_b=int(bout.contest.rikishi_b),
                rating_a_before=prediction.rating_a_before,
                rating_b_before=prediction.rating_b_before,
                rated_bouts_a_before=prediction.rated_bouts_a_before,
                rated_bouts_b_before=prediction.rated_bouts_b_before,
                probability_a_wins=prediction.probability_a_wins,
                a_won=bout.a_won,
                delta_a=transition.delta_a,
                rating_a_after=transition.rating_a_after,
                rating_b_after=transition.rating_b_after,
            )
        )
    return tuple(rows)
