from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from src.analysis.equelo.fixed_v2 import model as fixed_v2_model
from src.analysis.equelo.fixed_v2.api import load_day_end_ratings
from src.analysis.equelo.expt1.simulate import expect
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.BasicEnums import Side
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History


@dataclass(frozen=True)
class ObservedTracePoint:
    selected_chii: str
    opponent_chii: str
    selected_ordinal: int
    opponent_ordinal: int
    n_obs: int
    n_selected_wins: int
    n_opponent_wins: int
    p_selected_wins: float
    ci95_lower: float
    ci95_upper: float


@dataclass(frozen=True)
class SidelessRating:
    sideless_chii: str
    sideless_ordinal: int
    rating: float
    n_process_ratings: int
    process_ratings_used: str


@dataclass(frozen=True)
class EqueloTracePoint:
    selected_chii: str
    opponent_chii: str
    selected_ordinal: int
    opponent_ordinal: int
    selected_rating: float
    opponent_rating: float
    p_selected_wins: float


def build_observed_trace_points(sideless_pair_csv: Path) -> tuple[ObservedTracePoint, ...]:
    """Expand canonical sideless pair rows into selected/opponent trace points."""
    points: list[ObservedTracePoint] = []

    with sideless_pair_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            same_chii = int(row["same_chii"])
            higher = _observed_point_from_pair_row(row, selected_is_higher=True)
            points.append(higher)

            if same_chii:
                continue

            points.append(_observed_point_from_pair_row(row, selected_is_higher=False))

    return tuple(sorted(points, key=lambda p: (p.selected_ordinal, p.opponent_ordinal)))


def build_sideless_ratings(
    *,
    output_root: Path = fixed_v2_model.OUTPUT_ROOT,
    history: History | None = None,
) -> tuple[SidelessRating, ...]:
    """Average latest fixed_v2 process ratings by current sideless chii."""
    history = get_history() if history is None else history
    date, day, ratings = latest_rating_snapshot(output_root=output_root, history=history)
    banzuke = history(date).banzuke
    buckets: dict[int, list[tuple[int, Chii, float]]] = {}

    for rikishi_id_text, rating in ratings.items():
        rikishi_id = int(rikishi_id_text)
        if rikishi_id not in banzuke.rikchii:
            continue
        chii = banzuke.rikchii[rikishi_id]
        sideless_chii = _remove_side(chii)
        buckets.setdefault(sideless_chii.ordinal(), []).append(
            (rikishi_id, chii, float(rating))
        )

    rows: list[SidelessRating] = []
    for sideless_ordinal in sorted(buckets):
        values = buckets[sideless_ordinal]
        rating = sum(value for _, _, value in values) / len(values)
        sideless_chii = _remove_side(values[0][1])
        process_ratings_used = ";".join(
            f"{rikishi_id}:{chii}:{value:.12g}"
            for rikishi_id, chii, value in sorted(
                values,
                key=lambda item: (item[1].ordinal(), item[0]),
            )
        )
        rows.append(
            SidelessRating(
                sideless_chii=str(sideless_chii),
                sideless_ordinal=sideless_ordinal,
                rating=rating,
                n_process_ratings=len(values),
                process_ratings_used=process_ratings_used,
            )
        )

    return tuple(rows)


def latest_rating_snapshot(
    *,
    output_root: Path = fixed_v2_model.OUTPUT_ROOT,
    history: History | None = None,
) -> tuple[Date, int, dict[str, float]]:
    """Return the latest fixed_v2 day-end snapshot that aligns with History."""
    history = get_history() if history is None else history
    day_end_ratings = load_day_end_ratings(output_root=output_root)
    history_date_by_text = {str(date): date for date in history}
    available_date_texts = [
        date_text for date_text in day_end_ratings if date_text in history_date_by_text
    ]
    if not available_date_texts:
        raise ValueError("No fixed_v2 day-end rating snapshot matches the live history")

    date_text = sorted(available_date_texts, key=_date_from_text)[-1]
    date = history_date_by_text[date_text]
    date_ratings = day_end_ratings[date_text]
    day = max((int(day_text) for day_text in date_ratings), default=0)
    if day == 0:
        raise ValueError(f"No fixed_v2 day-end ratings found for {date}")
    return date, day, date_ratings[str(day)]


def filter_observed_points_to_rating_domain(
    observed_points: tuple[ObservedTracePoint, ...],
    sideless_ratings: tuple[SidelessRating, ...],
) -> tuple[ObservedTracePoint, ...]:
    """Restrict observed trace points to selected/opponent chii in the rating domain."""
    rated_chii = {row.sideless_chii for row in sideless_ratings}
    return tuple(
        point for point in observed_points
        if point.selected_chii in rated_chii and point.opponent_chii in rated_chii
    )


