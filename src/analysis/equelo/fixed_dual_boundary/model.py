"""Geometry-defined prior assignments for the joint boundary model."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.analysis.boundary_positions import boundary_positions
from src.analysis.equelo.fixed_boundary.model import (
    JMS_BOUNDARY,
    LITERAL_CHII,
    MJ_BOUNDARY,
    PriorKey,
)
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class WeightedPriorKey:
    key: PriorKey
    weight: float


PriorAssignment = tuple[WeightedPriorKey, ...]


@dataclass(frozen=True)
class DualBoundaryWorld:
    assignments_by_date_rikishi: dict[Date, dict[RikId, PriorAssignment]]
    labels: dict[PriorKey, str]
    appearances: Counter[PriorKey]

    @property
    def keys(self) -> frozenset[PriorKey]:
        return frozenset(self.appearances)


def build_dual_boundary_world(
    history: History,
    *,
    juryo_weighting: str = "nearest",
) -> DualBoundaryWorld:
    """Assign Juryo to both boundary maps using a declared geometry rule."""

    if juryo_weighting not in {"nearest", "linear"}:
        raise ValueError(f"Unknown Juryo weighting rule: {juryo_weighting}")

    assignments = {}
    labels: dict[PriorKey, str] = {}
    appearances: Counter[PriorKey] = Counter()

    for date in sorted(history):
        banzuke = history[date].banzuke
        positions = boundary_positions(banzuke.rikchii)
        date_assignments = {}
        for rikid, chii in banzuke.rikchii.items():
            division, from_top, from_bottom = positions[rikid]
            if division == "M":
                assignment = _single(MJ_BOUNDARY, -from_bottom)
            elif division == "J":
                assignment = _juryo_assignment(
                    from_top=from_top,
                    from_bottom=from_bottom,
                    weighting=juryo_weighting,
                )
            elif division == "Ms":
                assignment = _single(JMS_BOUNDARY, from_top - 1)
            else:
                collapsed = collapse_chii(chii)
                assignment = _single(LITERAL_CHII, collapsed.ordinal())

            date_assignments[rikid] = assignment
            for item in assignment:
                labels[item.key] = _label(item.key, chii)
                appearances[item.key] += item.weight
        assignments[date] = date_assignments

    return DualBoundaryWorld(
        assignments_by_date_rikishi=assignments,
        labels=labels,
        appearances=appearances,
    )


def assignment_rating(assignment: PriorAssignment, ratings: dict[PriorKey, float]) -> float:
    return sum(item.weight * ratings[item.key] for item in assignment)


def _single(kind: str, value: int) -> PriorAssignment:
    return (WeightedPriorKey(PriorKey(kind, value), 1.0),)


def _juryo_assignment(
    *, from_top: int, from_bottom: int, weighting: str
) -> PriorAssignment:
    mj_key = PriorKey(MJ_BOUNDARY, from_top - 1)
    jms_key = PriorKey(JMS_BOUNDARY, -from_bottom)
    if weighting == "nearest":
        if from_top < from_bottom:
            return (WeightedPriorKey(mj_key, 1.0),)
        if from_bottom < from_top:
            return (WeightedPriorKey(jms_key, 1.0),)
        return (
            WeightedPriorKey(mj_key, 0.5),
            WeightedPriorKey(jms_key, 0.5),
        )

    size = from_top + from_bottom - 1
    if size == 1:
        return (
            WeightedPriorKey(mj_key, 0.5),
            WeightedPriorKey(jms_key, 0.5),
        )
    mj_weight = (from_bottom - 1) / (size - 1)
    jms_weight = (from_top - 1) / (size - 1)
    return tuple(
        item
        for item in (
            WeightedPriorKey(mj_key, mj_weight),
            WeightedPriorKey(jms_key, jms_weight),
        )
        if item.weight > 0.0
    )


def _label(key: PriorKey, chii) -> str:
    if key.kind == MJ_BOUNDARY:
        return f"M/J {key.value:+d}"
    if key.kind == JMS_BOUNDARY:
        return f"J/Ms {key.value:+d}"
    return str(collapse_chii(chii))
