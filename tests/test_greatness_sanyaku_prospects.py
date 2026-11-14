from __future__ import annotations

import csv
import json
from datetime import date
from types import MappingProxyType

import pytest

from src.analysis.greatness.sanyaku_prospects.producer import produce
from src.analysis.greatness.sanyaku_prospects.lifecycle import classify_non_success_outcome
from src.analysis.greatness.sanyaku_prospects.cached_charts import render_cached_career_charts
from src.analysis.greatness.sanyaku_prospects.__main__ import build_parser
from src.infra.get_bios.api import (
    BioBashoDate,
    BioStore,
    BirthDate,
    RikishiBio,
    ShikonaUse,
)
from src.infra.get_bios.career_rows import CutoffCareerStatus
from src.sumo_core.BasicPrimitives import RikId, Riks, Shikona
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary


def test_producer_writes_debut_state_and_audit_bundle(tmp_path) -> None:
    dates = (
        Date.from_ints(2000, 1),
        Date.from_ints(2000, 3),
        Date.from_ints(2000, 5),
        Date.from_ints(2000, 7),
    )
    history = History(
        {
            dates[0]: _state({1: "Y1e"}),
            dates[1]: _state({2: "M1e", 3: "M1w", 4: "M3e", 5: "M4e", 6: "M5e"}),
            dates[2]: _state({2: "K1e", 4: "M2e"}),
            dates[3]: _state({4: "M2e"}),
        }
    )
    bios = BioStore(
        MappingProxyType(
            {
                RikId(1): _bio(1, date(1970, 1, 1)),
                RikId(2): _bio(2, date(1973, 3, 6)),
                RikId(3): _bio(3, date(1973, 3, 6), intai=BioBashoDate(2000, 5)),
                RikId(4): _bio(4, date(1973, 3, 1)),
                RikId(5): _bio(5, date(1973, 3, 1)),
                RikId(6): _bio(6, date(1973, 3, 1)),
            }
        )
    )
    results = tmp_path / "results"
    _daily(results, dates[0], "December 26, 1999")
    _daily(results, dates[1], "March 5, 2000")
    _daily(results, dates[2], "April 30, 2000")
    _daily(results, dates[3], "July 2, 2000")
    career_pages = tmp_path / "rikishi-pages"
    career_pages.mkdir()
    _career_page(career_pages, 5, (("200007", "Mz"),))
    _career_page(career_pages, 6, (("200003", "M5e"),))

    paths = produce(
        history,
        bios,
        results_root=results,
        output_root=tmp_path / "output",
        chart_rikishi_ids=(2, 3, 4),
        career_pages_root=career_pages,
    )

    with paths.debut_probabilities.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    age_26 = next(row for row in rows if row["division"] == "M" and row["age"] == "26")
    age_27 = next(row for row in rows if row["division"] == "M" and row["age"] == "27")
    assert (age_26["success"], age_26["failure"], age_26["rikishi"]) == ("1", "1", "2")
    assert (age_27["failure"], age_27["right_censored"], age_27["unknown"]) == ("1", "2", "0")

    with paths.population_summary.open(newline="", encoding="utf-8") as stream:
        summary = {row["measure"]: int(row["count"]) for row in csv.DictReader(stream)}
    assert summary["boundary_incumbents"] == 1
    assert summary["complete_record_rikishi"] == 5
    assert summary["complete_records_with_birth_date"] == 5

    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    assert manifest["age_policy"] == "completed years on exact basho Day 1"
    assert manifest["rank_state_observation_unit"] == "one eligible pre-sanyaku banzuke appearance"
    assert manifest["chart_rikishi_ids"] == [2, 3, 4]
    assert manifest["schema_version"] == 5
    assert paths.cohort_observations.is_file()
    assert paths.basho_date_coverage.is_file()

    with paths.cohort_observations.open(newline="", encoding="utf-8") as stream:
        cohort_rows = list(csv.DictReader(stream))
    evidence_by_id = {
        row["rikishi_id"]: row["outcome_evidence"]
        for row in cohort_rows
        if row["cohort_type"] == "division_debut"
    }
    assert evidence_by_id["5"] == "cutoff_unranked_status:Mz"
    assert evidence_by_id["6"] == "absent_from_cutoff_banzuke_and_career_rows"

    with paths.rank_state_probabilities.open(newline="", encoding="utf-8") as stream:
        rank_rows = list(csv.DictReader(stream))
    m1_age_26 = next(
        row for row in rank_rows
        if (row["division"], row["rank_number"], row["age"]) == ("M", "1", "26")
    )
    m2_age_27 = next(
        row for row in rank_rows
        if (row["division"], row["rank_number"], row["age"]) == ("M", "2", "27")
    )
    assert (
        m1_age_26["success"],
        m1_age_26["failure"],
        m1_age_26["observations"],
        m1_age_26["unique_rikishi"],
        m1_age_26["resolved_probability"],
    ) == ("1", "1", "2", "2", "0.5")
    assert (
        m2_age_27["failure"],
        m2_age_27["right_censored"],
        m2_age_27["observations"],
        m2_age_27["unique_rikishi"],
    ) == (
        "0",
        "1",
        "2",
        "1",
    )
    assert m2_age_27["resolved_probability"] == ""

    with paths.career_chart_points.open(newline="", encoding="utf-8") as stream:
        chart_points = list(csv.DictReader(stream))
    rikishi_2 = [row for row in chart_points if row["rikishi_id"] == "2"]
    rikishi_3 = [row for row in chart_points if row["rikishi_id"] == "3"]
    rikishi_4 = [row for row in chart_points if row["rikishi_id"] == "4"]
    assert [row["point_kind"] for row in rikishi_2] == [
        "cohort_probability",
        "sanyaku_attainment",
    ]
    assert rikishi_2[-1]["probability"] == "1.0"
    assert [row["point_kind"] for row in rikishi_3] == ["cohort_probability"]
    assert [row["chii"] for row in rikishi_4] == ["M3e", "M2e", "M2e"]
    assert rikishi_2[0]["support_tier"] == "very_low"

    chart_2 = (tmp_path / "output" / "career_charts" / "2.html").read_text(encoding="utf-8")
    chart_3 = (tmp_path / "output" / "career_charts" / "3.html").read_text(encoding="utf-8")
    assert "https://cdn.plot.ly/plotly-2.35.2.min.js" in chart_2
    assert '"symbol":"star"' in chart_2
    assert '"name":"Very low support (<10)"' in chart_2
    assert '"line":{"color":"#315a7d","width":1}' in chart_2
    assert '"size":10,"color":"#e31a1c"' in chart_2
    assert '"name":"First san\'yaku"' in chart_2
    assert '"name":"First san\'yaku"' not in chart_3
    assert "How to read this chart" in chart_2
    assert "historical probability of eventually attaining a san'yaku rank, given rank and age" in chart_2
    assert '"title":"Age at basho (years)"' in chart_2
    assert "successes / (successes + failures)" in chart_2
    assert "cohort can contain rikishi" in chart_2
    assert "Normally a rikishi still active at the analysis cutoff" in chart_2
    traces_text = chart_2.split("const traces = ", 1)[1].split(";\n    const layout", 1)[0]
    traces = json.loads(traces_text)
    assert all(
        isinstance(x, (int, float))
        for trace in traces
        for x in trace["x"]
    )

    with pytest.raises(ValueError, match="eligible birth-dated rikishi IDs: 1"):
        produce(
            history,
            bios,
            results_root=results,
            output_root=tmp_path / "invalid-output",
            chart_rikishi_ids=(1,),
            career_pages_root=career_pages,
        )

    cached_charts = render_cached_career_charts(
        output_root=tmp_path / "output",
        bios=bios,
        rikishi_ids=(2, 4),
    )
    assert [path.name for path in cached_charts] == ["2.html", "4.html"]
    with paths.career_chart_points.open(newline="", encoding="utf-8") as stream:
        cached_points = list(csv.DictReader(stream))
    assert {row["rikishi_id"] for row in cached_points} == {"2", "4"}
    assert cached_points[0]["exact_age"]
    assert cached_points[-1]["chii"] == "M2e"


