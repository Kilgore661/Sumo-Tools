"""Command-line interface for building and deploying the public site."""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import build_site
from .deploy import HOST, LOCAL_ROOT, REMOTE_ROOT, deploy_local, deploy_remote
from .site_definition import BUILD_CONFIG, SITE


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
        "--local-only",
        action="store_true",
        help="Build and deploy locally, but do not upload remotely.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    build_site(SITE, BUILD_CONFIG)
    print(f"built {BUILD_CONFIG.output_root}")
    if args.build_only:
        return
    local_root = args.local_root.resolve()
    deploy_local(BUILD_CONFIG.output_root, local_root)
    print(f"locally deployed {local_root}")
    if args.local_only:
        return
    count = deploy_remote(local_root, args.remote_root)
    print(f"remotely deployed {count} files to {HOST}:{args.remote_root}")
    print(f"https://www.661.org.uk{args.remote_root.removeprefix('/var/www/html')}/")
