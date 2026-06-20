"""Master chii initial-rating map IO and conversion helpers."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Protocol
from src.sumo_core.Chii import Chii

from .model import policy_metadata


@dataclass(frozen=True)
class MasterChiiInitialRatingRow:
    chii: str
    chii_ordinal: int
    initial_rating: str
    source_kind: str
    source_chii: str
    source_chii_ordinal: int
    source_rating: str


class CompletedInitialRatingLike(Protocol):
    chii: Chii
    initial_rating: float
    source_chii: Chii
    source_rating: float
    source_kind: str


def rows_from_completed(
    rows: Iterable[CompletedInitialRatingLike],
) -> tuple[MasterChiiInitialRatingRow, ...]:
    """Convert completion rows to the production master-map row shape."""

    return tuple(
        MasterChiiInitialRatingRow(
            chii=str(row.chii),
            chii_ordinal=row.chii.ordinal(),
            initial_rating=f"{row.initial_rating:.12f}",
            source_kind=row.source_kind,
            source_chii=str(row.source_chii),
            source_chii_ordinal=row.source_chii.ordinal(),
            source_rating=f"{row.source_rating:.12f}",
        )
        for row in rows
    )


def write_master_chii_initial_rating_map(
    path: Path,
    rows: Iterable[MasterChiiInitialRatingRow],
) -> Path:
    """Write the master chii initial-rating map CSV."""

    materialised = tuple(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=tuple(MasterChiiInitialRatingRow.__dataclass_fields__),
        )
        writer.writeheader()
        for row in materialised:
            writer.writerow(asdict(row))
    return path


def write_master_map_metadata(
    path: Path,
    *,
    master_map_path: Path,
    source_csv: Path,
    direct_count: int,
    nearest_supported_count: int,
    required_chii_count: int,
) -> Path:
    """Write metadata for the master chii initial-rating map."""

    payload = {
        "kind": "master_chii_initial_rating_map",
        "generated_at": datetime.now().astimezone().isoformat(),
        "master_map_path": str(master_map_path),
        "source_csv": str(source_csv),
        "required_chii_count": required_chii_count,
        "direct_count": direct_count,
        "nearest_supported_count": nearest_supported_count,
        "policy": policy_metadata(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_master_chii_initial_rating_map(
    path: Path,
) -> tuple[MasterChiiInitialRatingRow, ...]:
    """Load the master chii initial-rating map CSV."""

    with path.open("r", newline="", encoding="utf-8") as f:
        return tuple(
            MasterChiiInitialRatingRow(
                chii=row["chii"],
                chii_ordinal=int(row["chii_ordinal"]),
                initial_rating=row["initial_rating"],
                source_kind=row["source_kind"],
                source_chii=row["source_chii"],
                source_chii_ordinal=int(row["source_chii_ordinal"]),
                source_rating=row["source_rating"],
            )
            for row in csv.DictReader(f)
        )


def ratings_by_chii(rows: Iterable[MasterChiiInitialRatingRow]) -> dict[Chii, float]:
    """Return the simulator-facing chii-to-initial-rating map."""

    return {
        Chii.from_str(row.chii): float(row.initial_rating)
        for row in rows
    }
