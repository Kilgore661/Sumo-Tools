from __future__ import annotations

from src.infra.get_bios.api import BioStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History

from ..eligible_rikishi import select_complete_record_population
from .model import ExclusionRow, Population


def build_population(
    history: History,
    bios: BioStore,
    *,
    epoch: Date | None = None,
) -> Population:
    selected = select_complete_record_population(history, epoch=epoch)
    first = _first_observations(history, selected.dates)
    exclusions: list[ExclusionRow] = []
    for rikishi_id in sorted(selected.boundary_ids, key=int):
        exclusions.append(_exclusion(rikishi_id, "boundary_incumbent", first, "present on epoch banzuke"))

    birth_dated: set[RikId] = set()
    for rikishi_id in sorted(selected.complete_ids, key=int):
        bio = bios.bios.get(rikishi_id)
        if bio is None:
            exclusions.append(_exclusion(rikishi_id, "missing_bio", first, "no parsed bio record"))
        elif bio.birth_date is None:
            exclusions.append(_exclusion(rikishi_id, "missing_birth_date", first, "no usable full birth date"))
        else:
            birth_dated.add(rikishi_id)

    return Population(
        epoch=selected.epoch,
        cutoff=selected.last_basho,
        dates=selected.dates,
        history_ids=selected.observed_ids,
        boundary_ids=selected.boundary_ids,
        complete_ids=selected.complete_ids,
        birth_dated_ids=frozenset(birth_dated),
        exclusions=tuple(exclusions),
    )


def _first_observations(history: History, dates: tuple[Date, ...]):
    first = {}
    for basho in dates:
        for rikishi_id in history[basho].banzuke.riks:
            first.setdefault(
                rikishi_id,
                (
                    str(history[basho].banzuke.rikshik[rikishi_id]),
                    str(basho),
                    str(history[basho].banzuke.rikchii[rikishi_id]),
                ),
            )
    return first


def _exclusion(rikishi_id, reason, first, detail):
    shikona, basho, chii = first[rikishi_id]
    return ExclusionRow(int(rikishi_id), shikona, reason, basho, chii, detail)
