"""Derive basho, rolling, and cumulative paired-loss series."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.History import Date

from .scoring import ScoredForecast


@dataclass(frozen=True)
class BashoLossRow:
    """Paired predictive losses aggregated over one basho."""

    date: Date
    bout_count: int
    log_loss_sum: float
    reference_log_loss_sum: float
    log_loss_difference_sum: float
    brier_score_sum: float
    reference_brier_score_sum: float
    brier_difference_sum: float
    mean_log_loss: float
    mean_reference_log_loss: float
    mean_log_loss_difference: float
    mean_brier_score: float
    mean_reference_brier_score: float
    mean_brier_difference: float


@dataclass(frozen=True)
class RollingLossRow:
    """Paired losses over one complete trailing window of basho."""

    window_basho: int
    start_date: Date
    end_date: Date
    basho_count: int
    bout_count: int
    mean_log_loss: float
    mean_reference_log_loss: float
    mean_log_loss_difference: float
    mean_brier_score: float
    mean_reference_brier_score: float
    mean_brier_difference: float


@dataclass(frozen=True)
class CumulativeLossRow:
    """Paired losses from the epoch through one basho."""

    start_date: Date
    end_date: Date
    basho_count: int
    bout_count: int
    mean_log_loss: float
    mean_reference_log_loss: float
    mean_log_loss_difference: float
    mean_brier_score: float
    mean_reference_brier_score: float
    mean_brier_difference: float


def build_basho_loss_rows(
    scored: tuple[ScoredForecast, ...],
) -> tuple[BashoLossRow, ...]:
    """Aggregate scored forecasts into their natural basho blocks."""

    grouped: dict[Date, list[ScoredForecast]] = {}
    for row in scored:
        date = row.forecast.bout_id.date
        grouped.setdefault(date, []).append(row)

    rows: list[BashoLossRow] = []
    for date in sorted(grouped):
        values = grouped[date]
        n = len(values)
        log_loss_sum = sum(row.log_loss for row in values)
        reference_log_loss_sum = sum(row.reference_log_loss for row in values)
        log_difference_sum = sum(row.log_loss_difference for row in values)
        brier_sum = sum(row.brier_score for row in values)
        reference_brier_sum = sum(row.reference_brier_score for row in values)
        brier_difference_sum = sum(row.brier_difference for row in values)
        rows.append(
            BashoLossRow(
                date=date,
                bout_count=n,
                log_loss_sum=log_loss_sum,
                reference_log_loss_sum=reference_log_loss_sum,
                log_loss_difference_sum=log_difference_sum,
                brier_score_sum=brier_sum,
                reference_brier_score_sum=reference_brier_sum,
                brier_difference_sum=brier_difference_sum,
                mean_log_loss=log_loss_sum / n,
                mean_reference_log_loss=reference_log_loss_sum / n,
                mean_log_loss_difference=log_difference_sum / n,
                mean_brier_score=brier_sum / n,
                mean_reference_brier_score=reference_brier_sum / n,
                mean_brier_difference=brier_difference_sum / n,
            )
        )
    return tuple(rows)


def build_rolling_loss_rows(
    basho_rows: tuple[BashoLossRow, ...],
    windows: tuple[int, ...],
) -> tuple[RollingLossRow, ...]:
    """Build complete trailing windows for every predeclared basho count."""

    rows: list[RollingLossRow] = []
    for window in windows:
        for end_index in range(window - 1, len(basho_rows)):
            block = basho_rows[end_index - window + 1:end_index + 1]
            totals = _block_totals(block)
            rows.append(
                RollingLossRow(
                    window_basho=window,
                    start_date=block[0].date,
                    end_date=block[-1].date,
                    basho_count=len(block),
                    **totals,
                )
            )
    return tuple(rows)


def build_cumulative_loss_rows(
    basho_rows: tuple[BashoLossRow, ...],
) -> tuple[CumulativeLossRow, ...]:
    """Build loss estimates from the experiment epoch through each basho."""

    rows: list[CumulativeLossRow] = []
    for end_index in range(len(basho_rows)):
        block = basho_rows[:end_index + 1]
        rows.append(
            CumulativeLossRow(
                start_date=block[0].date,
                end_date=block[-1].date,
                basho_count=len(block),
                **_block_totals(block),
            )
        )
    return tuple(rows)


def _block_totals(block: tuple[BashoLossRow, ...]) -> dict[str, float | int]:
    bout_count = sum(row.bout_count for row in block)
    log_loss_sum = sum(row.log_loss_sum for row in block)
    reference_log_loss_sum = sum(row.reference_log_loss_sum for row in block)
    log_difference_sum = sum(row.log_loss_difference_sum for row in block)
    brier_sum = sum(row.brier_score_sum for row in block)
    reference_brier_sum = sum(row.reference_brier_score_sum for row in block)
    brier_difference_sum = sum(row.brier_difference_sum for row in block)
    return {
        "bout_count": bout_count,
        "mean_log_loss": log_loss_sum / bout_count,
        "mean_reference_log_loss": reference_log_loss_sum / bout_count,
        "mean_log_loss_difference": log_difference_sum / bout_count,
        "mean_brier_score": brier_sum / bout_count,
        "mean_reference_brier_score": reference_brier_sum / bout_count,
        "mean_brier_difference": brier_difference_sum / bout_count,
    }
