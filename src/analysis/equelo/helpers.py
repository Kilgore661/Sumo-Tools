import csv
import gzip
import pickle
from pathlib import Path
from typing import TypeAlias

from src.sumo_core.Chii import Chii
from src.analysis.equelo.config_main import EQUELO_RATINGS, OUTPUT_ROOT

from .classes import Ratings


EqueloRatings: TypeAlias = dict[Chii, float]

RATINGS_ZIP = OUTPUT_ROOT / "equelo.zip"


def load_equelo(path: str | Path | None = None) -> EqueloRatings:
    """
    Load the Equelo ratings CSV into memory as:

        dict[Chii, float]

    The CSV is expected to have columns:

        chii,ordinal,rating

    We key the mapping by Chii reconstructed from the authoritative ordinal.
    As a sanity check, if the textual chii column is present, it must agree
    with the ordinal-derived Chii.
    """
    csv_path = Path(path) if path is not None else Path(EQUELO_RATINGS)

    if not csv_path.exists():
        raise FileNotFoundError(f"Equelo ratings file not found: {csv_path}")

    ratings: EqueloRatings = {}

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        expected = {"chii", "ordinal", "rating"}
        if reader.fieldnames is None:
            raise ValueError(f"Equelo ratings CSV has no header: {csv_path}")

        missing = expected - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Equelo ratings CSV missing required columns {sorted(missing)}: {csv_path}"
            )

        for row_num, row in enumerate(reader, start=2):
            try:
                ordinal = int(row["ordinal"])
                rating = float(row["rating"])
                chii = Chii.from_ordinal(ordinal)

                chii_text = row["chii"].strip()
                if chii_text and str(chii) != chii_text:
                    raise ValueError(
                        f"row {row_num}: chii/ordinal mismatch "
                        f"(csv chii={chii_text!r}, ordinal={ordinal}, decoded={str(chii)!r})"
                    )

                if chii in ratings:
                    raise ValueError(f"row {row_num}: duplicate chii {chii}")

                ratings[chii] = rating

            except Exception as e:
                raise ValueError(
                    f"Failed to parse Equelo ratings row {row_num} in {csv_path}: {row}"
                ) from e

    return ratings


def load_ratings() -> Ratings:
    if not RATINGS_ZIP.exists():
        raise RuntimeError(f"Ratings zip not found: {RATINGS_ZIP}")
    with gzip.open(RATINGS_ZIP, "rb") as f:
        return pickle.load(f)
