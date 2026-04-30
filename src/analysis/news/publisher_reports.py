"""
Persistence contract for Banzuke Change Report publisher outputs.
"""

import csv
import json

from src.analysis.news.classes import BcrReport, PublishedFiles


DATA_FILE_NAME = "banzuke_change_report.csv"
SITE_CONFIG_FILE_NAME = "site_config.json"
DEFAULT_DIVISION_ID = "makuuchi"

CSV_FIELDNAMES = (
    "division_id",
    "division_label",
    "bz_chii",
    "east_rikishi_id",
    "east_shikona",
    "east_graph_shikona",
    "east_old_chii",
    "east_result",
    "east_delta",
    "east_delta_class",
    "west_rikishi_id",
    "west_shikona",
    "west_graph_shikona",
    "west_old_chii",
    "west_result",
    "west_delta",
    "west_delta_class",
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

    write_report_csv(report=report, output_file=csv_file)
    write_site_config(report=report, output_file=site_config_file)

    return PublishedFiles(
        csv_file=csv_file,
        site_config_file=site_config_file,
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
            f"{prefix}_shikona": "",
            f"{prefix}_graph_shikona": "",
            f"{prefix}_old_chii": "",
            f"{prefix}_result": "",
            f"{prefix}_delta": "",
            f"{prefix}_delta_class": "",
        }

    return {
        f"{prefix}_rikishi_id": str(int(side.rikishi_id)),
        f"{prefix}_shikona": str(side.shikona),
        f"{prefix}_graph_shikona": side.graph_shikona,
        f"{prefix}_old_chii": side.old_chii,
        f"{prefix}_result": side.previous_result,
        f"{prefix}_delta": side.delta,
        f"{prefix}_delta_class": side.delta_class,
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
