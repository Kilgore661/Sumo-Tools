from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.analysis.career_bout_volume.analysis import (
    analyse_history,
    build_bout_probability_rows,
)
from src.analysis.career_bout_volume.model import HistorySource
from src.analysis.career_bout_volume import reports
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
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
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult, DailyResults, Decision, ResultLookup, Summary


def test_analysis_normalizes_actual_banzuke_and_excludes_fusen_from_fought_bouts() -> None:
    rikishi1, rikishi2, rikishi3 = RikId(1), RikId(2), RikId(3)
    history = History(
        {
            basho_date(1980, 1): basho_state(
                {
                    rikishi1: ("One", "J1e"),
                    rikishi2: ("Two", "J1w"),
                    rikishi3: ("Three", "J2e"),
                },
                {
                    Day(1): [bout(rikishi1, Outcome.W, rikishi2, Outcome.L)],
                    Day(2): [bout(rikishi2, Outcome.FS, rikishi3, Outcome.FP)],
                    Day(3): [bout(rikishi1, Outcome.DRAW, rikishi3, Outcome.DRAW)],
                },
            )
        }
    )

    result = analyse_history(history)
    by_id = {row.rikishi_id: row for row in result.basho_rows}

    assert by_id[1].normalized_position == pytest.approx(0.0)
    assert by_id[2].normalized_position == pytest.approx(0.5)
    assert by_id[3].normalized_position == pytest.approx(1.0)
    assert (by_id[1].recorded_results, by_id[1].fought_bouts) == (2, 2)
    assert (by_id[2].recorded_results, by_id[2].fought_bouts) == (2, 1)
    assert (by_id[3].recorded_results, by_id[3].fought_bouts) == (2, 1)
    assert (by_id[2].fusensho, by_id[3].fusenpai) == (1, 1)
    assert result.exception_count == 0


def test_analysis_counts_missing_banzuke_participants_and_keeps_listed_opponent() -> None:
    listed, opponent, missing = RikId(1), RikId(2), RikId(8262)
    history = History(
        {
            basho_date(1980, 1): basho_state(
                {listed: ("Listed", "J1e"), opponent: ("Opponent", "J1w")},
                {Day(1): [bout(listed, Outcome.W, missing, Outcome.L)]},
            )
        }
    )

    result = analyse_history(history)
    by_id = {row.rikishi_id: row for row in result.basho_rows}

    assert result.exception_count == 1
    assert by_id[1].fought_bouts == 1
    assert by_id[2].fought_bouts == 0


def test_career_rows_identify_completed_non_partial_primary_population() -> None:
    rikishi1, rikishi2, rikishi3, rikishi4 = (
        RikId(1),
        RikId(2),
        RikId(3),
        RikId(4),
    )
    history = History(
        {
            basho_date(1980, 1): basho_state(
                {rikishi1: ("One", "J1e"), rikishi2: ("Two", "J1w")},
                {},
            ),
            basho_date(1980, 3): basho_state(
                {
                    rikishi1: ("One", "J1e"),
                    rikishi2: ("Two", "J1w"),
                    rikishi3: ("Three", "J2e"),
                    rikishi4: ("Four", "J2w"),
                },
                {Day(1): [bout(rikishi2, Outcome.W, rikishi3, Outcome.L)]},
            ),
            basho_date(1980, 5): basho_state(
                {rikishi1: ("One", "J1e"), rikishi3: ("Three", "J1w")},
                {},
            ),
        }
    )

    result = analyse_history(history)
    by_id = {row.rikishi_id: row for row in result.career_rows}

    assert by_id[2].career_status == "partial_start"
    assert not by_id[2].primary_population
    assert by_id[3].career_status == "active"
    assert not by_id[3].primary_population
    assert by_id[1].career_status == "active_partial_start"
    assert by_id[3].total_fought_bouts == 1
    assert by_id[4].career_status == "completed"
    assert by_id[4].primary_population


def test_probability_rows_use_completed_non_partial_careers_only() -> None:
    history = History(
        {
            basho_date(1980, 1): basho_state(
                {RikId(1): ("One", "J1e"), RikId(2): ("Two", "J1w")},
                {},
            ),
            basho_date(1980, 3): basho_state(
                {
                    RikId(1): ("One", "J1e"),
                    RikId(2): ("Two", "J1w"),
                    RikId(3): ("Three", "J2e"),
                },
                {Day(1): [bout(RikId(1), Outcome.W, RikId(3), Outcome.L)]},
            ),
            basho_date(1980, 5): basho_state(
                {RikId(1): ("One", "J1e"), RikId(2): ("Two", "J1w")},
                {},
            ),
        }
    )

    rows = build_bout_probability_rows(analyse_history(history).career_rows)

    assert {row.position_band for row in rows} == {"0.8395–1.0000"}
    assert [(row.bout_threshold, row.reaching_count) for row in rows] == [
        (0, 1),
        (1, 1),
    ]
    assert all(row.career_count == 1 for row in rows)


