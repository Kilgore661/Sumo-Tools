"""Assemble and deploy the accepted Elo-89 website."""

from __future__ import annotations

import argparse
from pathlib import Path
from time import time

from src.products.make_site89.build import build_site
from src.products.make_site89.deploy import (
    build_output_from_existing,
    deploy_targets,
    load_deployment_plan,
    preflight_deploy_targets,
    select_deploy_targets,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_BUNDLE = Path("files/output/analysis/elo89_site_bundle")
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "files" / "output" / "make_elo89"
DEFAULT_DEPLOY_TARGETS_PATH = Path("distro/make_elo89_targets.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the accepted Elo-89 site into its independent make_elo89 "
            "output tree and deploy it to the configured sumo-elo89 targets."
        )
    )
    parser.add_argument(
        "--data-bundle",
        type=Path,
        default=DEFAULT_DATA_BUNDLE,
        help=f"Produced Elo-89 site-data bundle. Default: {DEFAULT_DATA_BUNDLE}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Generated site directory. Default: {DEFAULT_OUTPUT_ROOT}.",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Build without development cache-busting query parameters.",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build the output tree and do not copy it to the local server.",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Deploy the existing make_elo89 output without rebuilding it.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Deploy only local filesystem-copy targets and skip remote SFTP.",
    )
    return parser


def reject_conflicting_modes(args: argparse.Namespace) -> None:
    if args.build_only and args.no_build:
        raise SystemExit("--build-only and --no-build cannot be used together")
    if args.no_build and args.prod:
        raise SystemExit("--prod does not apply with --no-build")


def main(argv: list[str] | None = None) -> None:
    started = time()
    args = build_parser().parse_args(argv)
    reject_conflicting_modes(args)
    targets = ()
    if not args.build_only:
        plan = load_deployment_plan(DEFAULT_DEPLOY_TARGETS_PATH)
        targets = select_deploy_targets(plan, local_only=args.local_only)
        targets = preflight_deploy_targets(targets)
    if args.no_build:
        output = build_output_from_existing(args.output)
        print(f"Using existing build: {output.root}")
    else:
        output = build_site(
            data_bundle=args.data_bundle,
            output_root=args.output,
            cache_mode="prod" if args.prod else "dev",
        )
        print(f"Built: {output.entrypoint}")
        print(f"Files: {output.file_count}")
    if not args.build_only:
        for result in deploy_targets(output, targets):
            print(
                f"Deployed {result.file_count} files to "
                f"{result.method} target {result.target_name}: {result.target_root}"
            )
            if result.public_url:
                print(result.public_url)
    print(f"Elapsed: {time() - started:.1f}s")


if __name__ == "__main__":
    main()
