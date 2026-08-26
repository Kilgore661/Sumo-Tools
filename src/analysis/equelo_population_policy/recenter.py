"""Post-iteration recentering policies for a chii-indexed prior map."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

from ...sumo_core.Chii import Chii


@dataclass(frozen=True, slots=True)
class RecenteringResult:
    ratings: dict[Chii, float]
    correction_mass: float
    mean_adjustment: float
    minimum_adjustment: float
    maximum_adjustment: float
    maximum_pairwise_difference_change: float
    rms_pairwise_difference_change: float


def recenter(
    ratings: Mapping[Chii, float],
    *,
    base: float,
    support: Mapping[Chii, int],
    alpha: float,
) -> RecenteringResult:
    """Centre the unweighted chii-map mean, allocating correction by support.

    ``alpha=0`` is the old uniform additive shift and preserves every rating
    difference. ``alpha=1`` allocates the required correction mass directly in
    proportion to chii support. Intermediate exponents provide a controlled
    continuum between those rules.
    """

    if not ratings:
        return RecenteringResult({}, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    if alpha < 0.0:
        raise ValueError("recentering alpha must be non-negative")
    missing = set(ratings) - set(support)
    if missing:
        raise KeyError(f"Missing support for {len(missing)} chii")

    correction_mass = float(base) * len(ratings) - sum(ratings.values())
    weights = {
        chii: float(max(1, support[chii])) ** alpha
        for chii in ratings
    }
    total_weight = sum(weights.values())
    adjustments = {
        chii: correction_mass * weights[chii] / total_weight
        for chii in ratings
    }
    shifted = {
        chii: rating + adjustments[chii]
        for chii, rating in ratings.items()
    }
    values = tuple(adjustments.values())
    mean_adjustment = sum(values) / len(values)
    minimum = min(values)
    maximum = max(values)
    population_variance = sum(
        (value - mean_adjustment) ** 2 for value in values
    ) / len(values)
    rms_pairwise = (
        math.sqrt(2.0 * len(values) / (len(values) - 1) * population_variance)
        if len(values) > 1
        else 0.0
    )
    return RecenteringResult(
        ratings=shifted,
        correction_mass=correction_mass,
        mean_adjustment=mean_adjustment,
        minimum_adjustment=minimum,
        maximum_adjustment=maximum,
        maximum_pairwise_difference_change=maximum - minimum,
        rms_pairwise_difference_change=rms_pairwise,
    )
