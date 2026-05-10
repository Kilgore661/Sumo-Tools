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


def publisher_page_bundle_file(run_stamp: str) -> Path:
    return publisher_run_output_dir(run_stamp) / "page_bundle.json"


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


def write_page_bundle_json(
    output_file: Path,
    anchor_date: Date,
    direction: str,
    supported_num_basho: tuple[int, ...],
    default_num_basho: int,
    default_division: str,
) -> None:
    """
    Write the first make_site-facing bundle contract for Standings by Wins.

    The existing standalone browser app remains during migration, but this
    file records the producer-owned data/config/metadata that a native
    make_site renderer should consume.
    """

    payload = {
        "schema": "sumo-tools.table-page-bundle.v0",
        "page": {
            "id": "standings_by_wins",
            "title": "Standings by Wins",
            "summary": "Rolling recent-performance standings by wins.",
            "status": "candidate",
        },
        "producer": {
            "module": "src.analysis.standings",
            "legacy_app_shell": "src/analysis/standings/files/index.html",
            "public_ui_owner": "make_site",
        },
        "view": {
            "kind": "table",
            "layout": "tool",
        },
        "data": {
            "site_config": "site_config.json",
            "window_files": [
                {
                    "num_basho": num_basho,
                    "csv": (
                        "multiple basho standings view "
                        f"({escape_date(anchor_date)}, {direction}, {num_basho}).csv"
                    ),
                    "metadata": (
                        "multiple basho standings view "
                        f"({escape_date(anchor_date)}, {direction}, {num_basho}).json"
                    ),
                }
                for num_basho in supported_num_basho
            ],
        },
        "options": [
            {
                "id": "viewMode",
                "kind": "enum",
                "default": "standard",
                "values": [
                    {"value": "standard", "label": "Wins per Basho"},
                    {"value": "percentages", "label": "Wins per Bout"},
                    {"value": "combined", "label": "Combined"},
                ],
            },
            {
                "id": "currentNumBasho",
                "kind": "enum",
                "default": default_num_basho,
                "values": [
                    {"value": num_basho, "label": str(num_basho)}
                    for num_basho in supported_num_basho
                ],
            },
            {
                "id": "currentOnly",
                "kind": "boolean",
                "default": True,
                "label": "Active Rikishi Only",
            },
            {
                "id": "currentDivision",
                "kind": "enum",
                "default": default_division,
                "values": [
                    {"value": "all", "label": "All"},
                    {"value": "makuuchi", "label": "Makuuchi"},
                    {"value": "juryo", "label": "Juryo"},
                    {"value": "makushita", "label": "Makushita"},
                    {"value": "sandanme", "label": "Sandanme"},
                    {"value": "jonidan", "label": "Jonidan"},
                    {"value": "jonokuchi", "label": "Jonokuchi"},
                ],
            },
        ],
        "columns": [
            {
                "id": "row_number",
                "label": "#",
                "sortable": False,
                "views": ["standard", "percentages", "combined"],
            },
            {
                "id": "shikona",
                "label": "Shikona",
                "sortable": True,
                "sort_key": "shikona",
                "views": ["standard", "percentages", "combined"],
                "link": "rikishi",
                "note": "note-identity",
            },
            {
                "id": "chii",
                "label": "Chii",
                "sortable": True,
                "sort_key": "chii_ordinal",
                "views": ["standard", "percentages", "combined"],
                "note": "note-identity",
            },
            {
                "id": "credited_wins",
                "label": "Wins",
                "sortable": True,
                "sort_key": "credited_wins",
                "views": ["standard", "percentages", "combined"],
                "note": "note-wins",
            },
            {
                "id": "selected_average_credited_wins",
                "label": "Average",
                "sortable": True,
                "sort_key": "selected_average_credited_wins",
                "views": ["standard", "combined"],
            },
            {
                "id": "selected_expected_bout_count",
                "label": "Bouts",
                "sortable": True,
                "sort_key": "selected_expected_bout_count",
                "views": ["percentages", "combined"],
                "note": "note-bouts",
            },
            {
                "id": "win_percent",
                "label": "Win %",
                "sortable": True,
                "sort_key": "win_percent",
                "views": ["percentages", "combined"],
            },
        ],
        "sort_defaults": {
            "column": "selected_average_credited_wins",
            "sort_id": "standard-average",
            "descending": True,
        },
        "notes": [
            {
                "id": "note-identity",
                "for": "all",
                "text": (
                    "The reported Shikona and Chii are those that pertain to "
                    "the rikishi in the latest basho."
                ),
            },
            {
                "id": "note-wins",
                "for": "all",
                "text": "Wins include fusensho.",
            },
            {
                "id": "note-active",
                "for": "all",
                "text": (
                    "An Active rikishi is one that is listed on the banzuke "
                    "for the latest basho."
                ),
            },
            {
                "id": "note-bouts",
                "for": "percentages combined",
                "text": (
                    "Bouts is the expected number of scheduled bouts in the "
                    "selected window."
                ),
            },
        ],
        "behaviour": {
            "url_state": True,
            "sortable_columns": True,
            "sticky_headers": True,
            "rikishi_links": True,
            "note_popovers": True,
        },
    }

    write_json(output_file, payload)
