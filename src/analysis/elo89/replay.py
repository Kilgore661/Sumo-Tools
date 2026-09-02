"""Exact post-1988 Elo-89 replay with production observations."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
import math

from src.analysis.elo_model_selection.model import AdoptedPrior
from src.analysis.prediction.bouts import RatedBout, select_rated_bouts
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .model import BashoAdjustment, Elo89Run, Forecast


Q = 400.0


@dataclass(slots=True)
class _State:
    ratings: dict[RikId, float] = field(default_factory=dict)
    counts: dict[RikId, int] = field(default_factory=dict)
    sources: dict[RikId, str] = field(default_factory=dict)


def replay_elo89(
    *,
    history: History,
    start_date: Date,
    end_date: Date,
    prior: AdoptedPrior,
    divisional_k: Callable[[int], float],
    q: float = Q,
) -> Elo89Run:
    """Replay the accepted Elo-89 model and retain publication observations."""

    if not math.isfinite(q) or q <= 0:
        raise ValueError(f"q must be a positive finite number, got {q!r}")
    selection = select_rated_bouts(
        history,
        start_date=start_date,
        end_date=end_date,
    )
    bouts_by_date_and_day: dict[Date, dict[Day, list[RatedBout]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for bout in selection.bouts:
        bouts_by_date_and_day[bout.contest.id.date][bout.contest.id.day].append(bout)

    dates = sorted(date for date in history if start_date <= date <= end_date)
    if not dates:
        raise ValueError("The Elo-89 interval contains no represented basho")

    state = _State()
    previous_active: set[RikId] = set()
    target_mean: float | None = None
    starts = {}
    daily = {}
    ends = {}
    forecasts: list[Forecast] = []
    adjustments: list[BashoAdjustment] = []

    for date in dates:
        basho = history[date]
        by_day = bouts_by_date_and_day.get(date, {})
        active = set(basho.banzuke.riks)
        for bouts in by_day.values():
            for bout in bouts:
                active.add(bout.contest.rikishi_a)
                active.add(bout.contest.rikishi_b)

        departing = previous_active - active
        for rikishi in departing:
            state.ratings.pop(rikishi, None)
            state.sources.pop(rikishi, None)
        known = set(state.ratings)
        new_rikishi = active - known
        for rikishi in sorted(new_rikishi):
            chii = basho.banzuke.rikchii.get(rikishi)
            rating, source = prior.rating_for(chii)
            state.ratings[rikishi] = rating
            state.sources[rikishi] = source
            state.counts.setdefault(rikishi, 0)

        if not active:
            previous_active = active
            continue
        raw_start_mean = _mean(state.ratings, active)
        if target_mean is None:
            target_mean = raw_start_mean
        start_adjustment = _shift_to_target(state.ratings, active, target_mean)
        starts[date] = _snapshot(state.ratings, active)

        date_daily = {}
        represented_days = sorted(basho.summary.keys())
        for day in represented_days:
            for bout in by_day.get(day, ()):
                forecasts.append(
                    _forecast_and_update(
                        state=state,
                        bout=bout,
                        chii_a=basho.banzuke.rikchii.get(bout.contest.rikishi_a),
                        chii_b=basho.banzuke.rikchii.get(bout.contest.rikishi_b),
                        divisional_k=divisional_k,
                        q=q,
                    )
                )
            date_daily[day] = _snapshot(state.ratings, active)
        daily[date] = date_daily

        raw_end_mean = _mean(state.ratings, active)
        end_adjustment = _shift_to_target(state.ratings, active, target_mean)
        ends[date] = _snapshot(state.ratings, active)
        adjustments.append(
            BashoAdjustment(
                date=date,
                active_count=len(active),
                new_rikishi_count=len(new_rikishi),
                departing_rikishi_count=len(departing),
                target_mean=target_mean,
                raw_start_mean=raw_start_mean,
                start_adjustment=start_adjustment,
                raw_end_mean=raw_end_mean,
                end_adjustment=end_adjustment,
            )
        )
        previous_active = active

    if target_mean is None:
        raise ValueError("The Elo-89 interval contains no active rikishi")
    return Elo89Run(
        target_mean=target_mean,
        basho_start_ratings=starts,
        day_end_ratings=daily,
        basho_end_ratings=ends,
        forecasts=tuple(forecasts),
        adjustments=tuple(adjustments),
        raw_result_count=selection.raw_result_count,
        rated_bout_count=selection.rated_bout_count,
        excluded_fusen_count=selection.excluded_fusen_count,
        excluded_draw_count=selection.excluded_draw_count,
    )


def _forecast_and_update(
    *,
    state: _State,
    bout: RatedBout,
    chii_a: Chii | None,
    chii_b: Chii | None,
    divisional_k: Callable[[int], float],
    q: float,
) -> Forecast:
    a = bout.contest.rikishi_a
    b = bout.contest.rikishi_b
    rating_a = state.ratings[a]
    rating_b = state.ratings[b]
    probability = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / q))
    k_a = divisional_k(chii_a.ordinal()) if chii_a else 35.0
    k_b = divisional_k(chii_b.ordinal()) if chii_b else 35.0
    residual = float(bout.a_won) - probability
    delta_a = k_a * residual
    delta_b = -k_b * residual
    forecast = Forecast(
        date=bout.contest.id.date,
        day=bout.contest.id.day,
        rikishi_a=a,
        rikishi_b=b,
        chii_a=chii_a,
        chii_b=chii_b,
        rating_a_before=rating_a,
        rating_b_before=rating_b,
        rated_bouts_a_before=state.counts[a],
        rated_bouts_b_before=state.counts[b],
        probability_a_wins=probability,
        a_won=bout.a_won,
        k_a=k_a,
        k_b=k_b,
        delta_a=delta_a,
        delta_b=delta_b,
        rating_a_after=rating_a + delta_a,
        rating_b_after=rating_b + delta_b,
        initialisation_a=state.sources[a],
        initialisation_b=state.sources[b],
    )
    state.ratings[a] += delta_a
    state.ratings[b] += delta_b
    state.counts[a] += 1
    state.counts[b] += 1
    return forecast


def _shift_to_target(
    ratings: dict[RikId, float], active: set[RikId], target: float
) -> float:
    adjustment = target - _mean(ratings, active)
    for rikishi in active:
        ratings[rikishi] += adjustment
    return adjustment


def _mean(ratings: dict[RikId, float], active: set[RikId]) -> float:
    return sum(ratings[rikishi] for rikishi in active) / len(active)


def _snapshot(ratings: dict[RikId, float], active: set[RikId]) -> dict[RikId, float]:
    return {rikishi: ratings[rikishi] for rikishi in sorted(active)}
