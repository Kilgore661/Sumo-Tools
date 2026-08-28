"""Chronological whole-population replay for the Equelo2 baseline."""

from __future__ import annotations

from collections.abc import Callable

from src.sumo_core.BashoState import BashoState
from src.sumo_core.History import Date

from .model import (
    BashoReplay,
    BashoSelection,
    ForecastRow,
    PopulationAdjustment,
    ReplayState,
)
from .prior import CompletedPrior


class ReplayEngine:
    """Replay one rating world while retaining inactive ratings as archive state."""

    def __init__(
        self,
        *,
        name: str,
        prior: CompletedPrior,
        divisional_k: Callable[[int], float],
        target_mean: float,
        q: float = 400.0,
        persist_inactive_ratings: bool = True,
    ) -> None:
        self.name = name
        self.prior = prior
        self.divisional_k = divisional_k
        self.target_mean = target_mean
        self.q = q
        self.persist_inactive_ratings = persist_inactive_ratings
        self.state = ReplayState()

    def process_basho(
        self,
        date: Date,
        basho: BashoState,
        selection: BashoSelection,
    ) -> BashoReplay:
        active = set(basho.banzuke.riks)
        if not active:
            raise ValueError(f"Cannot replay empty banzuke at {date}")
        for bout in selection.bouts:
            if bout.rikishi_a not in active or bout.rikishi_b not in active:
                raise AssertionError(f"Selected off-banzuke bout at {date}")

        departing = self.state.previous_active - active
        if not self.persist_inactive_ratings:
            for rikishi in departing:
                self.state.ratings.pop(rikishi, None)
                self.state.initialisation_sources.pop(rikishi, None)
        known_before = set(self.state.ratings)
        new_rikishi = active - known_before
        returning = (active & known_before) - self.state.previous_active
        for rikishi in sorted(new_rikishi):
            chii = basho.banzuke.rikchii[rikishi]
            rating, source = self.prior.rating_for(chii)
            self.state.ratings[rikishi] = rating
            self.state.rated_bouts.setdefault(rikishi, 0)
            self.state.initialisation_sources[rikishi] = source

        raw_start_mean = _mean(self.state.ratings, active)
        start_adjustment = _shift_to_target(
            self.state.ratings, active, self.target_mean
        )
        start_ratings = {rikishi: self.state.ratings[rikishi] for rikishi in active}
        counts_before = {
            rikishi: self.state.rated_bouts[rikishi] for rikishi in active
        }

        forecasts: list[ForecastRow] = []
        for bout in selection.bouts:
            a = bout.rikishi_a
            b = bout.rikishi_b
            rating_a = self.state.ratings[a]
            rating_b = self.state.ratings[b]
            probability = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / self.q))
            actual = float(bout.a_won)
            residual = actual - probability
            k_a = self.divisional_k(bout.chii_a.ordinal())
            k_b = self.divisional_k(bout.chii_b.ordinal())
            delta_a = k_a * residual
            delta_b = -k_b * residual
            forecasts.append(
                ForecastRow(
                    run=self.name,
                    date=date,
                    day=bout.day,
                    rikishi_a=a,
                    rikishi_b=b,
                    chii_a=bout.chii_a,
                    chii_b=bout.chii_b,
                    rating_a_before=rating_a,
                    rating_b_before=rating_b,
                    rated_bouts_a_before=self.state.rated_bouts[a],
                    rated_bouts_b_before=self.state.rated_bouts[b],
                    probability_a_wins=probability,
                    a_won=bout.a_won,
                    k_a=k_a,
                    k_b=k_b,
                    delta_a=delta_a,
                    delta_b=delta_b,
                    rating_a_after=rating_a + delta_a,
                    rating_b_after=rating_b + delta_b,
                )
            )
            self.state.ratings[a] += delta_a
            self.state.ratings[b] += delta_b
            self.state.rated_bouts[a] += 1
            self.state.rated_bouts[b] += 1

        raw_end_mean = _mean(self.state.ratings, active)
        end_adjustment = _shift_to_target(
            self.state.ratings, active, self.target_mean
        )
        end_ratings = {rikishi: self.state.ratings[rikishi] for rikishi in active}
        counts_after = {
            rikishi: self.state.rated_bouts[rikishi] for rikishi in active
        }
        self.state.previous_active = active
        return BashoReplay(
            forecasts=tuple(forecasts),
            adjustment=PopulationAdjustment(
                run=self.name,
                date=date,
                active_count=len(active),
                new_rikishi_count=len(new_rikishi),
                returning_rikishi_count=len(returning),
                departing_rikishi_count=len(departing),
                target_mean=self.target_mean,
                raw_start_mean=raw_start_mean,
                start_adjustment=start_adjustment,
                adjusted_start_mean=_mean(start_ratings, active),
                raw_end_mean=raw_end_mean,
                end_adjustment=end_adjustment,
                adjusted_end_mean=_mean(end_ratings, active),
            ),
            start_ratings=start_ratings,
            end_ratings=end_ratings,
            rated_bouts_before=counts_before,
            rated_bouts_after=counts_after,
            initialisation_sources={
                rikishi: self.state.initialisation_sources[rikishi]
                for rikishi in active
            },
        )


def _shift_to_target(
    ratings: dict,
    active: set,
    target_mean: float,
) -> float:
    adjustment = target_mean - _mean(ratings, active)
    for rikishi in active:
        ratings[rikishi] += adjustment
    return adjustment


def _mean(ratings: dict, active: set) -> float:
    return sum(ratings[rikishi] for rikishi in active) / len(active)
