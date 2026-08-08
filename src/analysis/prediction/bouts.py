"""Select the chronological binary bout stream owned by Proposal 1."""

from __future__ import annotations

from dataclasses import dataclass

from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.BasicPrimitives import Day, Pair, RikId
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class BoutId:
    """Deterministic identity of one represented result."""

    date: Date
    day: Day
    pair: Pair


@dataclass(frozen=True)
class Contest:
    """A bout presented to a prediction producer without its result."""

    id: BoutId

    @property
    def rikishi_a(self) -> RikId:
        return self.id.pair[0]

    @property
    def rikishi_b(self) -> RikId:
        return self.id.pair[1]


@dataclass(frozen=True)
class RatedBout:
    """An eligible binary result in canonical participant orientation."""

    contest: Contest
    a_won: bool


@dataclass(frozen=True)
class BoutSelection:
    """Rated bouts and exact counts of the excluded outcome domains."""

    bouts: tuple[RatedBout, ...]
    raw_result_count: int
    rated_bout_count: int
    excluded_fusen_count: int
    excluded_draw_count: int


def select_rated_bouts(
    history: History,
    *,
    start_date: Date,
    end_date: Date,
) -> BoutSelection:
    """Return every W/L result in the inclusive date interval."""

    bouts: list[RatedBout] = []
    raw_result_count = 0
    excluded_fusen_count = 0
    excluded_draw_count = 0

    dates = sorted(
        date for date in history
        if start_date <= date <= end_date
    )
    for date in dates:
        summary = history[date].summary
        for day in sorted(summary):
            results = sorted(
                summary[day].results_lookup.values(),
                key=lambda bout: Pair(bout.rikishi1, bout.rikishi2),
            )
            for bout in results:
                raw_result_count += 1
                outcome_pair = {bout.outcome1, bout.outcome2}
                if outcome_pair == {Outcome.W, Outcome.L}:
                    pair = Pair(bout.rikishi1, bout.rikishi2)
                    outcome_a = (
                        bout.outcome1
                        if bout.rikishi1 == pair[0]
                        else bout.outcome2
                    )
                    bouts.append(
                        RatedBout(
                            contest=Contest(BoutId(date=date, day=day, pair=pair)),
                            a_won=outcome_a == Outcome.W,
                        )
                    )
                elif outcome_pair == {Outcome.FS, Outcome.FP}:
                    excluded_fusen_count += 1
                else:
                    excluded_draw_count += 1

    return BoutSelection(
        bouts=tuple(bouts),
        raw_result_count=raw_result_count,
        rated_bout_count=len(bouts),
        excluded_fusen_count=excluded_fusen_count,
        excluded_draw_count=excluded_draw_count,
    )
