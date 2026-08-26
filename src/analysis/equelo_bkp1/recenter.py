"""The fixed support-proportional post-iteration recentering rule for BKP1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ...sumo_core.Chii import Chii


@dataclass(frozen=True, slots=True)
class RecenteringResult:
    ratings: dict[Chii, float]
    mean_adjustment: float
    minimum_adjustment: float
    maximum_adjustment: float


def recenter(
    ratings: Mapping[Chii, float],
    *,
    base: float,
    support: Mapping[Chii, int],
) -> RecenteringResult:
    """Restore the unweighted map mean, allocating mass in proportion to support."""

    if not ratings:
        return RecenteringResult({}, 0.0, 0.0, 0.0)
    missing = set(ratings) - set(support)
    if missing:
        raise KeyError(f"Missing support for {len(missing)} chii")
    correction_mass = float(base) * len(ratings) - sum(ratings.values())
    total_support = sum(max(1, support[chii]) for chii in ratings)
    adjustments = {
        chii: correction_mass * max(1, support[chii]) / total_support
        for chii in ratings
    }
    values = tuple(adjustments.values())
    return RecenteringResult(
        ratings={chii: rating + adjustments[chii] for chii, rating in ratings.items()},
        mean_adjustment=sum(values) / len(values),
        minimum_adjustment=min(values),
        maximum_adjustment=max(values),
    )
