"""
Persistence contract for Banzuke Change Report publisher outputs.
"""

import csv
import json

from .classes import BcrReport, PublishedFiles


DATA_FILE_NAME = "banzuke_change_report.csv"
SITE_CONFIG_FILE_NAME = "site_config.json"
PAGE_BUNDLE_FILE_NAME = "page_bundle.json"
DEFAULT_DIVISION_ID = "makuuchi"

CSV_FIELDNAMES = (
    "division_id",
    "division_label",
    "bz_chii",
    "east_rikishi_id",
    "east_chii",
    "east_shikona",
    "east_graph_shikona",
    "east_old_chii",
    "east_result",
    "east_delta",
    "east_delta_class",
    "east_equelo",
    "west_rikishi_id",
    "west_chii",
    "west_shikona",
    "west_graph_shikona",
    "west_old_chii",
    "west_result",
    "west_delta",
    "west_delta_class",
    "west_equelo",
)


def write_publication_data(report: BcrReport) -> PublishedFiles:
    """
    Contract:
        report satisfies report_view.build_bcr_report's output contract.

        Writes the BCR CSV and site_config.json.  The written files satisfy the
        BCR browser data contracts.
    """

    request = report.diff.source.request
    request.output_root.mkdir(parents=True, exist_ok=True)
    request.data_dir.mkdir(parents=True, exist_ok=True)

    csv_file = request.data_dir / DATA_FILE_NAME
    site_config_file = request.output_root / SITE_CONFIG_FILE_NAME
    page_bundle_file = request.output_root / PAGE_BUNDLE_FILE_NAME

    write_report_csv(report=report, output_file=csv_file)
    write_site_config(report=report, output_file=site_config_file)
    write_page_bundle(report=report, output_file=page_bundle_file)

    return PublishedFiles(
        csv_file=csv_file,
        site_config_file=site_config_file,
        page_bundle_file=page_bundle_file,
    )


def write_report_csv(report: BcrReport, output_file) -> None:
    """
    Contract:
        report satisfies the BCR report-view contract.

        Writes one flattened CSV row per displayed banzuke row.
    """

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()

        for division in report.divisions:
            for row in division.rows:
                writer.writerow(csv_row(division, row))


def csv_row(division, row) -> dict[str, str]:
    """
    Contract:
        division and row are members of the same BCR report.

        Returns the flattened browser CSV row.
    """

    return {
        "division_id": division.division_id,
        "division_label": division.division_label,
        "bz_chii": row.bz_chii,
        **side_fields("east", row.east),
        **side_fields("west", row.west),
    }


def side_fields(prefix: str, side) -> dict[str, str]:
    """
    Contract:
        prefix is east or west.  side is either a BcrReportSide or None.

        Returns flattened CSV fields for that side.
    """

    if side is None:
        return {
            f"{prefix}_rikishi_id": "",
            f"{prefix}_chii": "",
            f"{prefix}_shikona": "",
            f"{prefix}_graph_shikona": "",
            f"{prefix}_old_chii": "",
            f"{prefix}_result": "",
            f"{prefix}_delta": "",
            f"{prefix}_delta_class": "",
            f"{prefix}_equelo": "",
        }

    return {
        f"{prefix}_rikishi_id": str(int(side.rikishi_id)),
        f"{prefix}_chii": side.chii,
        f"{prefix}_shikona": str(side.shikona),
        f"{prefix}_graph_shikona": side.graph_shikona,
        f"{prefix}_old_chii": side.old_chii,
        f"{prefix}_result": side.previous_result,
        f"{prefix}_delta": side.delta,
        f"{prefix}_delta_class": side.delta_class,
        f"{prefix}_equelo": side.equelo_rating,
    }


