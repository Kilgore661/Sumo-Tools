"""Compare latest support-domain fixed-point runs with original fixed_v2."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Iterable

from src.analysis.equelo.fixed_v2.model import FP_SOURCE


SWEEP_ROOT = Path("files/output/Equelo/experiments/support_domain_fp/min_appearance_sweeps")
LANDMARKS = ("Y1e", "O1e", "S1e", "K1e", "M1e", "J1e", "Ms1e", "Sd1e", "Jd1e", "Jk1e")


@dataclass(frozen=True)
class CandidateRun:
    label: str
    run_dir: Path
    combined_final_csv: Path


def main() -> None:
    sweep_dir = latest_sweep_dir()
    runs = latest_sweep_runs(sweep_dir)
    outputs = write_v2_comparison(
        runs,
        original_csv=FP_SOURCE,
        output_root=sweep_dir / "comparison_to_v2",
    )
    print(f"Sweep directory: {sweep_dir}")
    print(f"Original v2: {FP_SOURCE}")
    print(f"Compared runs: {len(runs)}")
    for row in read_csv(outputs.summary_csv):
        print(
            f"{row['label']:24} common={row['common_chii']:>4} "
            f"excluded={row['excluded_original_chii']:>4} "
            f"mean_abs={row['mean_abs_delta']:>8} "
            f"p95_abs={row['p95_abs_delta']:>8} "
            f"max_abs={row['max_abs_delta']:>8} "
            f"max_chii={row['max_abs_delta_chii']}"
        )
    print(f"Summary CSV: {outputs.summary_csv}")
    print(f"Delta CSV: {outputs.delta_csv}")
    print(f"Excluded CSV: {outputs.excluded_csv}")


@dataclass(frozen=True)
class V2ComparisonOutputs:
    output_root: Path
    summary_csv: Path
    delta_csv: Path
    excluded_csv: Path


def write_v2_comparison(
    runs: Iterable[CandidateRun],
    *,
    original_csv: Path,
    output_root: Path,
) -> V2ComparisonOutputs:
    output_root.mkdir(parents=True, exist_ok=True)
    original = ratings_by_chii(original_csv)
    summary_rows: list[dict[str, str]] = []
    delta_rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []

    for run in runs:
        candidate = ratings_by_chii(run.combined_final_csv)
        summary_rows.append(summary_row(run, original, candidate))
        delta_rows.extend(delta_detail_rows(run, original, candidate))
        excluded_rows.extend(excluded_detail_rows(run, original, candidate))

    outputs = V2ComparisonOutputs(
        output_root=output_root,
        summary_csv=output_root / "summary_vs_v2.csv",
        delta_csv=output_root / "delta_by_chii_vs_v2.csv",
        excluded_csv=output_root / "excluded_original_chii.csv",
    )
    write_csv(outputs.summary_csv, summary_rows)
    write_csv(outputs.delta_csv, delta_rows)
    write_csv(outputs.excluded_csv, excluded_rows)
    return outputs


def latest_sweep_dir() -> Path:
    if not SWEEP_ROOT.exists():
        raise FileNotFoundError(f"Sweep root not found: {SWEEP_ROOT}")
    sweep_dirs = sorted(
        (path for path in SWEEP_ROOT.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not sweep_dirs:
        raise FileNotFoundError(f"No sweep folders found under {SWEEP_ROOT}")
    return sweep_dirs[0]


def latest_sweep_runs(sweep_dir: Path) -> list[CandidateRun]:
    runs = [resolve_manifest(path) for path in sorted(sweep_dir.glob("rfsc_min_app_*/*/manifest.json"))]
    return sorted(runs, key=lambda run: min_app_sort_key(run.label), reverse=True)


def resolve_manifest(path: Path) -> CandidateRun:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    result = manifest.get("result", {})
    csv_path = result.get("combined_final_csv")
    if not csv_path:
        raise ValueError(f"Manifest has no result.combined_final_csv: {path}")
    label = str(manifest.get("domain_label") or manifest.get("domain") or path.parent.name)
    return CandidateRun(
        label=label.replace("min_appearances_", "min_app_"),
        run_dir=path.parent,
        combined_final_csv=Path(csv_path),
    )


def min_app_sort_key(label: str) -> int:
    if label.startswith("min_app_"):
        return int(label.removeprefix("min_app_"))
    return -1


def summary_row(
    run: CandidateRun,
    original: dict[str, dict[str, float | int | str]],
    candidate: dict[str, dict[str, float | int | str]],
) -> dict[str, str]:
    common = sorted(set(original) & set(candidate), key=lambda chii: int(original[chii]["ordinal"]))
    excluded = sorted(set(original) - set(candidate), key=lambda chii: int(original[chii]["ordinal"]))
    deltas = [float(candidate[chii]["rating"]) - float(original[chii]["rating"]) for chii in common]
    abs_deltas = [abs(delta) for delta in deltas]
    max_chii = ""
    max_abs = 0.0
    if common:
        max_chii = max(common, key=lambda chii: abs(float(candidate[chii]["rating"]) - float(original[chii]["rating"])))
        max_abs = abs(float(candidate[max_chii]["rating"]) - float(original[max_chii]["rating"]))
    row = {
        "label": run.label,
        "run_dir": str(run.run_dir),
        "candidate_csv": str(run.combined_final_csv),
        "common_chii": str(len(common)),
        "candidate_chii": str(len(candidate)),
        "original_chii": str(len(original)),
        "excluded_original_chii": str(len(excluded)),
        "mean_delta": metric_text(sum(deltas) / len(deltas) if deltas else None),
        "mean_abs_delta": metric_text(sum(abs_deltas) / len(abs_deltas) if abs_deltas else None),
        "median_abs_delta": metric_text(median(abs_deltas) if abs_deltas else None),
        "p95_abs_delta": metric_text(percentile(abs_deltas, 0.95) if abs_deltas else None),
        "max_abs_delta": metric_text(max_abs if common else None),
        "max_abs_delta_chii": max_chii,
        "max_abs_delta_old_rating": rating_text(float(original[max_chii]["rating"])) if max_chii else "",
        "max_abs_delta_new_rating": rating_text(float(candidate[max_chii]["rating"])) if max_chii else "",
    }
    for chii in LANDMARKS:
        row[f"{chii}_delta"] = (
            metric_text(float(candidate[chii]["rating"]) - float(original[chii]["rating"]))
            if chii in candidate and chii in original
            else ""
        )
    return row


def delta_detail_rows(
    run: CandidateRun,
    original: dict[str, dict[str, float | int | str]],
    candidate: dict[str, dict[str, float | int | str]],
) -> list[dict[str, str]]:
    rows = []
    for chii in sorted(set(original) & set(candidate), key=lambda key: int(original[key]["ordinal"])):
        old_rating = float(original[chii]["rating"])
        new_rating = float(candidate[chii]["rating"])
        delta = new_rating - old_rating
        rows.append(
            {
                "label": run.label,
                "chii": chii,
                "ordinal": str(original[chii]["ordinal"]),
                "old_rating": rating_text(old_rating),
                "new_rating": rating_text(new_rating),
                "delta": metric_text(delta),
                "abs_delta": metric_text(abs(delta)),
            }
        )
    return rows


def excluded_detail_rows(
    run: CandidateRun,
    original: dict[str, dict[str, float | int | str]],
    candidate: dict[str, dict[str, float | int | str]],
) -> list[dict[str, str]]:
    rows = []
    for chii in sorted(set(original) - set(candidate), key=lambda key: int(original[key]["ordinal"])):
        rows.append(
            {
                "label": run.label,
                "chii": chii,
                "ordinal": str(original[chii]["ordinal"]),
                "old_rating": rating_text(float(original[chii]["rating"])),
            }
        )
    return rows


def ratings_by_chii(path: Path) -> dict[str, dict[str, float | int | str]]:
    return {
        row["chii"]: {
            "chii": row["chii"],
            "ordinal": int(row["ordinal"]),
            "rating": float(row["rating"]),
        }
        for row in read_csv(path)
    }


def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    if not values:
        raise ValueError("Cannot compute percentile of empty list")
    index = (len(values) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    fraction = index - lower
    return values[lower] + (values[upper] - values[lower]) * fraction


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def rating_text(value: float) -> str:
    return f"{value:.3f}"


def metric_text(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


if __name__ == "__main__":
    main()
