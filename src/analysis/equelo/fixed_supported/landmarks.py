"""Public-facing fixed-supported Equelo landmark ratings."""

from __future__ import annotations

import argparse
import csv
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
from src.sumo_core.Chii import Chii

from .build import ChiiRatings
from .model import LANDMARKS_OUTPUT_DIR, MODEL_VERSION, OUTPUT_ROOT
from .api import master_chii_initial_rating_map_path


def fixed_supported_initial_rating_curve(
    *,
    source: Path | None = None,
) -> InitialRatingCurve:
    """Build the public curve from fixed-supported chii initial ratings."""

    ratings = load_initial_rating_rows(
        master_chii_initial_rating_map_path(OUTPUT_ROOT) if source is None else source
    )
    return InitialRatingCurve.from_ordinal_ratings({
        chii.ordinal(): float(rating)
        for chii, rating in ratings.items()
    })


def load_initial_rating_rows(path: Path) -> ChiiRatings:
    """Load chii ratings from fixed-point or master-map CSVs."""

    ratings: ChiiRatings = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rating_text = row.get("rating", "") or row["initial_rating"]
            ratings[Chii.from_str(row["chii"])] = float(rating_text)
    return ratings


def build_typical_equelo_values(
    *,
    output_dir: Path = LANDMARKS_OUTPUT_DIR,
    master_map_path: Path | None = None,
) -> V5LandmarkOutputs:
    """Build Typical Equelo Values from the fixed-supported master map."""

    return write_typical_equelo_outputs(
        output_dir=output_dir,
        source=master_map_path,
    )


def write_typical_equelo_outputs(
    *,
    output_dir: Path = LANDMARKS_OUTPUT_DIR,
    source: Path | None = None,
) -> V5LandmarkOutputs:
    """Write fixed-supported curated landmark CSV and site metadata."""

    output_dir.mkdir(parents=True, exist_ok=True)
    curve = fixed_supported_initial_rating_curve(source=source)
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
    source_path = master_chii_initial_rating_map_path(OUTPUT_ROOT) if source is None else source
    _write_metadata(outputs.metadata_json, rows=rows, source=source_path, domain_count=len(curve.ordinals))
    _write_metadata(outputs.site_metadata_json, rows=rows, source=source_path, domain_count=len(curve.ordinals))
    return outputs


def _write_metadata(
    output_path: Path,
    *,
    rows: tuple[TypicalEqueloRow, ...],
    source: Path,
    domain_count: int,
) -> None:
    payload = {
        "title": "Typical Equelo Ratings",
        "model_version": MODEL_VERSION,
        "row_count": len(rows),
        "source": str(source),
        "rating_source": (
            "InitialRatingCurve.from_ordinal_ratings(master chii initial-rating "
            "map) monotone fit"
        ),
        "domain_count": domain_count,
        "rating_policy": (
            "Chii-like labels are represented internally as typed ChiiLabel "
            "values. Each label is resolved to real side-bearing Chii support "
            "before fixed-supported landmark ratings are looked up. These are "
            "public interpretive landmarks, not the raw operational simulation "
            "state."
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
        description="Write fixed-supported curated public typical Equelo ratings."
    )
    parser.add_argument("--output-dir", type=Path, default=LANDMARKS_OUTPUT_DIR)
    parser.add_argument("--source", type=Path, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = write_typical_equelo_outputs(
        output_dir=args.output_dir,
        source=args.source,
    )
    print("fixed-supported typical Equelo ratings generated")
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
    "fixed_supported_initial_rating_curve",
    "v5_landmark_for",
    "write_typical_equelo_outputs",
]


if __name__ == "__main__":
    main()
