"""Tests for optional playoff data consumed by production GOAT analysis."""

from __future__ import annotations

from dataclasses import dataclass

from src.goat.playoffs import (
    PlayoffDataStatus,
    playoff_evidence,
    rikishi_playoff_record,
)
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


@dataclass(frozen=True)
class ParserPlayoffBout:
    sequence: int
    winner_id: RikId
    loser_id: RikId
    source: str


def test_old_history_reports_appearances_but_not_bout_record() -> None:
    basho, history = playoff_history()

    evidence = playoff_evidence(history, basho)
    record = rikishi_playoff_record(history, RikId(1))

    assert evidence.status is PlayoffDataStatus.UNAVAILABLE
    assert evidence.expected_participants == frozenset({1, 2, 3})
    assert record.appearances == 1
    assert record.wins is None
    assert record.losses is None
    assert record.unavailable_basho == (basho,)


def test_new_history_shape_supplies_complete_multiway_record() -> None:
    basho, history = playoff_history()
    history.playoffs = {
        basho: (
            ParserPlayoffBout(2, RikId(1), RikId(3), "https://sumodb/2"),
            ParserPlayoffBout(1, RikId(1), RikId(2), "https://sumodb/1"),
        )
    }

    evidence = playoff_evidence(history, basho)
    champion = rikishi_playoff_record(history, RikId(1))
    loser = rikishi_playoff_record(history, RikId(2))

    assert evidence.status is PlayoffDataStatus.COMPLETE
    assert [bout.sequence for bout in evidence.bouts] == [1, 2]
    assert (champion.appearances, champion.wins, champion.losses) == (1, 2, 0)
    assert (loser.appearances, loser.wins, loser.losses) == (1, 0, 1)


def test_absent_detail_is_not_needed_for_a_non_playoff_basho() -> None:
    basho, history = playoff_history(playoff=False)

    evidence = playoff_evidence(history, basho)
    record = rikishi_playoff_record(history, RikId(1))

    assert evidence.status is PlayoffDataStatus.NO_PLAYOFF
    assert (record.appearances, record.wins, record.losses) == (0, 0, 0)
    assert record.bout_record_available


def test_lower_division_playoff_markers_do_not_create_makuuchi_playoff() -> None:
    basho, history = playoff_history(playoff=False)

    evidence = playoff_evidence(history, basho)

    assert evidence.status is PlayoffDataStatus.NO_PLAYOFF
    assert not evidence.expected_participants


def test_participant_mismatch_is_incomplete_not_silently_accepted() -> None:
    basho, history = playoff_history()
    history.playoffs = {
        basho: (ParserPlayoffBout(1, RikId(1), RikId(2), "source"),)
    }

    evidence = playoff_evidence(history, basho)
    record = rikishi_playoff_record(history, RikId(1))

    assert evidence.status is PlayoffDataStatus.INCOMPLETE
    assert "actual=[1, 2]" in evidence.issues[0]
    assert record.wins is None
    assert record.losses is None


def playoff_history(*, playoff: bool = True) -> tuple[Date, History]:
    ranks = {
        1: "Y1e",
        2: "O1e",
        3: "S1e",
        4: "M1e",
        5: "M1w",
        6: "M2e",
        7: "J1e",
        8: "J1w",
    }
    rikchii = RikChii(
        {RikId(rikishi_id): Chii.from_str(chii) for rikishi_id, chii in ranks.items()}
    )
    riks = Riks(rikchii)
    bouts = (_win(1, 4), _win(2, 5), _win(3, 6))
    results = ResultLookup({Pair(bout.rikishi1, bout.rikishi2): bout for bout in bouts})
    prizes = (
        {
            RikId(1): Performance(prizes=frozenset({Prize.YUSHO})),
            RikId(2): Performance(prizes=frozenset({Prize.DOTEN_YUSHO})),
            RikId(3): Performance(prizes=frozenset({Prize.DOTEN_YUSHO})),
        }
        if playoff
        else {
            RikId(1): Performance(prizes=frozenset({Prize.YUSHO})),
            RikId(7): Performance(prizes=frozenset({Prize.YUSHO})),
            RikId(8): Performance(prizes=frozenset({Prize.DOTEN_YUSHO})),
        }
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
            {Day(1): DailyResults(Torikumi(results.keys()), results)},
            Performances(prizes),
        ),
    )
    basho = Date(Year(1958), Month(1))
    return basho, History({basho: state})


def _win(winner: int, loser: int) -> BoutResult:
    return BoutResult(
        rikishi1=RikId(winner),
        outcome1=Outcome.W,
        rikishi2=RikId(loser),
        outcome2=Outcome.L,
        decision=Kimarite.YORIKIRI,
        symbol=Symbol.W,
    )
