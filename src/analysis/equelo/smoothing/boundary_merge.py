"""Produce a literal-chii merge of the M/J and lower-banzuke results."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .boundary_merge_chart import write_boundary_merge_chart


UPPER_DIVISIONS = {"Y", "O", "S", "K", "M"}


@dataclass(frozen=True)
class BoundaryMergeOutputs:
    data_csv: Path
    metadata_json: Path
    chart_html: Path


def build_boundary_merge(
    mj_csv: Path,
    lower_csv: Path,
    output_csv: Path,
    *,
    cutoff_chii: str = "Jd100e",
) -> BoundaryMergeOutputs:
    """Produce persisted merged values, metadata, and a chart."""

    mj_rows = _read_rows(mj_csv)
    lower_rows = _read_rows(lower_csv)
    mj_by_chii = {row["chii"]: row for row in mj_rows}
    lower_by_chii = {row["chii"]: row for row in lower_rows}
    upper = [row for row in mj_rows if row["division"] in UPPER_DIVISIONS]
    juryo = [row for row in mj_rows if row["division"] == "J"]
    lower_non_juryo = [row for row in lower_rows if row["division"] != "J"]
    if not juryo:
        raise ValueError("M/J comparison contains no Juryo chii")
    missing = [row["chii"] for row in juryo if row["chii"] not in lower_by_chii]
    if missing:
        raise ValueError(f"Lower comparison is missing Juryo chii: {missing}")
    if cutoff_chii not in lower_by_chii:
        raise ValueError(f"Lower comparison does not contain cutoff {cutoff_chii}")

    lower_shift = _weighted_juryo_shift(juryo, lower_by_chii)
    output_rows: list[dict[str, object]] = []
    for row in upper:
        rating = _rating(row)
        output_rows.append(
            _output_row(row["chii"], row["division"], rating, None, rating, "M/J")
        )

    denominator = max(len(juryo) - 1, 1)
    for index, row in enumerate(juryo):
        chii = row["chii"]
        mj_rating = _rating(mj_by_chii[chii])
        lower_rating = _rating(lower_by_chii[chii]) + lower_shift
        mj_weight = 1.0 - index / denominator
        merged = mj_weight * mj_rating + (1.0 - mj_weight) * lower_rating
        output_rows.append(
            _output_row(
                chii,
                "J",
                mj_rating,
                lower_rating,
                merged,
                "linear Juryo blend",
                mj_weight,
            )
        )

    cutoff_rating = _rating(lower_by_chii[cutoff_chii]) + lower_shift
    below_cutoff = False
    for row in lower_non_juryo:
        chii = row["chii"]
        lower_rating = _rating(row) + lower_shift
        merged = cutoff_rating if below_cutoff else lower_rating
        source = (
            f"flat tail from {cutoff_chii}"
            if below_cutoff
            else "aligned lower-banzuke"
        )
        output_rows.append(
            _output_row(chii, row["division"], None, lower_rating, merged, source)
        )
        if chii == cutoff_chii:
            below_cutoff = True

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(output_csv, output_rows)
    chart_html = write_boundary_merge_chart(
        output_csv,
        output_csv.with_suffix(".html"),
        cutoff_chii=cutoff_chii,
        lower_shift=lower_shift,
    )
    metadata_json = output_csv.with_suffix(".metadata.json")
    _write_metadata(
        metadata_json,
        mj_csv=mj_csv,
        lower_csv=lower_csv,
        output_csv=output_csv,
        chart_html=chart_html,
        cutoff_chii=cutoff_chii,
        lower_shift=lower_shift,
        cutoff_rating=cutoff_rating,
        row_count=len(output_rows),
    )
    return BoundaryMergeOutputs(output_csv, metadata_json, chart_html)


def _weighted_juryo_shift(
    juryo: list[dict[str, str]],
    lower_by_chii: dict[str, dict[str, str]],
) -> float:
    weighted_difference = 0.0
    observations = 0
    for row in juryo:
        lower = lower_by_chii[row["chii"]]
        count = int(lower["appearance_count"])
        weighted_difference += (_rating(row) - _rating(lower)) * count
        observations += count
    return weighted_difference / observations


def _rating(row: dict[str, str]) -> float:
    return float(row["contextual_resolved_prior_mean"])


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _output_row(
    chii: str,
    division: str,
    mj_rating: float | None,
    lower_rating: float | None,
    merged_rating: float | None,
    source: str,
    mj_weight: float | None = None,
) -> dict[str, object]:
    return {
        "chii": chii,
        "division": division,
        "mj_resolved_rating": mj_rating,
        "aligned_lower_resolved_rating": lower_rating,
        "mj_weight": mj_weight,
        "pre_smoothing_rating": merged_rating,
        "source": source,
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_metadata(
    path: Path,
    *,
    mj_csv: Path,
    lower_csv: Path,
    output_csv: Path,
    chart_html: Path,
    cutoff_chii: str,
    lower_shift: float,
    cutoff_rating: float,
    row_count: int,
) -> None:
    metadata = {
        "kind": "equelo_literal_chii_boundary_merge_candidate",
        "generated_at": datetime.now().astimezone().isoformat(),
        "inputs": {
            "mj_comparison_csv": _file_reference(mj_csv),
            "lower_banzuke_comparison_csv": _file_reference(lower_csv),
        },
        "construction": {
            "alignment": (
                "appearance-weighted mean M/J minus lower-banzuke rating "
                "over matching literal Juryo chii"
            ),
            "lower_banzuke_additive_shift": lower_shift,
            "juryo_merge": "linear M/J weight from 1 at J1e to 0 at J14w",
            "upper_source": "M/J contextual estimate through Makuuchi",
            "lower_source": f"aligned lower-banzuke estimate through {cutoff_chii}",
            "tail_policy": f"constant at the {cutoff_chii} value below {cutoff_chii}",
            "cutoff_chii": cutoff_chii,
            "pre_smoothing_cutoff_rating": cutoff_rating,
            "smoothing_applied": False,
        },
        "outputs": {
            "data_csv": _file_reference(output_csv),
            "chart_html": _file_reference(chart_html),
            "row_count": row_count,
        },
    }
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def _file_reference(path: Path) -> dict[str, object]:
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mj-csv", type=Path, required=True)
    parser.add_argument("--lower-csv", type=Path, required=True)
    parser.add_argument("--cutoff-chii", default="Jd100e")
    parser.add_argument("--output-csv", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = build_boundary_merge(
        args.mj_csv,
        args.lower_csv,
        args.output_csv,
        cutoff_chii=args.cutoff_chii,
    )
    print(f"Data: {outputs.data_csv}")
    print(f"Metadata: {outputs.metadata_json}")
    print(f"Chart: {outputs.chart_html}")


if __name__ == "__main__":
    main()
