"""Run Proposal 5's deterministic division-only initialization experiment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.sumo_core.BasicEnums import Division
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History

from .definition import Proposal1Definition
from .randomised_prior import (
    CumulativeScore,
    PassProgress,
    PreparedPlaceboBouts,
    PriorValue,
    division_for_chii,
    initial_ratings_for_mapping,
    prepare_placebo_bouts,
    score_prepared_bouts,
)


@dataclass(frozen=True)
class DivisionPriorRow:
    """One deterministic mean over Proposal 3 Chii values in a division."""

    division: Division
    initial_rating: float
    chii_count: int
    minimum_chii_rating: float
    maximum_chii_rating: float


@dataclass(frozen=True)
class DivisionInitialisationResult:
    """Proposal 5's prior audit and three deterministic score series."""

    definition: Proposal1Definition
    prior_values: tuple[PriorValue, ...]
    division_prior: tuple[DivisionPriorRow, ...]
    prepared: PreparedPlaceboBouts
    equal_scores: tuple[CumulativeScore, ...]
    genuine_scores: tuple[CumulativeScore, ...]
    division_scores: tuple[CumulativeScore, ...]


def build_division_prior(
    prior_values: tuple[PriorValue, ...],
) -> tuple[DivisionPriorRow, ...]:
    """Take the unweighted mean of completed Chii values in each division."""

    grouped: dict[Division, list[float]] = {}
    for row in prior_values:
        grouped.setdefault(division_for_chii(row.chii), []).append(row.rating)
    return tuple(
        DivisionPriorRow(
            division=division,
            initial_rating=sum(values) / len(values),
            chii_count=len(values),
            minimum_chii_rating=min(values),
            maximum_chii_rating=max(values),
        )
        for division, values in grouped.items()
    )


def run_division_initialisation(
    history: History,
    definition: Proposal1Definition,
    prior_values: tuple[PriorValue, ...],
    progress: Callable[[PassProgress], None] | None = None,
) -> DivisionInitialisationResult:
    """Run equal, genuine Chii, and division-only initialization."""

    prepared = prepare_placebo_bouts(history, definition)
    division_prior = build_division_prior(prior_values)
    equal_scores = score_prepared_bouts(
        prepared,
        definition,
        initial_ratings=None,
    )
    _progress(progress, 1, "equal")
    genuine_scores = score_prepared_bouts(
        prepared,
        definition,
        initial_ratings=initial_ratings_for_mapping(
            prepared,
            prior_values,
            tuple(row.rating for row in prior_values),
        ),
    )
    _progress(progress, 2, "genuine Chii")
    division_scores = score_prepared_bouts(
        prepared,
        definition,
        initial_ratings=_division_initial_ratings(prepared, division_prior),
    )
    _progress(progress, 3, "division only")
    return DivisionInitialisationResult(
        definition=definition,
        prior_values=prior_values,
        division_prior=division_prior,
        prepared=prepared,
        equal_scores=equal_scores,
        genuine_scores=genuine_scores,
        division_scores=division_scores,
    )


def _division_initial_ratings(
    prepared: PreparedPlaceboBouts,
    prior: tuple[DivisionPriorRow, ...],
) -> dict[RikId, float]:
    rating_by_division = {
        row.division: row.initial_rating for row in prior
    }
    result = {
        rikishi_id: rating_by_division[division_for_chii(chii)]
        for rikishi_id, chii in prepared.first_chii_by_rikishi.items()
    }
    result.update({
        rikishi_id: rating_by_division[Division.JONOKUCHI]
        for rikishi_id in prepared.unranked_initial_rikishi
    })
    return result


def _progress(
    callback: Callable[[PassProgress], None] | None,
    completed: int,
    label: str,
) -> None:
    if callback is not None:
        callback(PassProgress(completed, 3, label))
