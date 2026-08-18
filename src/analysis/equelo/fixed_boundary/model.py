"""Prior-key model for the experimental Makuuchi--Juryo boundary producer."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from src.analysis.boundary_positions import boundary_positions
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


MJ_BOUNDARY = "mj_boundary"
JMS_BOUNDARY = "jms_boundary"
LITERAL_CHII = "literal_chii"


@dataclass(frozen=True, order=True)
class PriorKey:
    """One bucket in the entrant-prior fixed-point map."""

    kind: str
    value: int


@dataclass(frozen=True)
class PriorWorld:
    """Contextual prior keys assigned from complete pre-filter banzuke."""

    key_by_date_rikishi: dict[Date, dict[RikId, PriorKey]]
    labels: dict[PriorKey, str]
    appearances: Counter[PriorKey]

    @property
    def keys(self) -> frozenset[PriorKey]:
        return frozenset(self.appearances)


def build_prior_world(history: History) -> PriorWorld:
    """Assign M/J boundary indices and literal lower-division chii keys."""

    key_by_date_rikishi: dict[Date, dict[RikId, PriorKey]] = {}
    labels: dict[PriorKey, str] = {}
    appearances: Counter[PriorKey] = Counter()

    for date in sorted(history):
        banzuke = history[date].banzuke
        positions = boundary_positions(banzuke.rikchii)
        date_keys: dict[RikId, PriorKey] = {}
        for rikid, chii in banzuke.rikchii.items():
            division, from_top, from_bottom = positions[rikid]
            if division == "M":
                key = PriorKey(MJ_BOUNDARY, -from_bottom)
                label = f"M/J {key.value}"
            elif division == "J":
                key = PriorKey(MJ_BOUNDARY, from_top - 1)
                label = f"M/J +{key.value}"
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


def build_literal_prior_world(history: History) -> PriorWorld:
    """Assign the fixed-supported literal-chii key to every rikishi."""

    key_by_date_rikishi: dict[Date, dict[RikId, PriorKey]] = {}
    labels: dict[PriorKey, str] = {}
    appearances: Counter[PriorKey] = Counter()

    for date in sorted(history):
        date_keys: dict[RikId, PriorKey] = {}
        for rikid, chii in history[date].banzuke.rikchii.items():
            collapsed = collapse_chii(chii)
            key = PriorKey(LITERAL_CHII, collapsed.ordinal())
            date_keys[rikid] = key
            labels[key] = str(collapsed)
            appearances[key] += 1
        key_by_date_rikishi[date] = date_keys

    return PriorWorld(
        key_by_date_rikishi=key_by_date_rikishi,
        labels=labels,
        appearances=appearances,
    )


def build_jms_prior_world(history: History) -> PriorWorld:
    """Assign contextual keys around the Juryo--Makushita boundary."""

    key_by_date_rikishi: dict[Date, dict[RikId, PriorKey]] = {}
    labels: dict[PriorKey, str] = {}
    appearances: Counter[PriorKey] = Counter()

    for date in sorted(history):
        banzuke = history[date].banzuke
        positions = boundary_positions(banzuke.rikchii)
        date_keys: dict[RikId, PriorKey] = {}
        for rikid, chii in banzuke.rikchii.items():
            division, from_top, from_bottom = positions[rikid]
            if division == "J":
                key = PriorKey(JMS_BOUNDARY, -from_bottom)
                label = f"J/Ms {key.value}"
            elif division == "Ms":
                key = PriorKey(JMS_BOUNDARY, from_top - 1)
                label = f"J/Ms +{key.value}"
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


def key_sort_value(key: PriorKey) -> tuple[int, int]:
    """Return the stable public/report order for a prior key."""

    return (0 if key.kind in {MJ_BOUNDARY, JMS_BOUNDARY} else 1, key.value)
