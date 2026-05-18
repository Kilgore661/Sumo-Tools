"""CLI for the make_site2 public-site builder."""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import DEFAULT_OUTPUT_ROOT, build_brb_shell
from .deploy import HOST, LOCAL_ROOT, REMOTE_ROOT, deploy_local, deploy_remote


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and deploy the make_site2 static prototype."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output directory for the generated make_site2 site.",
    )
    parser.add_argument(
        "--local-root",
        type=Path,
        default=LOCAL_ROOT,
        help="Local web directory to receive the deployable make_site2 site.",
    )
    parser.add_argument(
        "--remote-root",
        default=REMOTE_ROOT,
        help="Remote web root to receive the deployable make_site2 site.",
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
    parser.add_argument(
        "--no-banzuke",
        action="store_true",
        help="Do not include Basho Results Browser per-basho payload data.",
    )
    parser.add_argument(
        "--one-banzuke",
        "--one-basho",
        dest="one_banzuke",
        action="store_true",
        help="Include only the latest Basho Results Browser per-basho payload data.",
    )
    args = parser.parse_args()
    if args.no_banzuke and args.one_banzuke:
        raise SystemExit("--no-banzuke and --one-banzuke cannot be used together")
    basho_results_payload_mode = "latest" if args.one_banzuke else "all"
    if args.no_banzuke:
        basho_results_payload_mode = "none"
    build_brb_shell(
        args.output,
        basho_results_payload_mode=basho_results_payload_mode,
    )
    print(f"built {args.output}")
    if args.build_only:
        return
    local_root = args.local_root.resolve()
    deploy_local(args.output, local_root)
    print(f"locally deployed {local_root}")
    if args.local_only:
        return
    count = deploy_remote(local_root, args.remote_root)
    print(f"remotely deployed {count} files to {HOST}:{args.remote_root}")
    print(f"https://www.661.org.uk{args.remote_root.removeprefix('/var/www/html')}/")
