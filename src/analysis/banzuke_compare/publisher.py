"""
Static publisher for the Banzuke Change Report browser app.

This module is intentionally written top-down.  The public contract of
``main`` is the publication contract: given a valid project/data world and a
requested current banzuke date, leave behind a static browser app whose data
files satisfy the BCR browser contract.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.parser.parser2_IntDate import IntDate

from .classes import (
    PublicationRequest,
)
from .banzuke_diff import build_banzuke_diff
from .banzuke_source import load_publication_source
from .deploy import copy_static_assets
from .publisher_reports import write_publication_data
from .report_view import build_bcr_report


STATIC_FILE_NAMES = (
    "index.html",
    "banzuke_change_report.css",
    "banzuke_change_report.js",
)

DATA_FILE_NAME = "banzuke_change_report.csv"
SITE_CONFIG_FILE_NAME = "site_config.json"

DEFAULT_WEB_ROOT = Path(r"A:/local/html/bcr")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish the static Banzuke Change Report browser app."
    )
    parser.add_argument(
        "--date",
        default=None,
        help=(
            "Current banzuke date in YYYY/MM format. "
            "Defaults to the next basho after the latest completed basho."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_WEB_ROOT,
        help="Directory to receive the deployable static BCR app.",
    )
    return parser


def _parse_date(date_text: str) -> IntDate:
    year_text, month_text = date_text.split("/", 1)
    return IntDate(int(year_text), int(month_text))


def build_publication_request(args: argparse.Namespace) -> PublicationRequest:
    """
    Contract:
        args is the parsed command-line namespace from _build_parser.
        Returns the complete filesystem/date policy for one publisher run.
    """

    package_dir = Path(__file__).resolve().parent

    return PublicationRequest(
        requested_date=None if args.date is None else _parse_date(args.date),
        output_root=args.output_root,
        static_dir=package_dir / "files",
        common_static_dir=package_dir.parent / "common" / "files",
    )


def main() -> None:
    """
    Contract:
        Inputs are the current filesystem/data world and command-line state.

        Preconditions:
            - The requested current banzuke date, or the next basho after the
              latest completed basho when no date is requested, is available
              to the project parser/history layer.
            - The previous banzuke and previous-result context required by BCR
              are available.
            - BCR static assets exist in the news files directory.
            - Shared lab CSS assets exist in analysis/common/files.
            - The output root is writable.

        Guarantees:
            - Writes BCR CSV data satisfying the browser CSV contract.
            - Writes BCR site_config.json satisfying the browser config
              contract.
            - Copies HTML/CSS/JS and shared CSS assets needed by the static
              browser app.
            - Leaves output_root in a state that can be served as the BCR
              static page.
    """

    args = _build_parser().parse_args()
    request = build_publication_request(args)

    source = load_publication_source(request)
    diff = build_banzuke_diff(source)
    report = build_bcr_report(diff)
    published_files = write_publication_data(report)
    copy_static_assets(request)

    print("BCR publisher run complete")
    print(f"Current banzuke: {source.current_date}")
    print(f"Output: {request.output_root}")
    print(f"Data: {published_files.csv_file}")
    print(f"Config: {published_files.site_config_file}")


if __name__ == "__main__":
    main()
    from .deploy import main as upload
    upload()
