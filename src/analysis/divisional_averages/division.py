"""Authoritative conversion from a chii to its professional division."""

from __future__ import annotations

from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.Chii import Chii


def division_name(chii: Chii) -> str:
    """Return the six-division name represented by ``chii``."""

    if isinstance(chii.level, MSD):
        return "Makuuchi"
    names = {
        Division.JURYO: "Juryo",
        Division.MAKUSHITA: "Makushita",
        Division.SANDANME: "Sandanme",
        Division.JONIDAN: "Jonidan",
        Division.JONOKUCHI: "Jonokuchi",
    }
    try:
        return names[chii.level]
    except KeyError as error:
        raise ValueError(f"Unsupported professional division for {chii}") from error

