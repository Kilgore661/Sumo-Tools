from __future__ import annotations

import csv
from datetime import datetime

from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Month,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
    Year,
)
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Summary import (
    BoutResult,
    DailyResults,
    ResultLookup,
    Summary,
)
from src.validation.kimarite import DIVISIONS, count_missing_kimarite, write_csv


def test_counts_blank_wl_by_higher_ranked_bout_division() -> None:
    january = Date(Year(2000), Month(1))
    march = Date(Year(2000), Month(3))
    history = History()
    history[january] = _basho(
        {
            1: "M1e",
            2: "M1w",
            3: "J1e",
            4: "Ms1e",
            5: "M2e",
            6: "M2w",
        },
        [
            _bout(1, 2, "blank"),
            _bout(3, 4, "blank"),
            _bout(5, 6, Kimarite.OSHIDASHI),
        ],
    )
    history[march] = _basho({1: "M1e", 2: "M1w"}, [])

    counts = count_missing_kimarite(history)

    assert counts[january] == {
        "Makuuchi": 1,
        "Juryo": 1,
        "Makushita": 0,
        "Sandanme": 0,
        "Jonidan": 0,
        "Jonokuchi": 0,
    }
    assert counts[march] == {division: 0 for division in DIVISIONS}


def test_csv_has_row_and_column_totals_but_grand_total_is_separate(tmp_path) -> None:
    january = Date(Year(2000), Month(1))
    march = Date(Year(2000), Month(3))
    counts = {
        january: {
            division: int(division == "Makuuchi") for division in DIVISIONS
        },
        march: {
            division: int(division == "Jonokuchi") * 2 for division in DIVISIONS
        },
    }

    path, grand_total = write_csv(
        counts,
        tmp_path,
        timestamp=datetime(2026, 10, 24, 13, 14, 15),
    )

    assert path.name == (
        "missing_kimarite_by_basho_division_2000-01_to_2000-03_"
        "2026-10-24_13-14-15.csv"
    )
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["Date", *DIVISIONS, "Total"]
    assert rows[1] == ["2000-01", "1", "0", "0", "0", "0", "0", "1"]
    assert rows[2] == ["2000-03", "0", "0", "0", "0", "0", "2", "2"]
    assert rows[3] == ["Total", "1", "0", "0", "0", "0", "2", ""]
    assert grand_total == 3


def test_date_bounds_select_the_historical_interval() -> None:
    january = Date(Year(2000), Month(1))
    march = Date(Year(2000), Month(3))
    may = Date(Year(2000), Month(5))
    history = History()
    history[january] = _basho({1: "Ms1e", 2: "Ms1w"}, [_bout(1, 2, "blank")])
    history[march] = _basho({1: "Ms1e", 2: "Ms1w"}, [_bout(1, 2, "blank")])
    history[may] = _basho({1: "Ms1e", 2: "Ms1w"}, [_bout(1, 2, "blank")])

    counts = count_missing_kimarite(history, start=march, end=march)

    assert list(counts) == [march]
    assert counts[march]["Makushita"] == 1


def _basho(ranks: dict[int, str], bouts: list[BoutResult]) -> BashoState:
    rikids = {RikId(value) for value in ranks}
    lookup = ResultLookup(
        {Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts}
    )
    summary = Summary({})
    if bouts:
        summary[Day(1)] = DailyResults(
            torikumi=Torikumi(set(lookup)),
            results_lookup=lookup,
        )
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(rikids),
            rikchii=RikChii(
                {RikId(value): Chii.from_str(rank) for value, rank in ranks.items()}
            ),
            rikshik=RikShikona(
                {rikishi: Shikona(f"Rikishi {rikishi}") for rikishi in rikids}
            ),
        ),
        summary=summary,
    )


def _bout(winner: int, loser: int, decision) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(winner),
        outcome1=Outcome.W,
        rikishi2=RikId(loser),
        outcome2=Outcome.L,
        decision=decision,
        symbol=Symbol.W,
    )