def build_equelo_trace_points(
    observed_points: tuple[ObservedTracePoint, ...],
    sideless_ratings: tuple[SidelessRating, ...],
    *,
    q: float,
) -> tuple[EqueloTracePoint, ...]:
    """Project observed trace points through the sideless Equelo rating map."""
    ratings = {row.sideless_chii: row for row in sideless_ratings}
    points: list[EqueloTracePoint] = []

    for observed in observed_points:
        selected = ratings.get(observed.selected_chii)
        opponent = ratings.get(observed.opponent_chii)
        if selected is None or opponent is None:
            continue

        points.append(
            EqueloTracePoint(
                selected_chii=observed.selected_chii,
                opponent_chii=observed.opponent_chii,
                selected_ordinal=observed.selected_ordinal,
                opponent_ordinal=observed.opponent_ordinal,
                selected_rating=selected.rating,
                opponent_rating=opponent.rating,
                p_selected_wins=expect(selected.rating, opponent.rating, q),
            )
        )

    return tuple(points)


def write_trace_outputs(
    *,
    output_dir: Path,
    observed_points: tuple[ObservedTracePoint, ...],
    sideless_ratings: tuple[SidelessRating, ...],
    equelo_points: tuple[EqueloTracePoint, ...],
    fixed_v2_output_root: Path,
    q: float,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "observed_trace_csv": output_dir / "observed_sideless_trace_points.csv",
        "equelo_ratings_csv": output_dir / "equelo_sideless_ratings.csv",
        "equelo_trace_csv": output_dir / "equelo_sideless_trace_points.csv",
        "trace_metadata_json": output_dir / "sideless_trace_metadata.json",
    }
    _write_dataclass_csv(observed_points, paths["observed_trace_csv"])
    _write_dataclass_csv(sideless_ratings, paths["equelo_ratings_csv"])
    _write_dataclass_csv(equelo_points, paths["equelo_trace_csv"])
    _write_trace_metadata(
        output_path=paths["trace_metadata_json"],
        observed_points=observed_points,
        sideless_ratings=sideless_ratings,
        equelo_points=equelo_points,
        fixed_v2_output_root=fixed_v2_output_root,
        q=q,
    )
    return paths


def _observed_point_from_pair_row(row: dict[str, str], *, selected_is_higher: bool) -> ObservedTracePoint:
    if selected_is_higher:
        return ObservedTracePoint(
            selected_chii=row["higher_or_equal_chii"],
            opponent_chii=row["other_chii"],
            selected_ordinal=int(row["higher_or_equal_ordinal"]),
            opponent_ordinal=int(row["other_ordinal"]),
            n_obs=int(row["n_obs"]),
            n_selected_wins=int(row["n_higher_or_equal_wins"]),
            n_opponent_wins=int(row["n_other_wins"]),
            p_selected_wins=float(row["p_higher_or_equal_wins"]),
            ci95_lower=float(row["ci95_lower"]),
            ci95_upper=float(row["ci95_upper"]),
        )

    n_obs = int(row["n_obs"])
    n_selected_wins = int(row["n_other_wins"])
    n_opponent_wins = int(row["n_higher_or_equal_wins"])
    p_selected = n_selected_wins / n_obs
    return ObservedTracePoint(
        selected_chii=row["other_chii"],
        opponent_chii=row["higher_or_equal_chii"],
        selected_ordinal=int(row["other_ordinal"]),
        opponent_ordinal=int(row["higher_or_equal_ordinal"]),
        n_obs=n_obs,
        n_selected_wins=n_selected_wins,
        n_opponent_wins=n_opponent_wins,
        p_selected_wins=p_selected,
        ci95_lower=1.0 - float(row["ci95_upper"]),
        ci95_upper=1.0 - float(row["ci95_lower"]),
    )


def _write_dataclass_csv(rows, output_path: Path) -> None:
    rows = tuple(rows)
    if not rows:
        raise ValueError(f"Cannot write empty CSV without fieldnames: {output_path}")

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tuple(rows[0].__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in row.__dataclass_fields__})


def _write_trace_metadata(
    *,
    output_path: Path,
    observed_points: tuple[ObservedTracePoint, ...],
    sideless_ratings: tuple[SidelessRating, ...],
    equelo_points: tuple[EqueloTracePoint, ...],
    fixed_v2_output_root: Path,
    q: float,
) -> None:
    observed_keys = {(row.selected_chii, row.opponent_chii) for row in observed_points}
    equelo_keys = {(row.selected_chii, row.opponent_chii) for row in equelo_points}
    payload = {
        "observed_trace_points": len(observed_points),
        "equelo_trace_points": len(equelo_points),
        "missing_equelo_trace_points": len(observed_keys - equelo_keys),
        "sideless_rating_count": len(sideless_ratings),
        "fixed_v2_output_root": str(fixed_v2_output_root),
        "rating_source": "latest fixed_v2 process ratings averaged by current sideless chii",
        "fixed_v2_raw_rating_source": str(
            fixed_v2_output_root / fixed_v2_model.DAY_END_RATINGS_FILE_NAME
        ),
        "q": q,
        "domain_policy": (
            "Observed and Equelo trace points are restricted to sideless chii "
            "represented in the latest fixed_v2 process-rating snapshot."
        ),
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _date_from_text(value: str) -> Date:
    year_text, month_text = value.split("/", 1)
    return Date(Year(int(year_text)), Month(int(month_text)))


def _remove_side(chii: Chii) -> Chii:
    return Chii(
        level=chii.level,
        number=chii.number,
        side=Side.NONE,
        ann=chii.ann,
    )
