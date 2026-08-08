"""Run the Proposal 4 randomized Chii-prior placebo experiment."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import groupby
import math
from pathlib import Path
import random
from typing import Callable

from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .bouts import BoutSelection, RatedBout, select_rated_bouts
from .definition import Proposal1Definition
from .sekitori import is_sekitori


ALL_BOUTS = "all eligible bouts"
SEKITORI = "both participants sekitori"
SUB_SEKITORI = "both participants sub-sekitori"
SCOPES = (ALL_BOUTS, SEKITORI, SUB_SEKITORI)
GLOBAL_PLACEBO = "global"
WITHIN_DIVISION_PLACEBO = "within division"
PLACEBOS = (GLOBAL_PLACEBO, WITHIN_DIVISION_PLACEBO)

_ALL_MASK = 1
_SEKITORI_MASK = 2
_SUB_SEKITORI_MASK = 4
SCOPE_MASKS = (
    (ALL_BOUTS, _ALL_MASK),
    (SEKITORI, _SEKITORI_MASK),
    (SUB_SEKITORI, _SUB_SEKITORI_MASK),
)


@dataclass(frozen=True)
class RandomisationDefinition:
    """The deliberately small fixed Proposal 4 randomization design."""

    replicate_count: int = 100
    seed: int = 20260807
    horizons_basho: tuple[int, ...] = (6, 12, 30, 60)


@dataclass(frozen=True)
class PriorValue:
    """One authoritative Chii ordinal and its Proposal 3 rating."""

    chii: Chii
    rating: float


@dataclass(frozen=True)
class ScopedBout:
    """One rated bout with its precomputed evaluation-population mask."""

    bout: RatedBout
    scope_mask: int


@dataclass(frozen=True)
class PreparedPlaceboBouts:
    """The immutable bout stream and first-entry Chii contract."""

    selection: BoutSelection
    bouts: tuple[ScopedBout, ...]
    first_chii_by_rikishi: dict[RikId, Chii]
    unranked_initial_rikishi: tuple[RikId, ...]


@dataclass(frozen=True)
class CumulativeScore:
    """Cumulative proper scores for one population through one basho."""

    scope: str
    end_date: Date
    basho_count: int
    bout_count: int
    mean_log_loss: float
    mean_brier_score: float


@dataclass(frozen=True)
class RandomisedMapping:
    """One fixed permutation in generation order."""

    placebo: str
    replicate: int
    ratings: tuple[float, ...]


@dataclass(frozen=True)
class PassProgress:
    """One completed chronological Elo pass."""

    completed_passes: int
    total_passes: int
    label: str


@dataclass(frozen=True)
class RandomisedPriorResult:
    """Retained proof-of-concept products without full forecast ledgers."""

    elo_definition: Proposal1Definition
    randomisation: RandomisationDefinition
    prior_values: tuple[PriorValue, ...]
    prepared: PreparedPlaceboBouts
    equal_scores: tuple[CumulativeScore, ...]
    genuine_scores: tuple[CumulativeScore, ...]
    mappings: tuple[RandomisedMapping, ...]
    randomised_scores: tuple[tuple[CumulativeScore, ...], ...]


@dataclass(frozen=True)
class OrderSummary:
    """The Proposal 4 order-statistic convention for 100 values."""

    median: float
    percentile_5: float
    percentile_95: float


def load_prior_values(filename: Path) -> tuple[PriorValue, ...]:
    """Load Proposal 3's completed table through authoritative ordinals."""

    with filename.open(newline="", encoding="utf-8") as stream:
        rows = tuple(csv.DictReader(stream))
    return tuple(
        PriorValue(
            chii=Chii.from_ordinal(int(row["chii_ordinal"])),
            rating=float(row["initial_rating"]),
        )
        for row in sorted(rows, key=lambda row: int(row["chii_ordinal"]))
    )


def build_randomised_mappings(
    prior_values: tuple[PriorValue, ...],
    definition: RandomisationDefinition,
) -> tuple[RandomisedMapping, ...]:
    """Apply the proposal's single-stream, one-shuffle-per-replicate rule."""

    base = [row.rating for row in prior_values]
    generator = random.Random(definition.seed)
    mappings: list[RandomisedMapping] = []
    for replicate in range(1, definition.replicate_count + 1):
        values = base.copy()
        generator.shuffle(values)
        mappings.append(
            RandomisedMapping(GLOBAL_PLACEBO, replicate, tuple(values))
        )
    return tuple(mappings)


