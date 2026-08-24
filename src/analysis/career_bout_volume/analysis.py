"""Derive career bout volume from banzuke-relative History observations."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict

from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History
from src.sumo_core.Summary import BoutResult

from .model import BoutProbabilityRow, ProbeResult, RikishiBashoRow, RikishiCareerRow


FOUGHT_OUTCOMES = frozenset({Outcome.W, Outcome.L, Outcome.DRAW})
POSITION_BAND_CUTS = (0.0, 0.2, 0.4, 0.6, 0.8395, 1.0000000001)


def analyse_history(history: History) -> ProbeResult:
    """Transform a non-empty History into basho and career observations."""

    dates = sorted(history)
    if not dates:
        raise ValueError("Career bout volume requires a non-empty History")

    basho_rows: list[RikishiBashoRow] = []
    exception_count = 0
    for date in dates:
        state = history(date)
        banzuke = state.banzuke
        ordered_rikishi = sorted(
            banzuke.riks,
            key=lambda rikishi_id: banzuke.rikchii[rikishi_id].ordinal(),
        )
        if len(ordered_rikishi) < 2:
            raise ValueError(f"Banzuke {date} contains fewer than two rikishi")

        result_counts = {
            rikishi_id: _empty_result_counts()
            for rikishi_id in ordered_rikishi
        }
        for daily_results in state.summary.values():
            for bout in daily_results.results_lookup.values():
                exception_count += _count_bout(bout, result_counts)

        banzuke_size = len(ordered_rikishi)
        for zero_based_position, rikishi_id in enumerate(ordered_rikishi):
            chii = banzuke.rikchii[rikishi_id]
            counts = result_counts[rikishi_id]
            basho_rows.append(
                RikishiBashoRow(
                    rikishi_id=int(rikishi_id),
                    shikona=str(banzuke.rikshik[rikishi_id]),
                    basho=str(date),
                    chii=str(chii),
                    chii_ordinal=chii.ordinal(),
                    banzuke_size=banzuke_size,
                    position_from_top=zero_based_position + 1,
                    position_from_bottom=banzuke_size - zero_based_position,
                    normalized_position=zero_based_position / (banzuke_size - 1),
                    recorded_results=counts["recorded_results"],
                    fought_bouts=counts["fought_bouts"],
                    fought_wins=counts["fought_wins"],
                    fought_losses=counts["fought_losses"],
                    draws=counts["draws"],
                    fusensho=counts["fusensho"],
                    fusenpai=counts["fusenpai"],
                )
            )

    career_rows = _aggregate_careers(
        basho_rows,
        first_history_basho=str(dates[0]),
        last_history_basho=str(dates[-1]),
    )
    return ProbeResult(
        history_first_basho=str(dates[0]),
        history_last_basho=str(dates[-1]),
        history_basho_count=len(dates),
        exception_count=exception_count,
        basho_rows=tuple(basho_rows),
        career_rows=tuple(career_rows),
    )


def _empty_result_counts() -> dict[str, int]:
    return {
        "recorded_results": 0,
        "fought_bouts": 0,
        "fought_wins": 0,
        "fought_losses": 0,
        "draws": 0,
        "fusensho": 0,
        "fusenpai": 0,
    }


def _count_bout(
    bout: BoutResult,
    counts_by_rikishi: dict[RikId, dict[str, int]],
) -> int:
    """Count listed participants and return missing-banzuke exceptions."""

    exception_count = 0
    for rikishi_id, outcome in (
        (bout.rikishi1, bout.outcome1),
        (bout.rikishi2, bout.outcome2),
    ):
        try:
            counts = counts_by_rikishi[rikishi_id]
        except KeyError:
            exception_count += 1
            continue
        _count_outcome(counts, outcome)
    return exception_count


def _count_outcome(counts: dict[str, int], outcome: Outcome) -> None:
    counts["recorded_results"] += 1
    if outcome in FOUGHT_OUTCOMES:
        counts["fought_bouts"] += 1
    if outcome == Outcome.W:
        counts["fought_wins"] += 1
    elif outcome == Outcome.L:
        counts["fought_losses"] += 1
    elif outcome == Outcome.DRAW:
        counts["draws"] += 1
    elif outcome == Outcome.FS:
        counts["fusensho"] += 1
    elif outcome == Outcome.FP:
        counts["fusenpai"] += 1


def _aggregate_careers(
    basho_rows: list[RikishiBashoRow],
    *,
    first_history_basho: str,
    last_history_basho: str,
) -> list[RikishiCareerRow]:
    rows_by_rikishi: dict[int, list[RikishiBashoRow]] = defaultdict(list)
    for row in basho_rows:
        rows_by_rikishi[row.rikishi_id].append(row)

    careers: list[RikishiCareerRow] = []
    for rikishi_id in sorted(rows_by_rikishi):
        rows = rows_by_rikishi[rikishi_id]
        positions = [row.normalized_position for row in rows]
        mean_position = statistics.fmean(positions)
        position_stdev = statistics.stdev(positions) if len(positions) > 1 else 0.0
        position_sem = position_stdev / math.sqrt(len(positions))
        ci95_half_width = 1.96 * position_sem
        active = rows[-1].basho == last_history_basho
        partial_start = rows[0].basho == first_history_basho
        primary_population = not active and not partial_start
        careers.append(
            RikishiCareerRow(
                rikishi_id=rikishi_id,
                shikona=rows[-1].shikona,
                first_basho=rows[0].basho,
                last_basho=rows[-1].basho,
                banzuke_appearances=len(rows),
                mean_normalized_position=mean_position,
                stdev_normalized_position=position_stdev,
                sem_normalized_position=position_sem,
                ci95_normalized_position_low=max(0.0, mean_position - ci95_half_width),
                ci95_normalized_position_high=min(1.0, mean_position + ci95_half_width),
                best_normalized_position=min(positions),
                worst_normalized_position=max(positions),
                total_recorded_results=sum(row.recorded_results for row in rows),
                total_fought_bouts=sum(row.fought_bouts for row in rows),
                total_fought_wins=sum(row.fought_wins for row in rows),
                total_fought_losses=sum(row.fought_losses for row in rows),
                total_draws=sum(row.draws for row in rows),
                total_fusensho=sum(row.fusensho for row in rows),
                total_fusenpai=sum(row.fusenpai for row in rows),
                active=active,
                partial_start=partial_start,
                primary_population=primary_population,
                career_status=_career_status(active=active, partial_start=partial_start),
            )
        )
    return careers


def _career_status(*, active: bool, partial_start: bool) -> str:
    if active and partial_start:
        return "active_partial_start"
    if active:
        return "active"
    if partial_start:
        return "partial_start"
    return "completed"


def build_bout_probability_rows(
    career_rows: tuple[RikishiCareerRow, ...],
) -> tuple[BoutProbabilityRow, ...]:
    """Build empirical bout-tail probabilities for primary-population bands."""

    primary_rows = [row for row in career_rows if row.primary_population]
    probability_rows: list[BoutProbabilityRow] = []
    for low, high in zip(POSITION_BAND_CUTS, POSITION_BAND_CUTS[1:]):
        band_rows = [
            row
            for row in primary_rows
            if low <= row.mean_normalized_position < high
        ]
        if not band_rows:
            continue
        bout_counts = [row.total_fought_bouts for row in band_rows]
        career_count = len(bout_counts)
        display_high: float | str = "" if high > 1.0 else high
        label = _position_band_label(low, high)
        for threshold in range(max(bout_counts) + 1):
            reaching_count = sum(count >= threshold for count in bout_counts)
            probability = reaching_count / career_count
            ci95_low, ci95_high = wilson_interval(reaching_count, career_count)
            probability_rows.append(
                BoutProbabilityRow(
                    position_band=label,
                    position_low_inclusive=low,
                    position_high_exclusive=display_high,
                    career_count=career_count,
                    bout_threshold=threshold,
                    reaching_count=reaching_count,
                    empirical_probability=probability,
                    ci95_low=ci95_low,
                    ci95_high=ci95_high,
                )
            )
    return tuple(probability_rows)


def wilson_interval(successes: int, observations: int) -> tuple[float, float]:
    """Return the two-sided 95% Wilson interval for a binomial proportion."""

    z = 1.96
    probability = successes / observations
    z_squared = z * z
    denominator = 1.0 + z_squared / observations
    centre = (probability + z_squared / (2.0 * observations)) / denominator
    half_width = (
        z
        * math.sqrt(
            probability * (1.0 - probability) / observations
            + z_squared / (4.0 * observations * observations)
        )
        / denominator
    )
    return centre - half_width, centre + half_width


def _position_band_label(low: float, high: float) -> str:
    if high > 1.0:
        return f"{low:.4f}–1.0000"
    return f"{low:.4f}–<{high:.4f}"
