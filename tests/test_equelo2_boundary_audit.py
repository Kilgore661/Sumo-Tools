"""Contracts for the Equelo2 January-1989 boundary audit."""

from __future__ import annotations

import csv
import json

import pytest

from src.analysis.equelo2_boundary_audit.analysis import run_audit


def test_audit_writes_matched_and_chii_views(tmp_path) -> None:
    handover = tmp_path / "handover.csv"
    fields = (
        "rikishi_id",
        "shikona_1988_11",
        "chii_1988_11",
        "chii_1989_01",
        "equelo2_1988_11_end_rating",
        "equelo2_1989_01_start_rating",
        "elo89_1989_01_start_rating",
        "equelo2_minus_elo89_at_1989_01_start",
        "pre_1989_rated_bouts",
    )
    with handover.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(
            (
                {
                    "rikishi_id": 1,
                    "shikona_1988_11": "East",
                    "chii_1988_11": "M2e",
                    "chii_1989_01": "M1e",
                    "equelo2_1988_11_end_rating": 1601,
                    "equelo2_1989_01_start_rating": 1600,
                    "elo89_1989_01_start_rating": 1550,
                    "equelo2_minus_elo89_at_1989_01_start": 50,
                    "pre_1989_rated_bouts": 100,
                },
                {
                    "rikishi_id": 2,
                    "shikona_1988_11": "West",
                    "chii_1988_11": "M2w",
                    "chii_1989_01": "M1w",
                    "equelo2_1988_11_end_rating": 1501,
                    "equelo2_1989_01_start_rating": 1500,
                    "elo89_1989_01_start_rating": 1550,
                    "equelo2_minus_elo89_at_1989_01_start": -50,
                    "pre_1989_rated_bouts": 80,
                },
            )
        )

    outputs = run_audit(handover, tmp_path / "output")

    assert outputs.matched_count == 2
    summary = next(
        csv.DictReader((outputs.output_root / "overall_summary.csv").open())
    )
    assert float(summary["difference_mean"]) == pytest.approx(0.0)
    assert float(summary["mean_absolute_difference"]) == pytest.approx(50.0)
    paired = list(
        csv.DictReader((outputs.output_root / "canonical_pair_comparison.csv").open())
    )
    assert len(paired) == 1
    assert paired[0]["chii"] == "M1"
    assert paired[0]["rikishi_count"] == "2"
    manifest = json.loads(outputs.manifest.read_text(encoding="utf-8"))
    assert manifest["matched_rikishi"] == 2
    assert "start of 1989/01" in outputs.findings.read_text(encoding="utf-8")


def test_audit_rejects_inconsistent_recorded_difference(tmp_path) -> None:
    handover = tmp_path / "handover.csv"
    handover.write_text(
        "rikishi_id,shikona_1988_11,chii_1989_01,"
        "equelo2_1988_11_end_rating,equelo2_1989_01_start_rating,"
        "elo89_1989_01_start_rating,equelo2_minus_elo89_at_1989_01_start,"
        "pre_1989_rated_bouts\n"
        "1,Test,M1e,1500,1500,1490,11,10\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Inconsistent difference"):
        run_audit(handover, tmp_path / "output")


def test_tenure_cohorts_use_first_candidate_start_date(tmp_path) -> None:
    handover = tmp_path / "handover.csv"
    handover.write_text(
        "rikishi_id,shikona_1988_11,chii_1989_01,"
        "equelo2_1988_11_end_rating,equelo2_1989_01_start_rating,"
        "elo89_1989_01_start_rating,equelo2_minus_elo89_at_1989_01_start,"
        "pre_1989_rated_bouts\n"
        "1,Veteran,M1e,1600,1600,1550,50,300\n"
        "2,Novice,M1w,1500,1500,1550,-50,7\n",
        encoding="utf-8",
    )
    ledger = tmp_path / "rating_ledger.csv"
    ledger.write_text(
        "run,basho,phase,rikishi_id,shikona,chii,rating,rated_bouts,"
        "initialisation_source\n"
        "equelo2_full_history,1970/01,start,1,Veteran,Jk1e,1400,0,prior\n"
        "equelo2_full_history,1988/01,start,2,Novice,Jk1w,1400,0,prior\n"
        "equelo2_full_history,1988/11,start,1,Veteran,M2e,1590,300,prior\n"
        "equelo2_full_history,1988/11,start,2,Novice,M2w,1490,7,prior\n",
        encoding="utf-8",
    )

    outputs = run_audit(
        handover, tmp_path / "output", rating_ledger_path=ledger
    )

    summaries = list(
        csv.DictReader(
            (outputs.output_root / "tenure_threshold_summary.csv").open()
        )
    )
    five_years = next(
        row for row in summaries if row["minimum_tenure_years"] == "5"
    )
    assert five_years["rikishi_count"] == "1"
    assert five_years["median_pre_1989_rated_bouts"] == "300"
    membership = list(
        csv.DictReader(
            (outputs.output_root / "tenure_cohort_membership.csv").open()
        )
    )
    novice = next(row for row in membership if row["rikishi_id"] == "2")
    assert novice["first_proper_chii_basho"] == "1988/01"
    assert novice["qualifies_1_years"] == "True"
    assert novice["qualifies_2_years"] == "False"
