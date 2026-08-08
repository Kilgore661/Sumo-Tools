"""Persistent Basic Elo producer fixed at q=400 and k=35 by Proposal 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from src.sumo_core.BasicPrimitives import RikId

from .bouts import Contest
from .definition import Proposal1Definition


@dataclass
class EloState:
    """Persistent ratings and rated-bout experience keyed by stable RikId."""

    ratings: dict[RikId, float] = field(default_factory=dict)
    rated_bout_counts: dict[RikId, int] = field(default_factory=dict)


@dataclass(frozen=True)
class PreBoutPrediction:
    """Basic Elo information produced before the bout result is revealed."""

    contest: Contest
    rating_a_before: float
    rating_b_before: float
    rated_bouts_a_before: int
    rated_bouts_b_before: int
    probability_a_wins: float


@dataclass(frozen=True)
class RatingTransition:
    """The result-dependent state transition following one prediction."""

    prediction: PreBoutPrediction
    a_won: bool
    delta_a: float
    rating_a_after: float
    rating_b_after: float


class BasicEloProducer:
    """Predict and update one persistent Basic Elo registry."""

    def __init__(
        self,
        definition: Proposal1Definition,
        initial_ratings: Mapping[RikId, float] | None = None,
    ) -> None:
        self.definition = definition
        self.initial_ratings = initial_ratings
        self.state = EloState()

    def predict(self, contest: Contest) -> PreBoutPrediction:
        """Produce a forecast from state containing no current result."""

        rikishi_a = contest.rikishi_a
        rikishi_b = contest.rikishi_b
        if rikishi_a not in self.state.ratings:
            self.state.ratings[rikishi_a] = self._initial_rating(rikishi_a)
            self.state.rated_bout_counts[rikishi_a] = 0
        if rikishi_b not in self.state.ratings:
            self.state.ratings[rikishi_b] = self._initial_rating(rikishi_b)
            self.state.rated_bout_counts[rikishi_b] = 0

        rating_a = self.state.ratings[rikishi_a]
        rating_b = self.state.ratings[rikishi_b]
        probability = 1.0 / (
            1.0 + 10.0 ** ((rating_b - rating_a) / self.definition.q)
        )
        return PreBoutPrediction(
            contest=contest,
            rating_a_before=rating_a,
            rating_b_before=rating_b,
            rated_bouts_a_before=self.state.rated_bout_counts[rikishi_a],
            rated_bouts_b_before=self.state.rated_bout_counts[rikishi_b],
            probability_a_wins=probability,
        )

    def update(
        self,
        prediction: PreBoutPrediction,
        *,
        a_won: bool,
    ) -> RatingTransition:
        """Reveal one result and apply the fixed symmetric Elo update."""

        actual_a = float(a_won)
        delta_a = self.definition.k * (
            actual_a - prediction.probability_a_wins
        )
        rating_a_after = prediction.rating_a_before + delta_a
        rating_b_after = prediction.rating_b_before - delta_a
        rikishi_a = prediction.contest.rikishi_a
        rikishi_b = prediction.contest.rikishi_b
        self.state.ratings[rikishi_a] = rating_a_after
        self.state.ratings[rikishi_b] = rating_b_after
        self.state.rated_bout_counts[rikishi_a] += 1
        self.state.rated_bout_counts[rikishi_b] += 1
        return RatingTransition(
            prediction=prediction,
            a_won=a_won,
            delta_a=delta_a,
            rating_a_after=rating_a_after,
            rating_b_after=rating_b_after,
        )

    def _initial_rating(self, rikishi_id: RikId) -> float:
        if self.initial_ratings is None:
            return self.definition.initial_rating
        return self.initial_ratings[rikishi_id]
