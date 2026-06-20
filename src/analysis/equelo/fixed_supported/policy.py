"""Fixed-supported chii support and completion policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.sumo_core.BasicEnums import Annotation, Division, MSD, Side
from src.sumo_core.Chii import Chii


POLICY_NAME = "rank_family_support_collapse"
POLICY_SHORT_NAME = "RFSC"


@dataclass(frozen=True)
class CompletedInitialRating:
    chii: Chii
    initial_rating: float
    source_chii: Chii
    source_rating: float
    source_kind: str


def is_sekitori(chii: Chii) -> bool:
    """Return True for Makuuchi-subdivision and Juryo chii."""

    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def is_numbered_sanyaku(chii: Chii) -> bool:
    """Return True for Y/O/S/K overflow slots beyond the canonical first pair."""

    return (
        isinstance(chii.level, MSD)
        and chii.level != MSD.MAEGASHIRA
        and chii.number > 1
    )


def collapse_chii(chii: Chii) -> Chii:
    """Apply the rank-family support collapse policy."""

    if is_numbered_sanyaku(chii):
        return Chii(
            level=chii.level,
            number=1,
            side=Side.WEST,
            ann=Annotation.EMPTY,
        )

    return Chii(
        level=chii.level,
        number=chii.number,
        side=chii.side,
        ann=Annotation.EMPTY,
    )


def max_possible_bouts_for_chii(chii: Chii) -> int:
    """Return the basho-level upper bound for rikishi-bouts at this chii."""

    return 15 if is_sekitori(chii) else 7


def complete_initial_ratings(
    *,
    required_chii: Iterable[Chii],
    source_ratings: dict[Chii, float],
) -> list[CompletedInitialRating]:
    """Complete required chii from direct or nearest-supported source ratings."""

    supported = sorted(source_ratings, key=lambda chii: chii.ordinal())
    if not supported:
        raise ValueError("Cannot complete initial ratings from an empty supported rating map")

    completed = []
    for chii in sorted(set(required_chii), key=lambda item: item.ordinal()):
        if chii in source_ratings:
            source_chii = chii
            source_kind = "direct"
        else:
            source_chii = nearest_supported_chii(chii, supported)
            source_kind = "nearest_supported"
        completed.append(
            CompletedInitialRating(
                chii=chii,
                initial_rating=float(source_ratings[source_chii]),
                source_chii=source_chii,
                source_rating=float(source_ratings[source_chii]),
                source_kind=source_kind,
            )
        )
    return completed


def nearest_supported_chii(chii: Chii, supported: list[Chii]) -> Chii:
    """Return nearest supported chii by ordinal, breaking ties upward."""

    target = chii.ordinal()
    best = supported[0]
    best_distance = abs(best.ordinal() - target)
    for candidate in supported[1:]:
        distance = abs(candidate.ordinal() - target)
        if distance < best_distance:
            best = candidate
            best_distance = distance
            continue
        if distance == best_distance and candidate.ordinal() < best.ordinal():
            best = candidate
            best_distance = distance
    return best
