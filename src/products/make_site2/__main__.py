"""Command entry point for early make_site2 builds."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import build_site


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Build without development cache-busting query parameters.",
    )
    parser.add_argument(
        "--no-basho",
        action="store_true",
        help="Do not include Basho Results Browser per-basho payload data.",
    )
    parser.add_argument(
        "--one-basho",
        action="store_true",
        help="Include only the latest Basho Results Browser payload data.",
    )
    parser.add_argument(
        "--brb-payload-mode",
        choices=("all", "latest", "none"),
        default="all",
        help=argparse.SUPPRESS,
    )
    return parser


def resolve_basho_results_payload_mode(args: argparse.Namespace) -> str:
    if args.no_basho and args.one_basho:
        raise SystemExit("--no-basho and --one-basho cannot be used together")
    if args.no_basho:
        return "none"
    if args.one_basho:
        return "latest"
    return args.brb_payload_mode


def resolve_cache_mode(args: argparse.Namespace) -> str:
    return "prod" if args.prod else "dev"


def main() -> None:
    args = build_parser().parse_args()
    kwargs = {
        "basho_results_payload_mode": resolve_basho_results_payload_mode(args),
        "cache_mode": resolve_cache_mode(args),
    }
    if args.history_zip is not None:
        kwargs["history_zip"] = args.history_zip
    output_root = build_site(**kwargs)
    print(output_root)


if __name__ == "__main__":
    main()
