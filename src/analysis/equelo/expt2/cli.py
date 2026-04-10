from pdb import set_trace

import argparse
import datetime
import json
import shlex
import sys
from pathlib import Path

from src.infra.config import EPOCH
from ....infra.connect import connect
from ....sumo_core.BasicPrimitives import RikId

from ..config_main import BIOS_PATH, CONSTANT_K, OUTPUT_ROOT
from ..expt1.Oracle import make_oracle
from ..expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from ..expt1.simulate import SimulationMode
from .diagnostics import IterationDiagnosticsWriter, default_probe_set
from .solve import solve_variant_combined, solve_variant_modern, solve_variant_naive


VALID_K_POLICIES = ("constant", "divisional")
VALID_VARIANTS = ("naive", "modern", "combined")
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



def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Experiment 2: fixed-point estimation of basho-start initial ratings"
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--epsilon", type=float, default=1)
    parser.add_argument("--max-iter", type=int, default=10000000)
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
    return parser



def _validate_k_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
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



def _mode_from_args(args: argparse.Namespace) -> SimulationMode:
    return SimulationMode.OPEN if args.open else SimulationMode.CLOSED



def _create_run_dir(now: datetime.datetime) -> Path:
    run_dir = RUNS_ROOT / now.strftime("%Y-%m-%d_%H-%M-%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir



def _stringify_arg(value):
    if isinstance(value, Path):
        return str(value)
    return value



def _resolved_params_dict(args: argparse.Namespace, mode: SimulationMode) -> dict[str, object]:
    params = {
        "start": args.start,
        "end": args.end,
        "zip": bool(args.zip),
        "epsilon": args.epsilon,
        "max_iter": args.max_iter,
        "variant": args.variant,
        "mode": mode.value,
        "modern_start_year": args.modern_start_year,
        "modern_end_year": args.modern_end_year,
        "k_policy": args.k_policy,
        "k_value": args.k_value,
        "k_config": None if args.k_config is None else str(args.k_config),
    }
    return params



def _expanded_command(params: dict[str, object]) -> str:
    command = ["python", "-m", "src.analysis.equelo.expt2"]
    command.extend(["--start", str(params["start"])])
    command.extend(["--end", str(params["end"])])
    if params["zip"]:
        command.append("--zip")
    command.extend(["--epsilon", f"{params['epsilon']:g}"])
    command.extend(["--max-iter", str(params["max_iter"])])
    command.extend(["--variant", str(params["variant"])])
    if params["mode"] == SimulationMode.OPEN.value:
        command.append("--open")
    command.extend(["--modern-start-year", str(params["modern_start_year"])])
    command.extend(["--modern-end-year", str(params["modern_end_year"])])
    command.extend(["--k-policy", str(params["k_policy"])])
    if params["k_policy"] == "constant":
        command.extend(["--k-value", f"{params['k_value']:g}"])
    else:
        command.extend(["--k-config", str(params["k_config"])])
    return shlex.join(command)



def _manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"



def _stdout_path(run_dir: Path) -> Path:
    return run_dir / "stdout.txt"



def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")



def main() -> None:
    parser = _build_parser()
    typed_argv = sys.argv[1:]
    args = parser.parse_args()
    _validate_k_args(parser, args)
    mode = _mode_from_args(args)
    resolved_params = _resolved_params_dict(args, mode)

    now = datetime.datetime.now().astimezone()
    run_dir = _create_run_dir(now)
    stdout_path = _stdout_path(run_dir)
    manifest_path = _manifest_path(run_dir)

    metadata = {
        "variant": args.variant,
        "mode": mode.value,
        "k_policy": args.k_policy,
    }
    if args.k_policy == "constant":
        metadata["k_value"] = f"{args.k_value:g}"
    else:
        metadata["k_config"] = str(args.k_config)

    primary_output_csv_path = run_dir / "primary_final.csv"
    modern_output_csv_path = run_dir / "modern_final.csv"
    primary_diagnostics = IterationDiagnosticsWriter(
        probes=default_probe_set(),
        stem="primary_iterations",
        metadata=metadata,
        output_root=run_dir,
    )
    modern_diagnostics = IterationDiagnosticsWriter(
        probes=default_probe_set(),
        stem="modern_iterations",
        metadata={**metadata, "variant": "modern"},
        output_root=run_dir,
    )

    initial_manifest = {
        "command": {
            "typed": shlex.join(["python", "-m", "src.analysis.equelo.expt2", *typed_argv]),
            "expanded": _expanded_command(resolved_params),
        },
        "outputs": {
            "primary_final_csv": str(primary_output_csv_path),
            "primary_stats_csv": str(primary_output_csv_path.with_name("primary_final_with_stats.csv")),
            "primary_diagnostics_csv": str(run_dir / "primary_iterations.csv"),
            "modern_final_csv": str(modern_output_csv_path),
            "modern_stats_csv": str(modern_output_csv_path.with_name("modern_final_with_stats.csv")),
            "modern_diagnostics_csv": str(run_dir / "modern_iterations.csv"),
        },
        "params": resolved_params,
        "result": None,
        "run": {
            "run_dir": str(run_dir),
            "started_at": now.isoformat(),
            "variant": args.variant,
        },
    }
    _write_manifest(manifest_path, initial_manifest)

    with open(stdout_path, "w", encoding="utf-8") as stdout_file:
        tee = Tee(sys.stdout, stdout_file)
        original_stdout = sys.stdout
        try:
            sys.stdout = tee
            print(f"Run directory: {run_dir}")

            raw_history = connect(args.start, args.end, use_zip=args.zip)
            with open(BIOS_PATH, "r", encoding="utf-8") as f:
                raw_bios = json.load(f)
            bios = {RikId(int(k)): v for k, v in raw_bios.items()}

            oracle = make_oracle(raw_history, bios)
            params = build_elo_params(
                k_policy=args.k_policy,
                k_value=args.k_value,
                config_path=args.k_config,
            )
            probes = default_probe_set()
            primary_diagnostics.probes = list(probes)
            modern_diagnostics.probes = list(probes)

            if args.variant == "naive":
                result = solve_variant_naive(
                    history=oracle.history,
                    params=params,
                    epsilon=args.epsilon,
                    max_iter=args.max_iter,
                    mode=mode,
                    probes=probes,
                    output_csv_path=primary_output_csv_path,
                    diagnostics=primary_diagnostics,
                )
            elif args.variant == "modern":
                result = solve_variant_modern(
                    history=oracle.history,
                    params=params,
                    epsilon=args.epsilon,
                    max_iter=args.max_iter,
                    modern_start_year=args.modern_start_year,
                    modern_end_year=args.modern_end_year,
                    mode=mode,
                    probes=probes,
                    output_csv_path=primary_output_csv_path,
                    diagnostics=primary_diagnostics,
                )
            else:
                result = solve_variant_combined(
                    history=oracle.history,
                    params=params,
                    epsilon=args.epsilon,
                    max_iter=args.max_iter,
                    modern_start_year=args.modern_start_year,
                    modern_end_year=args.modern_end_year,
                    mode=mode,
                    probes=probes,
                    output_csv_path=primary_output_csv_path,
                    diagnostics=primary_diagnostics,
                    modern_output_csv_path=modern_output_csv_path,
                    modern_diagnostics=modern_diagnostics,
                )

            print(f"K policy: {args.k_policy}")
            if args.k_policy == "constant":
                print(f"K value: {args.k_value:g}")
            else:
                print(f"K config: {args.k_config}")
            print(f"Converged: {result.converged}")
            print(f"Iterations: {result.iterations}")
            print(f"Final delta: {result.final_delta:.6f}")
            print(f"Primary diagnostics log: {result.diagnostics_path}")
            print(f"Primary CSV: {result.output_csv_path}")
            print(f"Primary stats CSV: {result.stats_csv_path}")
            print(f"Modern diagnostics log: {result.modern_diagnostics_path}")
            print(f"Modern CSV: {result.modern_output_csv_path}")
            print(f"Modern stats CSV: {result.modern_stats_csv_path}")
        finally:
            sys.stdout = original_stdout

    final_manifest = {
        "command": {
            "typed": shlex.join(["python", "-m", "src.analysis.equelo.expt2", *typed_argv]),
            "expanded": _expanded_command(resolved_params),
        },
        "outputs": {
            "primary_final_csv": None if result.output_csv_path is None else str(result.output_csv_path),
            "primary_stats_csv": None if result.stats_csv_path is None else str(result.stats_csv_path),
            "primary_diagnostics_csv": None if result.diagnostics_path is None else str(result.diagnostics_path),
            "modern_final_csv": None if result.modern_output_csv_path is None else str(result.modern_output_csv_path),
            "modern_stats_csv": None if result.modern_stats_csv_path is None else str(result.modern_stats_csv_path),
            "modern_diagnostics_csv": None if result.modern_diagnostics_path is None else str(result.modern_diagnostics_path),
            "stdout_txt": str(stdout_path),
        },
        "params": resolved_params,
        "result": {
            "converged": result.converged,
            "iterations": result.iterations,
            "final_delta": result.final_delta,
        },
        "run": {
            "run_dir": str(run_dir),
            "started_at": now.isoformat(),
            "variant": args.variant,
        },
    }
    _write_manifest(manifest_path, final_manifest)
