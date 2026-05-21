"""Data-output layer for make_site2."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from src.analysis.sumo_history.basho_results.build import (
    build_index,
    build_payload_rows,
)
from src.analysis.sumo_history.basho_results.dates import represented_dates
from src.analysis.sumo_history.basho_results.ratings import RatingLookup
from src.analysis.sumo_history.basho_results.reports import write_index, write_payload
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


BASHO_RESULTS_ROUTE_DATA_DIR = Path("sumo-history") / "basho-results" / "data"
FINISH_BY_CHII_ROUTE_DATA_DIR = Path("performance") / "finish-by-chii" / "data"
DIVISION_STABILITY_ROUTE_DATA_DIR = (
    Path("banzuke-rank") / "division-stability" / "data"
)
FIRST_CHII_APPEARANCE_ROUTE_DATA_DIR = (
    Path("banzuke-rank")
    / "rank-history"
    / "first-chii-appearance"
    / "data"
)
RANK_AT_RETIREMENT_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "career-lifecycle"
    / "rank-at-retirement"
    / "data"
)
BANZUKE_DIVISION_BY_ERA_ROUTE_DATA_DIR = (
    Path("banzuke-rank")
    / "banzuke-structure-over-time"
    / "banzuke-division-by-era"
    / "data"
)
MAKUUCHI_RANK_BY_ERA_ROUTE_DATA_DIR = (
    Path("banzuke-rank")
    / "banzuke-structure-over-time"
    / "makuuchi-rank-by-era"
    / "data"
)
BANZUKE_CHANGES_ROUTE_DIR = Path("current-sumo") / "banzuke-changes"
BANZUKE_CHANGES_SOURCE_ROOT = Path("files") / "output" / "bcr"
DIVISION_STABILITY_SOURCE_ROOT = (
    Path("files") / "output" / "persistence" / "site" / "division_stability"
)
FIRST_CHII_APPEARANCE_SOURCE_ROOT = (
    Path("files") / "output" / "first_app" / "site" / "first_chii_appearance"
)
RANK_AT_RETIREMENT_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "rank_at_retirement"
    / "site"
    / "rank_at_retirement_1958_01_to_2026_05"
)
BANZUKE_DIVISION_BY_ERA_SOURCE_ROOT = (
    Path("files") / "output" / "banzuke_division_era" / "site" / "banzuke_division_by_era"
)
MAKUUCHI_RANK_BY_ERA_SOURCE_ROOT = (
    Path("files") / "output" / "rank_era" / "site" / "makuuchi_rank_by_era"
)
STANDINGS_ROUTE_DATA_DIR = Path("current-sumo") / "standings-by-wins" / "data"
STANDINGS_SOURCE_ROOT = Path("files") / "output" / "standings" / "publisher" / "latest_data"


@dataclass(frozen=True, kw_only=True)
class BashoResultsDataOutput:
    index_path: Path
    payload_paths: tuple[Path, ...]


@dataclass(frozen=True, kw_only=True)
class FinishByChiiDataOutput:
    top_thresholds_path: Path
    bottom_thresholds_path: Path


@dataclass(frozen=True, kw_only=True)
class SingleCsvChartDataOutput:
    csv_path: Path


@dataclass(frozen=True, kw_only=True)
class BanzukeChangesDataOutput:
    site_config_path: Path
    report_csv_path: Path


@dataclass(frozen=True, kw_only=True)
class StandingsDataOutput:
    site_config_path: Path
    data_paths: tuple[Path, ...]


def load_history_from_zip(path: Path) -> History:
    """Load a History from a zip-backed annotated serialisation."""

    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def build_basho_results_data_output(
    *,
    history: History,
    output_root: Path,
    payload_mode: str = "all",
) -> BashoResultsDataOutput:
    """Build BRB index and CSV payloads into the make_site2 output tree."""

    if payload_mode not in {"all", "latest", "none"}:
        raise ValueError(f"Unsupported BRB payload mode: {payload_mode!r}")

    dates = represented_dates(history)
    if not dates:
        raise ValueError("No represented basho dates found")

    route_data_root = output_root / BASHO_RESULTS_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    index = build_index(history)
    index_path = write_index(index, route_data_root)

    if payload_mode == "none":
        payload_dates = ()
    elif payload_mode == "latest":
        payload_dates = (dates[-1],)
    else:
        payload_dates = dates

    ratings = RatingLookup.load()
    payload_paths = tuple(
        write_payload(
            date,
            build_payload_rows(history=history, date=date, ratings=ratings),
            route_data_root,
        )
        for date in payload_dates
    )

    return BashoResultsDataOutput(
        index_path=index_path,
        payload_paths=payload_paths,
    )


def copy_finish_by_chii_data_output(*, output_root: Path) -> FinishByChiiDataOutput:
    """Copy the public Finish by Chii CSV set into the make_site2 output tree."""

    source_root = Path("files") / "output" / "misc"
    route_data_root = output_root / FINISH_BY_CHII_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    top_thresholds_path = route_data_root / "top_thresholds.csv"
    bottom_thresholds_path = route_data_root / "bottom_thresholds.csv"
    shutil.copy2(
        source_root / "finish_by_chii_1958_2026_top_thresholds.csv",
        top_thresholds_path,
    )
    shutil.copy2(
        source_root / "finish_by_chii_1958_2026_bottom_thresholds.csv",
        bottom_thresholds_path,
    )
    return FinishByChiiDataOutput(
        top_thresholds_path=top_thresholds_path,
        bottom_thresholds_path=bottom_thresholds_path,
    )


def copy_division_stability_data_output(
    *,
    output_root: Path,
) -> SingleCsvChartDataOutput:
    """Copy the Division Stability CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=DIVISION_STABILITY_ROUTE_DATA_DIR,
        source_path=DIVISION_STABILITY_SOURCE_ROOT / "persistence.csv",
        target_name="persistence.csv",
    )
    return SingleCsvChartDataOutput(csv_path=csv_path)


