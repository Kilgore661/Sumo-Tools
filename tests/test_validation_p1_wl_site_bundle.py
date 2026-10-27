from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.analysis.site89 import producer
from src.products.make_site89.bundle import (
    REQUIRED_ARTIFACT_IDS,
    REQUIRED_FILES,
    STANDINGS_WINDOWS,
)
from src.sumo_core.BasicPrimitives import Riks
from src.sumo_core.Banzuke import Banzuke, RikChii, RikShikona
from src.sumo_core.BashoState import BashoState
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary
from src.validation.p1_wl_site_bundle.runner import compare_bundles


def test_site89_producer_forwards_explicit_prior(monkeypatch, tmp_path: Path) -> None:
    captured = {}

    class StopAfterElo(Exception):
        pass

    def stop_after_elo(**kwargs):
        captured.update(kwargs)
        raise StopAfterElo

    monkeypatch.setattr(producer, "produce_elo89", stop_after_elo)
    prior = tmp_path / "candidate.csv"
    with pytest.raises(StopAfterElo):
        producer.produce_site89_bundle(
            history=History(
                {
                    Date.from_ints(1989, 1): BashoState(
                        banzuke=Banzuke(
                            riks=Riks(), rikchii=RikChii(), rikshik=RikShikona()
                        ),
                        summary=Summary({}),
                    )
                }
            ),
            output_root=tmp_path / "bundle",
            prior_path=prior,
        )

    assert captured["prior_path"] == prior


