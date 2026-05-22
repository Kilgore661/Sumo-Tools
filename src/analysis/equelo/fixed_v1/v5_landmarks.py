"""Public-facing v5 Equelo landmark ratings.

This module is the policy boundary between chii-like public labels and real
``Chii`` objects.  Strings such as ``"S"`` and ``"M3"`` are accepted only as
input/output representations; internal rating logic uses ``ChiiLabel`` values
and resolves them to one or more real ``Chii`` instances before consulting the
v5 curve.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from src.sumo_core.BasicEnums import Annotation, Division, MSD, Side
from src.sumo_core.Chii import Chii, Level

from .initial_rating import InitialRatingCurve
from .model import OUTPUT_ROOT


DEFAULT_OUTPUT_DIR = OUTPUT_ROOT / "landmarks"
SITE_BUNDLE_DIR = "site/typical_equelo_values"
LANDMARKS_CSV = "typical_equelo_values.csv"
METADATA_JSON = "typical_equelo_values_metadata.json"
PAGE_JSON = "page.json"
SITE_METADATA_JSON = "metadata.json"
TYPICAL_EQUELO_VALUES_NOTE = (
    "<strong>Equelo Ratings.</strong> These are typical rating landmarks, not "
    "promises about every rikishi at a rank. Sideless labels such as M3 use "
    "the average of the east and west rank slots. See "
    '<a href="../../equelo-methodology/v5-landmark-policy/index.html">'
    "V5 Landmark Policy</a>."
)
JD100_NOTE = (
    "<strong>Why stop at Jd100?</strong> Below Jd100 the support is low and "
    "Jonokuchi has too much churn for Elo-like ratings such as Equelo to "
    "produce stable public landmarks. See "
    '<a href="../../equelo-methodology/lower-rank-rating-stability/index.html">'
    "Lower-Rank Rating Stability</a> for details."
)

SANYAKU_LEVELS = frozenset(
    {
        MSD.YOKOZUNA,
        MSD.OZEKI,
        MSD.SEKIWAKE,
        MSD.KOMUSUBI,
    }
)


class ChiiLabelKind(Enum):
    """Kinds of chii-like label understood by the v5 landmark policy."""

    EXACT = "exact"
    SIDELESS = "sideless"
    LEVEL = "level"


@dataclass(frozen=True)
class ChiiLabel:
    """Typed internal representation of a chii-like label."""

    kind: ChiiLabelKind
    level: Level | None = None
    number: int | None = None
    chii: Chii | None = None

    @classmethod
    def exact(cls, chii: Chii) -> "ChiiLabel":
        return cls(kind=ChiiLabelKind.EXACT, chii=chii)

    @classmethod
    def sideless(cls, level: Level, number: int) -> "ChiiLabel":
        if number <= 0:
            raise ValueError(f"ChiiLabel number must be positive, got {number}")
        return cls(kind=ChiiLabelKind.SIDELESS, level=level, number=number)

    @classmethod
    def from_level(cls, level: Level) -> "ChiiLabel":
        return cls(kind=ChiiLabelKind.LEVEL, level=level)

    def display(self) -> str:
        """Return the human-facing label text."""

        if self.kind == ChiiLabelKind.EXACT:
            if self.chii is None:
                raise ValueError("Exact ChiiLabel has no Chii")
            return str(self.chii)
        if self.level is None:
            raise ValueError(f"{self.kind.value} ChiiLabel has no level")
        if self.kind == ChiiLabelKind.LEVEL:
            return self.level.as_abbreviation()
        if self.kind == ChiiLabelKind.SIDELESS:
            if self.number is None:
                raise ValueError("Sideless ChiiLabel has no number")
            return f"{self.level.as_abbreviation()}{self.number}"
        raise ValueError(f"Unsupported ChiiLabel kind: {self.kind}")


@dataclass(frozen=True)
class V5Landmark:
    """Resolved v5 rating for one public chii-like label."""

    label: str
    label_kind: str
    rating: float
    support_count: int
    support_chii: str
    support_ratings: str
    policy: str


@dataclass(frozen=True)
class TypicalEqueloRow:
    """CSV row for the curated public table of typical Equelo values."""

    table: str
    table_order: int
    row_order: int
    label: str
    rating: float
    support_count: int
    support_chii: str
    policy: str


@dataclass(frozen=True)
class V5LandmarkOutputs:
    output_dir: Path
    bundle_dir: Path
    landmarks_csv: Path
    site_landmarks_csv: Path
    page_json: Path
    metadata_json: Path
    site_metadata_json: Path


def v5_landmark_for(
    label: ChiiLabel,
    *,
    curve: InitialRatingCurve | None = None,
) -> V5Landmark:
    """Resolve a typed label under the public v5 landmark policy."""

    curve = curve if curve is not None else InitialRatingCurve.v5()
    support = _support_chii_for_label(label)
    support_ratings = tuple((chii, curve.rating_for_chii(chii)) for chii in support)
    rating = sum(value for _, value in support_ratings) / len(support_ratings)
    return V5Landmark(
        label=label.display(),
        label_kind=label.kind.value,
        rating=rating,
        support_count=len(support_ratings),
        support_chii=";".join(str(chii) for chii, _ in support_ratings),
        support_ratings=";".join(
            f"{chii}:{value:.12g}" for chii, value in support_ratings
        ),
        policy=_policy_text(label),
    )


def build_typical_equelo_rows(
    *,
    curve: InitialRatingCurve | None = None,
) -> tuple[TypicalEqueloRow, ...]:
    """Return the curated table rows for the first public v5 landmark table."""

    curve = curve if curve is not None else InitialRatingCurve.v5()
    rows: list[TypicalEqueloRow] = []
    for table_order, (table, labels) in enumerate(_curated_labels(), start=1):
        for row_order, label in enumerate(labels, start=1):
            landmark = v5_landmark_for(label, curve=curve)
            rows.append(
                TypicalEqueloRow(
                    table=table,
                    table_order=table_order,
                    row_order=row_order,
                    label=landmark.label,
                    rating=round(landmark.rating),
                    support_count=landmark.support_count,
                    support_chii=landmark.support_chii,
                    policy=landmark.policy,
                )
            )
    return tuple(rows)


def write_typical_equelo_outputs(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fixed_v1_output_root: Path = OUTPUT_ROOT,
) -> V5LandmarkOutputs:
    """Write the curated v5 landmark CSV and metadata."""

    output_dir.mkdir(parents=True, exist_ok=True)
    curve = InitialRatingCurve.v5(output_root=fixed_v1_output_root)
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
        fixed_v1_output_root=fixed_v1_output_root,
        v5_domain_count=len(curve.ordinals),
    )
    _write_metadata(
        output_path=outputs.site_metadata_json,
        rows=rows,
        fixed_v1_output_root=fixed_v1_output_root,
        v5_domain_count=len(curve.ordinals),
    )
    return outputs


def _support_chii_for_label(label: ChiiLabel) -> tuple[Chii, ...]:
    if label.kind == ChiiLabelKind.EXACT:
        if label.chii is None:
            raise ValueError("Exact ChiiLabel has no Chii")
        return (_canonical_v5_chii(label.chii),)

    if label.level is None:
        raise ValueError(f"{label.kind.value} ChiiLabel has no level")

    if label.kind == ChiiLabelKind.LEVEL:
        return _support_for_level_label(label.level)

    if label.kind == ChiiLabelKind.SIDELESS:
        if label.number is None:
            raise ValueError("Sideless ChiiLabel has no number")
        return tuple(
            _canonical_v5_chii(
                Chii(
                    level=label.level,
                    number=label.number,
                    side=side,
                    ann=Annotation.EMPTY,
                )
            )
            for side in (Side.EAST, Side.WEST)
        )

    raise ValueError(f"Unsupported ChiiLabel kind: {label.kind}")


def _support_for_level_label(level: Level) -> tuple[Chii, ...]:
    if level not in SANYAKU_LEVELS:
        raise ValueError(
            f"Level-only v5 landmark policy is not defined for {level.as_abbreviation()}"
        )
    return tuple(
        Chii(level=level, number=1, side=side, ann=Annotation.EMPTY)
        for side in (Side.EAST, Side.WEST)
    )


def _canonical_v5_chii(chii: Chii) -> Chii:
    if chii.side == Side.NONE:
        raise ValueError(f"Exact v5 lookup requires a side-bearing Chii: {chii}")
    number = 1 if chii.level in SANYAKU_LEVELS else chii.number
    return Chii(
        level=chii.level,
        number=number,
        side=chii.side,
        ann=Annotation.EMPTY,
    )


def _policy_text(label: ChiiLabel) -> str:
    if label.kind == ChiiLabelKind.EXACT:
        return "annotation stripped; numbered sanyaku canonicalised to rank 1"
    if label.kind == ChiiLabelKind.LEVEL:
        return "level label; canonical rank 1 east/west support averaged"
    if label.kind == ChiiLabelKind.SIDELESS:
        if label.level in SANYAKU_LEVELS:
            return "sideless numbered sanyaku label; canonical rank 1 east/west support averaged"
        return "sideless numbered label; east/west support averaged"
    raise ValueError(f"Unsupported ChiiLabel kind: {label.kind}")


def _curated_labels() -> tuple[tuple[str, tuple[ChiiLabel, ...]], ...]:
    return (
        (
            "Sanyaku",
            (
                ChiiLabel.from_level(Level(MSD.YOKOZUNA)),
                ChiiLabel.from_level(Level(MSD.OZEKI)),
                ChiiLabel.from_level(Level(MSD.SEKIWAKE)),
                ChiiLabel.from_level(Level(MSD.KOMUSUBI)),
            ),
        ),
        (
            "Maegashira",
            tuple(
                ChiiLabel.sideless(Level(MSD.MAEGASHIRA), number)
                for number in range(1, 18)
            ),
        ),
        (
            "Other",
            (
                ChiiLabel.sideless(Level(Division.JURYO), 1),
                ChiiLabel.sideless(Level(Division.MAKUSHITA), 1),
                ChiiLabel.sideless(Level(Division.SANDANME), 1),
                ChiiLabel.sideless(Level(Division.JONIDAN), 1),
                ChiiLabel.sideless(Level(Division.JONIDAN), 100),
            ),
        ),
    )


def _write_dataclass_csv(rows: Iterable[object], output_path: Path) -> None:
    rows = tuple(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tuple(rows[0].__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _write_metadata(
    *,
    output_path: Path,
    rows: tuple[TypicalEqueloRow, ...],
    fixed_v1_output_root: Path,
    v5_domain_count: int,
) -> None:
    payload = {
        "title": "Typical Equelo Ratings",
        "row_count": len(rows),
        "fixed_v1_output_root": str(fixed_v1_output_root),
        "fixed_v1_rating_source": "InitialRatingCurve.v5 monotone fit",
        "v5_domain_count": v5_domain_count,
        "rating_policy": (
            "Chii-like labels are represented internally as typed ChiiLabel "
            "values. Each label is resolved to real side-bearing Chii support "
            "before v5 ratings are looked up."
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


def _write_page_json(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": "typical_equelo_values",
        "title": "Typical Equelo Ratings",
        "layout": "three_tables",
        "data_sources": [
            {
                "id": "typical_equelo_values",
                "label": "Typical Equelo Ratings",
                "data": LANDMARKS_CSV,
                "kind": "table",
            }
        ],
        "tables": [
            {"id": "sanyaku", "label": "Sanyaku", "source_value": "Sanyaku"},
            {
                "id": "maegashira",
                "label": "Maegashira",
                "source_value": "Maegashira",
            },
            {"id": "other", "label": "Other", "source_value": "Other"},
        ],
        "columns": [
            {"id": "label", "label": "Rank"},
            {"id": "rating", "label": "Equelo"},
        ],
        "notes": [
            {
                "id": "typical_equelo_values",
                "placement": "below_table",
                "format": "html",
                "note_for": "all",
                "notes": TYPICAL_EQUELO_VALUES_NOTE,
            },
            {
                "id": "jd100",
                "placement": "below_table",
                "format": "html",
                "note_for": "all",
                "notes": JD100_NOTE,
            },
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write the curated public table of typical Equelo ratings."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to receive typical Equelo value outputs.",
    )
    parser.add_argument(
        "--fixed-v1-output-root",
        type=Path,
        default=OUTPUT_ROOT,
        help="Directory containing fixed_v1 entrant_initial_ratings.json.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = write_typical_equelo_outputs(
        output_dir=args.output_dir,
        fixed_v1_output_root=args.fixed_v1_output_root,
    )
    print("Typical Equelo ratings generated")
    print(f"CSV: {outputs.landmarks_csv}")
    print(f"Site bundle: {outputs.bundle_dir}")
    print(f"Metadata: {outputs.metadata_json}")


if __name__ == "__main__":
    main()
