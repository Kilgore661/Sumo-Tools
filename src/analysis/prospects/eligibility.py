"""Complete-record population selection for the 1989+ prospects analysis."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class CompleteRecordPopulation:
    epoch: Date
    last_basho: Date
    dates: tuple[Date, ...]
    observed_ids: frozenset[RikId]
    boundary_ids: frozenset[RikId]
    complete_ids: frozenset[RikId]


def select_complete_record_population(history: History) -> CompleteRecordPopulation:
    dates = tuple(sorted(history))
    if not dates:
        raise ValueError("Prospects analysis requires a non-empty History")
    epoch = dates[0]
    if str(epoch) != "1989/01":
        raise ValueError("Prospects production History must begin at 1989/01")
    boundary_ids = frozenset(history[epoch].banzuke.riks)
    observed_ids = frozenset(
        rikishi_id for basho in dates for rikishi_id in history[basho].banzuke.riks
    )
    return CompleteRecordPopulation(
        epoch=epoch,
        last_basho=dates[-1],
        dates=dates,
        observed_ids=observed_ids,
        boundary_ids=boundary_ids,
        complete_ids=observed_ids - boundary_ids,
    )


def history_fingerprint(history: History) -> str:
    """Fingerprint the represented banzuke facts used by this analysis."""

    digest = hashlib.sha256()
    for basho in sorted(history):
        banzuke = history[basho].banzuke
        digest.update(f"{basho}\n".encode())
        for rikishi_id in sorted(banzuke.riks, key=int):
            digest.update(
                f"{int(rikishi_id)}\t{banzuke.rikchii[rikishi_id]}\t"
                f"{banzuke.rikshik[rikishi_id]}\n".encode("utf-8")
            )
    return digest.hexdigest()
