"""Legacy-compatible replay for BKP1 with a fixed q=400 expectation scale."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from ...sumo_core.BasicEnums import Outcome
from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from .model import ReplayResult
from .params import KFn, expected_score


class BoutEligibility(str, Enum):
    """Selectable bout domains for controlled P1 maintenance."""

    P1 = "p1"
    P1_WL = "p1-wl"


@dataclass(frozen=True, slots=True)
class EligibilityCounts:
    raw_results: int = 0
    rated_results: int = 0
    rated_blank_kimarite: int = 0
    excluded_blank_kimarite: int = 0
    excluded_fusen: int = 0
    excluded_non_binary: int = 0


def replay(
    history: History,
    priors: Mapping[Chii, float],
    divisional_k: KFn,
    *,
    eligibility: BoutEligibility = BoutEligibility.P1,
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
                if not bout_is_eligible(bout, eligibility):
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


def bout_is_eligible(bout, eligibility: BoutEligibility) -> bool:
    """Return whether one represented result belongs to the selected P1 domain."""

    if eligibility is BoutEligibility.P1:
        return bout.decision not in ("fusen", "blank")
    if eligibility is BoutEligibility.P1_WL:
        return {bout.outcome1, bout.outcome2} == {Outcome.W, Outcome.L}
    raise ValueError(f"Unsupported P1 bout eligibility: {eligibility!r}")


def count_eligibility(
    history: History,
    eligibility: BoutEligibility,
) -> EligibilityCounts:
    """Count the exact result domain presented to one P1 variant."""

    raw_results = 0
    rated_results = 0
    rated_blank_kimarite = 0
    excluded_blank_kimarite = 0
    excluded_fusen = 0
    excluded_non_binary = 0
    for basho in history.values():
        for daily in basho.summary.values():
            for bout in daily.results_lookup.values():
                raw_results += 1
                if bout_is_eligible(bout, eligibility):
                    rated_results += 1
                    if bout.decision == "blank":
                        rated_blank_kimarite += 1
                    continue
                outcomes = {bout.outcome1, bout.outcome2}
                if bout.decision == "blank" and outcomes == {Outcome.W, Outcome.L}:
                    excluded_blank_kimarite += 1
                elif outcomes == {Outcome.FS, Outcome.FP} or bout.decision == "fusen":
                    excluded_fusen += 1
                else:
                    excluded_non_binary += 1
    return EligibilityCounts(
        raw_results=raw_results,
        rated_results=rated_results,
        rated_blank_kimarite=rated_blank_kimarite,
        excluded_blank_kimarite=excluded_blank_kimarite,
        excluded_fusen=excluded_fusen,
        excluded_non_binary=excluded_non_binary,
    )


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
