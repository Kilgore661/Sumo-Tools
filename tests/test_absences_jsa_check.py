"""Tests for the first JSA-window observance experiment phase."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.analysis.absences.jsa_check.analysis import analyse_absence_windows
from src.analysis.absences.jsa_check.model import (
    AbsenceInference,
    FinalRecord,
    JsaCheckRunMetadata,
)
from src.analysis.absences.jsa_check.output import write_outputs
from src.analysis.absences.jsa_check.source import (
    latest_retirement_csv,
    load_retirement_last_appearances,
    parse_final_record,
)
from src.infra.parser.parser_daily import _convert_outcome
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.BasicEnums import Outcome, Symbol
from src.sumo_core.BasicPrimitives import (
    Day,
    Pair,
    RikId,
    Riks,
    Shikona,
    Torikumi,
)
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import (
    BoutResult,
    DailyResults,
    Decision,
    ResultLookup,
    Summary,
)


RIKISHI_A = RikId(1)
RIKISHI_B = RikId(2)
RIKISHI_C = RikId(3)
RIKISHI_D = RikId(4)


def test_diagnostics_do_not_suppress_ambiguous_absence_inference() -> None:
    history = History(
        {
            Date.from_ints(1989, 1): _basho(
                {
                    1: [_bout(RIKISHI_A, Outcome.W, RIKISHI_B, Outcome.L)],
                    2: [_bout(RIKISHI_C, Outcome.FS, RIKISHI_A, Outcome.FP)],
                    15: [_bout(RIKISHI_D, Outcome.FS, RIKISHI_C, Outcome.FP)],
                }
            )
        }
    )

    result = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "1-1-5",
                RIKISHI_B: "0-1-6",
                RIKISHI_D: "1-0-6",
            },
        ),
        _retirement_appearances(history),
    )
    rows = {row.rikishi_id: row for row in result.rows}

    assert set(rows) == {1, 2, 4}
    assert rows[1].daily_outcomes[:3] == ("W", "FP", ".")
    assert rows[1].window_outcome_counts == (2, 0, 0, 0, 0, 0, 0)
    assert rows[1].jsa_observant is False
    assert rows[1].dated_win_count == 1
    assert rows[1].dated_loss_count == 1
    assert rows[1].empty_window_count == 6
    assert rows[1].excess_outcome_count == 1
    assert rows[1].opportunity_total == 7
    assert rows[1].wins_reconcile is True
    assert rows[1].losses_reconcile is True
    assert rows[1].draws_reconcile is True
    assert rows[1].window_accounting_reconciles is True
    assert rows[1].absence_inference is AbsenceInference.AMBIGUOUS
    assert rows[1].assigned_absence_count == 0
    assert rows[1].assigned_absence_windows == ()
    assert rows[2].daily_outcomes[0] == "L"
    assert rows[2].jsa_observant is True
    assert rows[2].absence_inference is AbsenceInference.ALL_ASSIGNED
    assert rows[2].assigned_absence_windows == (2, 3, 4, 5, 6, 7)
    assert rows[4].daily_outcomes[14] == "FS"
    assert rows[4].window_outcome_counts == (0, 0, 0, 0, 0, 0, 1)
    assert result.summary.rikishi_basho_count == 3
    assert result.summary.observant_count == 2
    assert result.summary.non_observant_count == 1
    assert result.summary.observant_percentage == pytest.approx(200 / 3)
    assert result.summary.ambiguous_absence_windows_count == 1
    assert result.summary.all_absences_assigned_count == 2


def test_consecutive_bouts_across_a_window_boundary_are_observant() -> None:
    history = History(
        {
            Date.from_ints(1989, 1): _basho(
                {
                    2: [_bout(RIKISHI_A, Outcome.W, RIKISHI_B, Outcome.L)],
                    3: [_bout(RIKISHI_A, Outcome.L, RIKISHI_B, Outcome.W)],
                }
            )
        }
    )

    row = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "1-1-5",
                RIKISHI_B: "1-1-5",
                RIKISHI_D: "0-0-7",
            },
        ),
        _retirement_appearances(history),
    ).rows[0]

    assert row.rikishi_id == 1
    assert row.window_outcome_counts[:2] == (1, 1)
    assert row.jsa_observant is True


def test_draw_is_a_dated_outcome_and_occupies_its_window() -> None:
    history = History(
        {
            Date.from_ints(1994, 3): _basho(
                {5: [_bout(RIKISHI_A, Outcome.DRAW, RIKISHI_B, Outcome.DRAW)]}
            )
        }
    )

    row = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "0-0-6-1d",
                RIKISHI_B: "0-0-6-1d",
                RIKISHI_D: "0-0-7",
            },
        ),
        _retirement_appearances(history),
    ).rows[0]

    assert row.daily_outcomes[4] == "d"
    assert row.window_outcome_counts[2] == 1
    assert row.recorded_draws == 1
    assert row.dated_draw_count == 1
    assert row.draws_reconcile is True
    assert row.opportunity_total == 7
    assert row.absence_inference is AbsenceInference.ALL_ASSIGNED
    assert row.assigned_absence_windows == (1, 2, 4, 5, 6, 7)


def test_final_draw_without_dated_draw_rejects_stale_history() -> None:
    history = History({Date.from_ints(1994, 3): _basho({})})

    with pytest.raises(ValueError, match="requires a rebuilt History.*1994/03"):
        analyse_absence_windows(
            history,
            _final_records(
                history,
                {
                    RIKISHI_A: "0-0-6-1d",
                    RIKISHI_B: "0-0-7",
                    RIKISHI_D: "0-0-7",
                },
            ),
            _retirement_appearances(history),
        )


def test_eight_bouts_do_not_prevent_no_absence_inference() -> None:
    history = History(
        {
            Date.from_ints(1989, 1): _basho(
                {
                    day: [
                        _bout(
                            RIKISHI_A,
                            Outcome.W if day % 2 else Outcome.L,
                            RIKISHI_B,
                            Outcome.L if day % 2 else Outcome.W,
                        )
                    ]
                    for day in range(1, 9)
                }
            )
        }
    )

    row = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "4-4",
                RIKISHI_B: "4-4",
                RIKISHI_D: "0-0-7",
            },
        ),
        _retirement_appearances(history),
    ).rows[0]

    assert row.opportunity_total == 8
    assert row.jsa_observant is False
    assert row.window_accounting_reconciles is True
    assert row.absence_inference is AbsenceInference.NO_ABSENCES


def test_one_empty_window_identifies_one_recorded_absence() -> None:
    outcomes = (Outcome.W, Outcome.L, Outcome.W, Outcome.L, Outcome.W, Outcome.L)
    days = (1, 3, 7, 9, 11, 13)
    history = History(
        {
            Date.from_ints(1989, 1): _basho(
                {
                    day: [
                        _bout(
                            RIKISHI_A,
                            outcome,
                            RIKISHI_B,
                            Outcome.L if outcome is Outcome.W else Outcome.W,
                        )
                    ]
                    for day, outcome in zip(days, outcomes, strict=True)
                }
            )
        }
    )

    row = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "3-3-1",
                RIKISHI_B: "3-3-1",
                RIKISHI_D: "0-0-7",
            },
        ),
        _retirement_appearances(history),
    ).rows[0]

    assert row.window_outcome_counts == (1, 1, 0, 1, 1, 1, 1)
    assert row.empty_windows == (3,)
    assert row.absence_inference is AbsenceInference.ALL_ASSIGNED
    assert row.assigned_absence_count == 1
    assert row.assigned_absence_windows == (3,)


def test_more_absences_than_empty_windows_is_inconsistent() -> None:
    history = History({Date.from_ints(1989, 1): _basho({})})

    row = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "0-0-8",
                RIKISHI_B: "0-0-7",
                RIKISHI_D: "0-0-7",
            },
        ),
        _retirement_appearances(history),
    ).rows[0]

    assert row.empty_window_count == 7
    assert row.recorded_absences == 8
    assert row.absence_inference is AbsenceInference.INCONSISTENT
    assert row.assigned_absence_count == 0


def test_short_record_is_joined_to_final_observed_basho() -> None:
    history = History({Date.from_ints(1989, 1): _basho({})})
    result = analyse_absence_windows(
        history,
        _final_records(
            history,
            {
                RIKISHI_A: "0-0",
                RIKISHI_B: "0-0-7",
                RIKISHI_D: "0-0-7",
            },
        ),
        _retirement_appearances(history),
    )

    row = result.rows[0]
    assert row.opportunity_total == 0
    assert row.final_observed_basho is True
    assert result.summary.opportunity_total_below_7_count == 1
    assert result.summary.short_record_final_observed_basho_count == 1
    assert result.summary.short_record_not_final_observed_basho_count == 0


def test_trailing_incomplete_basho_is_excluded() -> None:
    complete = _basho({})
    incomplete = BashoState(
        banzuke=complete.banzuke,
        summary=Summary({Day(1): _daily_results([])}),
    )
    history = History(
        {
            Date.from_ints(1988, 11): complete,
            Date.from_ints(1989, 1): complete,
            Date.from_ints(1989, 3): incomplete,
        }
    )

    result = analyse_absence_windows(
        history,
        _final_records(history),
        _retirement_appearances(history),
    )

    assert result.summary.first_basho == "1989/01"
    assert result.summary.last_basho == "1989/01"
    assert result.summary.basho_count == 1


def test_incomplete_basho_inside_selected_history_is_rejected() -> None:
    complete = _basho({})
    incomplete = BashoState(
        banzuke=complete.banzuke,
        summary=Summary({Day(1): _daily_results([])}),
    )
    history = History(
        {
            Date.from_ints(1989, 1): incomplete,
            Date.from_ints(1989, 3): complete,
        }
    )

    with pytest.raises(ValueError, match="incomplete historical basho.*1989/01"):
        analyse_absence_windows(
            history,
            _final_records(history),
            _retirement_appearances(history),
        )


def test_writes_atomic_csv_and_minimal_summary(tmp_path: Path) -> None:
    history = History({Date.from_ints(1989, 1): _basho({})})
    result = analyse_absence_windows(
        history,
        _final_records(history),
        _retirement_appearances(history),
    )

    outputs = write_outputs(
        result,
        metadata=_run_metadata(),
        output_root=tmp_path,
    )

    with outputs.rows_csv.open(encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 3
    assert records[0]["day_01"] == "."
    assert records[0]["window_7_outcome_count"] == "0"
    assert records[0]["jsa_observant"] == "True"
    assert records[0]["final_record"] == "0-0-7"
    assert records[0]["recorded_absences"] == "7"
    assert records[0]["recorded_draws"] == "0"
    assert records[0]["final_observed_basho"] == "True"
    assert records[0]["wins_reconcile"] == "True"
    assert records[0]["losses_reconcile"] == "True"
    assert records[0]["draws_reconcile"] == "True"
    assert records[0]["window_accounting_reconciles"] == "True"
    assert records[0]["absence_inference"] == "all_absences_assigned"
    assert records[0]["assigned_absence_windows"] == "1;2;3;4;5;6;7"
    summary = outputs.summary_txt.read_text(encoding="utf-8")
    assert "Generated at: 2026-10-04T12:00:00+01:00" in summary
    assert "History source: test History" in summary
    assert "Final-record source: test standings" in summary
    assert "Retirement artifact: test retirement artifact" in summary
    assert "Rikishi-basho records: 3" in summary
    assert "At most one outcome per window: 3" in summary
    assert "All positive absences assigned: 3" in summary


@pytest.mark.parametrize(
    ("source_text", "expected"),
    (
        ("4-3", (4, 3, 0, 0)),
        ("0-0-7", (0, 0, 7, 0)),
        ("3-3-1d", (3, 3, 0, 1)),
        ("1-1-3-1d", (1, 1, 3, 1)),
    ),
)
def test_parses_published_final_record_forms(
    source_text: str,
    expected: tuple[int, int, int, int],
) -> None:
    record = parse_final_record(source_text)

    assert (
        record.wins,
        record.losses,
        record.absences,
        record.draws,
    ) == expected


def test_daily_parser_translates_sumodb_draw_token() -> None:
    assert _convert_outcome("D") is Outcome.DRAW


def test_loads_latest_retirement_artifact(tmp_path: Path) -> None:
    older = tmp_path / "rank_at_retirement_1958_01_to_2025_11_rikishi.csv"
    latest = tmp_path / "rank_at_retirement_1958_01_to_2026_09_rikishi.csv"
    older.write_text(
        "rikishi_id,shikona,last_appearance,last_chii,rank_group\n"
        "1,A,2025/09,Ms1e,Ms\n",
        encoding="utf-8",
    )
    latest.write_text(
        "rikishi_id,shikona,last_appearance,last_chii,rank_group\n"
        "1,A,2026/09,Ms1e,Ms\n",
        encoding="utf-8",
    )

    selected = latest_retirement_csv(tmp_path)
    appearances = load_retirement_last_appearances(selected)

    assert selected == latest
    assert appearances == {RIKISHI_A: "2026/09"}


def _basho(bouts_by_day: dict[int, list[BoutResult]]) -> BashoState:
    entries = {
        RIKISHI_A: ("A", "Ms1e"),
        RIKISHI_B: ("B", "Ms1w"),
        RIKISHI_C: ("C", "J1e"),
        RIKISHI_D: ("D", "Sd1e"),
    }
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
        summary=Summary(
            {
                Day(day): _daily_results(bouts_by_day.get(day, []))
                for day in range(1, 16)
            }
        ),
    )


def _daily_results(bouts: list[BoutResult]) -> DailyResults:
    lookup = ResultLookup(
        {
            Pair(bout.rikishi1, bout.rikishi2): bout
            for bout in bouts
        }
    )
    return DailyResults(torikumi=Torikumi(lookup), results_lookup=lookup)


def _bout(
    rikishi1: RikId,
    outcome1: Outcome,
    rikishi2: RikId,
    outcome2: Outcome,
) -> BoutResult:
    return BoutResult(
        rikishi1=rikishi1,
        outcome1=outcome1,
        rikishi2=rikishi2,
        outcome2=outcome2,
        decision=Decision(
            "fusen" if Outcome.FS in {outcome1, outcome2} else "blank"
        ),
        symbol=Symbol.FS if outcome1 == Outcome.FS else outcome1.to_symbol(),
    )


def _final_records(
    history: History,
    records: dict[RikId, str] | None = None,
) -> dict[Date, dict[RikId, FinalRecord]]:
    source_records = records or {
        RIKISHI_A: "0-0-7",
        RIKISHI_B: "0-0-7",
        RIKISHI_D: "0-0-7",
    }
    return {
        date: {
            rikishi_id: parse_final_record(source_text)
            for rikishi_id, source_text in source_records.items()
        }
        for date in history
    }


def _retirement_appearances(history: History) -> dict[RikId, str]:
    """Model a retirement artifact for the synthetic History."""

    result: dict[RikId, str] = {}
    for date in sorted(history):
        for rikishi_id in history[date].banzuke.riks:
            result[rikishi_id] = str(date)
    return result


def _run_metadata() -> JsaCheckRunMetadata:
    return JsaCheckRunMetadata(
        generated_at="2026-10-04T12:00:00+01:00",
        history_source="test History",
        final_records_source="test standings",
        retirement_source="test retirement artifact",
    )
