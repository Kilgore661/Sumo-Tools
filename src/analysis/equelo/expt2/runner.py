from __future__ import annotations

import argparse
import datetime
import json
import shlex
import sys
from pathlib import Path
from typing import Any

from src.infra.config import EPOCH
from ....infra.connect import connect
from ..config_main import CONSTANT_K, OUTPUT_ROOT
from ..expt1.Oracle import make_oracle
from ..expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from ..expt1.simulate import SimulationMode
from .diagnostics import IterationDiagnosticsWriter, default_probe_set
from .solve import solve_variant_combined, solve_variant_modern, solve_variant_naive
from .types import SolveResult

VALID_K_POLICIES = ("constant", "divisional")
VALID_VARIANTS = ("naive", "modern", "combined")
VALID_COLLAPSE_MODES = ("annotation-only", "chii-bucket")
RUNS_ROOT = OUTPUT_ROOT / "runs"


class Tee:
    def __init__(self, *streams) -> None:
        self.streams = streams

    def write(self, data: str) -> int:
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def build_single_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Experiment 2: fixed-point estimation of basho-start initial ratings"
    )
    _add_common_args(parser, include_variant=True)
    return parser


def build_run_all_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run naive and combined variants into a single timestamped output folder"
    )
    _add_common_args(parser, include_variant=False)
    return parser


def _add_common_args(parser: argparse.ArgumentParser, include_variant: bool) -> None:
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--epsilon", type=float, default=1)
    parser.add_argument("--max-iter", type=int, default=10000000)
    if include_variant:
        parser.add_argument("--variant", choices=VALID_VARIANTS, default="naive")
    parser.add_argument("--open", action="store_true", help="Use open active-universe semantics")
    parser.add_argument("--modern-start-year", type=int, default=1989)
    parser.add_argument("--modern-end-year", type=int, default=2026)
    parser.add_argument("--k-policy", choices=VALID_K_POLICIES, default="constant")
    parser.add_argument(
        "--k-value",
        type=float,
        default=None,
        help="Constant K value. Valid only with --k-policy constant.",
    )
    parser.add_argument(
        "--k-config",
        type=Path,
        default=None,
        help="Path to divisional K JSON config. Valid only with --k-policy divisional.",
    )
    parser.add_argument(
        "--collapse",
        "--collapse-mode",
        dest="collapse_mode_cli",
        choices=VALID_COLLAPSE_MODES,
        default="annotation-only",
        help="Select how chii values are canonicalised before simulation.",
    )


def validate_k_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.k_policy == "constant":
        if args.k_config is not None:
            parser.error("--k-config may only be used with --k-policy divisional")
        if args.k_value is None:
            args.k_value = CONSTANT_K
        return

    if args.k_policy == "divisional":
        if args.k_value is not None:
            parser.error("--k-value may only be used with --k-policy constant")
        if args.k_config is None:
            args.k_config = DEFAULT_K_CONFIG_PATH
        return

    parser.error(f"Unsupported --k-policy: {args.k_policy}")


def mode_from_args(args: argparse.Namespace) -> SimulationMode:
    return SimulationMode.OPEN if args.open else SimulationMode.CLOSED


def oracle_collapse_mode_from_args(args: argparse.Namespace) -> str:
    mapping = {
        "annotation-only": "annotation_only",
        "chii-bucket": "chii_bucket",
    }
    return mapping[args.collapse_mode_cli]