def test_reports_write_timestamped_fat_csv_manifest_and_responsive_chart(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    history = History(
        {
            basho_date(1980, 1): basho_state(
                {RikId(1): ("One", "J1e"), RikId(2): ("Two", "J1w")},
                {},
            ),
            basho_date(1980, 3): basho_state(
                {
                    RikId(1): ("One", "J1e"),
                    RikId(2): ("Two", "J1w"),
                    RikId(3): ("Three", "J2e"),
                },
                {Day(1): [bout(RikId(1), Outcome.W, RikId(3), Outcome.L)]},
            ),
            basho_date(1980, 5): basho_state(
                {RikId(1): ("One", "J1e"), RikId(2): ("Two", "J1w")},
                {},
            ),
        }
    )
    result = analyse_history(history)
    monkeypatch.setattr(reports, "git_state", lambda: ("abc123", True))

    outputs = reports.write_outputs(
        result,
        source=HistorySource("short_history_zip", "short.zip", "digest"),
        output_root=tmp_path,
        generated_at=datetime(2026, 8, 23, 12, 34, 56, tzinfo=timezone.utc),
    )

    assert outputs.run_directory.name == "2026-08-23_12-34-56"
    with outputs.rikishi_basho_csv.open(encoding="utf-8-sig", newline="") as stream:
        basho_rows = list(csv.DictReader(stream))
    with outputs.rikishi_careers_csv.open(encoding="utf-8-sig", newline="") as stream:
        career_rows = list(csv.DictReader(stream))
    with outputs.bout_probability_csv.open(
        encoding="utf-8-sig",
        newline="",
    ) as stream:
        probability_rows = list(csv.DictReader(stream))
    manifest = json.loads(outputs.manifest_json.read_text(encoding="utf-8"))
    scatter = outputs.scatter_html.read_text(encoding="utf-8")
    probability_chart = outputs.bout_probability_html.read_text(encoding="utf-8")

    assert len(basho_rows) == 7
    assert "normalized_position" in basho_rows[0]
    assert "total_fought_bouts" in career_rows[0]
    assert "empirical_probability" in probability_rows[0]
    assert manifest["source"]["kind"] == "short_history_zip"
    assert manifest["counts"]["exceptions"] == 0
    assert manifest["git"] == {"commit": "abc123", "dirty": True}
    assert manifest["position_band_cuts"] == [0.0, 0.2, 0.4, 0.6, 0.8395, 1.0]
    assert '"type":"scattergl"' in scatter
    assert '"visible":"legendonly"' in scatter
    assert '"range":[-0.01,1.01]' in scatter
    assert '"y":[0.0]' in scatter
    assert "Mean relative banzuke height: %{y:.5f}" in scatter
    assert "Height CI95: [%{customdata[6]:.5f}, %{customdata[7]:.5f}]" in scatter
    assert "Fought bouts: %{x}" in scatter
    assert '"type":"scatter"' in probability_chart
    assert '"fill":"toself"' in probability_chart
    assert 'CI95","visible":"legendonly"' in probability_chart
    assert 'name: "Toggle CI95 bands"' not in probability_chart
    assert "modeBarButtonsToAdd" not in probability_chart
    assert "displayModeBar: true" in probability_chart
    assert "width: 100vw" in probability_chart
    assert '"x":1.02' in probability_chart


def basho_date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))


def basho_state(
    entries: dict[RikId, tuple[str, str]],
    bouts_by_day: dict[Day, list[BoutResult]],
) -> BashoState:
    daily_results = {}
    for day, bouts in bouts_by_day.items():
        lookup = ResultLookup(
            {
                Pair(result.rikishi1, result.rikishi2): result
                for result in bouts
            }
        )
        daily_results[day] = DailyResults(
            torikumi=Torikumi(
                Pair(result.rikishi1, result.rikishi2) for result in bouts
            ),
            results_lookup=lookup,
        )
    return BashoState(
        banzuke=Banzuke(
            riks=Riks(entries),
            rikchii=RikChii(
                {
                    rikishi_id: Chii.from_str(chii)
                    for rikishi_id, (_, chii) in entries.items()
                }
            ),
            rikshik=RikShikona(
                {
                    rikishi_id: Shikona(shikona)
                    for rikishi_id, (shikona, _) in entries.items()
                }
            ),
        ),
        summary=Summary(daily_results),
    )


def bout(
    rikishi1: RikId,
    outcome1: Outcome,
    rikishi2: RikId,
    outcome2: Outcome,
) -> BoutResult:
    decision = Decision("fusen" if Outcome.FS in {outcome1, outcome2} else "blank")
    return BoutResult(
        rikishi1=rikishi1,
        outcome1=outcome1,
        rikishi2=rikishi2,
        outcome2=outcome2,
        decision=decision,
        symbol=Symbol.FS if outcome1 == Outcome.FS else outcome1.to_symbol(),
    )
