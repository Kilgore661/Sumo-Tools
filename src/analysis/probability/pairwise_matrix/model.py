"""Neutral data model for a current-banzuke pairwise probability matrix."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Mapping

from src.analysis.banzuke_compare.banzuke_diff import division_for_chii
from src.sumo_core.BasicEnums import Division
from src.sumo_core.Banzuke import Banzuke


SortOrder = Literal["rating", "chii"]


@dataclass(frozen=True, slots=True)
class RikishiRating:
    rikishi_id: int
    shikona: str
    chii: str
    chii_ordinal: int
    rating: float


@dataclass(frozen=True, slots=True)
class PairwiseSnapshot:
    basho: str
    latest_day: int
    division: str
    q: float
    rikishi: tuple[RikishiRating, ...]

    def ordered(self, order: SortOrder) -> tuple[RikishiRating, ...]:
        if order == "rating":
            return tuple(
                sorted(
                    self.rikishi,
                    key=lambda row: (-row.rating, row.chii_ordinal, row.rikishi_id),
                )
            )
        if order == "chii":
            return tuple(
                sorted(
                    self.rikishi,
                    key=lambda row: (row.chii_ordinal, -row.rating, row.rikishi_id),
                )
            )
        raise ValueError(f"Unknown matrix order: {order!r}")


def build_snapshot(
    *,
    basho: object,
    latest_day: int,
    banzuke: Banzuke,
    ratings: Mapping[str, float],
    division: Division,
    q: float,
) -> PairwiseSnapshot:
    """Select one division and attach its current Elo ratings."""

    if not math.isfinite(q) or q <= 0:
        raise ValueError("q must be a positive finite number")
    rows = []
    for rikishi in sorted(banzuke.riks, key=lambda rid: banzuke.get_chii(rid)):
        chii = banzuke.get_chii(rikishi)
        if division_for_chii(chii) != division:
            continue
        key = str(int(rikishi))
        if key not in ratings:
            raise ValueError(
                f"No rating for {banzuke.get_shik(rikishi)} ({key}) at {basho}"
            )
        rating = float(ratings[key])
        if not math.isfinite(rating):
            raise ValueError(f"Non-finite rating for rikishi {key} at {basho}")
        rows.append(
            RikishiRating(
                rikishi_id=int(rikishi),
                shikona=str(banzuke.get_shik(rikishi)),
                chii=str(chii),
                chii_ordinal=int(chii.ordinal()),
                rating=rating,
            )
        )
    if not rows:
        raise ValueError(f"No {division.name.lower()} rikishi found at {basho}")
    return PairwiseSnapshot(
        basho=str(basho),
        latest_day=int(latest_day),
        division=division.name.lower(),
        q=float(q),
        rikishi=tuple(rows),
    )


def win_probability(row_rating: float, column_rating: float, *, q: float) -> float:
    """Return P(row rikishi beats column rikishi)."""

    return 1.0 / (1.0 + 10.0 ** ((column_rating - row_rating) / q))
