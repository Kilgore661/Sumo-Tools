"""Command-line entry point for the career bout volume probe."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History

from .analysis import analyse_history
from .model import HistorySource
from .reports import DEFAULT_OUTPUT_ROOT, write_outputs


SHORT_HISTORY_ZIP = Path("files/output/Historys/1978_01 to 1980_11.zip")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plot career fought-bout volume against mean relative banzuke position."
        )
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--history-zip",
        type=Path,
        help="Use an explicit annotated History zip instead of the live store.",
    )
    source.add_argument(
        "--short",
        action="store_true",
        help=f"Use the standard short development History ({SHORT_HISTORY_ZIP}).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Timestamped run parent. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    return parser


def load_history(args: argparse.Namespace) -> tuple[History, HistorySource]:
    """Resolve the selected external History source."""

    if args.short:
        return load_zip_source(SHORT_HISTORY_ZIP, kind="short_history_zip")
    if args.history_zip is not None:
        return load_zip_source(args.history_zip, kind="history_zip")
    return get_history(), HistorySource(kind="live_store", path="", sha256="")


def load_zip_source(path: Path, *, kind: str) -> tuple[History, HistorySource]:
    """Load one annotated History zip and record its file identity."""

    resolved_path = path.resolve()
    zipless = resolved_path.with_suffix("") if resolved_path.suffix == ".zip" else resolved_path
    history = load_history_with_annotations(str(zipless))
    digest_path = (
        resolved_path
        if resolved_path.suffix == ".zip"
        else resolved_path.with_suffix(".zip")
    )
    digest = hashlib.sha256(digest_path.read_bytes()).hexdigest()
    return history, HistorySource(kind=kind, path=str(digest_path), sha256=digest)


def main() -> None:
    args = build_parser().parse_args()
    history, source = load_history(args)
    result = analyse_history(history)
    outputs = write_outputs(
        result,
        source=source,
        output_root=args.output_root,
    )
    print(f"History: {result.history_first_basho} to {result.history_last_basho}")
    print(f"Basho: {result.history_basho_count}")
    print(f"Rikishi: {len(result.career_rows)}")
    print(f"Primary population: {sum(row.primary_population for row in result.career_rows)}")
    print(f"Exceptions: {result.exception_count}")
    print(f"Run directory: {outputs.run_directory}")
    print(f"Scatter: {outputs.scatter_html}")
    print(f"Bout probability: {outputs.bout_probability_html}")
    print(f"Manifest: {outputs.manifest_json}")


if __name__ == "__main__":
    main()
