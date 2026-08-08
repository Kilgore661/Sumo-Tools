"""Test Proposal 1's probability-staked profit against fair-coin histories."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
import random
from typing import Callable, Iterable

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History

from .definition import Proposal1Definition
from .randomised_prior import (
    PassProgress,
    PreparedPlaceboBouts,
    SCOPES,
    SCOPE_MASKS,
    prepare_placebo_bouts,
)


@dataclass(frozen=True)
class FairCoinDefinition:
    """Reproducible Monte Carlo design for Proposal 6."""

    replicate_count: int = 2000
    seed: int = 20260807
    confidence_level: float = 0.95


@dataclass(frozen=True)
class BettingScore:
    """Probability-staked evens result averaged as one bout per day."""

    scope: str
    basho_count: int
    day_count: int
    mean_stake_per_basho: float
    mean_profit_per_basho: float
    return_on_stake: float


@dataclass(frozen=True)
class NullReplicate:
    """One complete fair-coin history's betting results."""

    replicate: int
    scores: tuple[BettingScore, ...]


@dataclass(frozen=True)
class NullSummary:
    """Observed statistic and its one-sided fair-coin comparison."""

    scope: str
    observed_profit: float
    null_median_profit: float
    null_lower_profit: float
    null_upper_profit: float
    null_at_least_observed: int
    replicate_count: int
    monte_carlo_p: float


@dataclass(frozen=True)
class FairCoinNullResult:
    """Proposal 6's historical and simulated evidence."""

    elo_definition: Proposal1Definition
    null_definition: FairCoinDefinition
    prepared: PreparedPlaceboBouts
    observed_scores: tuple[BettingScore, ...]
    null_replicates: tuple[NullReplicate, ...]
    summaries: tuple[NullSummary, ...]


def run_fair_coin_null(
    history: History,
    elo_definition: Proposal1Definition,
    null_definition: FairCoinDefinition = FairCoinDefinition(),
    progress: Callable[[PassProgress], None] | None = None,
) -> FairCoinNullResult:
    """Run the historical pass and complete fair-coin histories."""

    prepared = prepare_placebo_bouts(history, elo_definition)
    total_passes = 1 + null_definition.replicate_count
    observed = score_probability_stakes(
        prepared,
        elo_definition,
        outcomes=(row.bout.a_won for row in prepared.bouts),
    )
    _progress(progress, 1, total_passes, "historical outcomes")

    generator = random.Random(null_definition.seed)
    replicates: list[NullReplicate] = []
    for replicate in range(1, null_definition.replicate_count + 1):
        scores = score_probability_stakes(
            prepared,
            elo_definition,
            outcomes=(
                bool(generator.getrandbits(1)) for _ in prepared.bouts
            ),
        )
        replicates.append(NullReplicate(replicate, scores))
        _progress(
            progress,
            1 + replicate,
            total_passes,
            f"fair-coin history {replicate}/{null_definition.replicate_count}",
        )

    null_rows = tuple(replicates)
    return FairCoinNullResult(
        elo_definition=elo_definition,
        null_definition=null_definition,
        prepared=prepared,
        observed_scores=observed,
        null_replicates=null_rows,
        summaries=_summaries(observed, null_rows, null_definition),
    )


