"""Command-line entry point for producing a make_site89 data bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from .producer import DEFAULT_BANZUKE_SOURCE, DEFAULT_OUTPUT_ROOT, produce_site89_bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produce the complete Elo-89 site-data bundle.")
    parser.add_argument("--history-zip", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--banzuke-source-root", type=Path, default=DEFAULT_BANZUKE_SOURCE)
    args = parser.parse_args(argv)
    zipless = args.history_zip.with_suffix("") if args.history_zip.suffix == ".zip" else args.history_zip
    history = load_history_with_annotations(str(zipless))
    root = produce_site89_bundle(
        history=history,
        output_root=args.output_root,
        history_source=str(args.history_zip),
        banzuke_source_root=args.banzuke_source_root,
    )
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
