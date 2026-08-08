"""Apply proper probabilistic scores to the immutable forecast ledger."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .experiment import ForecastRecord


@dataclass(frozen=True)
class ScoredForecast:
    """One forecast with Basic Elo, reference, and paired losses."""

    forecast: ForecastRecord
    log_loss: float
    reference_log_loss: float
    log_loss_difference: float
    brier_score: float
    reference_brier_score: float
    brier_difference: float


def score_forecasts(
    forecasts: tuple[ForecastRecord, ...],
    *,
    reference_probability: float,
) -> tuple[ScoredForecast, ...]:
    """Score every pre-bout probability against its subsequently revealed result."""

    rows: list[ScoredForecast] = []
    for forecast in forecasts:
        probability_of_result = (
            forecast.probability_a_wins
            if forecast.a_won
            else 1.0 - forecast.probability_a_wins
        )
        log_loss = -math.log(probability_of_result)
        actual = float(forecast.a_won)
        reference_probability_of_result = (
            reference_probability
            if forecast.a_won
            else 1.0 - reference_probability
        )
        reference_log_loss = -math.log(reference_probability_of_result)
        brier_score = (forecast.probability_a_wins - actual) ** 2
        reference_brier = (reference_probability - actual) ** 2
        rows.append(
            ScoredForecast(
                forecast=forecast,
                log_loss=log_loss,
                reference_log_loss=reference_log_loss,
                log_loss_difference=log_loss - reference_log_loss,
                brier_score=brier_score,
                reference_brier_score=reference_brier,
                brier_difference=brier_score - reference_brier,
            )
        )
    return tuple(rows)
