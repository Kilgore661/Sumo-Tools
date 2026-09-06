"""Descriptive winner counts, with no fitted probability model."""

from dataclasses import dataclass

from src.analysis.prediction.bouts import select_rated_bouts
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import Date, History


DIVISIONS = ("MAKUUCHI", "JURYO", "MAKUSHITA", "SANDANME", "JONIDAN", "JONOKUCHI")


@dataclass(frozen=True)
class CountRow:
    population: str
    bouts: int
    higher_chii_wins: int

    @property
    def win_fraction(self) -> float | None:
        return self.higher_chii_wins / self.bouts if self.bouts else None


@dataclass(frozen=True)
class Analysis:
    first_basho: str
    last_basho: str
    basho_count: int
    rows: tuple[CountRow, ...]
    raw_results: int
    excluded_fusen: int
    excluded_other_outcomes: int
    excluded_missing_chii: int
    excluded_equal_chii: int


def analyse(history: History, *, start: Date, end: Date) -> Analysis:
    """Count each W/L bout once; lower ordinal means stronger chii.

    Division rows require both participants in that division. Cross-division
    bouts form a separate group, included in ALL. Missing ranks are excluded
    and reported, as are source records assigning equal chii to opponents.
    """
    if end < start:
        raise ValueError("End must not precede start")
    dates = sorted(date for date in history if start <= date <= end)
    if not dates:
        raise ValueError("No basho in the selected date range")
    selected = select_rated_bouts(history, start_date=start, end_date=end)
    counts = {name: [0, 0] for name in ("ALL", *DIVISIONS, "CROSS_DIVISION")}
    missing = 0
    equal = 0
    for bout in selected.bouts:
        contest = bout.contest
        ranks = history[contest.id.date].banzuke.rikchii
        a = ranks.get(contest.rikishi_a)
        b = ranks.get(contest.rikishi_b)
        if a is None or b is None:
            missing += 1
            continue
        if a.ordinal() == b.ordinal():
            equal += 1
            continue
        division_a = Division.MAKUUCHI if isinstance(a.level, MSD) else a.level
        division_b = Division.MAKUUCHI if isinstance(b.level, MSD) else b.level
        group = division_a.name if division_a == division_b else "CROSS_DIVISION"
        follows_chii = (a.ordinal() < b.ordinal()) == bout.a_won
        for name in ("ALL", group):
            counts[name][0] += 1
            counts[name][1] += int(follows_chii)
    return Analysis(
        str(dates[0]), str(dates[-1]), len(dates),
        tuple(CountRow(name, *values) for name, values in counts.items()),
        selected.raw_result_count, selected.excluded_fusen_count,
        selected.excluded_draw_count, missing, equal,
    )
