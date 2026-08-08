"""Evaluate existing Basic Elo forecasts only where both rikishi are sekitori."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .definition import Proposal1Definition
from .experiment import ForecastRecord
from .run import Proposal1Result
from .scoring import ScoredForecast
from .series import (
    BashoLossRow,
    CumulativeLossRow,
    RollingLossRow,
    build_basho_loss_rows,
    build_cumulative_loss_rows,
    build_rolling_loss_rows,
)
from .uncertainty import UncertaintyRow, build_uncertainty_rows


@dataclass(frozen=True)
class SekitoriSelection:
    """Counts produced by the both-participants domain rule."""

    evaluated_bout_count: int
    excluded_one_sekitori_count: int
    excluded_no_sekitori_count: int


@dataclass(frozen=True)
class SekitoriEvaluationResult:
    """Proposal 1 forecasts evaluated only inside the sekitori domain."""

    definition: Proposal1Definition
    selection: SekitoriSelection
    forecasts: tuple[ForecastRecord, ...]
    scored_forecasts: tuple[ScoredForecast, ...]
    basho_losses: tuple[BashoLossRow, ...]
    rolling_losses: tuple[RollingLossRow, ...]
    cumulative_losses: tuple[CumulativeLossRow, ...]
    uncertainty: tuple[UncertaintyRow, ...]


@dataclass(frozen=True)
class SubSekitoriSelection:
    """Counts produced by the both-participants sub-sekitori rule."""

    evaluated_bout_count: int
    excluded_one_sub_sekitori_count: int
    excluded_no_sub_sekitori_count: int


@dataclass(frozen=True)
class SubSekitoriEvaluationResult:
    """Proposal 1 forecasts evaluated only inside the sub-sekitori domain."""

    definition: Proposal1Definition
    selection: SubSekitoriSelection
    forecasts: tuple[ForecastRecord, ...]
    scored_forecasts: tuple[ScoredForecast, ...]
    basho_losses: tuple[BashoLossRow, ...]
    rolling_losses: tuple[RollingLossRow, ...]
    cumulative_losses: tuple[CumulativeLossRow, ...]
    uncertainty: tuple[UncertaintyRow, ...]


def is_sekitori(chii: Chii) -> bool:
    """Return domain membership from the authoritative Chii value."""

    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def evaluate_sekitori_bouts(
    history: History,
    baseline: Proposal1Result,
) -> SekitoriEvaluationResult:
    """Select scored rows without changing the all-bout rating pass."""

    scored, excluded_one, excluded_none = _select_domain(
        history,
        baseline,
        is_sekitori,
    )
    layers = _evaluation_layers(scored, baseline.definition)
    return SekitoriEvaluationResult(
        definition=baseline.definition,
        selection=SekitoriSelection(
            evaluated_bout_count=len(scored),
            excluded_one_sekitori_count=excluded_one,
            excluded_no_sekitori_count=excluded_none,
        ),
        forecasts=tuple(row.forecast for row in scored),
        scored_forecasts=scored,
        **layers,
    )


def evaluate_sub_sekitori_bouts(
    history: History,
    baseline: Proposal1Result,
) -> SubSekitoriEvaluationResult:
    """Evaluate only bouts with two ranked non-sekitori participants."""

    scored, excluded_one, excluded_none = _select_domain(
        history,
        baseline,
        lambda chii: not is_sekitori(chii),
    )
    layers = _evaluation_layers(scored, baseline.definition)
    return SubSekitoriEvaluationResult(
        definition=baseline.definition,
        selection=SubSekitoriSelection(
            evaluated_bout_count=len(scored),
            excluded_one_sub_sekitori_count=excluded_one,
            excluded_no_sub_sekitori_count=excluded_none,
        ),
        forecasts=tuple(row.forecast for row in scored),
        scored_forecasts=scored,
        **layers,
    )


def _select_domain(
    history: History,
    baseline: Proposal1Result,
    is_member: Callable[[Chii], bool],
) -> tuple[tuple[ScoredForecast, ...], int, int]:
    included: list[ScoredForecast] = []
    excluded_one = 0
    excluded_none = 0
    for row in baseline.scored_forecasts:
        forecast = row.forecast
        banzuke = history[forecast.bout_id.date].banzuke
        rikishi_a = RikId(forecast.rikishi_a)
        rikishi_b = RikId(forecast.rikishi_b)
        a_is_member = (
            rikishi_a in banzuke
            and is_member(banzuke.rikchii[rikishi_a])
        )
        b_is_member = (
            rikishi_b in banzuke
            and is_member(banzuke.rikchii[rikishi_b])
        )
        if a_is_member and b_is_member:
            included.append(row)
        elif a_is_member or b_is_member:
            excluded_one += 1
        else:
            excluded_none += 1
    return tuple(included), excluded_one, excluded_none


def _evaluation_layers(
    scored: tuple[ScoredForecast, ...],
    definition: Proposal1Definition,
) -> dict[str, object]:
    basho_losses = build_basho_loss_rows(scored)
    rolling_losses = build_rolling_loss_rows(
        basho_losses,
        definition.rolling_windows,
    )
    cumulative_losses = build_cumulative_loss_rows(basho_losses)
    uncertainty = build_uncertainty_rows(
        basho_losses,
        windows=definition.rolling_windows,
        seed=definition.bootstrap_seed,
        resamples=definition.bootstrap_resamples,
        confidence_level=definition.confidence_level,
    )
    return {
        "basho_losses": basho_losses,
        "rolling_losses": rolling_losses,
        "cumulative_losses": cumulative_losses,
        "uncertainty": uncertainty,
    }
