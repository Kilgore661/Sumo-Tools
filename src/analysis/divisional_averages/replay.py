"""Post-1988 replay which persists six fixed active divisional means."""

from __future__ import annotations

import math
from statistics import fmean
from typing import Mapping

from src.analysis.equelo_bkp1.params import KFn, expected_score
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .division import division_name
from .model import DIVISIONS, DivisionAdjustment, ReplayResult


def replay(
    history: History,
    priors: Mapping[Chii, float],
    divisional_k: KFn,
    targets: Mapping[str, float],
    *,
    iteration: int = 0,
) -> ReplayResult:
    """Replay with a common shift inside every represented division."""

    ratings: dict[RikId, float] = {}
    previous_active: set[RikId] = set()
    starts = {}
    ends = {}
    rows: list[DivisionAdjustment] = []
    rated_bouts = 0
    log_loss = 0.0
    brier_loss = 0.0

    for date in sorted(history):
        basho = history[date]
        active = set(basho.banzuke.riks)
        for rikishi in previous_active - active:
            ratings.pop(rikishi, None)
        for rikishi in sorted(active):
            if rikishi not in ratings:
                ratings[rikishi] = float(priors[basho.banzuke.rikchii[rikishi]])

        rows.extend(
            _shift_divisions(
                ratings,
                active,
                basho.banzuke.rikchii,
                targets,
                iteration=iteration,
                date=str(date),
                phase="start",
            )
        )
        starts[date] = {rikishi: ratings[rikishi] for rikishi in active}

        for day in sorted(basho.summary):
            for bout in basho.summary[day].results_lookup.values():
                if bout.decision == "fusen" or {
                    bout.outcome1.name,
                    bout.outcome2.name,
                } != {"W", "L"}:
                    continue
                rikishi_a = bout.rikishi1
                rikishi_b = bout.rikishi2
                expected_a = expected_score(ratings[rikishi_a], ratings[rikishi_b])
                actual_a = 1.0 if bout.outcome1.name == "W" else 0.0
                residual = actual_a - expected_a
                k_a = divisional_k(basho.banzuke.rikchii[rikishi_a].ordinal())
                k_b = divisional_k(basho.banzuke.rikchii[rikishi_b].ordinal())
                ratings[rikishi_a] += k_a * residual
                ratings[rikishi_b] -= k_b * residual
                probability = min(max(expected_a, 1e-15), 1.0 - 1e-15)
                log_loss -= actual_a * math.log(probability) + (
                    1.0 - actual_a
                ) * math.log(1.0 - probability)
                brier_loss += (actual_a - expected_a) ** 2
                rated_bouts += 1

        rows.extend(
            _shift_divisions(
                ratings,
                active,
                basho.banzuke.rikchii,
                targets,
                iteration=iteration,
                date=str(date),
                phase="end",
            )
        )
        ends[date] = {rikishi: ratings[rikishi] for rikishi in active}
        previous_active = active

    if not starts:
        raise ValueError("Cannot replay an empty history")
    denominator = rated_bouts or 1
    return ReplayResult(
        basho_start_ratings=starts,
        basho_end_ratings=ends,
        adjustments=tuple(rows),
        rated_bout_count=rated_bouts,
        mean_log_loss=log_loss / denominator,
        mean_brier_loss=brier_loss / denominator,
    )


def _shift_divisions(
    ratings: dict[RikId, float],
    active: set[RikId],
    chii_by_rikishi: Mapping[RikId, Chii],
    targets: Mapping[str, float],
    *,
    iteration: int,
    date: str,
    phase: str,
) -> list[DivisionAdjustment]:
    rows = []
    for division in DIVISIONS:
        members = [
            rikishi
            for rikishi in active
            if division_name(chii_by_rikishi[rikishi]) == division
        ]
        if not members:
            continue
        raw_mean = fmean(ratings[rikishi] for rikishi in members)
        target = float(targets[division])
        adjustment = target - raw_mean
        for rikishi in members:
            ratings[rikishi] += adjustment
        rows.append(
            DivisionAdjustment(
                iteration=iteration,
                date=date,
                phase=phase,
                division=division,
                active_count=len(members),
                target_mean=target,
                raw_mean=raw_mean,
                adjustment_per_rikishi=adjustment,
                adjusted_mean=fmean(ratings[rikishi] for rikishi in members),
            )
        )
    return rows
