"""
Offline publisher for website standings datasets.

Generates the published multiple-basho CSV/JSON pairs required by the
browser application, using fixed project policy and no command-line
parameters.
"""

import csv
import shutil
from pathlib import Path
from time import time
import pickle

from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import Month

from src.analysis.standings.helpers import make_run_stamp
from src.analysis.standings.multiple_basho import (
    resolve_date,
    resolve_window_dates,
    get_multiple_basho_core,
)
from src.analysis.standings.multiple_basho_view import (
    get_multiple_basho_view,
    MultipleBashoView,
)
from src.analysis.standings.publisher_reports import (
    publisher_run_output_dir,
    publisher_csv_file,
    publisher_json_file,
    publisher_page_bundle_file,
    publisher_site_config_file,
    write_sidecar_json,
    write_page_bundle_json,
    write_site_config_json,
)

from .config import PUBLISHER_LATEST_DATA, LEGACY_QUALIFIED_SHIKONA

with LEGACY_QUALIFIED_SHIKONA.open("rb") as f:
    QUALIFIED_SHIKONA = pickle.load(f)

WEB_ROOT = Path(r"A:/local/html/standings")
WEB_DATA = WEB_ROOT / "data"
WEB_COMMON = WEB_ROOT.parent / "common" / "files"

SUPPORTED_NUM_BASHO = (1, 2, 3, 4, 5, 6, 12, 18, 24, 36, 60)
DIRECTION = "BACKWARDS"

DEFAULT_DIVISION = "makuuchi"

