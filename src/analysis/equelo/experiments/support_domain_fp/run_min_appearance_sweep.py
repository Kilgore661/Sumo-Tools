"""Run a min-appearances support-domain sweep and compare the outputs."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from src.analysis.equelo.fixed_v2.model import FP_SOURCE
from src.sumo_core.Chii import Chii

from .compare_runs import (
    load_completed_run,
    print_comparison_report,
    write_comparison_report,
)
from .run import (
    DEFAULT_MAX_CHII,
    DEFAULT_THRESHOLD,
    OUTPUT_ROOT,
    run_experiment,
)


DEFAULT_CASES = (100, 80, 60, 50, 40, 30)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run min-appearances support-domain fixed-point cases in reverse "
            "order and compile a comparison report."
        )
    )
    parser.add_argument(
        "--cases",
        nargs="+",
        type=int,
        default=list(DEFAULT_CASES),
        help="Min-appearance thresholds to run. They are sorted descending before execution.",
    )
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--max-iter", type=int, default=10000000)
    parser.add_argument("--modern-start-year", type=int, default=1989)
    parser.add_argument("--modern-end-year", type=int, default=2026)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--fp-source", type=Path, default=FP_SOURCE)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument(
        "--baseline",
        default="min_app_50",
        help="Run label used for landmark delta columns in the comparison report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = sorted(set(args.cases), reverse=True)
    batch_root = args.output_root / "min_appearance_sweeps" / datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )
    batch_root.mkdir(parents=True, exist_ok=False)

    print(f"[min-appearance-sweep] cases={cases}")
    print(f"[min-appearance-sweep] batch_root={batch_root}")

    run_dirs: list[Path] = []
    run_timings: list[dict[str, str]] = []
    sweep_started = time.perf_counter()
    for min_appearances in cases:
        print(f"[min-appearance-sweep] running min_appearances={min_appearances}")
        case_started = time.perf_counter()
        outputs = run_experiment(
            threshold=DEFAULT_THRESHOLD,
            domain="min-appearances",
            max_chii=Chii.from_str(DEFAULT_MAX_CHII),
            min_appearances=min_appearances,
            epsilon=args.epsilon,
            max_iter=args.max_iter,
            modern_start_year=args.modern_start_year,
            modern_end_year=args.modern_end_year,
            output_root=batch_root,
            fp_source=args.fp_source,
        )
        elapsed_seconds = time.perf_counter() - case_started
        annotate_manifest(outputs.manifest_json, elapsed_seconds=elapsed_seconds)
        run_dirs.append(outputs.run_dir)
        run_timings.append(
            {
                "min_appearances": str(min_appearances),
                "run_dir": str(outputs.run_dir),
                "elapsed_seconds": f"{elapsed_seconds:.3f}",
            }
        )
        print(
            f"[min-appearance-sweep] completed min_appearances={min_appearances}: "
            f"{outputs.run_dir} ({elapsed_seconds:.1f}s)"
        )

    total_elapsed_seconds = time.perf_counter() - sweep_started
    write_sweep_manifest(
        batch_root / "sweep_manifest.json",
        cases=cases,
        run_timings=run_timings,
        total_elapsed_seconds=total_elapsed_seconds,
    )
    runs = [run for run_dir in run_dirs if (run := load_completed_run(run_dir)) is not None]
    comparison_root = write_comparison_report(
        runs,
        output_root=batch_root / "comparison",
        baseline_label=args.baseline,
        top_n=args.top_n,
        metadata={
            "total_elapsed_seconds": f"{total_elapsed_seconds:.3f}",
            "case_count": str(len(cases)),
        },
    )
    print("[min-appearance-sweep] comparison complete")
    print(f"[min-appearance-sweep] total elapsed: {total_elapsed_seconds:.1f}s")
    print_comparison_report(comparison_root)


def annotate_manifest(path: Path, *, elapsed_seconds: float) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["elapsed_seconds"] = elapsed_seconds
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_sweep_manifest(
    path: Path,
    *,
    cases: list[int],
    run_timings: list[dict[str, str]],
    total_elapsed_seconds: float,
) -> None:
    payload = {
        "cases": cases,
        "total_elapsed_seconds": total_elapsed_seconds,
        "runs": run_timings,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
