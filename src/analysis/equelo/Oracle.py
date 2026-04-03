# src/analysis/equelo/Oracle.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...sumo_core.History import History, Date
from ...sumo_core.BashoState import BashoState
from ...sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from ...sumo_core.Summary import Summary, DailyResults, ResultLookup
from ...sumo_core.BasicPrimitives import RikId, Riks, Torikumi
from ...sumo_core.BasicEnums import MSD, Division, Annotation
from ...sumo_core.Chii import Chii


Bios = dict[RikId, dict[str, Any]]


@dataclass(frozen=True)
class Oracle:
    history: History
    bios: Bios


def _is_sekitori(chii: Chii) -> bool:
    return isinstance(chii.level, MSD) or chii.level == Division.JURYO


def _collapse_annotation(chii: Chii) -> Chii:
    return Chii(
        level=chii.level,
        number=chii.number,
        side=chii.side,
        ann=Annotation.EMPTY,
    )


def _rebuild_banzuke(original_banzuke: Banzuke, rikishi_to_keep: set[RikId]) -> Banzuke:
    riks = Riks(rikishi_to_keep)

    rikchii = RikChii({
        rid: _collapse_annotation(original_banzuke.rikchii[rid])
        for rid in rikishi_to_keep
    })

    rikshik = RikShikona({
        rid: original_banzuke.rikshik[rid]
        for rid in rikishi_to_keep
    })

    return Banzuke(riks=riks, rikchii=rikchii, rikshik=rikshik)


def _filter_basho_pre_1989(basho: BashoState) -> BashoState:
    """
    Pre-1989 policy:
    keep only bouts where at least one participant is sekitori,
    then rebuild the banzuke from the participants in retained bouts.
    """
    filtered_days: dict = {}
    relevant_rikishi: set[RikId] = set()

    for day, daily_results in basho.summary.items():
        filtered_lookup = ResultLookup()

        for pair, bout in daily_results.results_lookup.items():
            r1 = bout.rikishi1
            r2 = bout.rikishi2

            r1_is_sekitori = (
                r1 in basho.banzuke.rikchii and _is_sekitori(basho.banzuke.rikchii[r1])
            )
            r2_is_sekitori = (
                r2 in basho.banzuke.rikchii and _is_sekitori(basho.banzuke.rikchii[r2])
            )

            if r1_is_sekitori or r2_is_sekitori:
                filtered_lookup[pair] = bout
                relevant_rikishi.add(r1)
                relevant_rikishi.add(r2)

        if filtered_lookup:
            filtered_days[day] = DailyResults(
                torikumi=Torikumi(filtered_lookup.keys()),
                results_lookup=filtered_lookup,
            )

    rebuilt_banzuke = _rebuild_banzuke(basho.banzuke, relevant_rikishi)
    return BashoState(
        banzuke=rebuilt_banzuke,
        summary=Summary(filtered_days, performances=basho.summary.performances),
    )


def _filter_basho_1989_onward(basho: BashoState) -> BashoState:
    """
    1989 onward policy:
    keep only bouts whose participants are both on the banzuke,
    then rebuild the banzuke on the original banzuke domain.
    """
    filtered_days: dict = {}

    for day, daily_results in basho.summary.items():
        filtered_lookup = ResultLookup()

        for pair, bout in daily_results.results_lookup.items():
            r1 = bout.rikishi1
            r2 = bout.rikishi2

            if r1 in basho.banzuke.riks and r2 in basho.banzuke.riks:
                filtered_lookup[pair] = bout

        if filtered_lookup:
            filtered_days[day] = DailyResults(
                torikumi=Torikumi(filtered_lookup.keys()),
                results_lookup=filtered_lookup,
            )

    rebuilt_banzuke = _rebuild_banzuke(basho.banzuke, set(basho.banzuke.riks))
    return BashoState(
        banzuke=rebuilt_banzuke,
        summary=Summary(filtered_days, performances=basho.summary.performances),
    )


def make_oracle(history: History, bios: Bios) -> Oracle:
    """
    Build a cleaned oracle history suitable for Elo processing.
    """
    clean_history = History()

    for date, basho in history.items():
        if date.year < 1958:
            continue

        if date.year < 1989:
            clean_basho = _filter_basho_pre_1989(basho)
        else:
            clean_basho = _filter_basho_1989_onward(basho)

        clean_history[date] = clean_basho

    return Oracle(history=clean_history, bios=bios)
