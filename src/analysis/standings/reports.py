import csv
import shutil
from pathlib import Path

from src.analysis.standings.config import (
    OUTPUT_DIR,
    LATEST_RUN_FILE,
    LATEST_STANDINGS_FILE,
)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_output_dir(run_stamp: str) -> Path:
    """
    Return the archive folder for a specific run.
    """
    return OUTPUT_DIR / run_stamp


def ensure_run_output_dir(run_stamp: str) -> Path:
    """
    Ensure the per-run archive folder exists and return it.
    """
    out_dir = run_output_dir(run_stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def standings_run_file(
    run_stamp: str,
    date: str,
    direction: str,
    num_basho: int,
    wins: str,
) -> Path:
    """
    Return the standings CSV path inside the per-run archive folder.

    The datetime is carried by the folder name, not the filename.
    """
    filename = f"standings ({date}, {direction}, {num_basho}, {wins}).csv"
    return run_output_dir(run_stamp) / filename


def run_log_file(run_stamp: str) -> Path:
    """
    Return the log file path inside the per-run archive folder.
    """
    return run_output_dir(run_stamp) / "last_run.txt"


def write_standings_csv(rows: list[dict], output_file: Path) -> None:
    fieldnames = ["position", "rikishi_id", "shikona", "real_wins", "all_wins"]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_to_latest(run_file: Path) -> Path:
    """
    Copy a run-specific standings CSV to the root 'latest' standings file.
    """
    LATEST_STANDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(run_file, LATEST_STANDINGS_FILE)
    return LATEST_STANDINGS_FILE


def copy_log_to_latest(run_log: Path) -> Path:
    """
    Copy a run-specific log file to the root 'latest' log file.
    """
    LATEST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(run_log, LATEST_RUN_FILE)
    return LATEST_RUN_FILE
