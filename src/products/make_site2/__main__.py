"""Command entry point for early make_site2 builds."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import build_site


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument(
        "--brb-payload-mode",
        choices=("all", "latest", "none"),
        default="all",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    kwargs = {"basho_results_payload_mode": args.brb_payload_mode}
    if args.history_zip is not None:
        kwargs["history_zip"] = args.history_zip
    output_root = build_site(**kwargs)
    print(output_root)


if __name__ == "__main__":
    main()
