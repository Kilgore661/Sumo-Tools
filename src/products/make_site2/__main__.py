"""Command entry point for make_site2 builds and deployment."""

from time import time
t0=time()

import argparse
from pathlib import Path
from time import perf_counter

from .build import DEFAULT_OUTPUT_ROOT, build_site
from .deploy import (
    DEFAULT_DEPLOY_TARGETS_PATH,
    build_output_from_existing,
    deploy_target,
    load_deployment_plan,
    preflight_deploy_targets,
    select_deploy_targets,
)


SHORT_HISTORY_ZIP = Path("files/output/Historys/1978_01 to 1980_11.zip")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the make_site2 static site and, unless told otherwise, "
            f"deploy it to the default targets in {DEFAULT_DEPLOY_TARGETS_PATH}."
        ),
        epilog="""Typical workflows:
  py -m src.products.make_site2
      Build the full site, deploy to the local filesystem target, then deploy
      to the configured remote SFTP target.

  py -m src.products.make_site2 --local-only
      Build the full site and deploy only to targets whose method is win_copy.
      This does not request SFTP credentials.

  py -m src.products.make_site2 --build-only
      Build files/output/make_site2 and stop. Nothing is deployed.

  py -m src.products.make_site2 --no-build
      Deploy the existing files/output/make_site2 tree without rebuilding.

  py -m src.products.make_site2 --no-build --local-only
      Copy the existing build to the local filesystem target only.

  py -m src.products.make_site2 --short --local-only
      Build from the standard short History zip and deploy locally. Useful for
      a quick smoke test; the site will show only the short-history range.

Deployment targets:
  The command line chooses the mode. The configured JSON chooses the sites.
  Edit distro/make_site2_targets.json to change destinations, transfer methods,
  URLs, hosts, users, or password environment variables.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--history-zip",
        type=Path,
        help=(
            "Build from an explicit History zip instead of the default live "
            "store/history source."
        ),
    )
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
        help=(
            "Output directory for the generated site. Default: "
            f"{DEFAULT_OUTPUT_ROOT}."
        ),
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help=(
            "Build the persisted output tree and stop. Use this when checking "
            "build output before touching any served target."
        ),
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help=(
            "Deploy the existing output tree without rebuilding it. This is "
            "the shortcut after a prior --build-only run."
        ),
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help=(
            "Deploy only targets whose configured method is win_copy. With the "
            "current config this means the local Apache filesystem target and "
            "no SFTP password prompt."
        ),
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help=(
            "Build without development cache-busting query parameters. Leave "
            "unset for ordinary local development/review builds."
        ),
    )
    parser.add_argument(
        "--no-basho",
        action="store_true",
        help=(
            "Do not include Basho Results Browser per-basho payload data. "
            "Useful only when deliberately shrinking or debugging the BRB "
            "payload surface."
        ),
    )
    parser.add_argument(
        "--one-basho",
        action="store_true",
        help=(
            "Include only the latest Basho Results Browser payload data. "
            "Useful for a faster build while keeping one BRB page usable."
        ),
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
    start_time = perf_counter()
    args = build_parser().parse_args()
    reject_conflicting_modes(args)
    deploy_targets = ()
    if not args.build_only:
        plan = load_deployment_plan(DEFAULT_DEPLOY_TARGETS_PATH)
        deploy_targets = select_deploy_targets(
            plan,
            local_only=args.local_only,
        )
        deploy_targets = preflight_deploy_targets(deploy_targets)
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
        print_elapsed_time(start_time)
        return
    for target in deploy_targets:
        result = deploy_target(build_output, target)
        print(
            f"deployed {result.file_count} files to "
            f"{result.method} target {result.target_name}: {result.target_root}"
        )
        if result.public_url:
            print(result.public_url)
    print_elapsed_time(start_time)


def print_elapsed_time(start_time: float) -> None:
    elapsed = perf_counter() - start_time
    print(f"completed in {elapsed:.1f} seconds")


if __name__ == "__main__":
    main()
    print( f'Run complete in {time()-t0:.0f}s' )