def score_probability_stakes(
    prepared: PreparedPlaceboBouts,
    definition: Proposal1Definition,
    *,
    outcomes: Iterable[bool],
) -> tuple[BettingScore, ...]:
    """Run Elo once and score a uniformly selected eligible bout each day."""

    ratings: dict[RikId, float] = {}
    daily_totals = {scope: [0.0, 0.0, 0] for scope in SCOPES}
    epoch_totals = {scope: [0.0, 0.0, 0] for scope in SCOPES}
    previous_day = None
    dates = set()

    for scoped, a_won in zip(prepared.bouts, outcomes, strict=True):
        bout = scoped.bout
        bout_day = (bout.contest.id.date, bout.contest.id.day)
        if previous_day is not None and bout_day != previous_day:
            _finish_day(daily_totals, epoch_totals)
        previous_day = bout_day
        dates.add(bout.contest.id.date)

        rikishi_a = bout.contest.rikishi_a
        rikishi_b = bout.contest.rikishi_b
        rating_a = ratings.setdefault(rikishi_a, definition.initial_rating)
        rating_b = ratings.setdefault(rikishi_b, definition.initial_rating)
        probability_a = 1.0 / (
            1.0 + 10.0 ** ((rating_b - rating_a) / definition.q)
        )
        favourite_probability = max(probability_a, 1.0 - probability_a)
        has_favourite = probability_a != 0.5
        favourite_won = (
            (probability_a > 0.5 and a_won)
            or (probability_a < 0.5 and not a_won)
        )
        stake = favourite_probability if has_favourite else 0.0
        profit = stake * (1.0 if favourite_won else -1.0) if stake else 0.0
        for scope, mask in SCOPE_MASKS:
            if scoped.scope_mask & mask:
                total = daily_totals[scope]
                total[0] += stake
                total[1] += profit
                total[2] += 1

        delta_a = definition.k * (float(a_won) - probability_a)
        ratings[rikishi_a] = rating_a + delta_a
        ratings[rikishi_b] = rating_b - delta_a

    if previous_day is not None:
        _finish_day(daily_totals, epoch_totals)

    basho_count = len(dates)
    return tuple(
        BettingScore(
            scope=scope,
            basho_count=basho_count,
            day_count=int(epoch_totals[scope][2]),
            mean_stake_per_basho=epoch_totals[scope][0] / basho_count,
            mean_profit_per_basho=epoch_totals[scope][1] / basho_count,
            return_on_stake=(
                epoch_totals[scope][1] / epoch_totals[scope][0]
            ),
        )
        for scope in SCOPES
    )


def _finish_day(daily_totals, epoch_totals) -> None:
    for scope in SCOPES:
        stake, profit, count = daily_totals[scope]
        if count:
            epoch_totals[scope][0] += stake / count
            epoch_totals[scope][1] += profit / count
            epoch_totals[scope][2] += 1
        daily_totals[scope][:] = (0.0, 0.0, 0)


def _summaries(
    observed: tuple[BettingScore, ...],
    replicates: tuple[NullReplicate, ...],
    definition: FairCoinDefinition,
) -> tuple[NullSummary, ...]:
    observed_by_scope = {row.scope: row for row in observed}
    result = []
    for scope in SCOPES:
        values = sorted(
            next(row for row in replicate.scores if row.scope == scope)
            .mean_profit_per_basho
            for replicate in replicates
        )
        observed_profit = observed_by_scope[scope].mean_profit_per_basho
        exceedances = sum(value >= observed_profit for value in values)
        confidence = Decimal(str(definition.confidence_level))
        lower_probability = (Decimal(1) - confidence) / 2
        upper_probability = (Decimal(1) + confidence) / 2
        lower_position = _nearest_rank_index(lower_probability, len(values))
        upper_position = _nearest_rank_index(upper_probability, len(values))
        middle = len(values) // 2
        result.append(NullSummary(
            scope=scope,
            observed_profit=observed_profit,
            null_median_profit=(values[middle - 1] + values[middle]) / 2.0,
            null_lower_profit=values[lower_position],
            null_upper_profit=values[upper_position],
            null_at_least_observed=exceedances,
            replicate_count=len(values),
            monte_carlo_p=(1 + exceedances) / (1 + len(values)),
        ))
    return tuple(result)


def _progress(progress, completed: int, total: int, label: str) -> None:
    if progress is not None:
        progress(PassProgress(completed, total, label))


def _nearest_rank_index(probability: Decimal, count: int) -> int:
    rank = int(
        (probability * count).to_integral_value(rounding=ROUND_CEILING)
    )
    return rank - 1
