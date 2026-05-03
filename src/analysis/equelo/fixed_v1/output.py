"""Persistence helpers for fixed v1 Equelo ratings."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.analysis.equelo.expt1.simulate import RatingsByDate
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .model import (
    DAY_END_RATINGS_FILE_NAME,
    ENTRANT_INITIAL_RATINGS_FILE_NAME,
    METADATA_FILE_NAME,
    MODEL_VERSION,
    OUTPUT_ROOT,
    model_metadata,
)


def write_outputs(
    *,
    history: History,
    day_end_ratings: RatingsByDate,
    entrant_initial_ratings: dict[Chii, float],
    output_root: Path = OUTPUT_ROOT,
) -> dict[str, Path]:
    """
    Write fixed v1 day-end ratings, entrant initial ratings, and metadata.

    Contract:
        history is the cleaned history used by the simulator.
        day_end_ratings is the simulator output for that same history.
        entrant_initial_ratings is the exact chii prior used by the simulator.
    """

    output_root.mkdir(parents=True, exist_ok=True)

    ratings_path = output_root / DAY_END_RATINGS_FILE_NAME
    entrant_path = output_root / ENTRANT_INITIAL_RATINGS_FILE_NAME
    metadata_path = output_root / METADATA_FILE_NAME

    ratings_payload = serialise_day_end_ratings(day_end_ratings)
    write_json(ratings_path, ratings_payload)

    entrant_payload = serialise_entrant_initial_ratings(entrant_initial_ratings)
    write_json(entrant_path, entrant_payload)

    metadata_payload = build_metadata(
        history=history,
        day_end_ratings=ratings_payload,
        entrant_initial_ratings=entrant_payload,
    )
    write_json(metadata_path, metadata_payload)

    return {
        "metadata": metadata_path,
        "day_end_ratings": ratings_path,
        "entrant_initial_ratings": entrant_path,
    }


def serialise_day_end_ratings(day_end_ratings: RatingsByDate) -> dict[str, dict[str, dict[str, float]]]:
    """Convert simulator day-end ratings to JSON-serialisable nested dicts."""

    payload: dict[str, dict[str, dict[str, float]]] = {}

    for date in sorted(day_end_ratings.keys()):
        date_key = str(date)
        payload[date_key] = {}

        for day in sorted(day_end_ratings[date].keys()):
            day_key = str(int(day))
            payload[date_key][day_key] = {
                str(int(rikishi_id)): rating
                for rikishi_id, rating in sorted(
                    day_end_ratings[date][day].items(),
                    key=lambda item: int(item[0]),
                )
            }

    return payload


def serialise_entrant_initial_ratings(
    entrant_initial_ratings: dict[Chii, float],
) -> dict[str, float]:
    """Convert the fixed v1 entrant prior to an ordinal-keyed JSON payload."""

    payload: dict[str, float] = {}

    for chii, rating in sorted(
        entrant_initial_ratings.items(),
        key=lambda item: item[0].ordinal(),
    ):
        payload[str(chii.ordinal())] = rating

    return payload


def build_metadata(
    *,
    history: History,
    day_end_ratings: dict[str, dict[str, dict[str, float]]],
    entrant_initial_ratings: dict[str, float],
) -> dict[str, object]:
    """Build metadata for a fixed v1 output set."""

    dates = sorted(history.keys())
    rating_points = sum(len(days) for days in day_end_ratings.values())
    rating_count = sum(
        len(ratings)
        for days in day_end_ratings.values()
        for ratings in days.values()
    )

    return {
        "model_version": MODEL_VERSION,
        "generated_at": datetime.now().astimezone().isoformat(),
        "history_min_date": str(dates[0]),
        "history_max_date": str(dates[-1]),
        "history_basho_count": len(dates),
        "rating_points": rating_points,
        "rating_count": rating_count,
        "entrant_initial_rating_count": len(entrant_initial_ratings),
        "model": model_metadata(),
    }


def write_json(path: Path, payload: object) -> None:
    """Write consistently formatted JSON."""

    path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
