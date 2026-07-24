"""Initial-rating and k-value policies for clean Elo."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from src.sumo_core.BasicEnums import Annotation
from src.sumo_core.Chii import Chii

from .config import DEFAULT_ELO, DEFAULT_FIDE_K_CONFIG_PATH


class InitialRatingPolicy(Protocol):
    """Resolve a first rating from the rikishi's current rank."""

    def rating_for(self, chii: Chii | None) -> float: ...

    def metadata(self) -> dict[str, object]: ...


class KPolicy(Protocol):
    """Resolve the k value used to update a rikishi at the current rank."""

    def k_for(self, chii: Chii | None) -> float: ...

    def metadata(self) -> dict[str, object]: ...


@dataclass(frozen=True)
class ConstantInitialRatingPolicy:
    value: float = DEFAULT_ELO

    def rating_for(self, chii: Chii | None) -> float:
        del chii
        return float(self.value)

    def metadata(self) -> dict[str, object]:
        return {"kind": "constant", "value": float(self.value)}


@dataclass(frozen=True)
class FileInitialRatingPolicy:
    """Rank-to-rating policy loaded from a CSV or JSON file."""

    path: Path
    ratings: dict[Chii, float]

    @classmethod
    def load(cls, path: Path) -> "FileInitialRatingPolicy":
        resolved = Path(path)
        if resolved.suffix.lower() == ".json":
            ratings = _load_initial_ratings_json(resolved)
        else:
            ratings = _load_initial_ratings_csv(resolved)
        if not ratings:
            raise ValueError(f"Initial-rating file contains no ratings: {resolved}")
        return cls(path=resolved, ratings=ratings)

    def rating_for(self, chii: Chii | None) -> float:
        if chii is None:
            raise KeyError(
                "Cannot use a rank-based initial-rating file for an unranked "
                f"entrant; no chii is available in {self.path}"
            )
        rating = self.ratings.get(chii)
        if rating is None:
            rating = self.ratings.get(_without_annotation(chii))
        if rating is None:
            raise KeyError(
                f"No initial rating for chii {chii} (ordinal {chii.ordinal()}) "
                f"in {self.path}"
            )
        return float(rating)

    def metadata(self) -> dict[str, object]:
        return {
            "kind": "file",
            "path": str(self.path),
            "rating_count": len(self.ratings),
        }


@dataclass(frozen=True)
class ConstantKPolicy:
    value: float

    def k_for(self, chii: Chii | None) -> float:
        del chii
        return float(self.value)

    def metadata(self) -> dict[str, object]:
        return {"kind": "constant", "value": float(self.value)}


@dataclass(frozen=True)
class FideKPolicy:
    """Legacy FIDE-style divisional k policy used by Equelo."""

    path: Path
    k_by_division_index: dict[int, float]
    unranked_k: float

    @classmethod
    def load(
        cls,
        path: Path = DEFAULT_FIDE_K_CONFIG_PATH,
    ) -> "FideKPolicy":
        resolved = Path(path)
        with resolved.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        max_k = float(payload["max"])
        limits = {
            int(upper): float(value)
            for upper, value in payload.get("lims", {}).items()
        }

        k_by_division_index: dict[int, float] = {}
        last_upper = -1
        for upper, value in sorted(limits.items()):
            if upper < last_upper:
                raise ValueError(f"Invalid FIDE k limit ordering in {resolved}")
            for division_index in range(last_upper + 1, upper + 1):
                k_by_division_index[division_index] = value
            last_upper = upper

        for division_index in range(last_upper + 1, 10):
            k_by_division_index[division_index] = max_k

        return cls(
            path=resolved,
            k_by_division_index=k_by_division_index,
            unranked_k=max_k,
        )

    def k_for(self, chii: Chii | None) -> float:
        if chii is None:
            return self.unranked_k
        division_index = chii.ordinal() // 100000
        try:
            return float(self.k_by_division_index[division_index])
        except KeyError as exc:
            raise KeyError(
                f"No FIDE k value for division index {division_index} "
                f"(chii {chii}) in {self.path}"
            ) from exc

    def metadata(self) -> dict[str, object]:
        return {
            "kind": "fide",
            "path": str(self.path),
            "unranked_k": self.unranked_k,
            "k_by_division_index": {
                str(key): value
                for key, value in sorted(self.k_by_division_index.items())
            },
        }


def _load_initial_ratings_csv(path: Path) -> dict[Chii, float]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "chii" not in reader.fieldnames:
            raise ValueError(f"Initial-rating CSV must contain a 'chii' column: {path}")

        rating_column = _rating_column(reader.fieldnames, path)
        return {
            Chii.from_str(row["chii"]): float(row[rating_column])
            for row in reader
            if row.get("chii") and row.get(rating_column)
        }


def _load_initial_ratings_json(path: Path) -> dict[Chii, float]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Initial-rating JSON must be an object: {path}")
    return {
        _chii_from_file_key(str(chii)): float(rating)
        for chii, rating in payload.items()
    }


def _rating_column(fieldnames: list[str], path: Path) -> str:
    for candidate in ("initial_rating", "rating"):
        if candidate in fieldnames:
            return candidate
    raise ValueError(
        "Initial-rating CSV must contain 'initial_rating' or 'rating': "
        f"{path}"
    )


def _without_annotation(chii: Chii) -> Chii:
    return Chii(
        level=chii.level,
        number=chii.number,
        side=chii.side,
        ann=Annotation.EMPTY,
    )


def _chii_from_file_key(value: str) -> Chii:
    if value.isdecimal():
        return Chii.from_ordinal(int(value))
    return Chii.from_str(value)
