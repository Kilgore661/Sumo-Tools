"""Support-proportional P2 map recentering within each division."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Mapping

from src.sumo_core.Chii import Chii

from .division import division_name
from .model import DIVISIONS


@dataclass(frozen=True, slots=True)
class DivisionRecentering:
    division: str
    chii_count: int
    observation_count: int
    target_mean: float
    raw_mean: float
    centred_mean: float
    correction_mass: float


@dataclass(frozen=True, slots=True)
class RecenteringResult:
    ratings: dict[Chii, float]
    divisions: tuple[DivisionRecentering, ...]


def recenter_by_division(
    ratings: Mapping[Chii, float],
    *,
    targets: Mapping[str, float],
    support: Mapping[Chii, int],
) -> RecenteringResult:
    """Restore each unweighted divisional map mean using P1's alpha=1 rule."""

    if not ratings:
        return RecenteringResult({}, ())
    missing_support = set(ratings) - set(support)
    if missing_support:
        raise KeyError(f"Missing support for {len(missing_support)} chii")

    shifted: dict[Chii, float] = {}
    summaries: list[DivisionRecentering] = []
    for division in DIVISIONS:
        members = [chii for chii in ratings if division_name(chii) == division]
        if not members:
            continue
        if division not in targets:
            raise KeyError(f"Missing target mean for {division}")
        target = float(targets[division])
        correction_mass = target * len(members) - sum(ratings[chii] for chii in members)
        total_support = sum(max(1, support[chii]) for chii in members)
        for chii in members:
            adjustment = correction_mass * max(1, support[chii]) / total_support
            shifted[chii] = ratings[chii] + adjustment
        summaries.append(
            DivisionRecentering(
                division=division,
                chii_count=len(members),
                observation_count=sum(support[chii] for chii in members),
                target_mean=target,
                raw_mean=fmean(ratings[chii] for chii in members),
                centred_mean=fmean(shifted[chii] for chii in members),
                correction_mass=correction_mass,
            )
        )
    if set(shifted) != set(ratings):
        raise AssertionError("Divisional recentering did not cover every chii")
    return RecenteringResult(shifted, tuple(summaries))

