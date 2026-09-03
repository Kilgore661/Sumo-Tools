"""Tests for the GOAT playoff-marker probe."""

from __future__ import annotations

from src.analysis.goat.playoffs import probe_playoffs
from src.sumo_core.BasicEnums import Outcome, Prize, Symbol
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
from src.sumo_core.Performance import Performance, Performances
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def test_three_way_tie_accepts_y_and_two_d_markers() -> None:
    history = three_way_history(
        {
            1: frozenset({Prize.YUSHO}),
            2: frozenset({Prize.DOTEN_YUSHO}),
            3: frozenset({Prize.DOTEN_YUSHO}),
        }
    )

    probe = probe_playoffs(history)

    assert len(probe.tied_basho) == 1
    basho = probe.tied_basho[0]
    assert basho.leader_count == 3
    assert basho.yusho_count == 1
    assert basho.doten_yusho_count == 2
    assert not probe.findings


def test_three_way_tie_reports_missing_d_marker() -> None:
    history = three_way_history(
        {
            1: frozenset({Prize.YUSHO}),
            2: frozenset({Prize.DOTEN_YUSHO}),
        }
    )

    probe = probe_playoffs(history)

    assert [finding.kind for finding in probe.findings] == [
        "doten_marker_mismatch"
    ]
    assert "Expected D=[2, 3]" in probe.findings[0].detail


def three_way_history(prizes_by_id: dict[int, frozenset[Prize]]) -> History:
    ranks = {
        1: "Y1e",
        2: "O1e",
        3: "S1e",
        4: "M1e",
        5: "M1w",
        6: "M2e",
    }
    rikchii = RikChii(
        {RikId(rikishi_id): Chii.from_str(chii) for rikishi_id, chii in ranks.items()}
    )
    riks = Riks(rikchii)
    bouts = (
        winning_bout(1, 4),
        winning_bout(2, 5),
        winning_bout(3, 6),
    )
    results = ResultLookup(
        {Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts}
    )
    state = BashoState(
        banzuke=Banzuke(
            riks=riks,
            rikchii=rikchii,
            rikshik=RikShikona(
                {
                    rikishi_id: Shikona(f"Rikishi {int(rikishi_id)}")
                    for rikishi_id in riks
                }
            ),
        ),
        summary=Summary(
            {
                Day(1): DailyResults(
                    torikumi=Torikumi(results.keys()),
                    results_lookup=results,
                )
            },
            Performances(
                {
                    RikId(rikishi_id): Performance(prizes=prizes)
                    for rikishi_id, prizes in prizes_by_id.items()
                }
            ),
        ),
    )
    return History({Date(Year(1958), Month(1)): state})


def winning_bout(winner: int, loser: int) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(winner),
        outcome1=Outcome.W,
        rikishi2=RikId(loser),
        outcome2=Outcome.L,
        decision=Kimarite.YORIKIRI,
        symbol=Symbol.W,
    )
