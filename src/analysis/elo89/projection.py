"""Project the exact Elo-89 start state for a published upcoming banzuke."""

from __future__ import annotations

import math

from src.analysis.elo_model_selection.model import rank_pair
from src.sumo_core.Banzuke import Banzuke

from .api import Elo89Artifacts


def project_basho_start_ratings(
    *, ratings: Elo89Artifacts, banzuke: Banzuke
) -> dict[str, float]:
    """Apply frozen persistence, P1WL entry and population normalization."""

    target_mean = float(ratings.manifest.get("target_mean", math.nan))
    if not math.isfinite(target_mean):
        raise ValueError("Elo-89 manifest contains no finite target_mean")

    latest_known: dict[str, float] = {}
    for date in sorted(ratings.basho_end_ratings, reverse=True):
        for rikishi, value in ratings.basho_end_ratings[date].items():
            latest_known.setdefault(str(rikishi), float(value))

    projected: dict[str, float] = {}
    for rikishi in sorted(banzuke.riks):
        key = str(int(rikishi))
        value = latest_known.get(key)
        if value is None:
            pair = rank_pair(banzuke.rikchii[rikishi])
            try:
                value = float(ratings.prior[pair])
            except KeyError as exc:
                raise ValueError(
                    f"Elo-89 prior contains no value for upcoming rank {pair}"
                ) from exc
        projected[key] = value

    if not projected:
        raise ValueError("Cannot project ratings for an empty upcoming banzuke")
    adjustment = target_mean - sum(projected.values()) / len(projected)
    return {
        rikishi: value + adjustment
        for rikishi, value in projected.items()
    }
