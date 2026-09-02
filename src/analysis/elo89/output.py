"""Stable production artifacts for Elo-89."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from src.analysis.elo_model_selection.model import AdoptedPrior

from .model import Elo89Run


@dataclass(frozen=True, kw_only=True)
class Elo89OutputPaths:
    root: Path
    manifest: Path
    prior: Path
    basho_start_ratings: Path
    day_end_ratings: Path
    basho_end_ratings: Path
    bout_ledger: Path
    basho_adjustments: Path


def write_elo89_outputs(
    *,
    run: Elo89Run,
    prior: AdoptedPrior,
    output_root: Path,
    history_source: str,
    start_date,
    end_date,
    k_config_path: Path,
    q: float,
) -> Elo89OutputPaths:
    """Write one complete, deterministic Elo-89 production run."""

    output_root.mkdir(parents=True, exist_ok=True)
    paths = Elo89OutputPaths(
        root=output_root,
        manifest=output_root / "manifest.json",
        prior=output_root / "prior.csv",
        basho_start_ratings=output_root / "basho_start_ratings.json",
        day_end_ratings=output_root / "day_end_ratings.json",
        basho_end_ratings=output_root / "basho_end_ratings.json",
        bout_ledger=output_root / "bout_ledger.csv",
        basho_adjustments=output_root / "basho_adjustments.csv",
    )
    _write_prior(paths.prior, prior)
    _write_json(paths.basho_start_ratings, _ratings_by_date(run.basho_start_ratings))
    _write_json(paths.day_end_ratings, _daily_ratings(run.day_end_ratings))
    _write_json(paths.basho_end_ratings, _ratings_by_date(run.basho_end_ratings))
    _write_rows(paths.bout_ledger, (_forecast_row(row) for row in run.forecasts))
    _write_rows(
        paths.basho_adjustments,
        (
            {**asdict(row), "date": str(row.date)}
            for row in run.adjustments
        ),
    )
    paths.manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "model_id": "elo-89",
                "history": {
                    "source": history_source,
                    "start": str(start_date),
                    "end": str(end_date),
                },
                "prior": {
                    "source": prior.source_path,
                    "copied_to": paths.prior.name,
                    "pair_count": len(prior.rating_by_pair),
                    "fallback_rating": prior.fallback_rating,
                },
                "q": q,
                "k_config": str(k_config_path),
                "target_mean": run.target_mean,
                "selection": {
                    "raw_result_count": run.raw_result_count,
                    "rated_bout_count": run.rated_bout_count,
                    "excluded_fusen_count": run.excluded_fusen_count,
                    "excluded_draw_count": run.excluded_draw_count,
                },
                "files": {
                    "prior": paths.prior.name,
                    "basho_start_ratings": paths.basho_start_ratings.name,
                    "day_end_ratings": paths.day_end_ratings.name,
                    "basho_end_ratings": paths.basho_end_ratings.name,
                    "bout_ledger": paths.bout_ledger.name,
                    "basho_adjustments": paths.basho_adjustments.name,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return paths


def _write_prior(path: Path, prior: AdoptedPrior) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("rank_pair", "rating"))
        writer.writeheader()
        for rank_pair, rating in sorted(prior.rating_by_pair.items()):
            writer.writerow({"rank_pair": rank_pair, "rating": _number(rating)})


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _ratings_by_date(values) -> dict[str, dict[str, float]]:
    return {
        str(date): {str(int(rikishi)): rating for rikishi, rating in ratings.items()}
        for date, ratings in sorted(values.items())
    }


def _daily_ratings(values) -> dict[str, dict[str, dict[str, float]]]:
    return {
        str(date): {
            str(int(day)): {
                str(int(rikishi)): rating for rikishi, rating in ratings.items()
            }
            for day, ratings in sorted(days.items())
        }
        for date, days in sorted(values.items())
    }


def _forecast_row(row) -> dict[str, object]:
    return {
        **asdict(row),
        "date": str(row.date),
        "day": int(row.day),
        "rikishi_a": int(row.rikishi_a),
        "rikishi_b": int(row.rikishi_b),
        "chii_a": "" if row.chii_a is None else str(row.chii_a),
        "chii_b": "" if row.chii_b is None else str(row.chii_b),
    }


def _write_rows(path: Path, rows) -> None:
    materialised = list(rows)
    if not materialised:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(materialised[0]))
        writer.writeheader()
        writer.writerows(materialised)


def _number(value: float) -> str:
    return f"{value:.12f}"
