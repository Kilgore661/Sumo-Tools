from pdb import set_trace

import argparse
import datetime
import json
from pathlib import Path

from src.infra.config import EPOCH
from ....infra.connect import connect
from ....sumo_core.BasicPrimitives import RikId

from ..config_main import BIOS_PATH, CONSTANT_K, OUTPUT_ROOT
from ..expt1.Oracle import make_oracle
from ..expt1.params import DEFAULT_K_CONFIG_PATH, build_elo_params
from ..expt1.simulate import SimulationMode
from .diagnostics import IterationDiagnosticsWriter, default_probe_set
from .solve import solve_variant_a, solve_variant_b


VALID_K_POLICIES = ("constant", "divisional")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Experiment 2: fixed-point estimation of basho-start initial ratings"
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--epsilon", type=float, default=1)
    parser.add_argument("--max-iter", type=int, default=150)
    parser.add_argument("--variant", choices=["a", "b"], default="a")
    parser.add_argument("--open", action="store_true", help="Use open active-universe semantics")
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



def _policy_stem(args: argparse.Namespace) -> str:
    if args.k_policy == "constant":
        return f"constant_k{args.k_value:g}"
    config_stem = Path(args.k_config).stem
    return f"divisional_{config_stem}"



def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_k_args(parser, args)

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
    mode = _mode_from_args(args)
    probes = default_probe_set()

    policy_stem = _policy_stem(args)
    stem = f"expt2_variant_{args.variant}_{mode.value}_{policy_stem}"
    metadata = {
        "variant": args.variant,
        "mode": mode.value,
        "k_policy": args.k_policy,
    }
    if args.k_policy == "constant":
        metadata["k_value"] = f"{args.k_value:g}"
    else:
        metadata["k_config"] = str(args.k_config)

    diagnostics = IterationDiagnosticsWriter(probes=probes, stem=stem, metadata=metadata)
    output_csv_path = OUTPUT_ROOT / f"{stem}_final.csv"

    if args.variant == "a":
        result = solve_variant_a(
            history=oracle.history,
            params=params,
            epsilon=args.epsilon,
            max_iter=args.max_iter,
            mode=mode,
            probes=probes,
            output_csv_path=output_csv_path,
            diagnostics=diagnostics,
        )
    else:
        result = solve_variant_b(
            history=oracle.history,
            params=params,
            epsilon=args.epsilon,
            max_iter=args.max_iter,
            mode=mode,
            probes=probes,
            output_csv_path=output_csv_path,
            diagnostics=diagnostics,
            calibration_stem=f"{stem}_calibration",
            calibration_metadata=metadata,
        )

    print(f"K policy: {args.k_policy}")
    if args.k_policy == "constant":
        print(f"K value: {args.k_value:g}")
    else:
        print(f"K config: {args.k_config}")
    print(f"Converged: {result.converged}")
    print(f"Iterations: {result.iterations}")
    print(f"Final delta: {result.final_delta:.6f}")
    print(f"Diagnostics log: {result.diagnostics_path}")
    print(f"Final CSV: {result.output_csv_path}")
