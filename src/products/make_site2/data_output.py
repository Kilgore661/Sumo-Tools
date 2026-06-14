"""Data-output layer for make_site2."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.api import EqueloLookup
from src.analysis.sumo_history.basho_results.build import (
    build_index,
    build_payload_rows,
)
from src.analysis.sumo_history.basho_results.dates import represented_dates
from src.analysis.sumo_history.basho_results.reports import write_index, write_payload
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History

from .perf_chart.build import MasterDataOutput, write_master_data


BASHO_RESULTS_ROUTE_DATA_DIR = Path("sumo-history") / "basho-results" / "data"
CAREER_COMPARISONS_ROUTE_DATA_DIR = Path("rikishi") / "career-comparisons" / "data"
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
CAREER_LENGTH_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "career-lifecycle"
    / "career-length"
    / "data"
)
MOST_CONSECUTIVE_BOUTS_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "records"
    / "most-consecutive-bouts"
    / "data"
)
MOST_CAREER_WINS_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "records"
    / "most-career-wins"
    / "data"
)
MOST_CAREER_LOSSES_ROUTE_DATA_DIR = (
    Path("sumo-history")
    / "records"
    / "most-career-losses"
    / "data"
)
TYPICAL_EQUELO_VALUES_ROUTE_DATA_DIR = (
    Path("ratings-models")
    / "rating-and-rank"
    / "typical-equelo-values"
    / "data"
)
WIN_PROBABILITY_BY_STANDING_ROUTE_DATA_DIR = (
    Path("ratings-models")
    / "observed-vs-modelled"
    / "win-probability-by-standing"
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
CAREER_LENGTH_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "career_length"
    / "site"
    / "career_length_1958_01_to_2026_05"
)
MOST_CONSECUTIVE_BOUTS_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "analysis"
    / "sumo_history"
    / "records"
    / "consecutive_bouts"
)
MOST_CAREER_WINS_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "analysis"
    / "sumo_history"
    / "records"
    / "career_wins"
)
MOST_CAREER_LOSSES_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "analysis"
    / "sumo_history"
    / "records"
    / "career_losses"
)
TYPICAL_EQUELO_VALUES_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "Equelo"
    / "fixed_v2"
    / "landmarks"
    / "site"
    / "typical_equelo_values"
)
WIN_PROBABILITY_BY_STANDING_SOURCE_ROOT = (
    Path("files")
    / "output"
    / "probability"
    / "matchups"
    / "site"
    / "win_probability_by_standing"
)
BANZUKE_DIVISION_BY_ERA_SOURCE_ROOT = (
    Path("files") / "output" / "banzuke_division_era" / "site" / "banzuke_division_by_era"
)
MAKUUCHI_RANK_BY_ERA_SOURCE_ROOT = (
    Path("files") / "output" / "rank_era" / "site" / "makuuchi_rank_by_era"
)
STANDINGS_ROUTE_DATA_DIR = Path("current-sumo") / "standings-by-wins" / "data"
STANDINGS_SOURCE_ROOT = Path("files") / "output" / "standings" / "publisher" / "latest_data"
PERF_CHART_SOURCE_ROOT = Path("files") / "output" / "perf_chart" / "career_comparisons"


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
class CareerLengthDataOutput:
    data_paths: tuple[Path, ...]


@dataclass(frozen=True, kw_only=True)
class MostConsecutiveBoutsDataOutput:
    csv_path: Path


@dataclass(frozen=True, kw_only=True)
class MostCareerWinsDataOutput:
    csv_path: Path


@dataclass(frozen=True, kw_only=True)
class MostCareerLossesDataOutput:
    csv_path: Path


@dataclass(frozen=True, kw_only=True)
class TypicalEqueloValuesDataOutput:
    csv_path: Path


@dataclass(frozen=True, kw_only=True)
class WinProbabilityByStandingDataOutput:
    data_paths: tuple[Path, ...]


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

    ratings = EqueloLookup.load(history)
    full_shikona_store = FullShikonaStore.from_sources(history)
    payload_paths = tuple(
        write_payload(
            date,
            build_payload_rows(
                history=history,
                date=date,
                ratings=ratings,
                full_shikona_store=full_shikona_store,
            ),
            route_data_root,
        )
        for date in payload_dates
    )

    return BashoResultsDataOutput(
        index_path=index_path,
        payload_paths=payload_paths,
    )


def build_career_comparisons_data_output(
    *,
    history: History,
    output_root: Path,
) -> MasterDataOutput:
    """Build the Career Comparisons master trajectory data file."""

    if PERF_CHART_SOURCE_ROOT.exists():
        shutil.rmtree(PERF_CHART_SOURCE_ROOT)
    producer_output = write_master_data(
        history=history,
        output_root=PERF_CHART_SOURCE_ROOT,
    )

    route_data_root = output_root / CAREER_COMPARISONS_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)
    data_path = route_data_root / producer_output.data_path.name
    report_path = route_data_root / producer_output.report_path.name
    shutil.copy2(producer_output.data_path, data_path)
    shutil.copy2(producer_output.report_path, report_path)
    return MasterDataOutput(data_path=data_path, report_path=report_path)


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


def copy_career_length_data_output(
    *,
    output_root: Path,
) -> CareerLengthDataOutput:
    """Copy the Career Length CSV set into the make_site2 output tree."""

    route_data_root = output_root / CAREER_LENGTH_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    names = ("distribution.csv", "pmf.csv", "cdf.csv", "survival.csv", "longest.csv")
    data_paths = tuple(route_data_root / name for name in names)
    for name, target_path in zip(names, data_paths, strict=True):
        shutil.copy2(CAREER_LENGTH_SOURCE_ROOT / name, target_path)
    return CareerLengthDataOutput(data_paths=data_paths)


def copy_most_consecutive_bouts_data_output(
    *,
    output_root: Path,
) -> MostConsecutiveBoutsDataOutput:
    """Copy the Most Consecutive Bouts CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=MOST_CONSECUTIVE_BOUTS_ROUTE_DATA_DIR,
        source_path=MOST_CONSECUTIVE_BOUTS_SOURCE_ROOT / "longest_streak_candidates.csv",
        target_name="longest_streak_candidates.csv",
    )
    return MostConsecutiveBoutsDataOutput(csv_path=csv_path)


