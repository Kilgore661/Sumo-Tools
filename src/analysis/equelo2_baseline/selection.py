"""Select every represented binary result without consulting kimarite."""

from __future__ import annotations

from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Pair
from src.sumo_core.BashoState import BashoState
from src.sumo_core.History import Date

from .model import BashoSelection, ExcludedBout, SelectedBout


def select_basho_bouts(date: Date, basho: BashoState) -> BashoSelection:
    """Select W/L bouts whose two participants occupy the represented banzuke."""

    bouts: list[SelectedBout] = []
    excluded: list[ExcludedBout] = []
    raw_count = 0
    fusen_count = 0
    non_binary_count = 0
    off_banzuke_count = 0
    for day in sorted(basho.summary):
        results = sorted(
            basho.summary[day].results_lookup.values(),
            key=lambda result: Pair(result.rikishi1, result.rikishi2),
        )
        for result in results:
            raw_count += 1
            outcomes = {result.outcome1, result.outcome2}
            reason: str | None = None
            if outcomes == {Outcome.FS, Outcome.FP}:
                reason = "fusen"
                fusen_count += 1
            elif outcomes != {Outcome.W, Outcome.L}:
                reason = "non_binary_outcome"
                non_binary_count += 1
            elif (
                result.rikishi1 not in basho.banzuke.riks
                or result.rikishi2 not in basho.banzuke.riks
            ):
                reason = "participant_not_on_banzuke"
                off_banzuke_count += 1

            if reason is not None:
                excluded.append(
                    ExcludedBout(
                        date=date,
                        day=int(day),
                        rikishi_1=result.rikishi1,
                        rikishi_2=result.rikishi2,
                        outcome_1=result.outcome1.name,
                        outcome_2=result.outcome2.name,
                        decision=result.decision,
                        reason=reason,
                    )
                )
                continue

            pair = Pair(result.rikishi1, result.rikishi2)
            outcome_a = (
                result.outcome1
                if result.rikishi1 == pair[0]
                else result.outcome2
            )
            bouts.append(
                SelectedBout(
                    date=date,
                    day=int(day),
                    rikishi_a=pair[0],
                    rikishi_b=pair[1],
                    chii_a=basho.banzuke.rikchii[pair[0]],
                    chii_b=basho.banzuke.rikchii[pair[1]],
                    a_won=outcome_a == Outcome.W,
                )
            )
    return BashoSelection(
        bouts=tuple(bouts),
        excluded=tuple(excluded),
        raw_result_count=raw_count,
        rated_bout_count=len(bouts),
        excluded_fusen_count=fusen_count,
        excluded_non_binary_count=non_binary_count,
        excluded_off_banzuke_count=off_banzuke_count,
    )
