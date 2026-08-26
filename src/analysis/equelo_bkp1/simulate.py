"""Legacy-compatible replay for BKP1 with a fixed q=400 expectation scale."""

from __future__ import annotations

from typing import Mapping

from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from .model import ReplayResult
from .params import KFn, expected_score


def replay(
    history: History,
    priors: Mapping[Chii, float],
    divisional_k: KFn,
) -> ReplayResult:
    ratings: dict[RikId, float] = {}
    previous_active: set[RikId] = set()
    starts = {}

    for date in sorted(history):
        basho = history[date]
        active = set(basho.banzuke.riks)
        _apply_legacy_departures(ratings, previous_active, active)
        for rikid in sorted(active):
            if rikid not in ratings:
                ratings[rikid] = float(priors[basho.banzuke.rikchii[rikid]])
        starts[date] = {rikid: ratings[rikid] for rikid in active}

        for day in sorted(basho.summary):
            for bout in basho.summary[day].results_lookup.values():
                if bout.decision in ("fusen", "blank"):
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
        previous_active = active

    if not starts:
        raise ValueError("Cannot replay an empty history")
    return ReplayResult(basho_start_ratings=starts)


def _apply_legacy_departures(
    ratings: dict[RikId, float],
    previous_active: set[RikId],
    current_active: set[RikId],
) -> None:
    for rikid in sorted(previous_active - current_active):
        active_before = [candidate for candidate in previous_active if candidate in ratings]
        if rikid not in active_before:
            continue
        mean_before = sum(ratings[candidate] for candidate in active_before) / len(active_before)
        survivors = [candidate for candidate in active_before if candidate != rikid]
        if survivors:
            adjustment = (ratings[rikid] - mean_before) / len(survivors)
            for survivor in survivors:
                ratings[survivor] += adjustment
        del ratings[rikid]