def build_within_division_mappings(
    prior_values: tuple[PriorValue, ...],
    definition: RandomisationDefinition,
) -> tuple[RandomisedMapping, ...]:
    """Shuffle values independently inside authoritative division groups."""

    base = [row.rating for row in prior_values]
    positions_by_division: dict[Division, list[int]] = {}
    for index, row in enumerate(prior_values):
        positions_by_division.setdefault(division_for_chii(row.chii), []).append(index)
    generator = random.Random(definition.seed)
    mappings: list[RandomisedMapping] = []
    for replicate in range(1, definition.replicate_count + 1):
        values = base.copy()
        for positions in positions_by_division.values():
            division_values = [base[index] for index in positions]
            generator.shuffle(division_values)
            for index, rating in zip(positions, division_values):
                values[index] = rating
        mappings.append(
            RandomisedMapping(
                WITHIN_DIVISION_PLACEBO,
                replicate,
                tuple(values),
            )
        )
    return tuple(mappings)


def prepare_placebo_bouts(
    history: History,
    elo_definition: Proposal1Definition,
) -> PreparedPlaceboBouts:
    """Select bouts once and attach scope and first-entry Chii information."""

    selection = select_rated_bouts(
        history,
        start_date=elo_definition.start_date,
        end_date=elo_definition.end_date,
    )
    first_chii: dict[RikId, Chii] = {}
    unranked: set[RikId] = set()
    scoped: list[ScopedBout] = []
    for bout in selection.bouts:
        banzuke = history[bout.contest.id.date].banzuke
        rikishi_a = bout.contest.rikishi_a
        rikishi_b = bout.contest.rikishi_b
        for rikishi_id in (rikishi_a, rikishi_b):
            if rikishi_id not in first_chii and rikishi_id not in unranked:
                if rikishi_id in banzuke:
                    first_chii[rikishi_id] = banzuke.rikchii[rikishi_id]
                else:
                    unranked.add(rikishi_id)

        scope_mask = _ALL_MASK
        if rikishi_a in banzuke and rikishi_b in banzuke:
            a_is_sekitori = is_sekitori(banzuke.rikchii[rikishi_a])
            b_is_sekitori = is_sekitori(banzuke.rikchii[rikishi_b])
            if a_is_sekitori and b_is_sekitori:
                scope_mask |= _SEKITORI_MASK
            elif not a_is_sekitori and not b_is_sekitori:
                scope_mask |= _SUB_SEKITORI_MASK
        scoped.append(ScopedBout(bout=bout, scope_mask=scope_mask))
    return PreparedPlaceboBouts(
        selection=selection,
        bouts=tuple(scoped),
        first_chii_by_rikishi=first_chii,
        unranked_initial_rikishi=tuple(sorted(unranked)),
    )


def run_randomised_prior_placebo(
    history: History,
    elo_definition: Proposal1Definition,
    prior_values: tuple[PriorValue, ...],
    randomisation: RandomisationDefinition = RandomisationDefinition(),
    progress: Callable[[PassProgress], None] | None = None,
) -> RandomisedPriorResult:
    """Run equal, genuine, and randomized initializations on the same bouts."""

    prepared = prepare_placebo_bouts(history, elo_definition)
    genuine_ratings = tuple(row.rating for row in prior_values)
    mappings = (
        build_randomised_mappings(prior_values, randomisation)
        + build_within_division_mappings(prior_values, randomisation)
    )
    total_passes = 2 + len(mappings)
    completed_passes = 0
    equal_scores = score_prepared_bouts(
        prepared,
        elo_definition,
        initial_ratings=None,
    )
    completed_passes += 1
    _report_progress(progress, completed_passes, total_passes, "equal")
    genuine_scores = score_prepared_bouts(
        prepared,
        elo_definition,
        initial_ratings=initial_ratings_for_mapping(
            prepared,
            prior_values,
            genuine_ratings,
        ),
    )
    completed_passes += 1
    _report_progress(progress, completed_passes, total_passes, "genuine Chii")
    randomized_scores: list[tuple[CumulativeScore, ...]] = []
    for mapping in mappings:
        randomized_scores.append(
            score_prepared_bouts(
                prepared,
                elo_definition,
                initial_ratings=initial_ratings_for_mapping(
                    prepared,
                    prior_values,
                    mapping.ratings,
                ),
            )
        )
        completed_passes += 1
        _report_progress(
            progress,
            completed_passes,
            total_passes,
            f"{mapping.placebo} {mapping.replicate}/{randomisation.replicate_count}",
        )
    return RandomisedPriorResult(
        elo_definition=elo_definition,
        randomisation=randomisation,
        prior_values=prior_values,
        prepared=prepared,
        equal_scores=equal_scores,
        genuine_scores=genuine_scores,
        mappings=mappings,
        randomised_scores=tuple(randomized_scores),
    )


