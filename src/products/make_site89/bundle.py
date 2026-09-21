"""Validated, produced-file input contract for make_site89."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


BUNDLE_SCHEMA_VERSION = 1
MODEL_ID = "elo-89"
STANDINGS_WINDOWS = (1, 2, 3, 4, 5, 6, 12, 18, 24, 36, 60)
MANIFEST_FILE_NAME = "manifest.json"
SITE_FILES_DIRECTORY = "site"

REQUIRED_ARTIFACT_IDS = frozenset(
    {
        "banzuke_changes",
        "banzuke_division_by_era",
        "basho_results_browser",
        "career_comparisons",
        "career_length",
        "division_stability",
        "finish_by_chii",
        "first_chii_appearance",
        "fastest_risers",
        "highest_rating",
        "longest_careers",
        "makuuchi_rank_by_era",
        "most_career_losses",
        "most_career_wins",
        "most_consecutive_bouts",
        "rank_at_retirement",
        "rating_changes",
        "standings_by_wins",
        "typical_rating_values",
        "win_probability_by_standing",
    }
)

REQUIRED_FILES = {
    "banzuke_changes": ("current-sumo/banzuke-changes/site_config.json", "current-sumo/banzuke-changes/data/banzuke_change_report.csv"),
    "banzuke_division_by_era": ("banzuke-rank/banzuke-structure-over-time/banzuke-division-by-era/data/divisions.csv",),
    "basho_results_browser": ("sumo-history/basho-results/data/basho_results_index.json",),
    "career_comparisons": ("rikishi/career-comparisons/data/trajectory_master.json",),
    "career_length": tuple(f"sumo-history/career-lifecycle/career-length/data/{name}.csv" for name in ("distribution", "pmf", "cdf", "survival")),
    "division_stability": ("banzuke-rank/division-stability/data/persistence.csv",),
    "finish_by_chii": tuple(f"performance/finish-by-chii/data/{name}_thresholds.csv" for name in ("top", "bottom")),
    "first_chii_appearance": ("banzuke-rank/rank-history/first-chii-appearance/data/appearances.csv",),
    "fastest_risers": ("sumo-history/records/fastest-risers/data/rankings.json",),
    "highest_rating": ("sumo-history/records/highest-rating/data/highest_rating.csv",),
    "longest_careers": ("sumo-history/records/longest-careers/data/longest.csv",),
    "makuuchi_rank_by_era": ("banzuke-rank/banzuke-structure-over-time/makuuchi-rank-by-era/data/ranks.csv",),
    "most_career_losses": ("sumo-history/records/most-career-losses/data/career_losses.csv",),
    "most_career_wins": ("sumo-history/records/most-career-wins/data/career_wins.csv",),
    "most_consecutive_bouts": ("sumo-history/records/most-consecutive-bouts/data/longest_streak_candidates.csv",),
    "rank_at_retirement": ("sumo-history/career-lifecycle/rank-at-retirement/data/distribution.csv",),
    "rating_changes": ("current-sumo/rating-changes/data/rating_changes_index.json",),
    "standings_by_wins": ("current-sumo/standings-by-wins/data/site_config.json",),
    "typical_rating_values": ("ratings-models/rating-and-rank/typical-rating-values/data/typical_rating_values.csv",),
    "win_probability_by_standing": tuple(f"ratings-models/observed-vs-modelled/win-probability-by-standing/data/{name}_trace_points.csv" for name in ("observed", "rating")),
}


@dataclass(frozen=True, kw_only=True)
class BundleArtifact:
    id: str
    producer: str
    files: tuple[PurePosixPath, ...]


@dataclass(frozen=True, kw_only=True)
class SiteDataBundle:
    root: Path
    history_start: str
    history_end: str
    artifacts: tuple[BundleArtifact, ...]
    manifest: dict[str, object]

    @property
    def site_root(self) -> Path:
        return self.root / SITE_FILES_DIRECTORY


def load_site_data_bundle(root: Path) -> SiteDataBundle:
    """Load and validate one complete post-1988 Elo-89 site-data bundle."""

    root = Path(root)
    manifest_path = root / MANIFEST_FILE_NAME
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Site-data bundle manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid site-data bundle manifest: {manifest_path}") from error
    if not isinstance(manifest, dict):
        raise ValueError("Site-data bundle manifest must be a JSON object")
    if manifest.get("schema_version") != BUNDLE_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported site-data bundle schema version: "
            f"{manifest.get('schema_version')!r}"
        )
    if manifest.get("model_id") != MODEL_ID:
        raise ValueError(
            f"make_site89 requires model_id {MODEL_ID!r}; "
            f"received {manifest.get('model_id')!r}"
        )

    history = manifest.get("history")
    if not isinstance(history, dict):
        raise ValueError("Site-data bundle history must be a JSON object")
    history_start = _required_string(history, "start")
    history_end = _required_string(history, "end")
    if history_start != "1989/01":
        raise ValueError(
            "make_site89 requires post-1988 History beginning at 1989/01; "
            f"received {history_start!r}"
        )

    raw_artifacts = manifest.get("artifacts")
    if not isinstance(raw_artifacts, list):
        raise ValueError("Site-data bundle artifacts must be a JSON array")
    artifacts = tuple(_parse_artifact(item) for item in raw_artifacts)
    artifact_ids = [artifact.id for artifact in artifacts]
    if len(artifact_ids) != len(set(artifact_ids)):
        raise ValueError("Site-data bundle contains duplicate artifact ids")
    missing = sorted(REQUIRED_ARTIFACT_IDS - set(artifact_ids))
    extra = sorted(set(artifact_ids) - REQUIRED_ARTIFACT_IDS)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unknown: {', '.join(extra)}")
        raise ValueError("Invalid site-data artifact set (" + "; ".join(details) + ")")
    for artifact in artifacts:
        missing_files = set(map(PurePosixPath, REQUIRED_FILES[artifact.id])) - set(artifact.files)
        if missing_files:
            raise ValueError(
                f"Artifact {artifact.id!r} is missing required files: "
                + ", ".join(map(str, sorted(missing_files)))
            )

    site_root = root / SITE_FILES_DIRECTORY
    if not site_root.is_dir():
        raise FileNotFoundError(f"Site-data directory not found: {site_root}")
    paths = [path for artifact in artifacts for path in artifact.files]
    if len(paths) != len(set(paths)):
        raise ValueError("Site-data bundle declares a file more than once")
    if not paths:
        raise ValueError("Site-data bundle declares no files")
    for relative_path in paths:
        source = site_root.joinpath(*relative_path.parts)
        if not source.is_file():
            raise FileNotFoundError(f"Declared site-data file not found: {source}")
    by_id = {artifact.id: artifact for artifact in artifacts}
    _validate_index_payloads(site_root, by_id["basho_results_browser"], "sumo-history/basho-results/data/basho_results_index.json")
    _validate_index_payloads(site_root, by_id["rating_changes"], "current-sumo/rating-changes/data/rating_changes_index.json")
    _validate_standings(site_root, by_id["standings_by_wins"])
    _validate_fastest_risers(site_root)

    undeclared = sorted(
        PurePosixPath(path.relative_to(site_root).as_posix())
        for path in site_root.rglob("*")
        if path.is_file()
        and PurePosixPath(path.relative_to(site_root).as_posix()) not in set(paths)
    )
    if undeclared:
        raise ValueError(
            "Site-data bundle contains undeclared files: "
            + ", ".join(str(path) for path in undeclared)
        )

    return SiteDataBundle(
        root=root,
        history_start=history_start,
        history_end=history_end,
        artifacts=artifacts,
        manifest=manifest,
    )


def copy_site_data_bundle(bundle: SiteDataBundle, output_root: Path) -> None:
    """Copy only manifest-declared producer files into a static-site tree."""

    for artifact in bundle.artifacts:
        for relative_path in artifact.files:
            source = bundle.site_root.joinpath(*relative_path.parts)
            destination = output_root.joinpath(*relative_path.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def _parse_artifact(value: object) -> BundleArtifact:
    if not isinstance(value, dict):
        raise ValueError("Each site-data artifact must be a JSON object")
    artifact_id = _required_string(value, "id")
    producer = _required_string(value, "producer")
    raw_files = value.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise ValueError(f"Artifact {artifact_id!r} must declare at least one file")
    files = tuple(_safe_relative_path(item, artifact_id) for item in raw_files)
    if len(files) != len(set(files)):
        raise ValueError(f"Artifact {artifact_id!r} declares duplicate files")
    return BundleArtifact(id=artifact_id, producer=producer, files=files)


def _safe_relative_path(value: object, artifact_id: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ValueError(f"Artifact {artifact_id!r} contains an invalid file path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError(
            f"Artifact {artifact_id!r} contains unsafe file path {value!r}"
        )
    if "\\" in value:
        raise ValueError(
            f"Artifact {artifact_id!r} file paths must use forward slashes: {value!r}"
        )
    return path


def _required_string(source: dict, key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Site-data bundle field {key!r} must be a non-empty string")
    return value


def _validate_index_payloads(
    site_root: Path, artifact: BundleArtifact, index_path: str
) -> None:
    index = json.loads((site_root / index_path).read_text(encoding="utf-8"))
    entries = index.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"Indexed artifact {artifact.id!r} has no entries")
    base = PurePosixPath(index_path).parent
    declared = set(artifact.files)
    for entry in entries:
        payload = entry.get("payload_path") if isinstance(entry, dict) else None
        if not isinstance(payload, str) or not payload:
            raise ValueError(f"Indexed artifact {artifact.id!r} has an invalid payload path")
        relative = PurePosixPath(payload)
        if relative.parts and relative.parts[0] == "data":
            relative = PurePosixPath(*relative.parts[1:])
        resolved = base / relative
        if resolved not in declared:
            raise ValueError(
                f"Indexed artifact {artifact.id!r} references undeclared payload {resolved}"
            )


def _validate_standings(site_root: Path, artifact: BundleArtifact) -> None:
    config_path = PurePosixPath("current-sumo/standings-by-wins/data/site_config.json")
    config = json.loads((site_root / config_path).read_text(encoding="utf-8"))
    anchor = config.get("anchor_token")
    windows = config.get("supported_num_basho")
    if not isinstance(anchor, str) or not anchor or not isinstance(windows, list) or not windows:
        raise ValueError("Standings site config has an invalid anchor or window list")
    if tuple(map(int, windows)) != STANDINGS_WINDOWS:
        raise ValueError(f"Standings site config must provide windows {STANDINGS_WINDOWS}")
    declared = set(artifact.files)
    base = config_path.parent
    for window in windows:
        stem = f"multiple basho standings view ({anchor}, BACKWARDS, {int(window)})"
        for suffix in (".csv", ".json"):
            expected = base / f"{stem}{suffix}"
            if expected not in declared:
                raise ValueError(f"Standings config references undeclared file {expected}")


def _validate_fastest_risers(site_root: Path) -> None:
    path = site_root / "sumo-history/records/fastest-risers/data/rankings.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise ValueError("Fastest Risers rankings must use schema version 2")
    history = data.get("history")
    if not isinstance(history, dict) or history.get("start") != "1989/01":
        raise ValueError("Fastest Risers rankings must begin at 1989/01")
    routes = data.get("routes")
    if not isinstance(routes, dict) or not routes:
        raise ValueError("Fastest Risers rankings must contain routes")
