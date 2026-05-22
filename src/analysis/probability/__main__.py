import argparse
import datetime
import json
from pathlib import Path

from src.infra.config import EPOCH

from ...infra.connect import connect
from ...sumo_core.BasicPrimitives import RikId
from ..equelo.config_main import BIOS_PATH
from ..equelo.expt1.Oracle import make_oracle
from .builder import (
    build_calibration_rows,
    calibration_summary,
    load_ratings_csv,
    write_calibration_csv,
)


VALID_RATINGS_STAGES = ("naive", "modern", "combined")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build Elo calibration rows from Expt2 ratings and cleaned observed bouts"
    )
    parser.add_argument("--start", type=int, default=EPOCH)
    parser.add_argument("--end", type=int, default=datetime.datetime.now().year)
    parser.add_argument("--zip", action="store_true")

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
        "--q",
        type=float,
        default=850.0,
        help="Elo logistic scale parameter.",
    )
    parser.add_argument(
        "--bin-width",
        type=float,
        default=0.01,
        help="Probability bin width.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV path.",
    )
    return parser


def _load_manifest(run_dir: Path) -> dict:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found in {run_dir}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ratings_csv_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"{stage}_final.csv"


def _default_output_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"{stage}_calibration.csv"


def _evaluation_year_bounds(manifest: dict, ratings_stage: str) -> tuple[int, int]:
    params = manifest.get("params", {})

    if ratings_stage == "modern":
        return int(params["modern_start_year"]), int(params["modern_end_year"])

    return int(params["start"]), int(params["end"])


def _slice_history_years(history, start_year: int, end_year: int):
    sliced = history.__class__()
    for date in sorted(history.keys()):
        if start_year <= date.year <= end_year:
            sliced[date] = history[date]
    return sliced


def _reconstruct_command(params: dict, stage: str) -> str:
    cmd = ["py", "-m", "src.analysis.equelo.expt2"]

    cmd += ["--variant", stage]
    cmd += ["--collapse", "annotation-only"]

    if params.get("start") is not None:
        cmd += ["--start", str(params["start"])]
    if params.get("end") is not None:
        cmd += ["--end", str(params["end"])]
    if params.get("zip"):
        cmd += ["--zip"]
    if params.get("epsilon") is not None:
        cmd += ["--epsilon", str(params["epsilon"])]
    if params.get("max_iter") is not None:
        cmd += ["--max-iter", str(params["max_iter"])]
    if params.get("mode") == "open":
        cmd += ["--open"]
    if params.get("modern_start_year") is not None:
        cmd += ["--modern-start-year", str(params["modern_start_year"])]
    if params.get("modern_end_year") is not None:
        cmd += ["--modern-end-year", str(params["modern_end_year"])]
    if params.get("k_policy"):
        cmd += ["--k-policy", params["k_policy"]]

    if params.get("k_policy") == "constant" and params.get("k_value") is not None:
        cmd += ["--k-value", str(params["k_value"])]
    if params.get("k_policy") == "divisional" and params.get("k_config"):
        cmd += ["--k-config", params["k_config"]]

    return " ".join(cmd)


def _validate_run(manifest: dict, run_dir: Path, stage: str) -> Path:
    params = manifest.get("params", {})

    collapse_mode = params.get("collapse_mode")
    ratings_csv = _ratings_csv_path(run_dir, stage)

    if collapse_mode != "annotation-only" or not ratings_csv.exists():
        print("\n=== Probability module error ===\n")

        print(f"Run directory: {run_dir}")
        print(f"Selected stage: {stage}")
        print(f"collapse_mode in run: {collapse_mode}")

        print("\nExpected ratings file:")
        print(ratings_csv)

        print("\nReason:")
        if collapse_mode != "annotation-only":
            print("This run uses chii-bucket (or other) rank type.")
            print("Probability module requires annotation-only (full Chii).")

        if not ratings_csv.exists():
            print("Expected ratings file does not exist.")

        print("\nTo create the required file, run:\n")
        print(_reconstruct_command(params, stage))
        print()

        raise SystemExit(1)

    return ratings_csv


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    manifest = _load_manifest(args.run_dir)
    ratings_csv = _validate_run(manifest, args.run_dir, args.ratings_stage)
    eval_start, eval_end = _evaluation_year_bounds(manifest, args.ratings_stage)

    raw_history = connect(eval_start, eval_end, use_zip=args.zip)

    with open(BIOS_PATH, "r", encoding="utf-8") as f:
        raw_bios = json.load(f)
    bios = {RikId(int(k)): v for k, v in raw_bios.items()}

    oracle = make_oracle(
        raw_history,
        bios,
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

    rows = build_calibration_rows(
        history=history,
        ratings=ratings,
        q=args.q,
        bin_width=args.bin_width,
    )
    summary = calibration_summary(rows)

    output_path = args.output if args.output else _default_output_path(
        args.run_dir, args.ratings_stage
    )
    written = write_calibration_csv(rows, output_path)

    print(f"Run directory: {args.run_dir}")
    print(f"Ratings stage: {args.ratings_stage}")
    print(f"Evaluation years: {eval_start}-{eval_end}")
    print(f"Rows written: {len(rows)}")
    print(f"Calibration MAE (all): {summary['mae_all']:.6f}")
    print(f"Calibration RMSE (all): {summary['rmse_all']:.6f}")
    print(f"Calibration MAE (core): {summary['mae_core']:.6f}")
    print(f"Calibration RMSE (core): {summary['rmse_core']:.6f}")
    print(f"Core rows: {summary['n_core_rows']}")
    print(f"Brier score: {summary['brier']:.6f}")
    print(f"Baseline Brier: {summary['baseline_brier']:.6f}")
    print(f"Brier skill score: {summary['brier_skill']:.6f}")
    print(f"Brier reliability: {summary['brier_reliability']:.6f}")
    print(f"Brier resolution: {summary['brier_resolution']:.6f}")
    print(f"Brier uncertainty: {summary['brier_uncertainty']:.6f}")
    print(f"Base rate: {summary['base_rate']:.6f}")
    print(f"Output CSV: {written}")


if __name__ == "__main__":
    main()
