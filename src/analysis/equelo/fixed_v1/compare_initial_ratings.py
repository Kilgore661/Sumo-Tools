"""Compare the three current chii-to-initial-rating maps.

This module is an audit tool for the fixed-v1/v5 rating work.  It compares:

* Expt2 combined raw fixed-point ratings
* fixed_v1 scaled fixed-point entrant ratings
* the v5 curated strictly monotone curve

Rows are restricted to the v5 curve domain, because v5 deliberately deletes
some rare or non-contemporary chii from the production-facing scale.  The CSV
therefore answers: "on the chii that v5 still represents, how far did each
successive transformation move the rating?"

Large differences are expected at masked/interpolated points.  In particular,
this report is intended to make those deliberate edits visible rather than hide
them inside the fitted curve.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from src.analysis.probability.builder import load_ratings_csv
from src.sumo_core.Chii import Chii

from .api import load_entrant_initial_ratings
from .initial_rating import InitialRatingCurve
from .model import FIXED_POINT_SOURCE, OUTPUT_ROOT


DEFAULT_OUTPUT_PATH = OUTPUT_ROOT / "comparisons" / "initial_rating_comparison.csv"
IGNORED_CHII = ("Sd101e", "O3w", "S3e")
IGNORED_ORDINALS = {Chii.from_str(chii).ordinal() for chii in IGNORED_CHII}


@dataclass(frozen=True)
class ComparisonRow:
    index: int
    ordinal: int
    chii: str
    expt2_raw: float
    fixed_v1_scaled: float
    v5_monotone: float
    fixed_minus_raw: float
    v5_minus_scaled: float
    v5_minus_raw: float


def build_comparison_rows(
    *,
    expt2_path: Path = FIXED_POINT_SOURCE,
    output_root: Path = OUTPUT_ROOT,
) -> list[ComparisonRow]:
    """Build comparison rows on the shared v5 curve domain."""

    expt2_raw = {
        chii.ordinal(): rating
        for chii, rating in load_ratings_csv(expt2_path).items()
    }
    fixed_scaled = {
        int(ordinal): float(rating)
        for ordinal, rating in load_entrant_initial_ratings(output_root=output_root).items()
    }
    v5 = InitialRatingCurve.v5(output_root=output_root)

    rows: list[ComparisonRow] = []
    for index, ordinal in enumerate(v5.ordinals):
        if ordinal in IGNORED_ORDINALS:
            continue

        raw = expt2_raw[ordinal]
        scaled = fixed_scaled[ordinal]
        fitted = v5.ratings[index]
        rows.append(
            ComparisonRow(
                index=index,
                ordinal=ordinal,
                chii=str(Chii.from_ordinal(ordinal)),
                expt2_raw=raw,
                fixed_v1_scaled=scaled,
                v5_monotone=fitted,
                fixed_minus_raw=scaled - raw,
                v5_minus_scaled=fitted - scaled,
                v5_minus_raw=fitted - raw,
            )
        )

    return rows


def write_comparison_csv(rows: list[ComparisonRow], output_path: Path) -> Path:
    """Write comparison rows to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "index",
                "ordinal",
                "chii",
                "expt2_raw",
                "fixed_v1_scaled",
                "v5_monotone",
                "fixed_minus_raw",
                "v5_minus_scaled",
                "v5_minus_raw",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.index,
                    row.ordinal,
                    row.chii,
                    row.expt2_raw,
                    row.fixed_v1_scaled,
                    row.v5_monotone,
                    row.fixed_minus_raw,
                    row.v5_minus_scaled,
                    row.v5_minus_raw,
                ]
            )

    return output_path


def summarise(rows: list[ComparisonRow]) -> list[str]:
    """Return a concise text summary of comparison magnitudes."""

    if not rows:
        return ["No rows to compare."]

    lines = [f"Rows compared: {len(rows)}"]
    for label, values in [
        ("fixed_v1_scaled - expt2_raw", [row.fixed_minus_raw for row in rows]),
        ("v5_monotone - fixed_v1_scaled", [row.v5_minus_scaled for row in rows]),
        ("v5_monotone - expt2_raw", [row.v5_minus_raw for row in rows]),
    ]:
        lines.extend(summary_lines(label, values))

    lines.append("")
    lines.append("Largest |v5_monotone - fixed_v1_scaled|:")
    for row in sorted(rows, key=lambda r: abs(r.v5_minus_scaled), reverse=True)[:12]:
        lines.append(
            f"  {row.index:>3} {row.chii:<7} "
            f"scaled={row.fixed_v1_scaled:9.3f} "
            f"v5={row.v5_monotone:9.3f} "
            f"diff={row.v5_minus_scaled:9.3f}"
        )

    return lines


def summary_lines(label: str, values: list[float]) -> list[str]:
    """Return summary lines for a difference vector."""

    n = len(values)
    mean = sum(values) / n
    mae = sum(abs(value) for value in values) / n
    rmse = (sum(value * value for value in values) / n) ** 0.5
    max_abs = max(abs(value) for value in values)
    return [
        "",
        label,
        f"  mean:    {mean: .6f}",
        f"  mean abs:{mae: .6f}",
        f"  RMSE:    {rmse: .6f}",
        f"  max abs: {max_abs: .6f}",
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare Expt2 raw, fixed v1 scaled, and v5 monotone initial ratings."
    )
    parser.add_argument(
        "--expt2",
        type=Path,
        default=FIXED_POINT_SOURCE,
        help="Expt2 final ratings CSV.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory containing fixed v1 artefacts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Comparison CSV output path.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_comparison_rows(expt2_path=args.expt2, output_root=args.output_root)
    written = write_comparison_csv(rows, args.output)
    print(f"Rating comparisons (ignoring {', '.join(IGNORED_CHII)})")
    print(f"Comparison CSV: {written}")
    for line in summarise(rows):
        print(line)


if __name__ == "__main__":
    main()
