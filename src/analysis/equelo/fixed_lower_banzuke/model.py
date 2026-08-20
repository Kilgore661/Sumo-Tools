"""Prior-key model for the continuous lower-banzuke experiment."""

from __future__ import annotations

from collections import Counter

from src.analysis.boundary_positions import boundary_positions
from src.analysis.equelo.fixed_boundary.model import (
    LITERAL_CHII,
    LOWER_BANZUKE,
    PriorKey,
    PriorWorld,
)
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


LOWER_DIVISIONS = ("Ms", "Sd", "Jd", "Jk")


def build_lower_banzuke_prior_world(history: History) -> PriorWorld:
    """Assign Juryo negative indices and one continuous index below it."""

    key_by_date_rikishi: dict[Date, dict[RikId, PriorKey]] = {}
    labels: dict[PriorKey, str] = {}
    appearances: Counter[PriorKey] = Counter()

    for date in sorted(history):
        banzuke = history[date].banzuke
        positions = boundary_positions(banzuke.rikchii)
        division_sizes = Counter(
            division for division, _, _ in positions.values()
        )
        offsets: dict[str, int] = {}
        offset = 0
        for division in LOWER_DIVISIONS:
            offsets[division] = offset
            offset += division_sizes[division]

        date_keys: dict[RikId, PriorKey] = {}
        for rikid, chii in banzuke.rikchii.items():
            division, from_top, from_bottom = positions[rikid]
            if division == "J":
                key = PriorKey(LOWER_BANZUKE, -from_bottom)
                label = f"lower {key.value}"
            elif division in offsets:
                key = PriorKey(LOWER_BANZUKE, offsets[division] + from_top - 1)
                label = f"lower +{key.value}"
            else:
                collapsed = collapse_chii(chii)
                key = PriorKey(LITERAL_CHII, collapsed.ordinal())
                label = str(collapsed)
            date_keys[rikid] = key
            labels[key] = label
            appearances[key] += 1
        key_by_date_rikishi[date] = date_keys

    return PriorWorld(
        key_by_date_rikishi=key_by_date_rikishi,
        labels=labels,
        appearances=appearances,
    )