def write_site_config(report: BcrReport, output_file) -> None:
    """
    Contract:
        report satisfies the BCR report-view contract.

        Writes browser metadata and discovery config.
    """

    source = report.diff.source
    divisions = [
        {
            "id": division.division_id,
            "label": division.division_label,
        }
        for division in report.divisions
    ]

    payload = {
        "title": f"The {source.current_date} Banzuke",
        "current_date": str(source.current_date),
        "previous_date": str(source.previous_date),
        "default_division": default_division_id(report),
        "data_file": f"data/{DATA_FILE_NAME}",
        "divisions": divisions,
    }

    output_file.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def write_page_bundle(report: BcrReport, output_file) -> None:
    """
    Write the first make_site-facing bundle contract for Banzuke Changes.

    The existing standalone browser app remains during migration, but this
    file records the producer-owned data/config/metadata that a native
    make_site renderer should consume.
    """

    source = report.diff.source
    payload = {
        "schema": "sumo-tools.table-page-bundle.v0",
        "page": {
            "id": "banzuke_changes",
            "title": "Banzuke Changes",
            "summary": "New-banzuke change report.",
            "status": "candidate",
        },
        "producer": {
            "module": "src.analysis.banzuke_compare",
            "legacy_app_shell": "src/analysis/banzuke_compare/files/index.html",
            "public_ui_owner": "make_site",
        },
        "view": {
            "kind": "table",
            "layout": "tool",
            "default_rendering": "banzuke_style",
            "supported_renderings": ["banzuke_style", "one_column"],
        },
        "data": {
            "site_config": SITE_CONFIG_FILE_NAME,
            "rows": f"data/{DATA_FILE_NAME}",
        },
        "options": [
            {
                "id": "division",
                "kind": "enum",
                "default": default_division_id(report),
                "values": [
                    {
                        "value": division.division_id,
                        "label": division.division_label,
                    }
                    for division in report.divisions
                ],
            },
            {
                "id": "context",
                "kind": "boolean",
                "label": "Previous Basho Context",
                "default": True,
            },
            {
                "id": "banzuke_style",
                "kind": "boolean",
                "label": "Banzuke Style",
                "default": True,
            },
            {
                "id": "delta",
                "kind": "boolean",
                "label": "Show Delta",
                "default": False,
            },
            {
                "id": "equelo",
                "kind": "boolean",
                "label": "Equelo Ratings",
                "default": False,
            },
        ],
        "columns": [
            {
                "id": "equelo",
                "label": "Equelo",
                "group": "equelo",
                "visible_when": "equelo",
            },
            {
                "id": "old_chii",
                "label": "Chii",
                "group": "context",
                "visible_when": "context",
            },
            {
                "id": "result",
                "label": "Result",
                "group": "context",
                "visible_when": "context",
                "note": "note-result",
            },
            {
                "id": "delta_direction",
                "label": "Direction",
                "group": "delta",
                "visible_when": "delta",
                "note": "note-direction",
            },
            {
                "id": "delta",
                "label": "Delta",
                "group": "delta",
                "visible_when": "delta",
                "note": "note-delta",
            },
            {
                "id": "shikona",
                "label": "Shikona",
                "link": "rikishi",
                "always_visible": True,
            },
            {
                "id": "bz_chii",
                "label": "Rank",
                "always_visible": True,
            },
        ],
        "notes": [
            {
                "id": "note-result",
                "for": "context",
                "text": (
                    "Result gives wins, losses and absences followed by prizes "
                    "if any. A trailing up/down marker indicates promotion or "
                    "demotion into the current division."
                ),
            },
            {
                "id": "note-direction",
                "for": "all",
                "text": (
                    "Direction indicates a better or worse position than in "
                    "the previous basho."
                ),
            },
            {
                "id": "note-delta",
                "for": "delta",
                "text": (
                    "Delta indicates the size of movement from the previous "
                    "basho's position, measured in banzuke rows."
                ),
            },
        ],
        "provenance": {
            "current_date": str(source.current_date),
            "previous_date": str(source.previous_date),
        },
        "behaviour": {
            "url_state": True,
            "rikishi_links": True,
            "note_popovers": True,
            "option_sensitive_notes": True,
        },
    }

    output_file.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def default_division_id(report: BcrReport) -> str:
    """
    Contract:
        report contains at least one division.

        Returns the default browser division id.
    """

    available_ids = {division.division_id for division in report.divisions}

    if DEFAULT_DIVISION_ID in available_ids:
        return DEFAULT_DIVISION_ID

    return report.divisions[0].division_id
