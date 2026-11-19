"""Run minimum-cost constrained late-basho torikumi forecasting."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from src.infra.persistence.annotated_serialiser import load_history_with_annotations

from .__main__ import DEFAULT_HISTORY_ZIP, parse_date
from .constrained_analysis import analyse_constrained
from .constrained_output import write_constrained_outputs
from .heya import DEFAULT_HEYA_INDEX, load_heya_index
from .output import DEFAULT_OUTPUT_ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, default=DEFAULT_HISTORY_ZIP)
    parser.add_argument("--heya-index", type=Path, default=DEFAULT_HEYA_INDEX)
    parser.add_argument("--start", type=parse_date)
    parser.add_argument("--end", type=parse_date)
    parser.add_argument("--first-day", type=int, default=11)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    history_path = args.history_zip.resolve()
    heya_path = args.heya_index.resolve()
    if history_path.suffix.lower() != ".zip" or not history_path.is_file():
        raise FileNotFoundError(f"History zip not found: {history_path}")
    if not heya_path.is_file():
        raise FileNotFoundError(
            f"Heya index not found: {heya_path}; run the heya compiler first"
        )

    print(f"[constrained] loading History: {history_path}", flush=True)
    history = load_history_with_annotations(str(history_path.with_suffix("")))
    print(f"[constrained] loading heya index: {heya_path}", flush=True)
    heya_index = load_heya_index(heya_path)
    print("[constrained] solving selected basho...", flush=True)
    result = analyse_constrained(
        history,
        heya_index,
        start=args.start,
        end=args.end,
        first_day=args.first_day,
        progress=lambda message: print(message, flush=True),
    )
    print("[constrained] hashing sources and writing outputs...", flush=True)
    outputs = write_constrained_outputs(
        result,
        sources={"history": _source(history_path), "heya_index": _source(heya_path)},
        output_root=args.output_root,
    )
    mean_recovery = sum(row.pair_recovery_rate for row in result.cases) / len(result.cases)
    optimal = sum(row.forecast.status == "OPTIMAL" for row in result.cases)
    infeasible = sum(row.forecast.status == "INFEASIBLE" for row in result.cases)
    print(f"[constrained] optimal cases: {optimal:,}")
    print(f"[constrained] infeasible cases: {infeasible:,}")
    print(f"[constrained] excluded extra-cross-division cases: {len(result.exclusions):,}")
    print(f"[constrained] mean pair recovery: {mean_recovery:.3%}")
    print(f"[constrained] exact cards: {sum(row.exact for row in result.cases):,}")
    print(f"[constrained] output: {outputs.run_directory.resolve()}")


def _source(path: Path) -> dict[str, object]:
    return {
        "path": str(path), "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    main()
