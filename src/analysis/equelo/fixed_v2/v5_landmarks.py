"""Public-facing fixed_v2 Equelo landmark ratings.

This module mirrors the fixed_v1 site-facing landmark writer, but builds the
public curve from the raw Expt2 fixed-point ratings rather than the fixed_v1
Brier-compressed entrant ratings.

The intent is to let products/make_site consume the Brierless Pivot outputs
without changing the site-building API.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.analysis.equelo.fixed_v1.initial_rating import InitialRatingCurve
from src.analysis.equelo.fixed_v1.v5_landmarks import (
    LANDMARKS_CSV,
    METADATA_JSON,
    PAGE_JSON,
    SITE_BUNDLE_DIR,
    SITE_METADATA_JSON,
    ChiiLabel,
    ChiiLabelKind,
    TypicalEqueloRow,
    V5Landmark,
    V5LandmarkOutputs,
    build_typical_equelo_rows,
    v5_landmark_for,
    _curated_labels,
    _write_dataclass_csv,
    _write_page_json,
)
from src.analysis.probability.builder import load_ratings_csv

from .build import to_ordinal_ratings
from .model import FP_SOURCE, MODEL_VERSION, OUTPUT_ROOT


DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "landmarks"


def fixed_v2_initial_rating_curve(
    *,
    fp_source: Path = FP_SOURCE,
) -> InitialRatingCurve:
    """Build the fixed_v2 public curve from raw Expt2 fixed-point ratings."""

    fp_by_chii = load_ratings_csv(fp_source)
    fp_by_ordinal = to_ordinal_ratings(fp_by_chii)
    return InitialRatingCurve.from_ordinal_ratings(fp_by_ordinal)


def write_typical_equelo_outputs(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fp_source: Path = FP_SOURCE,
) -> V5LandmarkOutputs:
    """Write fixed_v2 curated landmark CSV and site metadata.

    The returned object intentionally has the same shape as fixed_v1's
    ``write_typical_equelo_outputs`` return value so make_site can switch
    versions by changing imports only.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    curve = fixed_v2_initial_rating_curve(fp_source=fp_source)
    rows = build_typical_equelo_rows(curve=curve)
    outputs = V5LandmarkOutputs(
        output_dir=output_dir,
        bundle_dir=output_dir / SITE_BUNDLE_DIR,
        landmarks_csv=output_dir / LANDMARKS_CSV,
        site_landmarks_csv=output_dir / SITE_BUNDLE_DIR / LANDMARKS_CSV,
        page_json=output_dir / SITE_BUNDLE_DIR / PAGE_JSON,
        metadata_json=output_dir / METADATA_JSON,
        site_metadata_json=output_dir / SITE_BUNDLE_DIR / SITE_METADATA_JSON,
    )
    _write_dataclass_csv(rows, outputs.landmarks_csv)
    _write_dataclass_csv(rows, outputs.site_landmarks_csv)
    _write_page_json(outputs.page_json)
    _write_metadata(
        output_path=outputs.metadata_json,
        rows=rows,
        fp_source=fp_source,
        v5_domain_count=len(curve.ordinals),
    )
    _write_metadata(
        output_path=outputs.site_metadata_json,
        rows=rows,
        fp_source=fp_source,
        v5_domain_count=len(curve.ordinals),
    )
    return outputs


def _write_metadata(
    *,
    output_path: Path,
    rows: tuple[TypicalEqueloRow, ...],
    fp_source: Path,
    v5_domain_count: int,
) -> None:
    payload = {
        "title": "Typical Equelo Ratings",
        "model_version": MODEL_VERSION,
        "row_count": len(rows),
        "fp_source": str(fp_source),
        "rating_source": (
            "InitialRatingCurve.from_ordinal_ratings(FP) monotone fit; "
            "Brier compression is not applied"
        ),
        "v5_domain_count": v5_domain_count,
        "rating_policy": (
            "Chii-like labels are represented internally as typed ChiiLabel "
            "values. Each label is resolved to real side-bearing Chii support "
            "before fixed_v2 v5-style ratings are looked up. These are public "
            "interpretive landmarks, not the raw operational simulation state."
        ),
        "tables": [
            {
                "name": table,
                "row_count": sum(1 for row in rows if row.table == table),
            }
            for table, _ in _curated_labels()
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write fixed_v2 curated public typical Equelo ratings."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to receive typical Equelo value outputs.",
    )
    parser.add_argument(
        "--fp-source",
        type=Path,
        default=FP_SOURCE,
        help="Path to the Expt2 fixed-point CSV.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = write_typical_equelo_outputs(
        output_dir=args.output_dir,
        fp_source=args.fp_source,
    )
    print("fixed_v2 typical Equelo ratings generated")
    print(f"CSV: {outputs.landmarks_csv}")
    print(f"Site bundle: {outputs.bundle_dir}")
    print(f"Metadata: {outputs.metadata_json}")


__all__ = [
    "ChiiLabel",
    "ChiiLabelKind",
    "TypicalEqueloRow",
    "V5Landmark",
    "V5LandmarkOutputs",
    "build_typical_equelo_rows",
    "fixed_v2_initial_rating_curve",
    "v5_landmark_for",
    "write_typical_equelo_outputs",
]


if __name__ == "__main__":
    main()