def test_comparison_accepts_only_rating_dependent_changes(tmp_path: Path) -> None:
    baseline = _write_bundle(tmp_path / "baseline", rating="1500")
    candidate = _write_bundle(tmp_path / "candidate", rating="1510")

    summary = compare_bundles(
        baseline_root=baseline,
        candidate_root=candidate,
        output_root=tmp_path / "comparison",
    )

    assert summary["violations"] == []
    assert summary["changed_files"] == 3
    assert summary["model_independent_changed_files"] == 0
    with (tmp_path / "comparison/numeric_differences.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert any(
        row["artifact_id"] == "typical_rating_values"
        and row["field"] == "rating"
        and float(row["mean_difference"]) == 10.0
        for row in rows
    )
    with (tmp_path / "comparison/sekitori_rating_summary.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        sekitori = {
            row["division"]: row for row in csv.DictReader(stream)
        }
    assert sekitori["sekitori"]["observation_count"] == "1"
    assert sekitori["sekitori"]["changed_observation_count"] == "1"
    assert float(sekitori["sekitori"]["maximum_absolute_difference"]) == 10.0
    with (tmp_path / "comparison/sekitori_rating_differences.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        differences = list(csv.DictReader(stream))
    assert [(row["rikishi_id"], row["division"]) for row in differences] == [
        ("1", "makuuchi")
    ]
    assert differences[0]["shikona"] == "Alpha"


def test_comparison_rejects_model_independent_change(tmp_path: Path) -> None:
    baseline = _write_bundle(tmp_path / "baseline", rating="1500")
    candidate = _write_bundle(tmp_path / "candidate", rating="1510")
    target = candidate / "site/banzuke-rank/division-stability/data/persistence.csv"
    target.write_text("label,value\nchanged,1\n", encoding="utf-8")

    summary = compare_bundles(
        baseline_root=baseline,
        candidate_root=candidate,
        output_root=tmp_path / "comparison",
    )

    assert any(
        item["message"] == "model-independent content changed"
        for item in summary["violations"]
    )


def test_highest_rating_identity_is_rikishi_not_peak_attributes(tmp_path: Path) -> None:
    baseline = _write_bundle(tmp_path / "baseline", rating="1500")
    candidate = _write_bundle(tmp_path / "candidate", rating="1510")
    relative = "site/sumo-history/records/highest-rating/data/highest_rating.csv"
    fields = "position,rikishi_id,shikona,active,chii,chii_ordinal,rating,date\n"
    (baseline / relative).write_text(
        fields + "1,1,Alpha,False,M1e,10101,2000,2000-01\n"
        "2,2,Beta,False,J1w,20102,1900,2001-01\n",
        encoding="utf-8",
    )
    (candidate / relative).write_text(
        fields + "1,2,Beta,False,M16e,11601,1920,2002-01\n"
        "2,1,Alpha,False,M2w,10202,2010,2000-03\n",
        encoding="utf-8",
    )

    summary = compare_bundles(
        baseline_root=baseline,
        candidate_root=candidate,
        output_root=tmp_path / "comparison",
    )

    assert summary["violations"] == []
    with (tmp_path / "comparison/files.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    row = next(item for item in rows if item["artifact_id"] == "highest_rating")
    assert row["identity_fields"] == "rikishi_id"
    assert row["identity_keys_equal"] == "True"
    assert row["order_changed_count"] == "2"


def _write_bundle(root: Path, *, rating: str) -> Path:
    site_root = root / "site"
    artifacts = []
    for artifact_id in sorted(REQUIRED_ARTIFACT_IDS):
        relatives = list(REQUIRED_FILES[artifact_id])
        if artifact_id == "basho_results_browser":
            relatives.append("sumo-history/basho-results/data/by-basho/1989-01.csv")
        if artifact_id == "rating_changes":
            relatives.append("current-sumo/rating-changes/data/1989-03 1-change.csv")
        if artifact_id == "standings_by_wins":
            relatives.extend(
                f"current-sumo/standings-by-wins/data/multiple basho standings view (1989_01, BACKWARDS, {window}){suffix}"
                for window in STANDINGS_WINDOWS
                for suffix in (".csv", ".json")
            )
        for relative in relatives:
            path = site_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_content(relative, artifact_id, rating), encoding="utf-8")
        artifacts.append(
            {
                "id": artifact_id,
                "producer": f"fixture.{artifact_id}",
                "files": [Path(value).as_posix() for value in relatives],
            }
        )
    source_root = root / "sources/elo89"
    source_root.mkdir(parents=True)
    (source_root / "manifest.json").write_text("{}\n", encoding="utf-8")
    (source_root / "prior.csv").write_text(
        f"rank_pair,ordinal,rating\nM1,10000,{rating}\n", encoding="utf-8"
    )
    (source_root / "bout_ledger.csv").write_text(
        "date,day,rikishi_a,rikishi_b,chii_a,chii_b,rating_a_before,"
        "rating_b_before,rated_bouts_a_before,rated_bouts_b_before,"
        "probability_a_wins,a_won,k_a,k_b,delta_a,delta_b,rating_a_after,"
        "rating_b_after,initialisation_a,initialisation_b\n"
        f"1989/01,1,1,2,M1e,Ms1w,1490,1490,0,0,0.5,True,35,35,10,-10,"
        f"{rating},1480,adopted prior M1,adopted prior Ms1\n",
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "model_id": "elo-89",
                "history": {"start": "1989/01", "end": "1989/01"},
                "rating_run": "sources/elo89/manifest.json",
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    return root


def _content(relative: str, artifact_id: str, rating: str) -> str:
    if relative.endswith("basho_results_index.json"):
        return json.dumps({"entries": [{"payload_path": "data/by-basho/1989-01.csv"}]})
    if relative.endswith("rating_changes_index.json"):
        return json.dumps({"entries": [{"payload_path": "data/1989-03 1-change.csv"}]})
    if relative.endswith("torikumi_index.json"):
        return json.dumps({"entries": []})
    if relative.endswith("standings-by-wins/data/site_config.json"):
        return json.dumps({"anchor_token": "1989_01", "supported_num_basho": list(STANDINGS_WINDOWS)})
    if artifact_id == "basho_results_browser" and "data/by-basho/" in relative:
        return (
            "basho,division_id,division_label,rikishi_id,shikona,chii,rating\n"
            "1989/01,makuuchi,Makuuchi,1,Alpha,M1e,1500\n"
        )
    if relative.endswith("fastest-risers/data/rankings.json"):
        return json.dumps(
            {
                "schema_version": 2,
                "history": {"start": "1989/01", "end": "1989/01"},
                "routes": {"Jk:M": {}},
            }
        )
    if artifact_id == "typical_rating_values":
        return f"table,label,rating\nSanyaku,Y,{rating}\n"
    return "{}" if relative.endswith(".json") else "label,value\nfixture,1\n"
