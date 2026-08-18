"""Supported-domain filtering for the joint boundary model."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import Riks, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.History import History
from src.sumo_core.Summary import DailyResults, ResultLookup, Summary

from .model import DualBoundaryWorld


@dataclass(frozen=True)
class FilteredDualHistory:
    history: History
    world: DualBoundaryWorld
    supported_keys: frozenset
    retained_bouts: int
    ignored_bouts: int


def build_supported_history(
    history: History,
    world: DualBoundaryWorld,
    *,
    min_appearances: int,
) -> FilteredDualHistory:
    supported = frozenset(
        key for key, count in world.appearances.items() if count >= min_appearances
    )
    filtered = History()
    filtered_assignments = {}
    retained_bouts = 0
    ignored_bouts = 0

    for date in sorted(history):
        basho = history[date]
        assignments = world.assignments_by_date_rikishi[date]
        date_assignments = {}
        retained = set()
        for rikid in basho.banzuke.riks:
            available = [
                item for item in assignments[rikid] if item.key in supported
            ]
            if not available:
                continue
            total_weight = sum(item.weight for item in available)
            date_assignments[rikid] = tuple(
                type(item)(item.key, item.weight / total_weight)
                for item in available
            )
            retained.add(rikid)
        filtered_assignments[date] = date_assignments
        banzuke = Banzuke(
            riks=Riks(retained),
            rikchii=RikChii({rikid: basho.banzuke.rikchii[rikid] for rikid in retained}),
            rikshik=RikShikona({rikid: basho.banzuke.rikshik[rikid] for rikid in retained}),
        )
        days = {}
        for day in sorted(basho.summary):
            lookup = ResultLookup()
            for pair, bout in basho.summary[day].results_lookup.items():
                if bout.rikishi1 in retained and bout.rikishi2 in retained:
                    lookup[pair] = bout
                    retained_bouts += 1
                else:
                    ignored_bouts += 1
            days[day] = DailyResults(
                torikumi=Torikumi(lookup.keys()), results_lookup=lookup
            )
        filtered[date] = BashoState(
            banzuke=banzuke,
            summary=Summary(days, performances=basho.summary.performances),
        )
    return FilteredDualHistory(
        history=filtered,
        world=DualBoundaryWorld(
            assignments_by_date_rikishi=filtered_assignments,
            labels=world.labels,
            appearances=world.appearances,
        ),
        supported_keys=supported,
        retained_bouts=retained_bouts,
        ignored_bouts=ignored_bouts,
    )
