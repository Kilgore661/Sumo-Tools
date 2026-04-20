"""
Persistence and reporting for published multiple-basho website artefacts.

Builds publisher output paths, names published CSV/JSON artefacts, and writes
metadata sidecar files for browser consumption.

This module is responsible only for publication artefacts and contains no
standings calculation logic.
"""

from pathlib import Path

from src.analysis.standings.helpers import escape_date, write_json
from src.sumo_core.History import Date


PUBLISHER_OUTPUT_DIR = Path("files/output/standings/publisher")


def publisher_runs_dir() -> Path:
    return PUBLISHER_OUTPUT_DIR / "runs"


def publisher_run_output_dir(run_stamp: str) -> Path:
    return publisher_runs_dir() / run_stamp


def publisher_csv_file(
    run_stamp: str,
    anchor_date: Date,
    direction: str,
    num_basho: int,
) -> Path:
    filename = (
        f"multiple basho standings view "
        f"({escape_date(anchor_date)}, {direction}, {num_basho}).csv"
    )
    return publisher_run_output_dir(run_stamp) / filename


def publisher_json_file(
    run_stamp: str,
    anchor_date: Date,
    direction: str,
    num_basho: int,
) -> Path:
    filename = (
        f"multiple basho standings view "
        f"({escape_date(anchor_date)}, {direction}, {num_basho}).json"
    )
    return publisher_run_output_dir(run_stamp) / filename


def publisher_site_config_file(run_stamp: str) -> Path:
    return publisher_run_output_dir(run_stamp) / "site_config.json"


def write_sidecar_json(
    output_file: Path,
    anchor_date: Date,
    direction: str,
    num_basho: int,
    selected_dates: tuple[Date, ...],
) -> None:
    payload = {
        "anchor_date": str(anchor_date),
        "direction": direction,
        "num_basho": num_basho,
        "effective_start_date": str(selected_dates[0]),
        "effective_end_date": str(selected_dates[-1]),
    }

    write_json(output_file, payload)


def write_site_config_json(
    output_file: Path,
    anchor_date: Date,
    direction: str,
    supported_num_basho: tuple[int, ...],
    default_num_basho: int,
    default_division: str,
) -> None:
    payload = {
        "anchor_token": escape_date(anchor_date),
        "direction": direction,
        "supported_num_basho": list(supported_num_basho),
        "default_num_basho": default_num_basho,
        "default_division": default_division,
    }

    write_json(output_file, payload)