def create_run_dir(now: datetime.datetime) -> Path:
    run_dir = RUNS_ROOT / now.strftime("%Y-%m-%d_%H-%M-%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def stage_output_paths(run_dir: Path, stage: str) -> dict[str, Path]:
    final_csv = run_dir / f"{stage}_final.csv"
    return {
        "final_csv": final_csv,
        "stats_csv": final_csv.with_name(f"{stage}_final_with_stats.csv"),
        "diagnostics_csv": run_dir / f"{stage}_iterations.csv",
    }


def stdout_path(run_dir: Path) -> Path:
    return run_dir / "stdout.txt"


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _resolved_params_dict(
    args: argparse.Namespace,
    mode: SimulationMode,
    *,
    variants: list[str],
) -> dict[str, object]:
    return {
        "start": args.start,
        "end": args.end,
        "zip": bool(args.zip),
        "epsilon": args.epsilon,
        "max_iter": args.max_iter,
        "variants": variants,
        "mode": mode.value,
        "modern_start_year": args.modern_start_year,
        "modern_end_year": args.modern_end_year,
        "k_policy": args.k_policy,
        "k_value": args.k_value,
        "k_config": None if args.k_config is None else str(args.k_config),
        "collapse_mode": args.collapse_mode_cli,
    }


def _expanded_command(module_name: str, params: dict[str, object]) -> str:
    command = ["python", "-m", module_name]
    command.extend(["--start", str(params["start"])])
    command.extend(["--end", str(params["end"])])
    if params["zip"]:
        command.append("--zip")
    command.extend(["--epsilon", f"{params['epsilon']:g}"])
    command.extend(["--max-iter", str(params["max_iter"])])
    variants = list(params["variants"])
    if module_name.endswith(".run_all"):
        pass
    elif len(variants) == 1:
        command.extend(["--variant", variants[0]])
    else:
        raise ValueError(f"Single-run command expected exactly one variant, got {variants}")
    if params["mode"] == SimulationMode.OPEN.value:
        command.append("--open")
    command.extend(["--modern-start-year", str(params["modern_start_year"])])
    command.extend(["--modern-end-year", str(params["modern_end_year"])])
    command.extend(["--k-policy", str(params["k_policy"])])
    if params["k_policy"] == "constant":
        command.extend(["--k-value", f"{params['k_value']:g}"])
    else:
        command.extend(["--k-config", str(params["k_config"])])
    command.extend(["--collapse", str(params["collapse_mode"])])
    return shlex.join(command)


def _load_history_and_params(args: argparse.Namespace):
    raw_history = connect(args.start, args.end, use_zip=args.zip)
    oracle = make_oracle(
        raw_history,
        collapse_mode=oracle_collapse_mode_from_args(args),
    )
    params = build_elo_params(
        k_policy=args.k_policy,
        k_value=args.k_value,
        config_path=args.k_config,
    )
    return oracle.history, params


def _build_stage_metadata(args: argparse.Namespace, mode: SimulationMode, *, variant: str) -> dict[str, str]:
    metadata = {
        "variant": variant,
        "mode": mode.value,
        "k_policy": args.k_policy,
        "collapse_mode": args.collapse_mode_cli,
    }
    if args.k_policy == "constant":
        metadata["k_value"] = f"{args.k_value:g}"
    else:
        metadata["k_config"] = str(args.k_config)
    return metadata


def _run_one_variant(
    *,
    variant: str,
    history,
    params,
    args: argparse.Namespace,
    mode: SimulationMode,
    run_dir: Path,
) -> SolveResult:
    probes = default_probe_set()
    stage_paths = {stage: stage_output_paths(run_dir, stage) for stage in VALID_VARIANTS}

    if variant == "naive":
        naive_diagnostics = IterationDiagnosticsWriter(
            probes=probes,
            stem="naive_iterations",
            metadata=_build_stage_metadata(args, mode, variant="naive"),
            output_root=run_dir,
        )
        return solve_variant_naive(
            history=history,
            params=params,
            epsilon=args.epsilon,
            max_iter=args.max_iter,
            mode=mode,
            probes=probes,
            output_csv_path=stage_paths["naive"]["final_csv"],
            diagnostics=naive_diagnostics,
        )

    if variant == "modern":
        modern_diagnostics = IterationDiagnosticsWriter(
            probes=probes,
            stem="modern_iterations",
            metadata=_build_stage_metadata(args, mode, variant="modern"),
            output_root=run_dir,
        )
        return solve_variant_modern(
            history=history,
            params=params,
            epsilon=args.epsilon,
            max_iter=args.max_iter,
            modern_start_year=args.modern_start_year,
            modern_end_year=args.modern_end_year,
            mode=mode,
            probes=probes,
            output_csv_path=stage_paths["modern"]["final_csv"],
            diagnostics=modern_diagnostics,
        )

    combined_diagnostics = IterationDiagnosticsWriter(
        probes=probes,
        stem="combined_iterations",
        metadata=_build_stage_metadata(args, mode, variant="combined"),
        output_root=run_dir,
    )
    modern_diagnostics = IterationDiagnosticsWriter(
        probes=probes,
        stem="modern_iterations",
        metadata=_build_stage_metadata(args, mode, variant="modern"),
        output_root=run_dir,
    )
    return solve_variant_combined(
        history=history,
        params=params,
        epsilon=args.epsilon,
        max_iter=args.max_iter,
        modern_start_year=args.modern_start_year,
        modern_end_year=args.modern_end_year,
        mode=mode,
        probes=probes,
        output_csv_path=stage_paths["combined"]["final_csv"],
        diagnostics=combined_diagnostics,
        modern_output_csv_path=stage_paths["modern"]["final_csv"],
        modern_diagnostics=modern_diagnostics,
    )


def _print_single_variant_summary(variant: str, result: SolveResult, args: argparse.Namespace) -> None:
    print(f"K policy: {args.k_policy}")
    print(f"Collapse mode: {oracle_collapse_mode_from_args(args)}")
    if args.k_policy == "constant":
        print(f"K value: {args.k_value:g}")
    else:
        print(f"K config: {args.k_config}")
    print(f"Converged: {result.converged}")
    print(f"Iterations: {result.iterations}")
    print(f"Final delta: {result.final_delta:.6f}")

    if variant == "naive":
        print(f"Naive diagnostics log: {result.diagnostics_path}")
        print(f"Naive CSV: {result.output_csv_path}")
        print(f"Naive stats CSV: {result.stats_csv_path}")
    elif variant == "modern":
        print(f"Modern diagnostics log: {result.diagnostics_path}")
        print(f"Modern CSV: {result.output_csv_path}")
        print(f"Modern stats CSV: {result.stats_csv_path}")
    else:
        print(f"Combined diagnostics log: {result.diagnostics_path}")
        print(f"Combined CSV: {result.output_csv_path}")
        print(f"Combined stats CSV: {result.stats_csv_path}")
        print(f"Modern diagnostics log: {result.modern_diagnostics_path}")
        print(f"Modern CSV: {result.modern_output_csv_path}")
        print(f"Modern stats CSV: {result.modern_stats_csv_path}")


def _outputs_for_single_variant(variant: str, result: SolveResult) -> dict[str, object]:
    outputs: dict[str, object] = {"stdout_txt": None}
    if variant == "naive":
        outputs["naive"] = {
            "final_csv": None if result.output_csv_path is None else str(result.output_csv_path),
            "stats_csv": None if result.stats_csv_path is None else str(result.stats_csv_path),
            "diagnostics_csv": None if result.diagnostics_path is None else str(result.diagnostics_path),
        }
    elif variant == "modern":
        outputs["modern"] = {
            "final_csv": None if result.output_csv_path is None else str(result.output_csv_path),
            "stats_csv": None if result.stats_csv_path is None else str(result.stats_csv_path),
            "diagnostics_csv": None if result.diagnostics_path is None else str(result.diagnostics_path),
        }
    else:
        outputs["combined"] = {
            "final_csv": None if result.output_csv_path is None else str(result.output_csv_path),
            "stats_csv": None if result.stats_csv_path is None else str(result.stats_csv_path),
            "diagnostics_csv": None if result.diagnostics_path is None else str(result.diagnostics_path),
        }
        outputs["modern"] = {
            "final_csv": None if result.modern_output_csv_path is None else str(result.modern_output_csv_path),
            "stats_csv": None if result.modern_stats_csv_path is None else str(result.modern_stats_csv_path),
            "diagnostics_csv": None if result.modern_diagnostics_path is None else str(result.modern_diagnostics_path),
        }
    return outputs


def execute_single_run(args: argparse.Namespace, typed_argv: list[str], *, module_name: str) -> Path:
    mode = mode_from_args(args)
    now = datetime.datetime.now().astimezone()
    run_dir = create_run_dir(now)
    resolved_params = _resolved_params_dict(args, mode, variants=[args.variant])

    manifest = {
        "command": {
            "typed": shlex.join(["python", "-m", module_name, *typed_argv]),
            "expanded": _expanded_command(module_name, resolved_params),
        },
        "outputs": {"stdout_txt": str(stdout_path(run_dir))},
        "params": resolved_params,
        "result": None,
        "run": {
            "run_dir": str(run_dir),
            "started_at": now.isoformat(),
            "variants": [args.variant],
        },
    }
    write_manifest(manifest_path(run_dir), manifest)

    with open(stdout_path(run_dir), "w", encoding="utf-8") as stdout_file:
        tee = Tee(sys.stdout, stdout_file)
        original_stdout = sys.stdout
        try:
            sys.stdout = tee
            print(f"Run directory: {run_dir}")
            history, params = _load_history_and_params(args)
            result = _run_one_variant(
                variant=args.variant,
                history=history,
                params=params,
                args=args,
                mode=mode,
                run_dir=run_dir,
            )
            _print_single_variant_summary(args.variant, result, args)
        finally:
            sys.stdout = original_stdout

    outputs = _outputs_for_single_variant(args.variant, result)
    outputs["stdout_txt"] = str(stdout_path(run_dir))
    final_manifest = {
        "command": {
            "typed": shlex.join(["python", "-m", module_name, *typed_argv]),
            "expanded": _expanded_command(module_name, resolved_params),
        },
        "outputs": outputs,
        "params": resolved_params,
        "result": {
            args.variant: {
                "converged": result.converged,
                "iterations": result.iterations,
                "final_delta": result.final_delta,
            }
        },
        "run": {
            "run_dir": str(run_dir),
            "started_at": now.isoformat(),
            "variants": [args.variant],
        },
    }
    write_manifest(manifest_path(run_dir), final_manifest)
    return run_dir


def execute_run_all(args: argparse.Namespace, typed_argv: list[str], *, module_name: str) -> Path:
    mode = mode_from_args(args)
    now = datetime.datetime.now().astimezone()
    run_dir = create_run_dir(now)
    variants = ["naive", "combined"]
    resolved_params = _resolved_params_dict(args, mode, variants=variants)

    manifest = {
        "command": {
            "typed": shlex.join(["python", "-m", module_name, *typed_argv]),
            "expanded": _expanded_command(module_name, resolved_params),
        },
        "outputs": {"stdout_txt": str(stdout_path(run_dir))},
        "params": resolved_params,
        "result": None,
        "run": {
            "run_dir": str(run_dir),
            "started_at": now.isoformat(),
            "variants": variants,
        },
    }
    write_manifest(manifest_path(run_dir), manifest)

    with open(stdout_path(run_dir), "w", encoding="utf-8") as stdout_file:
        tee = Tee(sys.stdout, stdout_file)
        original_stdout = sys.stdout
        try:
            sys.stdout = tee
            print(f"Run directory: {run_dir}")
            print("[run_all] loading data once...")
            history, params = _load_history_and_params(args)

            print("[run_all] starting naive run")
            naive_result = _run_one_variant(
                variant="naive",
                history=history,
                params=params,
                args=args,
                mode=mode,
                run_dir=run_dir,
            )

            print("[run_all] starting combined run")
            combined_result = _run_one_variant(
                variant="combined",
                history=history,
                params=params,
                args=args,
                mode=mode,
                run_dir=run_dir,
            )

            print("\n=== run_all summary ===")
            print("\n[naive]")
            print(f"  converged: {naive_result.converged}")
            print(f"  iterations: {naive_result.iterations}")
            print(f"  final_delta: {naive_result.final_delta:.6f}")
            print(f"  output: {naive_result.output_csv_path}")

            print("\n[combined]")
            print(f"  converged: {combined_result.converged}")
            print(f"  iterations: {combined_result.iterations}")
            print(f"  final_delta: {combined_result.final_delta:.6f}")
            print(f"  output: {combined_result.output_csv_path}")
            print(f"  modern_output: {combined_result.modern_output_csv_path}")
        finally:
            sys.stdout = original_stdout

    outputs = {
        "stdout_txt": str(stdout_path(run_dir)),
        "naive": {
            "final_csv": None if naive_result.output_csv_path is None else str(naive_result.output_csv_path),
            "stats_csv": None if naive_result.stats_csv_path is None else str(naive_result.stats_csv_path),
            "diagnostics_csv": None if naive_result.diagnostics_path is None else str(naive_result.diagnostics_path),
        },
        "modern": {
            "final_csv": None if combined_result.modern_output_csv_path is None else str(combined_result.modern_output_csv_path),
            "stats_csv": None if combined_result.modern_stats_csv_path is None else str(combined_result.modern_stats_csv_path),
            "diagnostics_csv": None if combined_result.modern_diagnostics_path is None else str(combined_result.modern_diagnostics_path),
        },
        "combined": {
            "final_csv": None if combined_result.output_csv_path is None else str(combined_result.output_csv_path),
            "stats_csv": None if combined_result.stats_csv_path is None else str(combined_result.stats_csv_path),
            "diagnostics_csv": None if combined_result.diagnostics_path is None else str(combined_result.diagnostics_path),
        },
    }
    final_manifest = {
        "command": {
            "typed": shlex.join(["python", "-m", module_name, *typed_argv]),
            "expanded": _expanded_command(module_name, resolved_params),
        },
        "outputs": outputs,
        "params": resolved_params,
        "result": {
            "naive": {
                "converged": naive_result.converged,
                "iterations": naive_result.iterations,
                "final_delta": naive_result.final_delta,
            },
            "combined": {
                "converged": combined_result.converged,
                "iterations": combined_result.iterations,
                "final_delta": combined_result.final_delta,
            },
        },
        "run": {
            "run_dir": str(run_dir),
            "started_at": now.isoformat(),
            "variants": variants,
        },
    }
    write_manifest(manifest_path(run_dir), final_manifest)
    return run_dir
