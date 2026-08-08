"""Pointwise basho-block bootstrap intervals for rolling paired losses."""

from __future__ import annotations

from dataclasses import dataclass
import random

from src.sumo_core.History import Date

from .series import BashoLossRow


@dataclass(frozen=True)
class UncertaintyRow:
    """Pointwise bootstrap interval for one complete rolling window."""

    window_basho: int
    start_date: Date
    end_date: Date
    basho_count: int
    bout_count: int
    log_loss_difference: float
    log_loss_difference_lower: float
    log_loss_difference_upper: float
    brier_difference: float
    brier_difference_lower: float
    brier_difference_upper: float
    confidence_level: float
    bootstrap_resamples: int


def build_uncertainty_rows(
    basho_rows: tuple[BashoLossRow, ...],
    *,
    windows: tuple[int, ...],
    seed: int,
    resamples: int,
    confidence_level: float,
) -> tuple[UncertaintyRow, ...]:
    """Resample complete basho within each rolling window."""

    rng = random.Random(seed)
    rows: list[UncertaintyRow] = []
    alpha = (1.0 - confidence_level) / 2.0
    for window in windows:
        for end_index in range(window - 1, len(basho_rows)):
            block = basho_rows[end_index - window + 1:end_index + 1]
            log_samples: list[float] = []
            brier_samples: list[float] = []
            for _ in range(resamples):
                sample = tuple(rng.choice(block) for _ in block)
                bout_count = sum(row.bout_count for row in sample)
                log_samples.append(
                    sum(row.log_loss_difference_sum for row in sample)
                    / bout_count
                )
                brier_samples.append(
                    sum(row.brier_difference_sum for row in sample)
                    / bout_count
                )
            log_samples.sort()
            brier_samples.sort()
            lower_index = int(alpha * (resamples - 1))
            upper_index = int((1.0 - alpha) * (resamples - 1))
            bout_count = sum(row.bout_count for row in block)
            rows.append(
                UncertaintyRow(
                    window_basho=window,
                    start_date=block[0].date,
                    end_date=block[-1].date,
                    basho_count=len(block),
                    bout_count=bout_count,
                    log_loss_difference=(
                        sum(row.log_loss_difference_sum for row in block)
                        / bout_count
                    ),
                    log_loss_difference_lower=log_samples[lower_index],
                    log_loss_difference_upper=log_samples[upper_index],
                    brier_difference=(
                        sum(row.brier_difference_sum for row in block)
                        / bout_count
                    ),
                    brier_difference_lower=brier_samples[lower_index],
                    brier_difference_upper=brier_samples[upper_index],
                    confidence_level=confidence_level,
                    bootstrap_resamples=resamples,
                )
            )
    return tuple(rows)