def test_cli_rebuild_is_opt_in() -> None:
    parser = build_parser()
    assert parser.parse_args(["--chart-rikishi-id", "12320"]).rebuild is False
    assert parser.parse_args(["--rebuild"]).rebuild is True


def test_cached_chart_requires_rebuilt_artifacts(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="Run once with --rebuild"):
        render_cached_career_charts(
            output_root=tmp_path,
            bios=BioStore(MappingProxyType({})),
            rikishi_ids=(12320,),
        )


@pytest.mark.parametrize("status", ("Mz", "Bg", "Kg", "Sj"))
def test_unranked_cutoff_status_is_right_censored(status: str) -> None:
    rikishi_id = RikId(7)
    outcome = classify_non_success_outcome(
        rikishi_id,
        bio=_bio(7, date(2000, 1, 1)),
        latest_ids=Riks({}),
        cutoff_bio=BioBashoDate(2026, 11),
        cutoff_statuses={rikishi_id: CutoffCareerStatus(status, "cutoff_status_row")},
    )
    assert outcome == ("right_censored", f"cutoff_unranked_status:{status}")


def test_absent_and_unreadable_cutoff_evidence_are_distinguished() -> None:
    rikishi_id = RikId(7)
    common = {
        "bio": _bio(7, date(2000, 1, 1)),
        "latest_ids": Riks({}),
        "cutoff_bio": BioBashoDate(2026, 11),
    }
    assert classify_non_success_outcome(
        rikishi_id,
        **common,
        cutoff_statuses={rikishi_id: CutoffCareerStatus(None, "no_cutoff_status_row")},
    ) == ("failure", "absent_from_cutoff_banzuke_and_career_rows")
    assert classify_non_success_outcome(
        rikishi_id,
        **common,
        cutoff_statuses={rikishi_id: CutoffCareerStatus(None, "missing_career_page")},
    ) == ("unknown", "missing_career_page")
    assert classify_non_success_outcome(
        rikishi_id,
        **common,
        cutoff_statuses={},
    ) == ("unknown", "career_status_source_not_supplied")


