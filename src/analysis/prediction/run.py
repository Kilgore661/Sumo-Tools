"""Application-level composition of the Proposal 1 analytical pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.History import History

from .bouts import BoutSelection, select_rated_bouts
from .definition import Proposal1Definition
from .experiment import ForecastRecord, build_forecast_ledger
from .scoring import ScoredForecast, score_forecasts
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
class Proposal1Result:
    """All computational products of one Proposal 1 run."""

    definition: Proposal1Definition
    selection: BoutSelection
    forecasts: tuple[ForecastRecord, ...]
    scored_forecasts: tuple[ScoredForecast, ...]
    basho_losses: tuple[BashoLossRow, ...]
    rolling_losses: tuple[RollingLossRow, ...]
    cumulative_losses: tuple[CumulativeLossRow, ...]
    uncertainty: tuple[UncertaintyRow, ...]


def run_proposal_1(
    history: History,
    definition: Proposal1Definition,
) -> Proposal1Result:
    """Run the fixed Basic Elo producer and every downstream evaluation stage."""

    selection = select_rated_bouts(
        history,
        start_date=definition.start_date,
        end_date=definition.end_date,
    )
    forecasts = build_forecast_ledger(selection.bouts, definition)
    scored = score_forecasts(
        forecasts,
        reference_probability=definition.reference_probability,
    )
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
    return Proposal1Result(
        definition=definition,
        selection=selection,
        forecasts=forecasts,
        scored_forecasts=scored,
        basho_losses=basho_losses,
        rolling_losses=rolling_losses,
        cumulative_losses=cumulative_losses,
        uncertainty=uncertainty,
    )
