"""Measure chii support under a support-domain policy."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from src.analysis.equelo.support_domain.policy import (
    collapse_chii,
    max_possible_bouts_for_chii,
)
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History


SCORED_OUTCOMES = {Outcome.W, Outcome.L}


@dataclass(frozen=True)
class SupportMeasurement:
    """Raw and collapsed support counts for a cleaned Equelo history."""

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


def measure_support(history: History) -> SupportMeasurement:
    """Count support after applying RFSC to every banzuke chii."""

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

        for _rikid, raw_chii in banzuke.rikchii.items():
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

    frozen_members = {
        chii: frozenset(raw_chiis)
        for chii, raw_chiis in members.items()
    }
    return SupportMeasurement(
        appearances=appearances,
        max_possible_rikishi_bouts=max_possible,
        actual_scored_rikishi_bouts=actual,
        raw_members_by_collapsed_chii=frozen_members,
        total_max_possible_rikishi_bouts=total_max,
        total_actual_scored_rikishi_bouts=total_actual_rikishi_bouts,
        total_actual_scored_bouts=total_actual_bouts,
        actual_scored_bouts_by_pair=bout_pairs,
    )


def _collapsed_bout_chii(rikchii, rikishi_id) -> Chii | None:
    raw_chii = rikchii.get(rikishi_id)
    if raw_chii is None:
        return None
    return collapse_chii(raw_chii)


def _ordered_pair(chii1: Chii, chii2: Chii) -> tuple[Chii, Chii]:
    if chii1.ordinal() <= chii2.ordinal():
        return chii1, chii2
    return chii2, chii1

