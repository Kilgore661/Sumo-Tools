"""Core calculations for exploratory Equelo n-change tables."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Sequence

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate
from src.analysis.equelo.fixed_supported.api import DayEndRatings, master_chii_initial_rating_map_path
from src.analysis.equelo.fixed_supported.build import make_chii_initialiser, oracle_collapse_mode
from src.analysis.equelo.fixed_supported.master_map import (
    load_master_chii_initial_rating_map,
    ratings_by_chii,
)
from src.analysis.equelo.fixed_supported.model import K_CONFIG, K_POLICY, OUTPUT_ROOT as FIXED_SUPPORTED_OUTPUT_ROOT, Q
from src.analysis.equelo.fixed_supported.policy import max_possible_bouts_for_chii
from src.analysis.equelo.rating_changes.model import BoutWindowMetrics, RatingChangeRow
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

DEFAULT_WINDOWS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 12)
OUTPUT_ROOT = Path("files/output/analysis/equelo/rating_changes")


def build_rating_change_outputs(
    *,
    day_end_ratings: DayEndRatings,
    history: History,
    full_shikona_store: FullShikonaStore,
    target_date_text: str | None = None,
    windows: Sequence[int] = DEFAULT_WINDOWS,
    output_root: Path = OUTPUT_ROOT,
    master_map_path: Path | None = None,
    fixed_supported_output_root: Path = FIXED_SUPPORTED_OUTPUT_ROOT,
) -> tuple[Path, ...]:
    """Write one n-change CSV for each requested window."""

    bout_metrics_history, bout_metrics_by_rikishi_date = compute_bout_level_metrics(
        raw_history=history,
        master_map_path=(
            master_map_path
            if master_map_path is not None
            else master_chii_initial_rating_map_path(fixed_supported_output_root)
        ),
    )
    history = bout_metrics_history
    dates = represented_rating_dates(history, day_end_ratings)
    if not dates:
        raise ValueError("No History dates are represented in day-end ratings.")

    target_date = resolve_target_date(dates, target_date_text)
    target_index = dates.index(target_date)
    chii_at_end_by_rikishi = chii_at_date(history, target_date)

    output_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    target_label = output_date_label(target_date)

    for window in windows:
        if window <= 0:
            raise ValueError(f"Window must be positive, got {window!r}.")
        start_index = target_index - window
        if start_index < 0:
            # Exploratory tool: skip windows that cannot be computed for the selected date.
            continue
        start_date = dates[start_index]
        rows = rating_change_rows(
            day_end_ratings=day_end_ratings,
            dates=dates,
            start_date=start_date,
            target_date=target_date,
            full_shikona_store=full_shikona_store,
            history=history,
            chii_at_end_by_rikishi=chii_at_end_by_rikishi,
            bout_metrics_by_rikishi_date=bout_metrics_by_rikishi_date,
        )
        output_path = output_root / f"{target_label} {window}-change.csv"
        write_dataclass_csv(rows, output_path)
        written.append(output_path)

    return tuple(written)


class BoutMetricsObserver:
    """Collect actual rated bouts and delta/k movement during fixed-supported simulation."""

    def __init__(self, k_fn):
        self.k_fn = k_fn
        self._chii_by_date_rikishi: dict[Date, dict[RikId, Chii]] = {}
        self.metrics_by_rikishi_date: dict[RikId, dict[Date, BoutWindowMetrics]] = defaultdict(dict)
        self._actual_bouts: dict[RikId, dict[Date, int]] = defaultdict(lambda: defaultdict(int))
        self._normalised_delta: dict[RikId, dict[Date, float]] = defaultdict(lambda: defaultdict(float))

    def on_basho_start(self, date, ratings, banzuke) -> None:
        self._chii_by_date_rikishi[date] = dict(banzuke.rikchii)

    def on_entry(self, date, rikid, rating, ratings) -> None:
        pass

    def on_retirement(
        self,
        date,
        rikid,
        rating,
        n,
        delta,
        delta_per_rikishi,
        abs_delta_per_rikishi,
        closed,
    ) -> None:
        pass

    def on_day_start(self, date, day, ratings) -> None:
        pass

    def on_bout(
        self,
        date,
        day,
        bout,
        delta1,
        delta2,
        r1_before,
        r2_before,
        r1_after,
        r2_after,
        rating_mass_before,
        rating_mass_after,
    ) -> None:
        self._record(date=date, rikishi_id=bout.rikishi1, delta=float(delta1))
        self._record(date=date, rikishi_id=bout.rikishi2, delta=float(delta2))

    def on_ignored_bout(self, date, day, bout) -> None:
        pass

    def on_day_end(self, date, day, ratings) -> None:
        pass

    def on_basho_end(self, date, ratings, banzuke) -> None:
        rikishi_ids = set(self._actual_bouts) | set(self._normalised_delta)
        for rikishi_id in rikishi_ids:
            actual = int(self._actual_bouts[rikishi_id].get(date, 0))
            normalised = float(self._normalised_delta[rikishi_id].get(date, 0.0))
            if actual or normalised:
                self.metrics_by_rikishi_date[rikishi_id][date] = BoutWindowMetrics(
                    actual_bouts=actual,
                    normalised_delta=normalised,
                )

    def _record(self, *, date: Date, rikishi_id: RikId, delta: float) -> None:
        chii = self._chii_by_date_rikishi[date][rikishi_id]
        k = float(self.k_fn(chii.ordinal()))
        self._actual_bouts[rikishi_id][date] += 1
        self._normalised_delta[rikishi_id][date] += delta / k if k else 0.0


def compute_bout_level_metrics(
    *,
    raw_history: History,
    master_map_path: Path,
) -> tuple[History, dict[RikId, dict[Date, BoutWindowMetrics]]]:
    """Re-run the fixed-supported simulation and collect bout-level movement metrics."""

    oracle = make_oracle(raw_history, collapse_mode=oracle_collapse_mode())
    params = build_elo_params(k_policy=K_POLICY, q=Q, config_path=K_CONFIG)
    entrant_initial_ratings = ratings_by_chii(load_master_chii_initial_rating_map(master_map_path))
    observer = BoutMetricsObserver(params.k)
    simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=make_chii_initialiser(entrant_initial_ratings),
        mode=SimulationMode.CLOSED,
        observer=observer,
    )
    return oracle.history, observer.metrics_by_rikishi_date


def metrics_for_window(
    *,
    rikishi_id: RikId,
    dates: Sequence[Date],
    start_date: Date,
    target_date: Date,
    bout_metrics_by_rikishi_date: dict[RikId, dict[Date, BoutWindowMetrics]],
) -> BoutWindowMetrics:
    """Sum actual bouts and normalised movement after start_date through target_date."""

    start_index = dates.index(start_date)
    target_index = dates.index(target_date)
    by_date = bout_metrics_by_rikishi_date.get(rikishi_id, {})
    actual_bouts = 0
    normalised_delta = 0.0
    for date in dates[start_index + 1 : target_index + 1]:
        metrics = by_date.get(date)
        if metrics is None:
            continue
        actual_bouts += metrics.actual_bouts
        normalised_delta += metrics.normalised_delta
    return BoutWindowMetrics(
        actual_bouts=actual_bouts,
        normalised_delta=normalised_delta,
    )


def represented_rating_dates(history: History, day_end_ratings: DayEndRatings) -> list[Date]:
    """Return sorted History dates that also have fixed-supported day-end ratings."""

    rating_date_labels = set(day_end_ratings)
    return [
        date
        for date in sorted(history)
        if str(date) in rating_date_labels or output_date_label(date) in rating_date_labels
    ]


def resolve_target_date(dates: Sequence[Date], target_date_text: str | None) -> Date:
    """Resolve a requested target date, defaulting to the latest represented date."""

    if target_date_text is None:
        return dates[-1]

    normalised = normalise_date_text(target_date_text)
    for date in dates:
        if str(date) == normalised:
            return date
    available = ", ".join(output_date_label(date) for date in dates[-12:])
    raise ValueError(
        f"Target date {target_date_text!r} is not represented in ratings/History. "
        f"Latest available dates include: {available}"
    )


def normalise_date_text(value: str) -> str:
    """Return a History-style YYYY/MM date label from YYYY-MM or YYYY/MM input."""

    text = value.strip().replace("-", "/")
    parts = text.split("/")
    if len(parts) != 2:
        raise ValueError(f"Expected YYYY-MM or YYYY/MM date, got {value!r}.")
    year, month = parts
    return f"{int(year):04d}/{int(month):02d}"


def output_date_label(date: Date) -> str:
    """Return the file-name date label for a History date."""

    return str(date).replace("/", "-")


def chii_at_date(history: History, date: Date) -> dict[RikId, Chii]:
    """Return banzuke chii keyed by rikishi for one basho date."""

    state = history(date)
    return {rikishi_id: state.banzuke.get_chii(rikishi_id) for rikishi_id in state.banzuke.riks}


def rating_change_rows(
    *,
    day_end_ratings: DayEndRatings,
    dates: Sequence[Date],
    start_date: Date,
    target_date: Date,
    full_shikona_store: FullShikonaStore,
    history: History,
    chii_at_end_by_rikishi: dict[RikId, Chii],
    bout_metrics_by_rikishi_date: dict[RikId, dict[Date, BoutWindowMetrics]],
) -> list[RatingChangeRow]:
    """Return all rows for one start/end n-change table."""

    start_ratings = end_of_basho_ratings(day_end_ratings, start_date)
    end_ratings = end_of_basho_ratings(day_end_ratings, target_date)
    rikishi_ids = sorted(set(start_ratings) & set(end_ratings), key=int)
    chii_at_start_by_rikishi = chii_at_date(history, start_date)
    rows = [
        rating_change_row(
            rikishi_id=rikishi_id,
            start_rating=start_ratings[rikishi_id],
            end_rating=end_ratings[rikishi_id],
            dates=dates,
            target_date=target_date,
            day_end_ratings=day_end_ratings,
            full_shikona_store=full_shikona_store,
            chii_at_start_by_rikishi=chii_at_start_by_rikishi,
            chii_at_end_by_rikishi=chii_at_end_by_rikishi,
            expected_bouts=expected_bouts_for_window(
                history=history,
                rikishi_id=rikishi_id,
                dates=dates,
                start_date=start_date,
                target_date=target_date,
            ),
            bout_metrics=metrics_for_window(
                rikishi_id=rikishi_id,
                dates=dates,
                start_date=start_date,
                target_date=target_date,
                bout_metrics_by_rikishi_date=bout_metrics_by_rikishi_date,
            ),
        )
        for rikishi_id in rikishi_ids
    ]
    return sorted(
        rows,
        key=lambda row: (
            -float(row.delta),
            row.chii_ordinal_at_end if isinstance(row.chii_ordinal_at_end, int) else 10**9,
            row.shikona,
            row.rikishi_id,
        ),
    )


def rating_change_row(
    *,
    rikishi_id: RikId,
    start_rating: float,
    end_rating: float,
    dates: Sequence[Date],
    target_date: Date,
    day_end_ratings: DayEndRatings,
    full_shikona_store: FullShikonaStore,
    chii_at_start_by_rikishi: dict[RikId, Chii],
    chii_at_end_by_rikishi: dict[RikId, Chii],
    expected_bouts: int,
    bout_metrics: BoutWindowMetrics,
) -> RatingChangeRow:
    """Return one rating-change row."""

    start_chii = chii_at_start_by_rikishi.get(rikishi_id)
    end_chii = chii_at_end_by_rikishi.get(rikishi_id)
    delta = end_rating - start_rating
    return RatingChangeRow(
        rikishi_id=int(rikishi_id),
        shikona=full_shikona_store.full_shikona(rikishi_id),
        chii_at_start=str(start_chii) if start_chii is not None else "",
        chii_ordinal_at_start=start_chii.ordinal() if start_chii is not None else "",
        chii_at_end=str(end_chii) if end_chii is not None else "",
        chii_ordinal_at_end=end_chii.ordinal() if end_chii is not None else "",
        rating_at_start=format_rating(start_rating),
        rating_at_end=format_rating(end_rating),
        delta=format_rating(delta),
        length_of_streak=streak_length(
            rikishi_id=rikishi_id,
            direction=sign(delta),
            dates=dates,
            target_date=target_date,
            day_end_ratings=day_end_ratings,
        ),
        expected_bouts=expected_bouts,
        actual_bouts=bout_metrics.actual_bouts,
        bout_coverage=format_ratio(
            bout_metrics.actual_bouts / expected_bouts if expected_bouts else 0.0
        ),
        normalised_delta=format_rating(bout_metrics.normalised_delta),
        normalised_delta_per_actual_bout=format_rating(
            bout_metrics.normalised_delta / bout_metrics.actual_bouts
            if bout_metrics.actual_bouts
            else 0.0
        ),
        normalised_delta_per_expected_bout=format_rating(
            bout_metrics.normalised_delta / expected_bouts if expected_bouts else 0.0
        ),
    )


def end_of_basho_ratings(day_end_ratings: DayEndRatings, date: Date) -> dict[RikId, float]:
    """Return rikishi ratings from the final represented day of one basho."""

    date_ratings = day_end_ratings.get(str(date)) or day_end_ratings.get(output_date_label(date))
    if not date_ratings:
        raise ValueError(f"No day-end ratings found for {date}.")
    final_day = max(date_ratings, key=lambda day: int(day))
    return {
        RikId(int(rikishi_id_text)): float(raw_rating)
        for rikishi_id_text, raw_rating in date_ratings[final_day].items()
    }


def expected_bouts_for_window(
    *,
    history: History,
    rikishi_id: RikId,
    dates: Sequence[Date],
    start_date: Date,
    target_date: Date,
) -> int:
    """Return expected bouts from after start_date through target_date inclusive.

    A one-basho window compares the target basho end rating to the previous
    basho end rating, so the expected bouts are those for the target basho.
    Larger windows add each represented basho in that interval.
    """

    start_index = dates.index(start_date)
    target_index = dates.index(target_date)
    total = 0
    for date in dates[start_index + 1 : target_index + 1]:
        chii = chii_at_date(history, date).get(rikishi_id)
        if chii is not None:
            total += max_possible_bouts_for_chii(chii)
    return total


def streak_length(
    *,
    rikishi_id: RikId,
    direction: int,
    dates: Sequence[Date],
    target_date: Date,
    day_end_ratings: DayEndRatings,
) -> int:
    """Count consecutive same-sign 1-basho changes walking backwards from target."""

    if direction == 0:
        return 0

    index = dates.index(target_date)
    length = 0
    while index > 0:
        current_ratings = end_of_basho_ratings(day_end_ratings, dates[index])
        previous_ratings = end_of_basho_ratings(day_end_ratings, dates[index - 1])
        if rikishi_id not in current_ratings or rikishi_id not in previous_ratings:
            break
        one_change = current_ratings[rikishi_id] - previous_ratings[rikishi_id]
        if sign(one_change) != direction:
            break
        length += 1
        index -= 1
    return length


def sign(value: float) -> int:
    """Return -1, 0, or 1 for a numeric value."""

    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def format_rating(value: float) -> str:
    """Format a rating or rating delta for CSV display."""

    return f"{value:.3f}"


def format_ratio(value: float) -> str:
    """Format a fractional coverage value for CSV display."""

    return f"{value:.3f}"


def write_dataclass_csv(rows: Iterable[object], output_path: Path) -> None:
    """Write dataclass rows to CSV."""

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
