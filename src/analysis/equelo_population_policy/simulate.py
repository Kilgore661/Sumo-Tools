"""One shared Elo replay with switchable population policy.

This deliberately mirrors the old Expt1/Expt2 bout semantics.  The policy
switch is the only behavioural difference inside a comparison.
"""

from __future__ import annotations

import math
from typing import Mapping

from ...sumo_core.BasicPrimitives import RikId
from ...sumo_core.Chii import Chii
from ...sumo_core.History import History
from ..equelo.expt1.params import EloParams
from .model import BashoAdjustment, PopulationPolicy, ReplayResult


def replay(
    history: History,
    params: EloParams,
    priors: Mapping[Chii, float],
    policy: PopulationPolicy,
    *,
    variant: str | None = None,
    normalisation_support: Mapping[Chii, int] | None = None,
    normalisation_alpha: float = 0.0,
) -> ReplayResult:
    """Replay ``history`` under exactly one population-normalisation policy."""

    ratings: dict[RikId, float] = {}
    previous_active: set[RikId] = set()
    target_mean: float | None = None
    starts = {}
    ends = {}
    rows: list[BashoAdjustment] = []
    rated_bouts = 0
    log_loss = 0.0
    brier = 0.0

    for date in sorted(history):
        basho = history[date]
        active = set(basho.banzuke.riks)
        departures = previous_active - active
        entrants = active - set(ratings)

        legacy_adjustment = 0.0
        if policy in (
            PopulationPolicy.LEGACY_DEPARTURE,
            PopulationPolicy.LEGACY_DEPARTURE_BOUT_MASS,
        ):
            legacy_adjustment = _apply_legacy_departures(
                ratings, previous_active, active
            )
        else:
            for rikid in departures:
                ratings.pop(rikid, None)

        for rikid in sorted(active):
            if rikid not in ratings:
                chii = basho.banzuke.rikchii[rikid]
                ratings[rikid] = float(priors[chii])

        raw_start_mean = _active_mean(ratings, active)
        if target_mean is None:
            target_mean = raw_start_mean

        start_adjustment = legacy_adjustment
        if policy in (
            PopulationPolicy.POST_BASHO_MEAN_START_ONLY,
            PopulationPolicy.POST_BASHO_MEAN,
        ):
            start_adjustment = _shift_to_mean(
                ratings,
                active,
                target_mean,
                chii_by_rikishi=basho.banzuke.rikchii,
                support=normalisation_support,
                alpha=normalisation_alpha,
            )
        adjusted_start_mean = _active_mean(ratings, active)
        starts[date] = {rikid: ratings[rikid] for rikid in active}

        mass_before_bouts = sum(ratings[rikid] for rikid in active)
        for day in sorted(basho.summary):
            daily = basho.summary[day]
            for bout in daily.results_lookup.values():
                if bout.decision in ("fusen", "blank"):
                    continue
                rikishi_a = bout.rikishi1
                rikishi_b = bout.rikishi2
                rating_a = ratings[rikishi_a]
                rating_b = ratings[rikishi_b]
                expected_a = _expect(rating_a, rating_b, params.q)
                actual_a = 1.0 if bout.outcome1.name == "W" else 0.0
                residual = actual_a - expected_a
                k_a = params.k(basho.banzuke.rikchii[rikishi_a].ordinal())
                k_b = params.k(basho.banzuke.rikchii[rikishi_b].ordinal())
                ratings[rikishi_a] += k_a * residual
                ratings[rikishi_b] -= k_b * residual
                probability = min(max(expected_a, 1e-15), 1.0 - 1e-15)
                log_loss -= actual_a * math.log(probability) + (1.0 - actual_a) * math.log(
                    1.0 - probability
                )
                brier += (actual_a - expected_a) ** 2
                rated_bouts += 1

        mass_after_bouts = sum(ratings[rikid] for rikid in active)
        bout_mass_change = mass_after_bouts - mass_before_bouts
        raw_end_mean = _active_mean(ratings, active)
        end_adjustment = 0.0
        if policy is PopulationPolicy.POST_BASHO_MEAN:
            end_adjustment = _shift_to_mean(ratings, active, target_mean)
        elif policy is PopulationPolicy.LEGACY_DEPARTURE_BOUT_MASS:
            end_adjustment = -bout_mass_change / len(active)
            for rikid in active:
                ratings[rikid] += end_adjustment
        adjusted_end_mean = _active_mean(ratings, active)
        ends[date] = {rikid: ratings[rikid] for rikid in active}

        rows.append(
            BashoAdjustment(
                policy=variant or policy.value,
                date=str(date),
                active_count=len(active),
                entrant_count=len(entrants),
                departure_count=len(departures),
                target_mean=target_mean,
                raw_start_mean=raw_start_mean,
                start_adjustment_per_rikishi=start_adjustment,
                adjusted_start_mean=adjusted_start_mean,
                bout_mass_change=bout_mass_change,
                raw_end_mean=raw_end_mean,
                end_adjustment_per_rikishi=end_adjustment,
                adjusted_end_mean=adjusted_end_mean,
            )
        )
        previous_active = active

    if target_mean is None:
        raise ValueError("Cannot replay an empty history")
    denominator = rated_bouts or 1
    return ReplayResult(
        variant=variant or policy.value,
        policy=policy,
        target_mean=target_mean,
        basho_start_ratings=starts,
        basho_end_ratings=ends,
        adjustments=tuple(rows),
        rated_bout_count=rated_bouts,
        mean_log_loss=log_loss / denominator,
        mean_brier_score=brier / denominator,
    )


def _apply_legacy_departures(
    ratings: dict[RikId, float],
    previous_active: set[RikId],
    current_active: set[RikId],
) -> float:
    """Apply the current Expt1 departure rule and return its common net shift."""

    total_shift = 0.0
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
            total_shift += adjustment
        del ratings[rikid]
    return total_shift


def _shift_to_mean(
    ratings: dict[RikId, float],
    active: set[RikId],
    target_mean: float,
    *,
    chii_by_rikishi: Mapping[RikId, Chii] | None = None,
    support: Mapping[Chii, int] | None = None,
    alpha: float = 0.0,
) -> float:
    correction_mass = (target_mean - _active_mean(ratings, active)) * len(active)
    if support is None or chii_by_rikishi is None or alpha == 0.0:
        adjustment = correction_mass / len(active)
        for rikid in active:
            ratings[rikid] += adjustment
        return adjustment

    weights = {
        rikid: float(max(1, support.get(chii_by_rikishi[rikid], 1))) ** alpha
        for rikid in active
    }
    total_weight = sum(weights.values())
    for rikid, weight in weights.items():
        ratings[rikid] += correction_mass * weight / total_weight
    # Weighted corrections are not common. Return their active-population mean
    # so the ledger remains comparable across policies.
    return correction_mass / len(active)


def _active_mean(ratings: Mapping[RikId, float], active: set[RikId]) -> float:
    if not active:
        raise ValueError("A basho has no active rikishi")
    return sum(ratings[rikid] for rikid in active) / len(active)


def _expect(rating_a: float, rating_b: float, q: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / q))
