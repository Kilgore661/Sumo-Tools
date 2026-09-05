"""Contracts for the spreadsheet-first GOAT factual producer."""

from __future__ import annotations

import csv

from src.goat.facts import build_goat_facts, extract_goat_facts
from src.sumo_core.BasicEnums import Outcome, Prize, Symbol
from src.sumo_core.BasicPrimitives import Day, Month, Pair, RikId, Riks, Shikona, Torikumi, Year
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Kimarite import Kimarite
from src.sumo_core.Performance import Performance, Performances
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def test_summary_keeps_1958_makuuchi_and_1989_all_division_scopes_separate() -> None:
    facts = extract_goat_facts(_history())
    rows = {row.rikishi_id: row for row in facts.rikishi_summary}

    assert rows[1].makuuchi_yusho_1958_onwards == 1
    assert rows[1].makuuchi_W_1958_onwards == 1
    assert rows[1].all_division_W_1989_onwards == 1
    assert rows[1].makuuchi_banzuke_basho_1958_onwards == 1
    assert rows[1].yokozuna_banzuke_basho_1958_onwards == 1
    assert rows[2].makuuchi_W_1958_onwards == 0
    assert rows[1].makuuchi_contested_bouts_with_opponent_level_1958_onwards == 1
    assert rows[1].makuuchi_mean_opponent_level_1958_onwards == 4


def test_juryo_level_follows_the_last_maegashira_rank() -> None:
    facts = extract_goat_facts(_history())
    levels = {
        (row.basho, row.chii): row.opposition_level_index for row in facts.banzuke
    }

    assert levels[("1989/01", "M1e")] == 4
    assert levels[("1989/01", "J1e")] == 5


def test_opponent_form_uses_only_the_three_preceding_basho() -> None:
    ranks = {1: "M1e", 2: "O1e"}
    history = History(
        {
            Date(Year(1958), Month(1)): _state(ranks, _bout(2, 1), {}),
            Date(Year(1958), Month(3)): _state(ranks, _bout(2, 1), {}),
            Date(Year(1958), Month(5)): _state(ranks, _bout(2, 1), {}),
            Date(Year(1958), Month(7)): _state(ranks, _bout(1, 2), {}),
        }
    )

    facts = extract_goat_facts(history)
    current = next(row for row in facts.bouts if row.basho == "1958/07")
    summaries = {row.rikishi_id: row for row in facts.rikishi_summary}

    assert current.rikishi2_trailing_3_basho_W == 3
    assert current.rikishi2_trailing_3_basho_opportunities == 45
    assert current.rikishi2_trailing_3_basho_W_rate == 3 / 45
    assert summaries[1].makuuchi_opponent_trailing_3_basho_W_rate_bouts == 1
    assert summaries[1].makuuchi_opponent_trailing_3_basho_W_rate_unavailable_bouts == 3
    assert summaries[1].makuuchi_opponent_trailing_3_basho_W_rate_mean == 3 / 45
    assert summaries[1].makuuchi_yokozuna_or_ozeki_opponent_trailing_3_basho_W_rate_mean == 3 / 45


def test_producer_writes_csv_only_with_definitions_and_empty_playoff_header(tmp_path) -> None:
    outputs = build_goat_facts(_history(), tmp_path)

    assert not list(tmp_path.glob("*.json"))
    assert outputs.rikishi_summary_csv.exists()
    assert outputs.coverage_csv.exists()
    assert outputs.summary_definitions_csv.exists()
    assert outputs.validation_csv.exists()
    assert outputs.manifest_csv.exists()
    assert outputs.playoffs_csv.read_text(encoding="utf-8").splitlines() == [
        "basho,sequence,winner_id,loser_id,source"
    ]
    with outputs.manifest_csv.open(encoding="utf-8", newline="") as stream:
        manifest = list(csv.DictReader(stream))
    assert any(row["name"] == "rikishi_summary.csv" for row in manifest)


def _history() -> History:
    return History(
        {
            Date(Year(1958), Month(1)): _state(
                {1: "Y1e", 2: "J1e"},
                _bout(1, 2),
                {1: frozenset({Prize.YUSHO})},
            ),
            Date(Year(1989), Month(1)): _state(
                {1: "J1e", 2: "M1e"},
                _bout(1, 2),
                {},
            ),
        }
    )


def _state(ranks, bout, prizes) -> BashoState:
    rikchii = RikChii({RikId(rid): Chii.from_str(chii) for rid, chii in ranks.items()})
    riks = Riks(rikchii)
    lookup = ResultLookup({Pair(bout.rikishi1, bout.rikishi2): bout})
    return BashoState(
        Banzuke(
            riks,
            rikchii,
            RikShikona({rid: Shikona(f"Rikishi {int(rid)}") for rid in riks}),
        ),
        Summary(
            {Day(1): DailyResults(Torikumi(lookup.keys()), lookup)},
            Performances(
                {RikId(rid): Performance(prizes=markers) for rid, markers in prizes.items()}
            ),
        ),
    )


def _bout(winner: int, loser: int) -> BoutResult:
    return BoutResult(
        RikId(winner), Outcome.W, RikId(loser), Outcome.L,
        Kimarite.YORIKIRI, Symbol.W,
    )
