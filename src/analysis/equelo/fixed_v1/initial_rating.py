"""Curated initial rating curves derived from fixed v1 entrant priors.

The fixed_v1 entrant prior is the raw scaled fixed-point chii-to-rating map.
It is useful but not strictly monotone, and it contains rare historical chii
whose values are not suitable for the production-facing scale.

This module promotes the current v5 chart experiment into a reusable lookup
object.  The v5 curve:

* deletes chii outside the curated domain;
* masks selected unreliable support values while keeping their chii positions;
* builds a dense meta-ordinal index over the remaining domain;
* fits a strictly decreasing monotone cubic curve; and
* exposes cheap lookup by dense index, chii ordinal, or Chii object.

The result is not raw Equelo output.  It is a deterministic, auditable,
monotone scale derived from fixed_v1 for applications that need stable
rating-to-chii or chii-to-rating behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.sumo_core.Chii import Chii

from .api import load_entrant_initial_ratings
from .model import OUTPUT_ROOT


V1_MAX_CHII = Chii.from_str("Jd100w").ordinal()
V2_DELETE_ORDINALS = {
    Chii.from_str(f"J{rank}{side}").ordinal()
    for rank in range(13, 25)
    for side in ("e", "w")
}
V4_DELETE_ORDINALS = V2_DELETE_ORDINALS | {
    Chii.from_str(f"M{rank}{side}").ordinal()
    for rank in range(18, 23)
    for side in ("e", "w")
}
V3_MASK_ORDINALS = {
    Chii.from_str("O3w").ordinal(),
    Chii.from_str("S2e").ordinal(),
    Chii.from_str("S2w").ordinal(),
    Chii.from_str("S3e").ordinal(),
    Chii.from_str("K2e").ordinal(),
    Chii.from_str("Sd101e").ordinal(),
}
V5_BRIDGE_MASK_START = Chii.from_str("M12e").ordinal()
V5_BRIDGE_MASK_END = Chii.from_str("Ms2e").ordinal()
V5_EXTRA_MASK_ORDINALS = {Chii.from_str("Ms3e").ordinal()}


@dataclass(frozen=True)
class InitialRatingCurve:
    """Dense-indexed fixed v1 initial rating curve."""

    ordinals: list[int]
    ratings: list[float]
    index_by_ordinal: dict[int, int]

    @classmethod
    def v5(cls, output_root: Path = OUTPUT_ROOT) -> "InitialRatingCurve":
        """Build the current v5 curated monotone initial rating curve."""

        source = load_entrant_initial_ratings(output_root=output_root)
        rows = [
            (int(ordinal_text), float(rating))
            for ordinal_text, rating in source.items()
        ]
        return cls.from_ordinal_ratings(rows)

    @classmethod
    def from_ordinal_ratings(
        cls,
        ratings: dict[int, float] | list[tuple[int, float]],
    ) -> "InitialRatingCurve":
        """Build the v5-style curated curve from ordinal-keyed ratings."""

        # NOTE:
        # This constructor was added post hoc during the Brierless
        # investigation in order to reuse the original
        # fixed_v1 cleaning/smoothing pipeline with arbitrary ordinal?rating
        # mappings. The original module was written specifically around the
        # fixed_v1/Brier entrant-rating workflow and did not expose a
        # general-purpose curve-construction API.
        if isinstance(ratings, dict):
            rows = [(int(ordinal), float(rating)) for ordinal, rating in ratings.items()]
        else:
            rows = [(int(ordinal), float(rating)) for ordinal, rating in ratings]

        return cls._from_rows(rows)

    @classmethod
    def _from_rows(cls, rows: list[tuple[int, float]]) -> "InitialRatingCurve":
        """Build the curated monotone curve from raw ordinal-rating rows."""

        rows = sorted(rows, key=lambda item: item[0])

        rows = [
            row for row in rows
            if row[0] <= V1_MAX_CHII and row[0] not in V4_DELETE_ORDINALS
        ]

        mask_ordinals = v5_mask_ordinals(rows)
        support_rows = [
            row for row in rows
            if row[0] not in mask_ordinals
        ]
        index_by_ordinal = {
            ordinal: index
            for index, (ordinal, _) in enumerate(rows)
        }
        support_x = [index_by_ordinal[ordinal] for ordinal, _ in support_rows]
        support_y = strictly_decreasing([rating for _, rating in support_rows])
        ratings = [
            evaluate_monotone_cubic(support_x, support_y, index)
            for index in range(len(rows))
        ]
        ordinals = [ordinal for ordinal, _ in rows]

        return cls(
            ordinals=ordinals,
            ratings=ratings,
            index_by_ordinal=index_by_ordinal,
        )

    def rating_at_index(self, index: int) -> float:
        """Return the initial rating at dense chii index."""

        return self.ratings[index]

    def rating_for_ordinal(self, ordinal: int) -> float:
        """Return the initial rating for a chii ordinal in this curve domain."""

        return self.ratings[self.index_by_ordinal[int(ordinal)]]

    def rating_for_chii(self, chii: Chii) -> float:
        """Return the initial rating for a Chii in this curve domain."""

        return self.rating_for_ordinal(chii.ordinal())


def v5_mask_ordinals(rows: list[tuple[int, float]]) -> set[int]:
    """Return v5 masked ordinals for the supplied curated row domain."""

    return V3_MASK_ORDINALS | V5_EXTRA_MASK_ORDINALS | {
        ordinal
        for ordinal, _ in rows
        if V5_BRIDGE_MASK_START <= ordinal <= V5_BRIDGE_MASK_END
    }


def strictly_decreasing(values: list[float], epsilon: float = 0.001) -> list[float]:
    """Clamp values to a strictly decreasing sequence with minimal downward edits."""

    if not values:
        return []

    out = [float(values[0])]
    for value in values[1:]:
        candidate = float(value)
        if candidate >= out[-1]:
            candidate = out[-1] - epsilon
        out.append(candidate)
    return out


def evaluate_monotone_cubic(xs: list[int], ys: list[float], x: int) -> float:
    """Evaluate a monotone cubic Hermite interpolant."""

    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")
    if len(xs) < 2:
        raise ValueError("At least two support points are required")

    slopes = [
        (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i])
        for i in range(len(xs) - 1)
    ]
    tangents = monotone_tangents(xs, slopes)

    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]

    interval = 0
    while interval < len(xs) - 2 and x > xs[interval + 1]:
        interval += 1

    x0 = xs[interval]
    x1 = xs[interval + 1]
    y0 = ys[interval]
    y1 = ys[interval + 1]
    m0 = tangents[interval]
    m1 = tangents[interval + 1]
    h = x1 - x0
    t = (x - x0) / h

    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return h00 * y0 + h10 * h * m0 + h01 * y1 + h11 * h * m1


def monotone_tangents(xs: list[int], slopes: list[float]) -> list[float]:
    """Return monotonicity-preserving cubic tangents for monotone data."""

    tangents = [0.0 for _ in xs]
    tangents[0] = slopes[0]
    tangents[-1] = slopes[-1]

    for i in range(1, len(xs) - 1):
        left = slopes[i - 1]
        right = slopes[i]
        if left == 0.0 or right == 0.0 or (left > 0.0) != (right > 0.0):
            tangents[i] = 0.0
            continue

        h_left = xs[i] - xs[i - 1]
        h_right = xs[i + 1] - xs[i]
        w1 = 2 * h_right + h_left
        w2 = h_right + 2 * h_left
        tangents[i] = (w1 + w2) / ((w1 / left) + (w2 / right))

    return tangents
