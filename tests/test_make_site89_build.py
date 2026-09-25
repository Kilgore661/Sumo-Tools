import ast
import json
from pathlib import Path

from src.products.make_site89.bundle import REQUIRED_ARTIFACT_IDS, REQUIRED_FILES, STANDINGS_WINDOWS
from src.products.make_site89.build import build_site


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "products" / "make_site89"


def write_bundle(root: Path) -> Path:
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
        for relative in relatives:
            path = root / "site" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative.endswith("basho_results_index.json"):
                content = json.dumps({"entries": [{"payload_path": "data/by-basho/1989-01.csv"}]})
            elif relative.endswith("rating_changes_index.json"):
                content = json.dumps({"entries": [{"payload_path": "data/1989-03 1-change.csv"}]})
            elif relative.endswith("torikumi_index.json"):
                content = json.dumps({"entries": []})
            elif relative.endswith("standings-by-wins/data/site_config.json"):
                content = json.dumps({"anchor_token": "1989_01", "supported_num_basho": list(STANDINGS_WINDOWS)})
            elif relative.endswith("fastest-risers/data/rankings.json"):
                content = json.dumps(
                    {
                        "schema_version": 2,
                        "history": {"start": "1989/01", "end": "2026/07"},
                        "routes": {"Jk:M": {}},
                    }
                )
            else:
                content = "{}" if relative.endswith(".json") else "fixture\n"
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
                "model_id": "elo-89",
                "history": {"start": "1989/01", "end": "2026/07"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    return root


def test_build_uses_only_produced_bundle(tmp_path: Path) -> None:
    output = build_site(
        data_bundle=write_bundle(tmp_path / "bundle"),
        output_root=tmp_path / "output",
        cache_mode="prod",
    )

    assert output.entrypoint.is_file()
    assert (output.root / "runtime" / "site-manifest.json").is_file()
    assert (output.root / "runtime" / "site-data-bundle.json").is_file()
    assert (output.root / "sumo-history" / "basho-results" / "data" / "basho_results_index.json").is_file()
    assert (output.root / "prose" / "YokYDJ.html").is_file()
    assert (output.root / "prose" / "Ozeki32.html").is_file()


def test_package_does_not_import_analysis_history_or_make_site2() -> None:
    forbidden = ("src.analysis", "src.sumo_core", "src.infra", "src.products.make_site2")
    violations = []
    for path in PACKAGE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name.startswith(forbidden):
                    violations.append(f"{path.relative_to(ROOT)} imports {name}")
    assert violations == []


def test_site_uses_elo89_title(tmp_path: Path) -> None:
    output = build_site(
        data_bundle=write_bundle(tmp_path / "bundle"),
        output_root=tmp_path / "output",
        cache_mode="prod",
    )

    assert "The Sumo &#x27;89 Lab" in output.entrypoint.read_text(encoding="utf-8")


def test_goats_link_excludes_pre_1989_rikishi(tmp_path: Path) -> None:
    output = build_site(
        data_bundle=write_bundle(tmp_path / "bundle"),
        output_root=tmp_path / "output",
        cache_mode="prod",
    )
    index = output.entrypoint.read_text(encoding="utf-8")
    prose = (output.root / "prose" / "What this site is.html").read_text(
        encoding="utf-8"
    )

    assert "rikishi=1123%2C1354%2C2%2C3" in index
    assert "rikishi=1123%2C1354%2C2%2C3" in prose
    assert "3987" not in index + prose
    assert "4080" not in index + prose
