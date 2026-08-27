"""Command-line entry point for the bout-data completeness audit."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from time import perf_counter

from src.infra.get_bios.api import load_bio_store
from src.infra.live_store.api import get_history, published_name_file
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History

from .analysis import analyse_availability
from .model import SourceIdentity
from .output import DEFAULT_OUTPUT_ROOT, write_outputs


DEFAULT_HISTORY_ZIP = Path("files/output/Historys/1958_01 to 2026_11.zip")
DEFAULT_BIO_DIR = Path("files/output/infra/get_bios/rikishi")
DEFAULT_BIO_STORE = Path("files/output/infra/get_bios/rikishi_bios.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history-zip",
        type=Path,
        default=None,
        help=(
            "Use this annotated History zip instead of the live store. "
            "If the live store is unavailable, the default fallback is "
            f"{DEFAULT_HISTORY_ZIP}."
        ),
    )
    parser.add_argument("--rikishi-pages", type=Path, default=DEFAULT_BIO_DIR)
    parser.add_argument("--bio-store", type=Path, default=DEFAULT_BIO_STORE)
    parser.add_argument("--start", type=_parse_year_month, default=(1958, 1))
    parser.add_argument("--end", type=_parse_year_month, default=(2026, 3))
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    started = perf_counter()
    args = build_parser().parse_args()
    history, history_source = load_history(args.history_zip)
    bio_store_path = args.bio_store.resolve()
    if not bio_store_path.is_file():
        raise FileNotFoundError(f"BioStore not found: {bio_store_path}")
    bio_store = load_bio_store(bio_store_path)
    bio_store_source = SourceIdentity(
        path=str(bio_store_path),
        sha256=hashlib.sha256(bio_store_path.read_bytes()).hexdigest(),
        file_count=1,
        kind="bio_store",
    )
    print(f"History source: {history_source.kind}")
    audit = analyse_availability(
        history,
        history_source=history_source,
        bio_store_source=bio_store_source,
        intai_by_rikishi={
            rikishi_id: bio.intai for rikishi_id, bio in bio_store.bios.items()
        },
        bio_dir=args.rikishi_pages,
        start=args.start,
        end=args.end,
    )
    outputs = write_outputs(audit, output_root=args.output_root)
    print(f"History: {audit.first_basho} to {audit.last_basho}")
    print(f"Basho: {audit.basho_count}")
    print(f"Literal chii-rikishi occurrences: {len(audit.chii_rows):,}")
    print(f"Rikishi pages: {audit.rikishi_page_source.file_count:,}")
    print(f"BioStore records: {len(bio_store.bios):,}")
    print(f"Output: {outputs.output_root}")
    print(f"Findings: {outputs.findings_md}")
    print(f"Total wall-clock time: {perf_counter() - started:.2f} seconds")


def load_history(history_zip: Path | None) -> tuple[History, SourceIdentity]:
    """Prefer the live store, with the canonical zip as an automatic fallback."""

    if history_zip is not None:
        return _load_history_zip(history_zip)

    name_file = published_name_file()
    if name_file.is_file():
        try:
            history = get_history()
        except SystemExit as error:
            print(f"Live store unavailable ({error}); using History zip fallback.")
        else:
            return history, SourceIdentity(
                path=str(name_file.resolve()),
                sha256="",
                file_count=1,
                kind="live_store",
            )

    return _load_history_zip(DEFAULT_HISTORY_ZIP)


def _load_history_zip(history_path: Path) -> tuple[History, SourceIdentity]:
    """Load an annotated History zip and capture its reproducible identity."""

    history_path = history_path.resolve()
    digest_path = (
        history_path if history_path.suffix == ".zip" else history_path.with_suffix(".zip")
    )
    if not digest_path.is_file():
        raise FileNotFoundError(f"History zip not found: {digest_path}")
    zipless = history_path.with_suffix("") if history_path.suffix == ".zip" else history_path
    history = load_history_with_annotations(str(zipless))
    return history, SourceIdentity(
        path=str(digest_path),
        sha256=hashlib.sha256(digest_path.read_bytes()).hexdigest(),
        file_count=1,
        kind="history_zip",
    )


def _parse_year_month(value: str) -> tuple[int, int]:
    try:
        year_text, month_text = value.split("/", maxsplit=1)
        year, month = int(year_text), int(month_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"Expected YYYY/MM, got {value!r}") from error
    if month not in (1, 3, 5, 7, 9, 11):
        raise argparse.ArgumentTypeError(f"Not a basho month: {value}")
    return year, month


if __name__ == "__main__":
    main()
