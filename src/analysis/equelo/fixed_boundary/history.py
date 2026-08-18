"""Supported-domain history construction for contextual prior keys."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.BasicPrimitives import Riks, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.History import History
from src.sumo_core.Summary import DailyResults, ResultLookup, Summary

from .model import PriorKey, PriorWorld


@dataclass(frozen=True)
class FilteredPriorHistory:
    history: History
    supported_keys: frozenset[PriorKey]
    retained_bouts: int
    ignored_bouts: int


def build_supported_history(
    history: History,
    world: PriorWorld,
    *,
    min_appearances: int,
) -> FilteredPriorHistory:
    """Filter by preassigned prior-key support without recomputing positions."""

    supported = frozenset(
        key
        for key, count in world.appearances.items()
        if count >= min_appearances
    )
    filtered = History()
    retained_bouts = 0
    ignored_bouts = 0

    for date in sorted(history):
        basho = history[date]
        date_keys = world.key_by_date_rikishi[date]
        retained_rikishi = {
            rikid for rikid in basho.banzuke.riks if date_keys[rikid] in supported
        }
        banzuke = Banzuke(
            riks=Riks(retained_rikishi),
            rikchii=RikChii({
                rikid: basho.banzuke.rikchii[rikid]
                for rikid in retained_rikishi
            }),
            rikshik=RikShikona({
                rikid: basho.banzuke.rikshik[rikid]
                for rikid in retained_rikishi
            }),
        )
        days = {}
        for day in sorted(basho.summary):
            lookup = ResultLookup()
            for pair, bout in basho.summary[day].results_lookup.items():
                if bout.rikishi1 in retained_rikishi and bout.rikishi2 in retained_rikishi:
                    lookup[pair] = bout
                    retained_bouts += 1
                else:
                    ignored_bouts += 1
            days[day] = DailyResults(
                torikumi=Torikumi(lookup.keys()),
                results_lookup=lookup,
            )
        filtered[date] = BashoState(
            banzuke=banzuke,
            summary=Summary(days, performances=basho.summary.performances),
        )

    return FilteredPriorHistory(
        history=filtered,
        supported_keys=supported,
        retained_bouts=retained_bouts,
        ignored_bouts=ignored_bouts,
    )
