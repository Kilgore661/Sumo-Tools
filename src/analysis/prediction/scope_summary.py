"""Summarize proper scores over the all, sekitori, and sub-sekitori scopes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History
from src.sumo_core.History import Date

from .scoring import ScoredForecast
from .sekitori import is_sekitori
from .series import build_basho_loss_rows, build_rolling_loss_rows


class ScoredResult(Protocol):
    scored_forecasts: tuple[ScoredForecast, ...]


@dataclass(frozen=True)
class ScopeScoreSummary:
    """Whole-epoch paired losses for one evaluation population."""

    scope: str
    bout_count: int
    mean_log_loss: float
    mean_reference_log_loss: float
    mean_log_loss_difference: float
    mean_brier_score: float
    mean_reference_brier_score: float
    mean_brier_difference: float


@dataclass(frozen=True)
class RollingSignSummary:
    """Observed sign behaviour of one rolling log-loss curve."""

    scope: str
    window_basho: int
    first_defined_date: Date
    first_defined_difference: float
    first_favourable_date: Date | None
    persistently_favourable_from: Date | None
    zero_crossing_count: int


def summarize_scopes(
    history: History,
    result: ScoredResult,
) -> tuple[ScopeScoreSummary, ...]:
    """Calculate the three agreed whole-epoch evaluation scopes in one pass."""

    accumulators = {
        "all eligible bouts": _Accumulator(),
        "both participants sekitori": _Accumulator(),
        "both participants sub-sekitori": _Accumulator(),
    }
    for row in result.scored_forecasts:
        accumulators["all eligible bouts"].add(row)
        forecast = row.forecast
        banzuke = history[forecast.bout_id.date].banzuke
        rikishi_a = RikId(forecast.rikishi_a)
        rikishi_b = RikId(forecast.rikishi_b)
        if rikishi_a not in banzuke or rikishi_b not in banzuke:
            continue
        a_is_sekitori = is_sekitori(banzuke.rikchii[rikishi_a])
        b_is_sekitori = is_sekitori(banzuke.rikchii[rikishi_b])
        if a_is_sekitori and b_is_sekitori:
            accumulators["both participants sekitori"].add(row)
        elif not a_is_sekitori and not b_is_sekitori:
            accumulators["both participants sub-sekitori"].add(row)
    return tuple(
        accumulator.summary(scope)
        for scope, accumulator in accumulators.items()
    )


def summarize_rolling_signs(
    history: History,
    result: ScoredResult,
    windows: tuple[int, ...],
) -> tuple[RollingSignSummary, ...]:
    """Summarize first and persistent crossings for all three scopes."""

    scopes: dict[str, list[ScoredForecast]] = {
        "all eligible bouts": [],
        "both participants sekitori": [],
        "both participants sub-sekitori": [],
    }
    for row in result.scored_forecasts:
        scopes["all eligible bouts"].append(row)
        forecast = row.forecast
        banzuke = history[forecast.bout_id.date].banzuke
        rikishi_a = RikId(forecast.rikishi_a)
        rikishi_b = RikId(forecast.rikishi_b)
        if rikishi_a not in banzuke or rikishi_b not in banzuke:
            continue
        a_is_sekitori = is_sekitori(banzuke.rikchii[rikishi_a])
        b_is_sekitori = is_sekitori(banzuke.rikchii[rikishi_b])
        if a_is_sekitori and b_is_sekitori:
            scopes["both participants sekitori"].append(row)
        elif not a_is_sekitori and not b_is_sekitori:
            scopes["both participants sub-sekitori"].append(row)

    summaries: list[RollingSignSummary] = []
    for scope, scored in scopes.items():
        rolling = build_rolling_loss_rows(
            build_basho_loss_rows(tuple(scored)),
            windows,
        )
        for window in windows:
            rows = tuple(
                row for row in rolling
                if row.window_basho == window
            )
            first_favourable = next(
                (row for row in rows if row.mean_log_loss_difference < 0),
                None,
            )
            last_non_favourable_index = next(
                (
                    index for index, row in reversed(tuple(enumerate(rows)))
                    if row.mean_log_loss_difference >= 0
                ),
                -1,
            )
            persistent = (
                rows[last_non_favourable_index + 1]
                if last_non_favourable_index + 1 < len(rows)
                else None
            )
            crossings = sum(
                (current.mean_log_loss_difference < 0)
                != (previous.mean_log_loss_difference < 0)
                for previous, current in zip(rows, rows[1:])
            )
            summaries.append(
                RollingSignSummary(
                    scope=scope,
                    window_basho=window,
                    first_defined_date=rows[0].end_date,
                    first_defined_difference=rows[0].mean_log_loss_difference,
                    first_favourable_date=(
                        first_favourable.end_date
                        if first_favourable is not None else None
                    ),
                    persistently_favourable_from=(
                        persistent.end_date if persistent is not None else None
                    ),
                    zero_crossing_count=crossings,
                )
            )
    return tuple(summaries)


@dataclass
class _Accumulator:
    bout_count: int = 0
    log_loss: float = 0.0
    reference_log_loss: float = 0.0
    log_loss_difference: float = 0.0
    brier_score: float = 0.0
    reference_brier_score: float = 0.0
    brier_difference: float = 0.0

    def add(self, row: ScoredForecast) -> None:
        self.bout_count += 1
        self.log_loss += row.log_loss
        self.reference_log_loss += row.reference_log_loss
        self.log_loss_difference += row.log_loss_difference
        self.brier_score += row.brier_score
        self.reference_brier_score += row.reference_brier_score
        self.brier_difference += row.brier_difference

    def summary(self, scope: str) -> ScopeScoreSummary:
        return ScopeScoreSummary(
            scope=scope,
            bout_count=self.bout_count,
            mean_log_loss=self.log_loss / self.bout_count,
            mean_reference_log_loss=self.reference_log_loss / self.bout_count,
            mean_log_loss_difference=(
                self.log_loss_difference / self.bout_count
            ),
            mean_brier_score=self.brier_score / self.bout_count,
            mean_reference_brier_score=(
                self.reference_brier_score / self.bout_count
            ),
            mean_brier_difference=self.brier_difference / self.bout_count,
        )
