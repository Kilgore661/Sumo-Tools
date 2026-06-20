"""Compute rating-vs-rank monotonicity metrics for fixed-point chii ratings."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.sumo_core.Chii import Chii


SWEEP_ROOT = Path("files/output/Equelo/experiments/support_domain_fp/min_appearance_sweeps")
DEFAULT_CUTOFF = "Jd100w"


@dataclass(frozen=True)
class RatingInput:
    label: str
    path: Path


def main() -> None:
    sweep_dir = latest_sweep_dir()
    inputs = latest_sweep_inputs(sweep_dir)
    cutoff = Chii.from_str(DEFAULT_CUTOFF)
    output_root = sweep_dir / "monotonicity"
    outputs = write_monotonicity_report(
        inputs,
        cutoff=cutoff,
        output_root=output_root,
    )
    print(f"Sweep directory: {sweep_dir}")
    print(f"Compared inputs: {len(inputs)}")
    print(f"Cutoff: {cutoff}")
    for row in read_csv(outputs.summary_csv):
        print(
            f"{row['label']:24} n={row['n']:>4} "
            f"footrule={row['footrule']:>6} "
            f"mean_abs={row['mean_abs_displacement']:>7} "
            f"max_abs={row['max_abs_displacement']:>4} "
            f"inversions={row['inversions']:>6} "
            f"ratio={row['inversion_ratio']}"
        )
    print(f"Summary CSV: {outputs.summary_csv}")
    print(f"Detail CSV: {outputs.detail_csv}")


@dataclass(frozen=True)
class MonotonicityOutputs:
    output_root: Path
    summary_csv: Path
    detail_csv: Path


def write_monotonicity_report(
    inputs: Iterable[RatingInput],
    *,
    cutoff: Chii,
    output_root: Path,
) -> MonotonicityOutputs:
    output_root.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, str]] = []
    detail_rows: list[dict[str, str]] = []
    for rating_input in inputs:
        ranked = monotonicity_rank_rows(rating_input.path, cutoff=cutoff)
        summary_rows.append(summary_row(rating_input, ranked, cutoff=cutoff))
        detail_rows.extend(detail_row(rating_input, row, cutoff=cutoff) for row in ranked)

    outputs = MonotonicityOutputs(
        output_root=output_root,
        summary_csv=output_root / "monotonicity_summary.csv",
        detail_csv=output_root / "monotonicity_by_chii.csv",
    )
    write_csv(outputs.summary_csv, summary_rows)
    write_csv(outputs.detail_csv, detail_rows)
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


def latest_sweep_inputs(sweep_dir: Path) -> list[RatingInput]:
    manifest_paths = sorted(sweep_dir.glob("rfsc_min_app_*/*/manifest.json"))
    inputs = [resolve_manifest(path) for path in manifest_paths]
    return sorted(inputs, key=lambda item: min_app_sort_key(item.label), reverse=True)


def min_app_sort_key(label: str) -> int:
    if label.startswith("min_app_"):
        return int(label.removeprefix("min_app_"))
    return -1


def resolve_manifest(path: Path) -> RatingInput:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    result = manifest.get("result", {})
    csv_path = result.get("combined_final_csv")
    if not csv_path:
        raise ValueError(f"Manifest has no result.combined_final_csv: {path}")
    label = str(manifest.get("domain_label") or manifest.get("domain") or path.parent.name)
    return RatingInput(
        label=label.replace("min_appearances_", "min_app_"),
        path=Path(csv_path),
    )


def monotonicity_rank_rows(path: Path, *, cutoff: Chii) -> list[dict[str, int | float | str]]:
    cutoff_ordinal = cutoff.ordinal()
    rows = [
        {
            "chii": row["chii"],
            "ordinal": int(row["ordinal"]),
            "rating": float(row["rating"]),
        }
        for row in read_csv(path)
        if int(row["ordinal"]) <= cutoff_ordinal
    ]
    ordinal_rows = sorted(rows, key=lambda row: (int(row["ordinal"]), str(row["chii"])))
    rating_rows = sorted(
        rows,
        key=lambda row: (-float(row["rating"]), int(row["ordinal"]), str(row["chii"])),
    )
    for index, row in enumerate(ordinal_rows, start=1):
        row["ordinal_rank"] = index
    rating_rank_by_chii = {
        str(row["chii"]): index
        for index, row in enumerate(rating_rows, start=1)
    }
    for row in ordinal_rows:
        row["rating_rank"] = rating_rank_by_chii[str(row["chii"])]
    return ordinal_rows


def summary_row(
    rating_input: RatingInput,
    rows: list[dict[str, int | float | str]],
    *,
    cutoff: Chii,
) -> dict[str, str]:
    n = len(rows)
    if n == 0:
        return {
            "label": rating_input.label,
            "ratings_csv": str(rating_input.path),
            "cutoff": str(cutoff),
            "n": "0",
        }
    footrule = sum(abs(int(row["rating_rank"]) - int(row["ordinal_rank"])) for row in rows)
    max_abs = max(abs(int(row["rating_rank"]) - int(row["ordinal_rank"])) for row in rows)
    inversions = count_rating_inversions(rows)
    pair_count = n * (n - 1) // 2
    return {
        "label": rating_input.label,
        "ratings_csv": str(rating_input.path),
        "cutoff": str(cutoff),
        "n": str(n),
        "footrule": str(footrule),
        "mean_abs_displacement": f"{footrule / n:.3f}",
        "max_abs_displacement": str(max_abs),
        "inversions": str(inversions),
        "pair_count": str(pair_count),
        "inversion_ratio": "" if pair_count == 0 else f"{inversions / pair_count:.6f}",
    }


def detail_row(
    rating_input: RatingInput,
    row: dict[str, int | float | str],
    *,
    cutoff: Chii,
) -> dict[str, str]:
    ordinal_rank = int(row["ordinal_rank"])
    rating_rank = int(row["rating_rank"])
    return {
        "label": rating_input.label,
        "ratings_csv": str(rating_input.path),
        "cutoff": str(cutoff),
        "chii": str(row["chii"]),
        "ordinal": str(row["ordinal"]),
        "rating": rating_text(float(row["rating"])),
        "ordinal_rank": str(ordinal_rank),
        "rating_rank": str(rating_rank),
        "rank_delta": str(rating_rank - ordinal_rank),
        "abs_rank_delta": str(abs(rating_rank - ordinal_rank)),
    }


def count_rating_inversions(rows: list[dict[str, int | float | str]]) -> int:
    rating_ranks = [
        int(row["rating_rank"])
        for row in sorted(rows, key=lambda row: int(row["ordinal_rank"]))
    ]
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


if __name__ == "__main__":
    main()
