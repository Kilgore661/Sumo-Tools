from __future__ import annotations

import argparse
import datetime
import json

from src.infra.config import EPOCH
from ....infra.connect import connect
from ....sumo_core.BasicPrimitives import RikId

from ..config_main import BIOS_PATH, OUTPUT_ROOT
from ..expt1.Oracle import make_oracle
from ..expt1.params import EloParams
from ..expt1.simulate import SimulationMode
from .diagnostics import IterationDiagnosticsWriter, default_probe_set
from .solve import solve_variant_a, solve_variant_b


def main() -> None:
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
    args = parser.parse_args()

    raw_history = connect(args.start, args.end, use_zip=args.zip)
    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    bios = {RikId(int(k)): v for k, v in raw_bios.items()}

    oracle = make_oracle(raw_history, bios)
    params = EloParams.constant()
    mode = SimulationMode.OPEN if args.open else SimulationMode.CLOSED
    probes = default_probe_set()

    stem = f"expt2_variant_{args.variant}_{mode.value}"
    diagnostics = IterationDiagnosticsWriter(probes=probes, stem=stem)
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
        )

    print(f"Converged: {result.converged}")
    print(f"Iterations: {result.iterations}")
    print(f"Final delta: {result.final_delta:.6f}")
    print(f"Diagnostics log: {result.diagnostics_path}")
    print(f"Final CSV: {result.output_csv_path}")
