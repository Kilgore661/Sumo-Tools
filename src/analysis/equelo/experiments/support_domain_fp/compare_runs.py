"""Compare completed support-domain fixed-point experiment outputs."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.sumo_core.Chii import Chii


DEFAULT_ROOT = Path("files/output/Equelo/experiments/support_domain_fp")
DEFAULT_OUTPUT_ROOT = DEFAULT_ROOT / "comparisons"
LANDMARKS = ("Y1e", "O1e", "S1e", "K1e", "M1e", "J1e", "Ms1e", "Sd1e", "Jd1e", "Jk1e")
MONOTONICITY_CUTOFF = Chii.from_str("Jd100w").ordinal()


@dataclass(frozen=True)
class CompletedRun:
    label: str
    run_dir: Path
    manifest: dict
    combined_final_csv: Path
    combined_stats_csv: Path | None
    combined_iterations_csv: Path
    support_csv: Path | None
    threshold_summary_csv: Path | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare existing support-domain fixed-point runs without rerunning the solver."
    )
    parser.add_argument(
        "run_dirs",
        nargs="*",
        type=Path,
        help="Specific run directories. Defaults to all completed runs under --root.",
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--baseline",
        help="Optional run label to use for landmark delta columns.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of highest fixed-point chii to write per run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dirs = args.run_dirs if args.run_dirs else discover_run_dirs(args.root)
    runs = [run for run_dir in run_dirs if (run := load_completed_run(run_dir)) is not None]
    runs.sort(key=lambda run: run.label)

    output_root = write_comparison_report(
        runs,
        output_root=args.output_root / datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        baseline_label=args.baseline,
        top_n=args.top_n,
    )
    print_comparison_report(output_root)


def write_comparison_report(
    runs: list[CompletedRun],
    *,
    output_root: Path,
    baseline_label: str | None = None,
    top_n: int = 20,
    metadata: dict[str, str] | None = None,
) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)

    summary_rows = [summary_row(run) for run in runs]
    landmark_rows = [landmark_row(run) for run in runs]
    top_rows = [row for run in runs for row in top_chii_rows(run, top_n)]
    boundary_rows = [row for run in runs for row in boundary_chii_rows(run)]
    iteration_rows = [row for run in runs for row in iteration_sample_rows(run)]
    monotonicity_rows = [row for run in runs for row in monotonicity_detail_rows(run)]

    baseline = baseline_label or choose_baseline(runs)
    if baseline:
        add_landmark_deltas(landmark_rows, baseline)

    write_csv(output_root / "run_summary.csv", summary_rows)
    write_csv(output_root / "landmark_ratings.csv", landmark_rows)
    write_csv(output_root / "top_fixed_point_chii.csv", top_rows)
    write_csv(output_root / "boundary_chii.csv", boundary_rows)
    write_csv(output_root / "iteration_samples.csv", iteration_rows)
    write_csv(output_root / "monotonicity_by_chii.csv", monotonicity_rows)
    metadata_row = {"baseline_label": baseline or ""}
    if metadata:
        metadata_row.update(metadata)
    write_csv(output_root / "metadata.csv", [metadata_row])
    return output_root


def print_comparison_report(output_root: Path) -> None:
    summary_rows = read_csv(output_root / "run_summary.csv")
    metadata = first_csv_row(output_root / "metadata.csv")
    print(f"Compared completed runs: {len(summary_rows)}")
    for row in summary_rows:
        print(
            f"{row['label']:24} deepest={row['deepest_supported_chii']:7} "
            f"supported={row['supported_chii_count']:>4} "
            f"ignored_bouts={row['ignored_bouts']:>6} "
            f"violations={row['violations']:>4} "
            f"iters={row['iterations']:>3} "
            f"delta={row['final_delta']}"
        )
    if metadata.get("baseline_label"):
        print(f"Baseline for landmark deltas: {metadata['baseline_label']}")
    if metadata.get("total_elapsed_seconds"):
        print(f"Total sweep seconds: {metadata['total_elapsed_seconds']}")
    print(f"Summary CSV: {output_root / 'run_summary.csv'}")
    print(f"Landmark CSV: {output_root / 'landmark_ratings.csv'}")
    print(f"Top chii CSV: {output_root / 'top_fixed_point_chii.csv'}")
    print(f"Boundary CSV: {output_root / 'boundary_chii.csv'}")
    print(f"Iteration sample CSV: {output_root / 'iteration_samples.csv'}")
    print(f"Monotonicity CSV: {output_root / 'monotonicity_by_chii.csv'}")


def discover_run_dirs(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("*/*") if path.is_dir())


def load_completed_run(run_dir: Path) -> CompletedRun | None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = manifest.get("result", {})
    combined_final = result.get("combined_final_csv")
    if not combined_final:
        return None
    combined_final_csv = Path(combined_final)
    if not combined_final_csv.exists():
        return None
    combined_stats = result.get("combined_stats_csv")
    combined_stats_csv = Path(combined_stats) if combined_stats else None
    if combined_stats_csv is not None and not combined_stats_csv.exists():
        combined_stats_csv = None
    combined_iterations_csv = run_dir / "combined_iterations.csv"
    if not combined_iterations_csv.exists():
        return None
    support_dir = run_dir / "support_domain"
    return CompletedRun(
        label=label_for(manifest, run_dir),
        run_dir=run_dir,
        manifest=manifest,
        combined_final_csv=combined_final_csv,
        combined_stats_csv=combined_stats_csv,
        combined_iterations_csv=combined_iterations_csv,
        support_csv=support_dir / "support_by_chii.csv" if (support_dir / "support_by_chii.csv").exists() else None,
        threshold_summary_csv=(
            support_dir / "threshold_summary.csv"
            if (support_dir / "threshold_summary.csv").exists()
            else None
        ),
    )


def label_for(manifest: dict, run_dir: Path) -> str:
    domain = str(manifest.get("domain_label") or manifest.get("domain") or run_dir.parent.name)
    return domain.replace("min_appearances_", "min_app_")


def summary_row(run: CompletedRun) -> dict[str, str]:
    manifest = run.manifest
    result = manifest.get("result", {})
    final_iter = last_csv_row(run.combined_iterations_csv)
    threshold = first_csv_row(run.threshold_summary_csv) if run.threshold_summary_csv else {}
    supported = supported_chii_summary(run)
    monotonicity = monotonicity_summary(run)
    return {
        "label": run.label,
        "run_dir": str(run.run_dir),
        "policy": str(manifest.get("policy", "")),
        "domain": str(manifest.get("domain", "")),
        "min_appearances": str(manifest.get("min_appearances", "")),
        "configured_max_chii": str(manifest.get("configured_max_chii", manifest.get("max_chii", ""))),
        "deepest_supported_chii": supported.get("deepest_supported_chii", ""),
        "deepest_supported_M": supported.get("M", ""),
        "deepest_supported_J": supported.get("J", ""),
        "deepest_supported_Ms": supported.get("Ms", ""),
        "deepest_supported_Sd": supported.get("Sd", ""),
        "deepest_supported_Jd": supported.get("Jd", ""),
        "deepest_supported_Jk": supported.get("Jk", ""),
        "supported_chii_count": str(manifest.get("supported_chii_count", "")),
        "retained_bouts": str(manifest.get("retained_bouts", "")),
        "ignored_bouts": str(manifest.get("ignored_bouts", "")),
        "ignored_scored_bout_pct": str(threshold.get("ignored_scored_bout_pct", "")),
        "excluded_chii": str(threshold.get("excluded_chii", "")),
        "strongest_excluded_chii": str(threshold.get("strongest_excluded_chii", "")),
        "violations": str(count_violations(run.combined_stats_csv)),
        "monotonicity_cutoff": "Jd100w",
        "monotonicity_n": str(monotonicity.get("n", "")),
        "monotonicity_footrule": str(monotonicity.get("footrule", "")),
        "monotonicity_mean_abs_displacement": str(monotonicity.get("mean_abs_displacement", "")),
        "monotonicity_max_abs_displacement": str(monotonicity.get("max_abs_displacement", "")),
        "monotonicity_inversions": str(monotonicity.get("inversions", "")),
        "monotonicity_pair_count": str(monotonicity.get("pair_count", "")),
        "monotonicity_inversion_ratio": str(monotonicity.get("inversion_ratio", "")),
        "iterations": str(result.get("iterations", "")),
        "final_delta": str(result.get("final_delta", "")),
        "last_max_delta_chii": str(final_iter.get("max_delta_chii", "")),
        "last_max_delta_count": str(final_iter.get("max_delta_count", "")),
        "last_shift": str(final_iter.get("shift", "")),
        "elapsed_seconds": str(manifest.get("elapsed_seconds", "")),
    }


def landmark_row(run: CompletedRun) -> dict[str, str]:
    ratings = ratings_by_chii(run.combined_final_csv)
    row = {"label": run.label}
    for chii in LANDMARKS:
        row[chii] = rating_text(ratings.get(chii))
    return row


def top_chii_rows(run: CompletedRun, top_n: int) -> list[dict[str, str]]:
    rows = list(read_csv(run.combined_final_csv))
    rows.sort(key=lambda row: float(row["rating"]), reverse=True)
    return [
        {
            "label": run.label,
            "position": str(index),
            "chii": row["chii"],
            "rating": rating_text(float(row["rating"])),
        }
        for index, row in enumerate(rows[:top_n], start=1)
    ]


def monotonicity_detail_rows(run: CompletedRun) -> list[dict[str, str]]:
    rows = monotonicity_rank_rows(run)
    return [
        {
            "label": run.label,
            "chii": row["chii"],
            "ordinal": str(row["ordinal"]),
            "rating": rating_text(row["rating"]),
            "ordinal_rank": str(row["ordinal_rank"]),
            "rating_rank": str(row["rating_rank"]),
            "rank_delta": str(row["rating_rank"] - row["ordinal_rank"]),
            "abs_rank_delta": str(abs(row["rating_rank"] - row["ordinal_rank"])),
        }
        for row in rows
    ]


def monotonicity_summary(run: CompletedRun) -> dict[str, str]:
    rows = monotonicity_rank_rows(run)
    n = len(rows)
    if n == 0:
        return {}
    footrule = sum(abs(row["rating_rank"] - row["ordinal_rank"]) for row in rows)
    max_abs = max(abs(row["rating_rank"] - row["ordinal_rank"]) for row in rows)
    inversions = count_rating_inversions(rows)
    pair_count = n * (n - 1) // 2
    return {
        "n": str(n),
        "footrule": str(footrule),
        "mean_abs_displacement": f"{footrule / n:.3f}",
        "max_abs_displacement": str(max_abs),
        "inversions": str(inversions),
        "pair_count": str(pair_count),
        "inversion_ratio": "" if pair_count == 0 else f"{inversions / pair_count:.6f}",
    }


def monotonicity_rank_rows(run: CompletedRun) -> list[dict[str, int | float | str]]:
    rows = [
        {
            "chii": row["chii"],
            "ordinal": int(row["ordinal"]),
            "rating": float(row["rating"]),
        }
        for row in read_csv(run.combined_final_csv)
        if int(row["ordinal"]) <= MONOTONICITY_CUTOFF
    ]
    ordinal_rows = sorted(rows, key=lambda row: (row["ordinal"], row["chii"]))
    rating_rows = sorted(rows, key=lambda row: (-row["rating"], row["ordinal"], row["chii"]))
    for index, row in enumerate(ordinal_rows, start=1):
        row["ordinal_rank"] = index
    rating_rank_by_chii = {
        str(row["chii"]): index
        for index, row in enumerate(rating_rows, start=1)
    }
    for row in ordinal_rows:
        row["rating_rank"] = rating_rank_by_chii[str(row["chii"])]
    return ordinal_rows


def count_rating_inversions(rows: list[dict[str, int | float | str]]) -> int:
    rating_ranks = [int(row["rating_rank"]) for row in sorted(rows, key=lambda row: int(row["ordinal_rank"]))]
    _, inversions = merge_count_inversions(rating_ranks)
    return inversions


def merge_count_inversions(values: list[int]) -> tuple[list[int], int]:
    if len(values) < 2:
        return values, 0
    midpoint = len(values) // 2
    left, left_inversions = merge_count_inversions(values[:midpoint])
    right, right_inversions = merge_count_inversions(values[midpoint:])
    merged: list[int] = []
    inversions = left_inversions + right_inversions
    left_index = 0
    right_index = 0
    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            inversions += len(left) - left_index
            right_index += 1
    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged, inversions


def boundary_chii_rows(run: CompletedRun, window: int = 5) -> list[dict[str, str]]:
    if run.support_csv is None:
        return []
    support_rows = read_csv(run.support_csv)
    if not support_rows or "appearances" not in support_rows[0]:
        return []
    min_appearances = parse_optional_int(str(run.manifest.get("min_appearances", "")))
    if min_appearances is None:
        return []
    ratings = ratings_by_chii(run.combined_final_csv)
    annotated = [
        {
            **row,
            "label": run.label,
            "supported_by_min_appearances": str(int(row["appearances"]) >= min_appearances),
            "run_rating": rating_text(ratings.get(row["chii"])),
        }
        for row in support_rows
    ]
    first_excluded_index = next(
        (
            index
            for index, row in enumerate(annotated)
            if int(row["appearances"]) < min_appearances
        ),
        None,
    )
    if first_excluded_index is None:
        return annotated[-window:]
    start = max(0, first_excluded_index - window)
    end = min(len(annotated), first_excluded_index + window)
    return annotated[start:end]


def supported_chii_summary(run: CompletedRun) -> dict[str, str]:
    if run.support_csv is None:
        return {}
    support_rows = read_csv(run.support_csv)
    if not support_rows:
        return {}
    supported = supported_rows(run, support_rows)
    if not supported:
        return {}
    by_ordinal = sorted(supported, key=lambda row: int(row["ordinal"]))
    summary = {"deepest_supported_chii": by_ordinal[-1]["chii"]}
    for division in ("M", "J", "Ms", "Sd", "Jd", "Jk"):
        rows = [row for row in by_ordinal if division_of(row["chii"]) == division]
        summary[division] = rows[-1]["chii"] if rows else ""
    return summary


def supported_rows(run: CompletedRun, support_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    domain = run.manifest.get("domain")
    if domain == "min-appearances":
        min_appearances = parse_optional_int(str(run.manifest.get("min_appearances", "")))
        if min_appearances is None:
            return []
        return [row for row in support_rows if int(row["appearances"]) >= min_appearances]
    if domain == "max-chii":
        max_chii = str(run.manifest.get("max_chii", run.manifest.get("configured_max_chii", "")))
        max_ordinal = next(
            (int(row["ordinal"]) for row in support_rows if row["chii"] == max_chii),
            None,
        )
        if max_ordinal is None:
            return []
        return [row for row in support_rows if int(row["ordinal"]) <= max_ordinal]
    if domain == "support-threshold":
        threshold = parse_optional_float(str(run.manifest.get("threshold", "")))
        if threshold is None:
            return []
        return [
            row
            for row in support_rows
            if parse_optional_float(row.get("actual_total_pct", "")) is not None
            and float(row["actual_total_pct"]) >= threshold
        ]
    return []


def division_of(chii: str) -> str:
    if chii.startswith("Ms"):
        return "Ms"
    if chii.startswith("Sd"):
        return "Sd"
    if chii.startswith("Jd"):
        return "Jd"
    if chii.startswith("Jk"):
        return "Jk"
    if chii.startswith("J"):
        return "J"
    if chii.startswith("M"):
        return "M"
    if chii.startswith(("Y", "O", "S", "K")):
        return chii[0]
    return ""


def iteration_sample_rows(run: CompletedRun) -> list[dict[str, str]]:
    rows = read_csv(run.combined_iterations_csv)
    if not rows:
        return []
    selected_indexes = {0, len(rows) - 1}
    if len(rows) > 2:
        selected_indexes.add(len(rows) // 2)
    selected = []
    for index, row in enumerate(rows):
        if index not in selected_indexes:
            continue
        selected.append(
            {
                "label": run.label,
                "sample": "first" if index == 0 else "last" if index == len(rows) - 1 else "middle",
                "iter": row.get("iter", ""),
                "delta": row.get("delta", ""),
                "shift": row.get("shift", ""),
                "max_delta_chii": row.get("max_delta_chii", ""),
                "max_delta_count": row.get("max_delta_count", ""),
                "Y1e": row.get("Y1e", ""),
                "M1e": row.get("M1e", ""),
                "J1e": row.get("J1e", ""),
                "Ms1e": row.get("Ms1e", ""),
                "Sd1e": row.get("Sd1e", ""),
                "Jd1e": row.get("Jd1e", ""),
                "Jk1e": row.get("Jk1e", ""),
            }
        )
    return selected


def add_landmark_deltas(rows: list[dict[str, str]], baseline_label: str) -> None:
    baseline = next((row for row in rows if row["label"] == baseline_label), None)
    if baseline is None:
        return
    for row in rows:
        for chii in LANDMARKS:
            base = parse_optional_float(baseline.get(chii, ""))
            value = parse_optional_float(row.get(chii, ""))
            row[f"{chii}_delta_vs_{baseline_label}"] = (
                "" if base is None or value is None else rating_text(value - base)
            )


def choose_baseline(runs: list[CompletedRun]) -> str | None:
    labels = {run.label for run in runs}
    for candidate in ("min_app_50", "min_app_100"):
        if candidate in labels:
            return candidate
    return runs[0].label if runs else None


def ratings_by_chii(path: Path) -> dict[str, float]:
    return {row["chii"]: float(row["rating"]) for row in read_csv(path)}


def first_csv_row(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    rows = read_csv(path)
    return rows[0] if rows else {}


def last_csv_row(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    return rows[-1] if rows else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_violations(path: Path | None) -> int:
    if path is None:
        return 0
    return sum(1 for row in read_csv(path) if row.get("violation") == "True")


def write_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def rating_text(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def parse_optional_int(value: str) -> int | None:
    if value == "":
        return None
    return int(value)


if __name__ == "__main__":
    main()
