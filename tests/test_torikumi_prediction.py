"""Tests for empirical torikumi opponent distributions."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone

import pytest

from src.analysis.torikumi_prediction.analysis import analyse
from src.analysis.torikumi_prediction.__main__ import parse_date
from src.analysis.torikumi_prediction.model import BanzukeClass
from src.analysis.torikumi_prediction.output import write_outputs
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import Day, Pair, RikId, Riks, Shikona, Torikumi
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History
from src.sumo_core.Summary import BoutResult, DailyResults, ResultLookup, Summary


def _result(a: int, b: int, outcome_a: Outcome, outcome_b: Outcome) -> BoutResult:
    return BoutResult(
        RikId(a), outcome_a, RikId(b), outcome_b,
        "fusen" if {outcome_a, outcome_b} == {Outcome.FS, Outcome.FP} else "blank",
        Symbol[outcome_a.name],
    )


def _daily(*results: BoutResult, extra_pairs=()) -> DailyResults:
    lookup = ResultLookup({Pair(result.rikishi1, result.rikishi2): result for result in results})
    return DailyResults(Torikumi(set(lookup) | set(extra_pairs)), lookup)


def _history(*, completed: bool = True) -> History:
    ranks = {1: "O1e", 2: "O2w", 3: "M1e", 4: "J1e", 5: "Ms1w"}
    day1 = _daily(
        _result(1, 3, Outcome.W, Outcome.L),
        _result(4, 5, Outcome.L, Outcome.W),
        _result(2, 99, Outcome.FS, Outcome.FP),
    )
    day2 = _daily(_result(1, 2, Outcome.L, Outcome.W))
    last_day = 15 if completed else 14
    days = {Day(1): day1, Day(2): day2}
    days.update(
        {Day(day): DailyResults(Torikumi(), ResultLookup()) for day in range(3, last_day + 1)}
    )
    banzuke = Banzuke(
        riks=Riks(RikId(rikishi) for rikishi in ranks),
        rikchii=RikChii({RikId(rikishi): Chii.from_str(chii) for rikishi, chii in ranks.items()}),
        rikshik=RikShikona({RikId(rikishi): Shikona(f"Rikishi {rikishi}") for rikishi in ranks}),
    )
    return History({
        parse_date("2026/01"): BashoState(banzuke=banzuke, summary=Summary(days))
    })


def test_class_grouping_preserves_number_only_where_required():
    assert BanzukeClass.from_chii(Chii.from_str("Y2wHD")).label == "Y"
    assert BanzukeClass.from_chii(Chii.from_str("O3e")).label == "O"
    assert BanzukeClass.from_chii(Chii.from_str("M17w")).label == "M17"
    assert BanzukeClass.from_chii(Chii.from_str("Ms12eTD")).label == "Ms12"


def test_extracts_all_divisions_records_crossings_fusen_and_mz():
    result = analyse(_history())
    assert result.included_basho_count == 1
    assert result.scheduled_bout_count == 4
    assert len(result.observations) == 7  # one endpoint is unranked

    day2 = [row for row in result.observations if row.day == 2]
    assert {(row.focal_id, row.focal_class, row.opponent_class) for row in day2} == {
        (1, "O", "O"), (2, "O", "O")
    }
    assert {(row.focal_id, row.wins_before, row.losses_before) for row in day2} == {
        (1, 1, 0), (2, 1, 0)
    }

    mz = next(row for row in result.observations if row.opponent_class == "Mz")
    assert mz.focal_id == 2
    assert mz.opponent_chii == mz.opponent_division == ""
    assert mz.fusen and not mz.cross_division

    cross = [row for row in result.observations if row.cross_division]
    assert len(cross) == 2
    assert {row.focal_division for row in cross} == {"JURYO", "MAKUSHITA"}
    assert {row.roster_position_delta for row in cross} == {-1, 1}

    kinds = Counter(row.kind for row in result.diagnostics)
    assert kinds == {"missing_focal_chii": 1, "missing_opponent_chii": 1}


def test_aggregates_reconcile_and_use_directed_denominators():
    result = analyse(_history())
    o_day1 = [
        row for row in result.class_by_day
        if row.focal_class == "O" and row.day == 1
    ]
    assert {(row.opponent_class, row.observations) for row in o_day1} == {
        ("M1", 1), ("Mz", 1)
    }
    assert all(row.focal_total == 2 and row.probability == 0.5 for row in o_day1)

    for rows, group in (
        (result.class_by_day, lambda row: (row.focal_division, row.focal_class, row.day)),
        (result.class_by_day_wins, lambda row: (row.focal_division, row.focal_class, row.day, row.wins_before)),
        (result.class_by_record, lambda row: (
            row.focal_division, row.focal_class, row.day, row.wins_before, row.losses_before,
            row.bouts_before, row.bout_number,
        )),
        (result.overall_class, lambda row: (row.focal_division, row.focal_class)),
    ):
        probability_sums = {}
        for row in rows:
            probability_sums[group(row)] = probability_sums.get(group(row), 0.0) + row.probability
        assert all(total == pytest.approx(1.0) for total in probability_sums.values())


def test_incomplete_basho_are_excluded():
    with pytest.raises(ValueError, match="No completed basho"):
        analyse(_history(completed=False))


def test_writes_all_outputs_and_empty_diagnostics_header(tmp_path):
    history = _history()
    # Remove the missing-banzuke pair so the diagnostics output is deliberately empty.
    history[parse_date("2026/01")].summary[Day(1)].torikumi.remove(Pair(RikId(2), RikId(99)))
    del history[parse_date("2026/01")].summary[Day(1)].results_lookup[Pair(RikId(2), RikId(99))]
    result = analyse(history)
    outputs = write_outputs(
        result,
        source={"kind": "fixture", "path": "fixture.zip", "sha256": "abc"},
        output_root=tmp_path,
        generated_at=datetime(2026, 9, 28, tzinfo=timezone.utc),
    )
    assert all(
        path.is_file()
        for name, path in outputs.__dict__.items()
        if name != "run_directory"
    )
    with outputs.diagnostics_csv.open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.DictReader(stream)) == []
    manifest = json.loads(outputs.manifest_json.read_text(encoding="utf-8"))
    assert manifest["counts"]["observations"] == 6
    assert manifest["counts"]["diagnostics"] == 0


def test_draws_fail_the_no_draw_contract():
    history = _history()
    drawn = _result(1, 3, Outcome.DRAW, Outcome.DRAW)
    history[parse_date("2026/01")].summary[Day(1)] = _daily(drawn)
    with pytest.raises(ValueError, match="Draw result"):
        analyse(history)
