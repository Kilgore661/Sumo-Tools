"""Command entry point for make_site2 builds and deployment."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import DEFAULT_OUTPUT_ROOT, build_site
from .deploy import (
    HOST,
    LOCAL_ROOT,
    REMOTE_ROOT,
    DeploymentConfig,
    build_output_from_existing,
    deploy_local,
    deploy_remote,
    preflight_remote_auth,
)


SHORT_HISTORY_ZIP = Path("files/output/Historys/1978_01 to 1980_11.zip")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument(
        "--short",
        action="store_true",
        help=(
            "Use the standard short History zip for a faster development build "
            f"({SHORT_HISTORY_ZIP})."
        ),
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
        help="Server directory to receive the deployable make_site2 site.",
    )
    parser.add_argument(
        "--remote-root",
        default=REMOTE_ROOT,
        help="Remote server web root to receive the deployable make_site2 site.",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build the persisted output tree without deployment.",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Deploy the existing output tree without rebuilding it.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Build/deploy to the server, but do not deploy to the remote server.",
    )
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


def resolve_history_zip(args: argparse.Namespace) -> Path | None:
    if args.short and args.history_zip is not None:
        raise SystemExit("--short and --history-zip cannot be used together")
    if args.short:
        return SHORT_HISTORY_ZIP
    return args.history_zip


def reject_conflicting_modes(args: argparse.Namespace) -> None:
    if args.no_build and args.build_only:
        raise SystemExit("--no-build and --build-only cannot be used together")
    if args.no_build and args.history_zip is not None:
        raise SystemExit("--history-zip does not apply with --no-build")
    if args.no_build and args.short:
        raise SystemExit("--short does not apply with --no-build")
    if args.short and args.history_zip is not None:
        raise SystemExit("--short and --history-zip cannot be used together")
    if args.no_build and args.prod:
        raise SystemExit("--prod does not apply with --no-build")
    if args.no_build and args.no_basho:
        raise SystemExit("--no-basho does not apply with --no-build")
    if args.no_build and args.one_basho:
        raise SystemExit("--one-basho does not apply with --no-build")
    if args.no_build and args.brb_payload_mode != "all":
        raise SystemExit("--brb-payload-mode does not apply with --no-build")


def main() -> None:
    args = build_parser().parse_args()
    reject_conflicting_modes(args)
    deployment_config = DeploymentConfig(
        local_root=args.local_root.resolve(),
        remote_root=args.remote_root,
    )
    if not args.build_only and not args.local_only:
        deployment_config = preflight_remote_auth(deployment_config)
    if args.no_build:
        build_output = build_output_from_existing(args.output)
        print(f"using existing build {build_output.root}")
    else:
        kwargs = {
            "output_root": args.output,
            "basho_results_payload_mode": resolve_basho_results_payload_mode(args),
            "cache_mode": resolve_cache_mode(args),
        }
        history_zip = resolve_history_zip(args)
        if history_zip is not None:
            kwargs["history_zip"] = history_zip
        build_output = build_site(**kwargs)
        print(f"built {build_output.root}")
    if args.build_only:
        return
    local_result = deploy_local(build_output, deployment_config)
    print(
        f"deployed {local_result.file_count} files to server "
        f"{local_result.target_root}"
    )
    print(local_result.public_url)
    if args.local_only:
        return
    remote_result = deploy_remote(build_output, deployment_config)
    print(
        f"deployed {remote_result.file_count} files to remote server "
        f"{HOST}:{remote_result.target_root}"
    )
    print(remote_result.public_url)


if __name__ == "__main__":
    main()
