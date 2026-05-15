"""Command-line interface for building and deploying the public site."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from src.analysis.sumo_history.career_lifecycle.career_length import (
    build_career_length_outputs,
    load_history_from_zip,
)
from src.analysis.sumo_history.career_lifecycle.rank_at_retirement import (
    build_rank_at_retirement_outputs,
)
from src.analysis.equelo.fixed_v2.v5_landmarks import (
    write_typical_equelo_outputs,
)
from src.infra.live_store.api import get_history
from src.misc.first_appearance import build_first_chii_appearance_outputs
from src.misc.makuuchi_by_era import build_makuuchi_rank_by_era_outputs

from .builder import build_site
from .deploy import HOST, LOCAL_ROOT, REMOTE_ROOT, deploy_local, deploy_remote
from .site_definition import BUILD_CONFIG, site_with_career_lifecycle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local-root",
        type=Path,
        default=LOCAL_ROOT,
        help="Local web directory to receive the deployable site.",
    )
    parser.add_argument(
        "--remote-root",
        default=REMOTE_ROOT,
        help="Remote web root to receive the deployable site.",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build the persisted output tree without deployment.",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Build without dev cache-busting query parameters.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Build and deploy locally, but do not upload remotely.",
    )
    parser.add_argument(
        "--no-banzuke",
        action="store_true",
        help=(
            "Do not include the full Basho Results Browser per-basho payload "
            "data in the built/deployed site."
        ),
    )
    parser.add_argument(
        "--one-banzuke",
        action="store_true",
        help=(
            "Include only the most recent Basho Results Browser per-basho "
            "payload data in the built/deployed site."
        ),
    )
    parser.add_argument(
        "--career-history-zip",
        type=Path,
        help=(
            "Deprecated alias for --history-zip, retained for local/offline "
            "testing commands written before Rank at Retirement was added."
        ),
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help=(
            "Build generated site data from a History zip instead of the live "
            "store. Intended for local/offline testing."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.no_banzuke and args.one_banzuke:
        raise SystemExit("--no-banzuke and --one-banzuke cannot be used together")
    basho_results_payload_mode = "latest" if args.one_banzuke else "all"
    if args.no_banzuke:
        basho_results_payload_mode = "none"
    history_zip = args.history_zip or args.career_history_zip
    history = (
        load_history_from_zip(history_zip)
        if history_zip
        else get_history()
    )
    dates = sorted(history.keys())
    if not dates:
        raise SystemExit("No history available for site build")
    start_year = int(dates[0].year)
    end_year = int(dates[-1].year)
    career_outputs = build_career_length_outputs(history, print_summary=False)
    retirement_outputs = build_rank_at_retirement_outputs(history, print_summary=False)
    build_first_chii_appearance_outputs(
        history,
        start=start_year,
        end=end_year,
        print_summary=False,
    )
    build_makuuchi_rank_by_era_outputs(
        history,
        start=start_year,
        end=end_year,
        print_summary=False,
    )
    typical_equelo_outputs = write_typical_equelo_outputs()
    build_config = replace(
        BUILD_CONFIG,
        cache_mode="prod" if args.prod else BUILD_CONFIG.cache_mode,
    )
    build_site(
        site_with_career_lifecycle(
            career_outputs,
            retirement_outputs,
            typical_equelo_outputs,
            basho_results_payload_mode=basho_results_payload_mode,
        ),
        build_config,
    )
    print(f"built {build_config.output_root}")
    if args.build_only:
        return
    local_root = args.local_root.resolve()
    deploy_local(build_config.output_root, local_root)
    print(f"locally deployed {local_root}")
    if args.local_only:
        return
    count = deploy_remote(local_root, args.remote_root)
    print(f"remotely deployed {count} files to {HOST}:{args.remote_root}")
    print(f"https://www.661.org.uk{args.remote_root.removeprefix('/var/www/html')}/")
