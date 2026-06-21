#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.infra.connect import connect
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.probability.builder import load_ratings_csv
from src.analysis.probability.__main__ import _load_manifest, _evaluation_year_bounds


VALID_RATINGS_STAGES = ("naive", "modern", "combined")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build binned bout-level rating deltas from an Expt2 final ratings file."
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Timestamped Expt2 run directory",
    )
    parser.add_argument(
        "--ratings-stage",
        choices=VALID_RATINGS_STAGES,
        default="combined",
        help="Which Expt2 ratings file to use.",
    )
    parser.add_argument(
        "--n-bins",
        type=int,
        default=20,
        help="Number of equal-width bins across the observed delta range.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV path. Defaults to <run-dir>/<stage>_delta_bins.csv",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Load source history from zip, matching the existing loaders when needed.",
    )
    return parser


def _ratings_csv_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"{stage}_final.csv"


def _default_output_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"{stage}_delta_bins.csv"


def _slice_history_years(history, start_year: int, end_year: int):
    sliced = history.__class__()
    for date in sorted(history.keys()):
        if start_year <= date.year <= end_year:
            sliced[date] = history[date]
    return sliced


def _canonical_order(c1, c2):
    return (c1, c2) if c1.ordinal() < c2.ordinal() else (c2, c1)


def collect_deltas(history, ratings) -> list[float]:
    deltas: list[float] = []

    for date in sorted(history.keys()):
        basho_state = history[date]
        banzuke = basho_state.banzuke

        for day in sorted(basho_state.summary.keys()):
            daily_results = basho_state.summary[day]

            for bout in daily_results.results_lookup.values():
                if bout.decision in ("fusen", "blank"):
                    continue

                r1 = bout.rikishi1
                r2 = bout.rikishi2

                if r1 not in banzuke.rikchii or r2 not in banzuke.rikchii:
                    continue

                c_raw_1 = banzuke.rikchii[r1]
                c_raw_2 = banzuke.rikchii[r2]
                c1, c2 = _canonical_order(c_raw_1, c_raw_2)

                deltas.append(float(ratings[c1] - ratings[c2]))

    return deltas


def bin_deltas(deltas: list[float], n_bins: int) -> list[dict[str, float | int]]:
    if n_bins <= 0:
        raise ValueError(f"n_bins must be positive, got {n_bins}")
    if not deltas:
        raise ValueError("No valid deltas collected.")

    lo = min(deltas)
    hi = max(deltas)

    if lo == hi:
        return [
            {
                "bin_index": 0,
                "bin_lo": lo,
                "bin_hi": hi,
                "bin_mid": lo,
                "n_obs": len(deltas),
                "fraction": 1.0,
            }
        ]

    width = (hi - lo) / n_bins
    counts = [0] * n_bins

    for delta in deltas:
        if delta == hi:
            idx = n_bins - 1
        else:
            idx = int((delta - lo) / width)
            idx = max(0, min(n_bins - 1, idx))
        counts[idx] += 1

    total = len(deltas)
    rows: list[dict[str, float | int]] = []
    for idx, count in enumerate(counts):
        bin_lo = lo + idx * width
        bin_hi = hi if idx == n_bins - 1 else lo + (idx + 1) * width
        rows.append(
            {
                "bin_index": idx,
                "bin_lo": bin_lo,
                "bin_hi": bin_hi,
                "bin_mid": (bin_lo + bin_hi) / 2.0,
                "n_obs": count,
                "fraction": count / total,
            }
        )
    return rows


def write_bins_csv(rows: list[dict[str, float | int]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["bin_index", "bin_lo", "bin_hi", "bin_mid", "n_obs", "fraction"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    manifest = _load_manifest(args.run_dir)
    ratings_csv = _ratings_csv_path(args.run_dir, args.ratings_stage)
    if not ratings_csv.exists():
        raise FileNotFoundError(f"Missing ratings CSV: {ratings_csv}")

    eval_start, eval_end = _evaluation_year_bounds(manifest, args.ratings_stage)
    raw_history = connect(eval_start, eval_end, use_zip=args.zip)

    oracle = make_oracle(
        raw_history,
        collapse_mode="annotation_only",
    )

    history = oracle.history
    if args.ratings_stage == "modern":
        params = manifest["params"]
        history = _slice_history_years(
            history,
            int(params["modern_start_year"]),
            int(params["modern_end_year"]),
        )

    ratings = load_ratings_csv(ratings_csv)
    deltas = collect_deltas(history=history, ratings=ratings)
    rows = bin_deltas(deltas=deltas, n_bins=args.n_bins)

    output_path = args.output if args.output else _default_output_path(
        args.run_dir, args.ratings_stage
    )
    written = write_bins_csv(rows, output_path)

    print(f"Run directory: {args.run_dir}")
    print(f"Ratings stage: {args.ratings_stage}")
    print(f"Evaluation years: {eval_start}-{eval_end}")
    print(f"Valid bouts: {len(deltas)}")
    print(f"Delta min: {min(deltas):.6f}")
    print(f"Delta max: {max(deltas):.6f}")
    print(f"Bins written: {len(rows)}")
    print(f"Output CSV: {written}")


if __name__ == "__main__":
    main()

