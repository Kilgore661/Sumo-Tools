"""Chii-domain support policies for Equelo experiments."""

from __future__ import annotations

from src.sumo_core.BasicEnums import Annotation, Division, MSD, Side
from src.sumo_core.Chii import Chii


POLICY_NAME = "rank_family_support_collapse"
POLICY_SHORT_NAME = "RFSC"


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
    """
    Apply Rank-Family Support Collapse.

    RFSC removes annotations, and maps numbered Y/O/S/K overflow slots to the
    west side of the canonical rank-family pair. It is intentionally not the v5
    public-landmark policy.
    """

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