def copy_most_career_wins_data_output(
    *,
    output_root: Path,
) -> MostCareerWinsDataOutput:
    """Copy the Most Career Wins CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=MOST_CAREER_WINS_ROUTE_DATA_DIR,
        source_path=MOST_CAREER_WINS_SOURCE_ROOT / "career_wins.csv",
        target_name="career_wins.csv",
    )
    return MostCareerWinsDataOutput(csv_path=csv_path)


def copy_most_career_losses_data_output(
    *,
    output_root: Path,
) -> MostCareerLossesDataOutput:
    """Copy the Most Career Losses CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=MOST_CAREER_LOSSES_ROUTE_DATA_DIR,
        source_path=MOST_CAREER_LOSSES_SOURCE_ROOT / "career_losses.csv",
        target_name="career_losses.csv",
    )
    return MostCareerLossesDataOutput(csv_path=csv_path)


def copy_typical_equelo_values_data_output(
    *,
    output_root: Path,
) -> TypicalEqueloValuesDataOutput:
    """Copy the Typical Equelo Ratings CSV into the make_site2 output tree."""

    csv_path = copy_single_csv_chart_data_output(
        output_root=output_root,
        route_data_dir=TYPICAL_EQUELO_VALUES_ROUTE_DATA_DIR,
        source_path=TYPICAL_EQUELO_VALUES_SOURCE_ROOT / "typical_equelo_values.csv",
        target_name="typical_equelo_values.csv",
    )
    return TypicalEqueloValuesDataOutput(csv_path=csv_path)


def copy_win_probability_by_standing_data_output(
    *,
    output_root: Path,
) -> WinProbabilityByStandingDataOutput:
    """Copy the Win Probability by Standing CSV set into make_site2 output."""

    route_data_root = output_root / WIN_PROBABILITY_BY_STANDING_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    names = ("observed_trace_points.csv", "equelo_trace_points.csv")
    data_paths = tuple(route_data_root / name for name in names)
    for name, target_path in zip(names, data_paths, strict=True):
        shutil.copy2(WIN_PROBABILITY_BY_STANDING_SOURCE_ROOT / name, target_path)
    return WinProbabilityByStandingDataOutput(data_paths=data_paths)


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
