import json
from pathlib import Path

import pytest

from src.products.make_site89.bundle import (
    REQUIRED_ARTIFACT_IDS,
    REQUIRED_FILES,
    STANDINGS_WINDOWS,
    copy_site_data_bundle,
    load_site_data_bundle,
)


def write_bundle(root: Path, *, model_id: str = "elo-89") -> Path:
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
                for window in STANDINGS_WINDOWS for suffix in (".csv", ".json")
            )
        for relative_text in relatives:
            path = site_root / relative_text
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative_text.endswith("basho_results_index.json"):
                content = json.dumps({"entries": [{"payload_path": "data/by-basho/1989-01.csv"}]})
            elif relative_text.endswith("rating_changes_index.json"):
                content = json.dumps({"entries": [{"payload_path": "data/1989-03 1-change.csv"}]})
            elif relative_text.endswith("torikumi_index.json"):
                content = json.dumps({"entries": []})
            elif relative_text.endswith("standings-by-wins/data/site_config.json"):
                content = json.dumps({"anchor_token": "1989_01", "supported_num_basho": list(STANDINGS_WINDOWS)})
            elif relative_text.endswith("fastest-risers/data/rankings.json"):
                content = json.dumps(
                    {
                        "schema_version": 2,
                        "history": {"start": "1989/01", "end": "2026/07"},
                        "routes": {"Jk:M": {}},
                    }
                )
            else:
                content = "{}" if relative_text.endswith(".json") else "fixture\n"
            path.write_text(content, encoding="utf-8")
        artifacts.append(
            {
                "id": artifact_id,
                "producer": f"fixture.{artifact_id}",
                "files": [Path(relative).as_posix() for relative in relatives],
            }
        )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "model_id": model_id,
                "history": {"start": "1989/01", "end": "2026/07"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    return root


def test_loads_complete_elo89_bundle(tmp_path: Path) -> None:
    bundle = load_site_data_bundle(write_bundle(tmp_path))

    assert bundle.history_start == "1989/01"
    assert bundle.history_end == "2026/07"
    assert {artifact.id for artifact in bundle.artifacts} == REQUIRED_ARTIFACT_IDS


def test_torikumi_index_allows_disabled_days_without_payloads(tmp_path: Path) -> None:
    root = write_bundle(tmp_path)
    index_path = root / "site/current-sumo/torikumi/data/torikumi_index.json"
    index_path.write_text(
        json.dumps(
            {
                "entries": [
                    {"day": str(day), "label": f"Day {day}", "disabled": True}
                    for day in range(1, 16)
                ]
            }
        ),
        encoding="utf-8",
    )

    load_site_data_bundle(root)


def test_torikumi_index_rejects_enabled_day_without_payload(tmp_path: Path) -> None:
    root = write_bundle(tmp_path)
    index_path = root / "site/current-sumo/torikumi/data/torikumi_index.json"
    index_path.write_text(
        json.dumps({"entries": [{"day": "1", "disabled": False}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid payload path"):
        load_site_data_bundle(root)


def test_rejects_non_elo89_bundle(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires model_id 'elo-89'"):
        load_site_data_bundle(write_bundle(tmp_path, model_id="equelo"))


def test_rejects_missing_artifact(tmp_path: Path) -> None:
    root = write_bundle(tmp_path)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"].pop()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="missing:"):
        load_site_data_bundle(root)


def test_rejects_undeclared_file(tmp_path: Path) -> None:
    root = write_bundle(tmp_path)
    (root / "site" / "extra.txt").write_text("extra", encoding="utf-8")

    with pytest.raises(ValueError, match="undeclared files"):
        load_site_data_bundle(root)


def test_copies_only_declared_files(tmp_path: Path) -> None:
    bundle = load_site_data_bundle(write_bundle(tmp_path / "bundle"))
    output = tmp_path / "output"

    copy_site_data_bundle(bundle, output)

    copied = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    assert copied == {
        Path(relative).as_posix()
        for artifact in bundle.artifacts
        for relative in artifact.files
    }