def clear_dir_files(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

    for item in path.iterdir():
        if item.is_file():
            item.unlink()


def copy_data_files(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)

    for item in source_dir.iterdir():
        if item.is_file() and item.suffix.lower() in {".csv", ".json"}:
            shutil.copy2(item, target_dir / item.name)


def refresh_latest_data(run_dir: Path) -> None:
    clear_dir_files(PUBLISHER_LATEST_DATA)
    copy_data_files(run_dir, PUBLISHER_LATEST_DATA)

def determine_default_num_basho(history) -> int:
    return 6 # Product default; current spec does not mandate this.
    # Old code, may be useful, sets the number of basho to get a "Year to date"
    # display.
    dates = sorted(history.keys())

    for j in range(len(dates) - 1, -1, -1):
        if dates[j].month == Month(1):
            return len(dates) - j

    raise ValueError(
        "Cannot determine default_num_basho: "
        "the history does not contain records for a January basho."
    )


def write_published_view_csv(
    view: MultipleBashoView,
    output_file: Path,
    terminal_rikishi,
) -> None:
    fieldnames = [
        "position",
        "rikishi_id",
        "shikona",
        "graph_shikona",
        "chii",
        "chii_ordinal",
        "is_current",
        "fought_wins",
        "credited_wins",
        "bout_count",
        "selected_basho_count",
        "containing_basho_count",
        "selected_expected_bout_count",
        "selected_available_bout_count",
        "containing_expected_bout_count",
        "containing_available_bout_count",
        "selected_average_fought_wins",
        "selected_average_credited_wins",
        "win_percent",
        "containing_average_fought_wins",
        "containing_average_credited_wins",
        "selected_stdev_fought_wins",
        "selected_stdev_credited_wins",
        "containing_stdev_fought_wins",
        "containing_stdev_credited_wins",
        "selected_sem_fought_wins",
        "selected_sem_credited_wins",
        "containing_sem_fought_wins",
        "containing_sem_credited_wins",
        "selected_ci95_half_width_fought_wins",
        "selected_ci95_half_width_credited_wins",
        "containing_ci95_half_width_fought_wins",
        "containing_ci95_half_width_credited_wins",
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in view.rows:
            writer.writerow(
                {
                    "position": row.position,
                    "rikishi_id": int(row.rikishi_id),
                    "shikona": str(row.shikona),
                    "graph_shikona": QUALIFIED_SHIKONA.get(row.rikishi_id, str(row.shikona)),
                    "chii": row.chii,
                    "chii_ordinal": row.chii_ordinal,
                    "is_current": "1" if row.rikishi_id in terminal_rikishi else "0",
                    "fought_wins": row.fought_wins,
                    "credited_wins": row.credited_wins,
                    "bout_count": row.bout_count,
                    "selected_basho_count": row.selected_basho_count,
                    "containing_basho_count": row.containing_basho_count,
                    "selected_expected_bout_count": row.selected_expected_bout_count,
                    "selected_available_bout_count": row.selected_available_bout_count,
                    "containing_expected_bout_count": row.containing_expected_bout_count,
                    "containing_available_bout_count": row.containing_available_bout_count,
                    "selected_average_fought_wins": row.selected_average_fought_wins,
                    "selected_average_credited_wins": row.selected_average_credited_wins,
                    "win_percent": row.win_percent,
                    "containing_average_fought_wins": row.containing_average_fought_wins,
                    "containing_average_credited_wins": row.containing_average_credited_wins,
                    "selected_stdev_fought_wins": row.selected_stdev_fought_wins,
                    "selected_stdev_credited_wins": row.selected_stdev_credited_wins,
                    "containing_stdev_fought_wins": row.containing_stdev_fought_wins,
                    "containing_stdev_credited_wins": row.containing_stdev_credited_wins,
                    "selected_sem_fought_wins": row.selected_sem_fought_wins,
                    "selected_sem_credited_wins": row.selected_sem_credited_wins,
                    "containing_sem_fought_wins": row.containing_sem_fought_wins,
                    "containing_sem_credited_wins": row.containing_sem_credited_wins,
                    "selected_ci95_half_width_fought_wins": row.selected_ci95_half_width_fought_wins,
                    "selected_ci95_half_width_credited_wins": row.selected_ci95_half_width_credited_wins,
                    "containing_ci95_half_width_fought_wins": row.containing_ci95_half_width_fought_wins,
                    "containing_ci95_half_width_credited_wins": row.containing_ci95_half_width_credited_wins,
                }
            )


def publish_one_window(
    history,
    run_stamp: str,
    anchor_date,
    num_basho: int,
) -> None:
    selected_dates = resolve_window_dates(
        history=history,
        date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
    )

    core = get_multiple_basho_core(
        history=history,
        selected_dates=selected_dates,
    )

    view = get_multiple_basho_view(
        history=history,
        core=core,
    )

    terminal_date = selected_dates[-1]
    terminal_rikishi = set(history(terminal_date).banzuke.riks)

    csv_file = publisher_csv_file(
        run_stamp=run_stamp,
        anchor_date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
    )

    json_file = publisher_json_file(
        run_stamp=run_stamp,
        anchor_date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
    )

    write_published_view_csv(
        view=view,
        output_file=csv_file,
        terminal_rikishi=terminal_rikishi,
    )

    write_sidecar_json(
        output_file=json_file,
        anchor_date=anchor_date,
        direction=DIRECTION,
        num_basho=num_basho,
        selected_dates=selected_dates,
    )


def deploy_to_local_web() -> None:
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    WEB_COMMON.mkdir(parents=True, exist_ok=True)

    static_dir = Path(__file__).resolve().parent / "files"
    common_static_dir = Path(__file__).resolve().parents[1] / "common" / "files"

    for name in ["index.html", "standings.css", "standings.js"]:
        shutil.copy2(static_dir / name, WEB_ROOT / name)

    for name in ["site-wide.css", "tool-layout.css"]:
        shutil.copy2(common_static_dir / name, WEB_COMMON / name)

    clear_dir_files(WEB_DATA)
    copy_data_files(PUBLISHER_LATEST_DATA, WEB_DATA)


def main() -> None:
    t0 = time()

    history = get_history()
    run_stamp = make_run_stamp()

    run_dir = publisher_run_output_dir(run_stamp)
    run_dir.mkdir(parents=True, exist_ok=True)

    anchor_date = resolve_date(
        history=history,
        direction=DIRECTION,
        requested_date=None,
    )

    config_file = publisher_site_config_file(run_stamp)

    write_site_config_json(
        output_file=config_file,
        anchor_date=anchor_date,
        direction=DIRECTION,
        supported_num_basho=SUPPORTED_NUM_BASHO,
        default_num_basho=determine_default_num_basho(history),
        default_division=DEFAULT_DIVISION,
    )

    write_page_bundle_json(
        output_file=publisher_page_bundle_file(run_stamp),
        anchor_date=anchor_date,
        direction=DIRECTION,
        supported_num_basho=SUPPORTED_NUM_BASHO,
        default_num_basho=determine_default_num_basho(history),
        default_division=DEFAULT_DIVISION,
    )

    for num_basho in SUPPORTED_NUM_BASHO:
        publish_one_window(
            history=history,
            run_stamp=run_stamp,
            anchor_date=anchor_date,
            num_basho=num_basho,
        )

    refresh_latest_data(run_dir)
    deploy_to_local_web()

    print(f"Publisher run complete in {time() - t0:.0f}s")
    print(f"Output: {run_dir}")
    print(f"Deployed to: {WEB_ROOT}")


if __name__ == "__main__":
    main()
    from .deploy import main as upload
    upload()