def score_prepared_bouts(
    prepared: PreparedPlaceboBouts,
    definition: Proposal1Definition,
    *,
    initial_ratings: dict[RikId, float] | None,
) -> tuple[CumulativeScore, ...]:
    """Stream one Basic Elo pass and retain only cumulative scope scores."""

    ratings: dict[RikId, float] = {}
    totals = {scope: [0, 0.0, 0.0] for scope in SCOPES}
    rows: list[CumulativeScore] = []
    grouped = groupby(prepared.bouts, key=lambda row: row.bout.contest.id.date)
    for basho_count, (date, bouts) in enumerate(grouped, start=1):
        for scoped in bouts:
            bout = scoped.bout
            rikishi_a = bout.contest.rikishi_a
            rikishi_b = bout.contest.rikishi_b
            if rikishi_a not in ratings:
                ratings[rikishi_a] = (
                    definition.initial_rating
                    if initial_ratings is None else initial_ratings[rikishi_a]
                )
            if rikishi_b not in ratings:
                ratings[rikishi_b] = (
                    definition.initial_rating
                    if initial_ratings is None else initial_ratings[rikishi_b]
                )
            rating_a = ratings[rikishi_a]
            rating_b = ratings[rikishi_b]
            probability = 1.0 / (
                1.0 + 10.0 ** ((rating_b - rating_a) / definition.q)
            )
            probability_of_result = (
                probability if bout.a_won else 1.0 - probability
            )
            log_loss = -math.log(probability_of_result)
            brier = (probability - float(bout.a_won)) ** 2
            _add(totals[ALL_BOUTS], log_loss, brier)
            if scoped.scope_mask & _SEKITORI_MASK:
                _add(totals[SEKITORI], log_loss, brier)
            elif scoped.scope_mask & _SUB_SEKITORI_MASK:
                _add(totals[SUB_SEKITORI], log_loss, brier)

            delta_a = definition.k * (float(bout.a_won) - probability)
            ratings[rikishi_a] = rating_a + delta_a
            ratings[rikishi_b] = rating_b - delta_a

        for scope in SCOPES:
            count, log_sum, brier_sum = totals[scope]
            rows.append(
                CumulativeScore(
                    scope=scope,
                    end_date=date,
                    basho_count=basho_count,
                    bout_count=int(count),
                    mean_log_loss=log_sum / count,
                    mean_brier_score=brier_sum / count,
                )
            )
    return tuple(rows)


def summarize_ordered(values: tuple[float, ...]) -> OrderSummary:
    """Apply Proposal 4's explicit 100-replicate order statistics."""

    ordered = sorted(values)
    return OrderSummary(
        median=(ordered[49] + ordered[50]) / 2.0,
        percentile_5=ordered[4],
        percentile_95=ordered[94],
    )


def initial_ratings_for_mapping(
    prepared: PreparedPlaceboBouts,
    prior_values: tuple[PriorValue, ...],
    ratings: tuple[float, ...],
) -> dict[RikId, float]:
    rating_by_chii = {
        row.chii: rating for row, rating in zip(prior_values, ratings)
    }
    result = {
        rikishi_id: rating_by_chii[chii]
        for rikishi_id, chii in prepared.first_chii_by_rikishi.items()
    }
    weakest_edge_rating = ratings[-1]
    result.update({
        rikishi_id: weakest_edge_rating
        for rikishi_id in prepared.unranked_initial_rikishi
    })
    return result


def _add(total: list[float | int], log_loss: float, brier: float) -> None:
    total[0] += 1
    total[1] += log_loss
    total[2] += brier


def division_for_chii(chii: Chii) -> Division:
    if isinstance(chii.level, MSD):
        return Division.MAKUUCHI
    return chii.level


def _report_progress(
    progress: Callable[[PassProgress], None] | None,
    completed_passes: int,
    total_passes: int,
    label: str,
) -> None:
    if progress is not None:
        progress(PassProgress(completed_passes, total_passes, label))
