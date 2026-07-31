"""Division-relative banzuke coordinates shared by analysis packages."""

from __future__ import annotations

from collections import defaultdict
from typing import Mapping


MAKUUCHI_LEVELS = frozenset({"Y", "O", "S", "K", "M"})


def competitive_division(chii: object) -> str:
    """Return the competitive division containing ``chii``."""
    level = getattr(chii, "level")
    label = level.as_abbreviation()
    return "M" if label in MAKUUCHI_LEVELS else label


def boundary_positions(
    rikchii: Mapping[object, object],
) -> dict[object, tuple[str, int, int]]:
    """Map rikishi to division, position from top, and position from bottom."""
    by_division: dict[str, list[tuple[object, int]]] = defaultdict(list)
    for rikishi, chii in rikchii.items():
        by_division[competitive_division(chii)].append(
            (rikishi, chii.ordinal())
        )

    positions: dict[object, tuple[str, int, int]] = {}
    for division, rikishi_ordinals in by_division.items():
        rikishi_ordinals.sort(key=lambda item: item[1])
        size = len(rikishi_ordinals)
        for index, (rikishi, _ordinal) in enumerate(rikishi_ordinals):
            positions[rikishi] = (
                division,
                index + 1,
                size - index,
            )
    return positions


def paired_boundary_group(boundary_distance: int) -> int:
    """Collapse adjacent individual slots into a no-side boundary group."""
    if boundary_distance <= 0:
        raise ValueError("boundary_distance must be positive")
    return (boundary_distance + 1) // 2
