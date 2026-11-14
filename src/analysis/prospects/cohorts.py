from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.infra.get_bios.api import BioStore
from src.infra.parser.basho_calendar import BashoDateCoverage
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .model import CohortObservation, Population
from .age import completed_years


SANYAKU_LEVELS = frozenset(
    {MSD.KOMUSUBI, MSD.SEKIWAKE, MSD.OZEKI, MSD.YOKOZUNA}
)


@dataclass(frozen=True)
class PendingObservation:
    cohort_type: str
    rikishi_id: RikId
    division: str
    age: int
    basho_index: int
    chii: Chii
    division_debut_index: int
    division_debut_age: int


def build_pending_observations(
    history: History,
    bios: BioStore,
    population: Population,
    coverage: dict[Date, BashoDateCoverage],
):
    starts = {basho: row.start_date for basho, row in coverage.items()}
    if any(value is None for value in starts.values()):
        raise ValueError("Exact Day 1 coverage is required for all represented basho")

    first_sanyaku: dict[RikId, tuple[int, Chii]] = {}
    first_division: dict[tuple[RikId, str], tuple[int, int, Chii]] = {}
    state: dict[tuple[RikId, str, int], PendingObservation] = {}

    for index, basho in enumerate(population.dates):
        banzuke = history[basho].banzuke
        for rikishi_id, chii in banzuke.rikchii.items():
            if rikishi_id not in population.birth_dated_ids:
                continue
            if chii.level in SANYAKU_LEVELS:
                first_sanyaku.setdefault(rikishi_id, (index, chii))
                continue
            if rikishi_id in first_sanyaku:
                continue
            division = prospect_division(chii)
            if division is None:
                continue
            birth = bios[rikishi_id].birth_date
            age = completed_years(birth.value, starts[basho])
            debut = first_division.setdefault((rikishi_id, division), (index, age, chii))
            state.setdefault(
                (rikishi_id, division, age),
                PendingObservation("division_state", rikishi_id, division, age, index, chii, debut[0], debut[1]),
            )

    debut_rows = tuple(
        PendingObservation("division_debut", rikishi_id, division, age, index, chii, index, age)
        for (rikishi_id, division), (index, age, chii) in first_division.items()
    )
    return debut_rows + tuple(state.values()), first_sanyaku


def prospect_division(chii: Chii) -> str | None:
    if chii.level == MSD.MAEGASHIRA:
        return "M"
    return {
        Division.JURYO: "J",
        Division.MAKUSHITA: "Ms",
        Division.SANDANME: "Sd",
        Division.JONIDAN: "Jd",
        Division.JONOKUCHI: "Jk",
    }.get(chii.level)
