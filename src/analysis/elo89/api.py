"""Read-only access to one published Elo-89 run."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class Elo89Artifacts:
    root: Path
    manifest: dict[str, object]
    prior: dict[str, float]
    basho_start_ratings: dict[str, dict[str, float]]
    day_end_ratings: dict[str, dict[str, dict[str, float]]]
    basho_end_ratings: dict[str, dict[str, float]]
    bout_ledger: tuple[dict[str, str], ...]

    @classmethod
    def load(cls, root: Path) -> "Elo89Artifacts":
        root = Path(root)
        manifest = _json(root / "manifest.json")
        if manifest.get("model_id") != "elo-89":
            raise ValueError(f"Not an Elo-89 artifact set: {root}")
        files = manifest.get("files")
        if not isinstance(files, dict):
            raise ValueError("Elo-89 manifest has no files object")
        with (root / _file(files, "prior")).open(
            newline="", encoding="utf-8"
        ) as stream:
            prior = {
                row["rank_pair"]: float(row["rating"])
                for row in csv.DictReader(stream)
            }
        with (root / _file(files, "bout_ledger")).open(
            newline="", encoding="utf-8"
        ) as stream:
            bout_ledger = tuple(csv.DictReader(stream))
        return cls(
            root=root,
            manifest=manifest,
            prior=prior,
            basho_start_ratings=_json(root / _file(files, "basho_start_ratings")),
            day_end_ratings=_json(root / _file(files, "day_end_ratings")),
            basho_end_ratings=_json(root / _file(files, "basho_end_ratings")),
            bout_ledger=bout_ledger,
        )

    def start_rating(self, date, rikishi) -> float | None:
        return _lookup(self.basho_start_ratings, date, rikishi)

    def end_rating(self, date, rikishi) -> float | None:
        return _lookup(self.basho_end_ratings, date, rikishi)

    def day_end_rating(self, date, day, rikishi) -> float | None:
        date_values = self.day_end_ratings.get(str(date), {})
        return _lookup(date_values, int(day), rikishi)


def _json(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Elo-89 artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _file(files: dict, key: str) -> str:
    value = files.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Elo-89 manifest has no file named {key!r}")
    return value


def _lookup(values: dict, date, rikishi) -> float | None:
    raw = values.get(str(date), {}).get(str(int(rikishi)))
    return None if raw is None else float(raw)