def _daily(root, basho, day_one: str) -> None:
    directory = root / f"{int(basho.year)} {int(basho.month):02d}"
    directory.mkdir(parents=True)
    (directory / "01.html").write_text(
        f"<h1>Test {int(basho.year)}, Day 1</h1><h2>{day_one}</h2>",
        encoding="utf-8",
    )


def _career_page(root, rikishi_id: int, rows: tuple[tuple[str, str], ...]) -> None:
    body = "".join(
        f'<tr><td><a href="Banzuke.aspx?b={basho}">{basho}</a></td><td>{status}</td></tr>'
        for basho, status in rows
    )
    (root / f"{rikishi_id:05d}.html").write_text(f"<table>{body}</table>", encoding="utf-8")


def _state(ranks: dict[int, str]) -> BashoState:
    chii = {RikId(rikishi_id): Chii.from_str(rank) for rikishi_id, rank in ranks.items()}
    return BashoState(
        Banzuke(
            Riks(chii),
            RikChii(chii),
            RikShikona({rikishi_id: Shikona(f"Rikishi {int(rikishi_id)}") for rikishi_id in chii}),
        ),
        Summary({}),
    )


def _bio(rikishi_id: int, birth: date, *, intai=None) -> RikishiBio:
    return RikishiBio(
        RikId(rikishi_id),
        BirthDate(birth),
        "",
        (),
        (ShikonaUse(BioBashoDate(2000, 1), Shikona(f"Rikishi {rikishi_id}")),),
        None,
        intai,
        None,
        None,
        (),
        (),
    )
