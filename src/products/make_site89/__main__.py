"""Command entry point for make_site89 builds and local deployment."""

from __future__ import annotations

import argparse
from pathlib import Path
from time import time

from .build import DEFAULT_OUTPUT_ROOT, build_site
from .deploy import (
    DEFAULT_DEPLOY_TARGETS_PATH,
    build_output_from_existing,
    deploy_targets,
    load_deployment_plan,
    select_deploy_targets,
)


DEFAULT_DATA_BUNDLE = Path("files/output/analysis/site89_bundle")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the post-1988 Elo-89 site from a produced data bundle and "
            "deploy it to the configured local-server target."
        )
    )
    parser.add_argument(
        "--data-bundle",
        type=Path,
        default=DEFAULT_DATA_BUNDLE,
        help=(
            "Directory containing manifest.json and the produced site/ tree. "
            f"Default: {DEFAULT_DATA_BUNDLE}."
        ),
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
        help="Deploy the existing output tree without rebuilding it.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help=(
            "Deploy only to local win_copy targets. make_site89 currently has "
            "only its local Apache target."
        ),
    )
    return parser


def main() -> None:
    started = time()
    args = build_parser().parse_args()
    if args.build_only and args.no_build:
        raise SystemExit("--build-only and --no-build cannot be used together")
    if args.no_build and args.prod:
        raise SystemExit("--prod does not apply with --no-build")
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
        plan = load_deployment_plan(DEFAULT_DEPLOY_TARGETS_PATH)
        targets = select_deploy_targets(plan, local_only=args.local_only)
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
