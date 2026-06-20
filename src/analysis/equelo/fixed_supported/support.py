"""Support measurement and history filtering for fixed-supported Equelo."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from src.analysis.equelo.fixed_supported.policy import (
    collapse_chii,
    max_possible_bouts_for_chii,
)
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Riks, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History
from src.sumo_core.Summary import DailyResults, ResultLookup, Summary


SCORED_OUTCOMES = {Outcome.W, Outcome.L}


@dataclass(frozen=True)
class SupportMeasurement:
    appearances: Counter[Chii]
    max_possible_rikishi_bouts: Counter[Chii]
    actual_scored_rikishi_bouts: Counter[Chii]
    raw_members_by_collapsed_chii: dict[Chii, frozenset[Chii]]
    total_max_possible_rikishi_bouts: int
    total_actual_scored_rikishi_bouts: int
    total_actual_scored_bouts: int
    actual_scored_bouts_by_pair: Counter[tuple[Chii, Chii]] = field(
        default_factory=Counter
    )


@dataclass(frozen=True)
class FilteredHistory:
    history: History
    measurement: SupportMeasurement
    supported_chii: frozenset[Chii]
    domain_label: str
    retained_bouts: int
    ignored_bouts: int


def measure_support(history: History) -> SupportMeasurement:
    """Count support after applying rank-family support collapse."""

    appearances: Counter[Chii] = Counter()
    max_possible: Counter[Chii] = Counter()
    actual: Counter[Chii] = Counter()
    members: defaultdict[Chii, set[Chii]] = defaultdict(set)
    bout_pairs: Counter[tuple[Chii, Chii]] = Counter()
    total_max = 0
    total_actual_rikishi_bouts = 0
    total_actual_bouts = 0

    for basho in history.values():
        banzuke = basho.banzuke
        for raw_chii in banzuke.rikchii.values():
            chii = collapse_chii(raw_chii)
            bout_upper_bound = max_possible_bouts_for_chii(raw_chii)
            appearances[chii] += 1
            max_possible[chii] += bout_upper_bound
            members[chii].add(raw_chii)
            total_max += bout_upper_bound

        for daily_results in basho.summary.values():
            for bout in daily_results.results_lookup.values():
                if bout.outcome1 not in SCORED_OUTCOMES:
                    continue
                if bout.outcome2 not in SCORED_OUTCOMES:
                    continue

                chii1 = _collapsed_bout_chii(banzuke.rikchii, bout.rikishi1)
                chii2 = _collapsed_bout_chii(banzuke.rikchii, bout.rikishi2)
                if chii1 is None or chii2 is None:
                    continue

                actual[chii1] += 1
                actual[chii2] += 1
                total_actual_rikishi_bouts += 2
                total_actual_bouts += 1
                bout_pairs[_ordered_pair(chii1, chii2)] += 1

    return SupportMeasurement(
        appearances=appearances,
        max_possible_rikishi_bouts=max_possible,
        actual_scored_rikishi_bouts=actual,
        raw_members_by_collapsed_chii={
            chii: frozenset(raw_chiis)
            for chii, raw_chiis in members.items()
        },
        total_max_possible_rikishi_bouts=total_max,
        total_actual_scored_rikishi_bouts=total_actual_rikishi_bouts,
        total_actual_scored_bouts=total_actual_bouts,
        actual_scored_bouts_by_pair=bout_pairs,
    )


def build_min_appearances_filtered_history(
    history: History,
    *,
    min_appearances: int,
) -> FilteredHistory:
    """Keep collapsed chii with enough basho-start appearances."""

    if min_appearances < 1:
        raise ValueError(f"min_appearances must be positive: {min_appearances}")

    measurement = measure_support(history)
    supported_chii = frozenset(
        chii
        for chii, appearances in measurement.appearances.items()
        if appearances >= min_appearances
    )
    filtered_history, retained_bouts, ignored_bouts = _filter_history(
        history,
        supported_chii=supported_chii,
    )
    return FilteredHistory(
        history=filtered_history,
        measurement=measurement,
        supported_chii=supported_chii,
        domain_label=f"min_appearances_{min_appearances}",
        retained_bouts=retained_bouts,
        ignored_bouts=ignored_bouts,
    )


def _filter_history(
    history: History,
    *,
    supported_chii: frozenset[Chii],
) -> tuple[History, int, int]:
    filtered = History()
    retained_bouts = 0
    ignored_bouts = 0

    for date in sorted(history.keys()):
        basho = history[date]
        collapsed_by_rikishi = {
            rikid: collapse_chii(chii)
            for rikid, chii in basho.banzuke.rikchii.items()
        }
        rikishi_to_keep = {
            rikid
            for rikid, chii in collapsed_by_rikishi.items()
            if chii in supported_chii
        }
        banzuke = Banzuke(
            riks=Riks(rikishi_to_keep),
            rikchii=RikChii({
                rikid: collapsed_by_rikishi[rikid]
                for rikid in rikishi_to_keep
            }),
            rikshik=RikShikona({
                rikid: basho.banzuke.rikshik[rikid]
                for rikid in rikishi_to_keep
            }),
        )
        summary, kept, ignored = _filter_summary(
            basho.summary,
            rikishi_to_keep=rikishi_to_keep,
        )
        retained_bouts += kept
        ignored_bouts += ignored
        filtered[date] = BashoState(banzuke=banzuke, summary=summary)

    return filtered, retained_bouts, ignored_bouts


def _filter_summary(
    summary: Summary,
    *,
    rikishi_to_keep: set,
) -> tuple[Summary, int, int]:
    filtered_days = {}
    retained_bouts = 0
    ignored_bouts = 0

    for day in sorted(summary.keys()):
        filtered_lookup = ResultLookup()
        for pair, bout in summary[day].results_lookup.items():
            if bout.rikishi1 in rikishi_to_keep and bout.rikishi2 in rikishi_to_keep:
                filtered_lookup[pair] = bout
                retained_bouts += 1
            else:
                ignored_bouts += 1
        filtered_days[day] = DailyResults(
            torikumi=Torikumi(filtered_lookup.keys()),
            results_lookup=filtered_lookup,
        )

    return Summary(filtered_days, performances=summary.performances), retained_bouts, ignored_bouts


def _collapsed_bout_chii(rikchii, rikishi_id) -> Chii | None:
    raw_chii = rikchii.get(rikishi_id)
    return None if raw_chii is None else collapse_chii(raw_chii)


def _ordered_pair(chii1: Chii, chii2: Chii) -> tuple[Chii, Chii]:
    if chii1.ordinal() <= chii2.ordinal():
        return chii1, chii2
    return chii2, chii1