def copy_first_chii_appearance_data_output(
    *,
    output_root: Path,
) -> SingleCsvChartDataOutput:
    """Copy the First Chii Appearance CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=FIRST_CHII_APPEARANCE_ROUTE_DATA_DIR,
        source_path=FIRST_CHII_APPEARANCE_SOURCE_ROOT / "appearances.csv",
        target_name="appearances.csv",
    )
    return SingleCsvChartDataOutput(csv_path=csv_path)


def copy_rank_at_retirement_data_output(
    *,
    output_root: Path,
) -> SingleCsvChartDataOutput:
    """Copy the Rank at Retirement CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=RANK_AT_RETIREMENT_ROUTE_DATA_DIR,
        source_path=RANK_AT_RETIREMENT_SOURCE_ROOT / "distribution.csv",
        target_name="distribution.csv",
    )
    return SingleCsvChartDataOutput(csv_path=csv_path)


def copy_banzuke_division_by_era_data_output(
    *,
    output_root: Path,
) -> SingleCsvChartDataOutput:
    """Copy the Banzuke Division by Era CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=BANZUKE_DIVISION_BY_ERA_ROUTE_DATA_DIR,
        source_path=BANZUKE_DIVISION_BY_ERA_SOURCE_ROOT / "divisions.csv",
        target_name="divisions.csv",
    )
    return SingleCsvChartDataOutput(csv_path=csv_path)


def copy_makuuchi_rank_by_era_data_output(
    *,
    output_root: Path,
) -> SingleCsvChartDataOutput:
    """Copy the Makuuchi Rank by Era CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=MAKUUCHI_RANK_BY_ERA_ROUTE_DATA_DIR,
        source_path=MAKUUCHI_RANK_BY_ERA_SOURCE_ROOT / "ranks.csv",
        target_name="ranks.csv",
    )
    return SingleCsvChartDataOutput(csv_path=csv_path)


def copy_single_csv_chart_data_output(
    *,
    output_root: Path,
    route_data_dir: Path,
    source_path: Path,
    target_name: str,
) -> Path:
    route_data_root = output_root / route_data_dir
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    target_path = route_data_root / target_name
    shutil.copy2(source_path, target_path)
    return target_path


def copy_banzuke_changes_data_output(*, output_root: Path) -> BanzukeChangesDataOutput:
    """Copy Banzuke Compare producer output into the make_site2 output tree."""

    route_root = output_root / BANZUKE_CHANGES_ROUTE_DIR
    route_data_root = route_root / "data"
    if route_root.exists():
        shutil.rmtree(route_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    site_config_path = route_root / "site_config.json"
    report_csv_path = route_data_root / "banzuke_change_report.csv"
    shutil.copy2(BANZUKE_CHANGES_SOURCE_ROOT / "site_config.json", site_config_path)
    shutil.copy2(
        BANZUKE_CHANGES_SOURCE_ROOT / "data" / "banzuke_change_report.csv",
        report_csv_path,
    )
    return BanzukeChangesDataOutput(
        site_config_path=site_config_path,
        report_csv_path=report_csv_path,
    )


def copy_standings_by_wins_data_output(*, output_root: Path) -> StandingsDataOutput:
    """Copy Standings publisher output into the make_site2 output tree."""

    route_data_root = output_root / STANDINGS_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    site_config_path = route_data_root / "site_config.json"
    shutil.copy2(STANDINGS_SOURCE_ROOT / "site_config.json", site_config_path)
    data_paths = tuple(
        copy_standings_source_file(source_path, route_data_root)
        for source_path in sorted(STANDINGS_SOURCE_ROOT.iterdir())
        if source_path.name.startswith("multiple basho standings view ")
        and source_path.suffix in {".csv", ".json"}
    )
    return StandingsDataOutput(
        site_config_path=site_config_path,
        data_paths=data_paths,
    )


def copy_standings_source_file(source_path: Path, route_data_root: Path) -> Path:
    target_path = route_data_root / source_path.name
    shutil.copy2(source_path, target_path)
    return target_path
