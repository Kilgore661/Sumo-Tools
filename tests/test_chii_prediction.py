"""Check rank orientation, population denominators and exclusion accounting."""

import unittest

from src.analysis.chii_prediction.analysis import analyse
from src.analysis.chii_prediction.__main__ import parse_date
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Torikumi, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.Chii import Chii
from src.sumo_core.BashoState import BashoState
from src.sumo_core.History import History
from src.sumo_core.Summary import BoutResult, Summary, DailyResults, ResultLookup


def history_fixture():
    # Winners deliberately occur in either participant orientation, and chii
    # order deliberately differs from numeric rikishi-id order.
    ranks = {1: "M1w", 2: "M1e", 3: "J1e", 4: "J2e", 5: "Ms1e"}
    results = [
        (1, 2, Outcome.L, Outcome.W),  # stronger east wins
        (3, 4, Outcome.L, Outcome.W),  # weaker Juryo wins
        (5, 3, Outcome.L, Outcome.W),  # stronger cross-division wins
        (1, 99, Outcome.W, Outcome.L),  # missing rank
        (2, 4, Outcome.FS, Outcome.FP),  # default excluded
    ]
    lookup = {}
    for a, b, outcome_a, outcome_b in results:
        lookup[Pair(RikId(a), RikId(b))] = BoutResult(
            rikishi1=RikId(a), rikishi2=RikId(b), outcome1=outcome_a,
            outcome2=outcome_b, decision="", symbol=Symbol[outcome_a.name],
        )
    basho = BashoState(
        banzuke=Banzuke(riks=Riks(set(ranks)), rikshik=RikShikona({RikId(rid): Shikona(f"Rikishi {rid}") for rid in ranks}),
                        rikchii=RikChii({RikId(rid): Chii.from_str(rank) for rid, rank in ranks.items()})),
        summary=Summary({Day(1): DailyResults(torikumi=Torikumi(set(lookup)), results_lookup=ResultLookup(lookup))}),
    )
    return History({parse_date("1989/01"): basho})


def test_counts_orientation_cross_division_and_missing_rank():
    result = analyse(history_fixture(), start=parse_date("1989/01"), end=parse_date("1989/01"))
    rows = {row.population: row for row in result.rows}
    assert (rows["ALL"].bouts, rows["ALL"].higher_chii_wins) == (3, 2)
    assert rows["MAKUUCHI"].win_fraction == 1
    assert rows["JURYO"].win_fraction == 0
    assert rows["CROSS_DIVISION"].win_fraction == 1
    assert rows["MAKUSHITA"].win_fraction is None
    assert sum(row.bouts for row in result.rows[1:]) == rows["ALL"].bouts
    assert result.raw_results == 5
    assert result.excluded_fusen == result.excluded_missing_chii == 1
    assert result.excluded_other_outcomes == 0


def test_date_selection_and_equal_chii_exclusion():
    history = history_fixture()
    with unittest.TestCase().assertRaisesRegex(ValueError, "No basho"):
        analyse(history, start=parse_date("1990/01"), end=parse_date("1990/03"))
    with unittest.TestCase().assertRaisesRegex(ValueError, "End must not precede"):
        analyse(history, start=parse_date("1990/01"), end=parse_date("1989/01"))
    history[parse_date("1989/01")].banzuke.rikchii[RikId(2)] = Chii.from_str("M1w")
    result = analyse(history, start=parse_date("1989/01"), end=parse_date("1989/01"))
    assert result.excluded_equal_chii == 1
    assert result.rows[0].bouts == 2


if __name__ == "__main__":
    test_counts_orientation_cross_division_and_missing_rank()
    test_date_selection_and_equal_chii_exclusion()
    print("Chii prediction checks passed")
