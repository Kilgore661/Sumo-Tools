from pdb import set_trace

"""Historical cleansing logic used by Expt1.

This module still lives under ``expt1`` so the experiment is self-contained,
but its behaviour is intentionally documented as shared preprocessing logic.
If Expt2 depends on the same rules, this module is a candidate for promotion to
shared infrastructure.
"""

from dataclasses import dataclass
from typing import Any, Callable

from ....sumo_core.BasicEnums import MSD, Division, Annotation, Side
from ....sumo_core.BasicPrimitives import RikId, Riks, Torikumi
from ....sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from ....sumo_core.BashoState import BashoState
from ....sumo_core.Chii import Chii
from ....sumo_core.History import History
from ....sumo_core.Summary import Summary, DailyResults, ResultLookup


Bios = dict[RikId, dict[str, Any]]
ChiiCollapseFn = Callable[[Chii], Chii]


@dataclass(frozen=True)
class Oracle:
    """Cleaned historical input for Elo simulation."""

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


def _collapse_chii_bucket(chii: Chii) -> Chii:
    """Collapse chii to the coarser bucket scheme.

    Rules:
        * Y, O, S, K -> Y1e, O1e, S1e, K1e respectively
        * all other levels -> keep level + number, force east
        * annotations are always removed
    """
    top_levels = {
        MSD.YOKOZUNA,
        MSD.OZEKI,
        MSD.SEKIWAKE,
        MSD.KOMUSUBI,
    }

    if chii.level in top_levels:
        return Chii(
            level=chii.level,
            number=1,
            side=Side.EAST,
            ann=Annotation.EMPTY,
        )

    return Chii(
        level=chii.level,
        number=chii.number,
        side=Side.EAST,
        ann=Annotation.EMPTY,
    )


def _rebuild_banzuke(
    original_banzuke: Banzuke,
    rikishi_to_keep: set[RikId],
    collapse_fn: ChiiCollapseFn,
) -> Banzuke:
    riks = Riks(rikishi_to_keep)

    rikchii = RikChii({
        rid: collapse_fn(original_banzuke.rikchii[rid])
        for rid in rikishi_to_keep
    })

    rikshik = RikShikona({
        rid: original_banzuke.rikshik[rid]
        for rid in rikishi_to_keep
    })

    return Banzuke(riks=riks, rikchii=rikchii, rikshik=rikshik)

def _is_ignored_rank(chii: Chii) -> bool:
    return (
        chii.level == MSD.MAEGASHIRA
        and 19 <= chii.number <= 22
    )

def _filter_basho_pre_1989(
    basho: BashoState,
    collapse_fn: ChiiCollapseFn,
) -> BashoState:
    """Apply the pre-1989 observability policy.

    Retain only bouts in which at least one participant is sekitori, then
    rebuild the banzuke from the participants in the retained bouts.
    """
    filtered_days: dict = {}
    relevant_rikishi: set[RikId] = set()

    for day, daily_results in basho.summary.items():
        filtered_lookup = ResultLookup()

        for pair, bout in daily_results.results_lookup.items():
            r1 = bout.rikishi1
            r2 = bout.rikishi2
            # Experimental hack to see if M13 problem is caused by M19-M22s (in late '50s!) but it isn't
            #if r1 in basho.banzuke.rikchii and _is_ignored_rank(basho.banzuke.rikchii[r1]) or r2 in basho.banzuke.rikchii and _is_ignored_rank(basho.banzuke.rikchii[r2]):
            #    continue

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

    rebuilt_banzuke = _rebuild_banzuke(basho.banzuke, relevant_rikishi, collapse_fn)
    return BashoState(
        banzuke=rebuilt_banzuke,
        summary=Summary(filtered_days, performances=basho.summary.performances),
    )


def _filter_basho_1989_onward(
    basho: BashoState,
    collapse_fn: ChiiCollapseFn,
) -> BashoState:
    """Apply the 1989-onward observability policy.

    Retain only bouts whose participants are both on the banzuke, then rebuild
    the banzuke on the original banzuke domain with the requested collapse rule.
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

    rebuilt_banzuke = _rebuild_banzuke(
        basho.banzuke,
        set(basho.banzuke.riks),
        collapse_fn,
    )
    return BashoState(
        banzuke=rebuilt_banzuke,
        summary=Summary(filtered_days, performances=basho.summary.performances),
    )


def make_oracle(
    history: History,
    bios: Bios,
    *,
    collapse_mode: str = "annotation_only",
) -> Oracle:
    """Build a cleaned oracle history suitable for Elo simulation.

    Rules:
        * skip pre-1958 data
        * before 1989, keep only bouts with at least one sekitori
        * from 1989 onward, keep only bouts consistent with the banzuke
        * apply the requested chii collapse before the Elo layer sees ordinals

    collapse_mode:
        * "annotation_only": current behaviour; drop annotations only
        * "chii_bucket": Y/O/S/K -> l1e, all others -> lne
    """
    if collapse_mode == "annotation_only":
        collapse_fn = _collapse_annotation
    elif collapse_mode == "chii_bucket":
        collapse_fn = _collapse_chii_bucket
    else:
        raise ValueError(f"Unsupported collapse_mode: {collapse_mode}")

    clean_history = History()

    for date, basho in history.items():
        if date.year < 1958:
            continue

        if date.year < 1989:
            clean_basho = _filter_basho_pre_1989(basho, collapse_fn)
        else:
            clean_basho = _filter_basho_1989_onward(basho, collapse_fn)

        clean_history[date] = clean_basho

    return Oracle(history=clean_history, bios=bios)
