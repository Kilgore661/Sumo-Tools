"""Produce site-facing indexed Rating Changes table payloads."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable, Sequence

from src.analysis.equelo.fixed_supported.api import DayEndRatings, load_day_end_ratings
from src.analysis.equelo.fixed_supported.model import OUTPUT_ROOT as FIXED_SUPPORTED_OUTPUT_ROOT
from src.analysis.equelo.fixed_supported.policy import max_possible_bouts_for_chii
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.infra.live_store.api import get_history
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .metrics import collect_fixed_supported_bout_metrics
from .model import (
    DEFAULT_WINDOW,
    DEFAULT_WINDOWS,
    OUTPUT_ROOT,
    BoutMetrics,
    RatingChangeRow,
    RatingChangesIndexEntry,
    RatingChangesOutputs,
)
from .writer import write_index, write_payload


def build_rating_changes_outputs(
    *,
    history: History,
    output_root: Path = OUTPUT_ROOT,
    windows: Sequence[int] = DEFAULT_WINDOWS,
    day_end_ratings: DayEndRatings | None = None,
    full_shikona_store: FullShikonaStore | None = None,
    fixed_supported_output_root: Path = FIXED_SUPPORTED_OUTPUT_ROOT,
    master_map_path: Path | None = None,
    clear_output_root: bool = True,
) -> RatingChangesOutputs:
    """Write one indexed Rating Changes dataset for the latest represented basho."""

    if clear_output_root and output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    ratings = (
        day_end_ratings
        if day_end_ratings is not None
        else load_day_end_ratings(output_root=fixed_supported_output_root)
    )
    shikona_store = (
        full_shikona_store
        if full_shikona_store is not None
        else FullShikonaStore.from_sources(history)
    )
    fixed_history, bout_metrics = collect_fixed_supported_bout_metrics(
        raw_history=history,
        master_map_path=master_map_path,
        fixed_supported_output_root=fixed_supported_output_root,
    )
    dates = represented_rating_dates(fixed_history, ratings)
    if not dates:
        raise ValueError("No History dates are represented in fixed-supported day-end ratings.")

    target_date = dates[-1]
    target_index = dates.index(target_date)
    entries: list[RatingChangesIndexEntry] = []
    payload_paths: list[Path] = []

    for window in sorted(set(int(value) for value in windows)):
        if window <= 0:
            raise ValueError(f"Window must be positive, got {window!r}")
        start_index = target_index - window
        if start_index < 0:
            continue
        start_date = dates[start_index]
        rows = build_rows_for_window(
            history=fixed_history,
            day_end_ratings=ratings,
            shikona_store=shikona_store,
            bout_metrics_by_rikishi_date=bout_metrics,
            dates=dates,
            start_date=start_date,
            target_date=target_date,
        )
        payload_name = payload_filename(target_date, window)
        payload_path = write_payload(rows, output_root / payload_name)
        payload_paths.append(payload_path)
        entries.append(
            RatingChangesIndexEntry(
                n=window,
                label=f"{window} basho",
                target_date=str(target_date),
                start_date=str(start_date),
                payload_path=f"data/{payload_name}",
            )
        )

    index_path = write_index(entries=entries, output_root=output_root, default_n=DEFAULT_WINDOW)
    return RatingChangesOutputs(
        output_root=output_root,
        index_path=index_path,
        payload_paths=tuple(payload_paths),
    )


def build_rows_for_window(
    *,
    history: History,
    day_end_ratings: DayEndRatings,
    shikona_store: FullShikonaStore,
    bout_metrics_by_rikishi_date: dict[RikId, dict[Date, BoutMetrics]],
    dates: Sequence[Date],
    start_date: Date,
    target_date: Date,
) -> list[RatingChangeRow]:
    """Return ranked rows for one latest-basho n-change payload."""

    start_ratings = end_of_basho_ratings(day_end_ratings, start_date)
    end_ratings = end_of_basho_ratings(day_end_ratings, target_date)
    start_chii = chii_by_rikishi(history, start_date)
    end_chii = chii_by_rikishi(history, target_date)
    rikishi_ids = sorted(set(start_ratings) & set(end_ratings), key=int)

    rows = [
        build_row(
            rikishi_id=rikishi_id,
            start_rating=start_ratings[rikishi_id],
            end_rating=end_ratings[rikishi_id],
            shikona_store=shikona_store,
            start_chii=start_chii.get(rikishi_id),
            end_chii=end_chii.get(rikishi_id),
            expected_bouts=expected_bouts_for_window(
                history=history,
                dates=dates,
                rikishi_id=rikishi_id,
                start_date=start_date,
                target_date=target_date,
            ),
            bout_metrics=metrics_for_window(
                dates=dates,
                rikishi_id=rikishi_id,
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


def build_row(
    *,
    rikishi_id: RikId,
    start_rating: float,
    end_rating: float,
    shikona_store: FullShikonaStore,
    start_chii: Chii | None,
    end_chii: Chii | None,
    expected_bouts: int,
    bout_metrics: BoutMetrics,
) -> RatingChangeRow:
    """Return one site-facing Rating Changes row."""

    delta = end_rating - start_rating
    return RatingChangeRow(
        rikishi_id=int(rikishi_id),
        shikona=shikona_store.full_shikona(rikishi_id),
        division_id=division_id_for_chii(end_chii),
        chii_at_start=str(start_chii) if start_chii is not None else "",
        chii_ordinal_at_start=start_chii.ordinal() if start_chii is not None else "",
        chii_at_end=str(end_chii) if end_chii is not None else "",
        chii_ordinal_at_end=end_chii.ordinal() if end_chii is not None else "",
        rating_at_start=format_number(start_rating),
        rating_at_end=format_number(end_rating),
        delta=format_number(delta),
        expected_bouts=expected_bouts,
        delta_per_expected_bout=format_number(delta / expected_bouts if expected_bouts else 0.0),
        normalised_delta_per_expected_bout=format_number(
            bout_metrics.normalised_delta / expected_bouts if expected_bouts else 0.0
        ),
        actual_bouts=bout_metrics.actual_bouts,
        delta_per_actual_bout=format_number(
            delta / bout_metrics.actual_bouts if bout_metrics.actual_bouts else 0.0
        ),
        normalised_delta_per_actual_bout=format_number(
            bout_metrics.normalised_delta / bout_metrics.actual_bouts
            if bout_metrics.actual_bouts
            else 0.0
        ),
    )


def division_id_for_chii(chii: Chii | None) -> str:
    """Return the site division id for a rikishi's end-of-window chii."""

    if chii is None:
        return ""
    division = division_for_chii(chii)
    return DIVISION_IDS[division]


def division_for_chii(chii: Chii) -> Division:
    """Return the main division containing a chii."""

    if isinstance(chii.level, MSD):
        return Division.MAKUUCHI
    return chii.level


DIVISION_IDS = {
    Division.MAKUUCHI: "makuuchi",
    Division.JURYO: "juryo",
    Division.MAKUSHITA: "makushita",
    Division.SANDANME: "sandanme",
    Division.JONIDAN: "jonidan",
    Division.JONOKUCHI: "jonokuchi",
}


def represented_rating_dates(history: History, day_end_ratings: DayEndRatings) -> list[Date]:
    """Return sorted History dates with persisted fixed-supported ratings."""

    rating_keys = set(day_end_ratings)
    return [
        date
        for date in sorted(history)
        if str(date) in rating_keys or file_date_label(date) in rating_keys
    ]


def end_of_basho_ratings(day_end_ratings: DayEndRatings, date: Date) -> dict[RikId, float]:
    """Return ratings from the final represented day of one basho."""

    by_day = day_end_ratings.get(str(date)) or day_end_ratings.get(file_date_label(date))
    if not by_day:
        raise ValueError(f"No fixed-supported day-end ratings found for {date}")
    final_day = max(by_day, key=lambda day: int(day))
    return {
        RikId(int(rikishi_id_text)): float(rating)
        for rikishi_id_text, rating in by_day[final_day].items()
    }


def chii_by_rikishi(history: History, date: Date) -> dict[RikId, Chii]:
    """Return chii keyed by rikishi for one basho."""

    state = history(date)
    return {rikishi_id: state.banzuke.get_chii(rikishi_id) for rikishi_id in state.banzuke.riks}


def expected_bouts_for_window(
    *,
    history: History,
    dates: Sequence[Date],
    rikishi_id: RikId,
    start_date: Date,
    target_date: Date,
) -> int:
    """Return expected bouts after the baseline basho through the target basho."""

    total = 0
    for date in dates[dates.index(start_date) + 1 : dates.index(target_date) + 1]:
        chii = chii_by_rikishi(history, date).get(rikishi_id)
        if chii is not None:
            total += max_possible_bouts_for_chii(chii)
    return total


def metrics_for_window(
    *,
    dates: Sequence[Date],
    rikishi_id: RikId,
    start_date: Date,
    target_date: Date,
    bout_metrics_by_rikishi_date: dict[RikId, dict[Date, BoutMetrics]],
) -> BoutMetrics:
    """Sum actual-bout and normalised movement metrics over a change window."""

    actual_bouts = 0
    normalised_delta = 0.0
    by_date = bout_metrics_by_rikishi_date.get(rikishi_id, {})
    for date in dates[dates.index(start_date) + 1 : dates.index(target_date) + 1]:
        metrics = by_date.get(date)
        if metrics is None:
            continue
        actual_bouts += metrics.actual_bouts
        normalised_delta += metrics.normalised_delta
    return BoutMetrics(actual_bouts=actual_bouts, normalised_delta=normalised_delta)


def payload_filename(target_date: Date, window: int) -> str:
    """Return a stable payload file name for one latest-basho window."""

    return f"{file_date_label(target_date)} {window}-change.csv"


def file_date_label(date: Date) -> str:
    """Return YYYY-MM date text for file names and tolerant rating-key lookup."""

    return str(date).replace("/", "-")


def format_number(value: float) -> str:
    """Format numeric fields consistently for site CSV payloads."""

    return f"{value:.3f}"


def build_parser() -> argparse.ArgumentParser:
    """Build the standalone producer command-line parser."""

    parser = argparse.ArgumentParser(description="Produce Rating Changes site payloads.")
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--history-zip", type=Path)
    parser.add_argument("--day-end-ratings-root", type=Path)
    parser.add_argument("--fixed-supported-output-root", type=Path, default=FIXED_SUPPORTED_OUTPUT_ROOT)
    parser.add_argument("--master-map-path", type=Path)
    parser.add_argument("--windows", nargs="+", type=int, default=DEFAULT_WINDOWS)
    return parser


def load_history(path: Path | None) -> History:
    """Load History from a zip-backed path or the live store."""

    if path is None:
        return get_history()
    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def main() -> int:
    """Run the standalone Rating Changes producer."""

    args = build_parser().parse_args()
    history = load_history(args.history_zip)
    day_end_ratings = (
        load_day_end_ratings(output_root=args.day_end_ratings_root)
        if args.day_end_ratings_root
        else None
    )
    outputs = build_rating_changes_outputs(
        history=history,
        output_root=args.output_root,
        windows=args.windows,
        day_end_ratings=day_end_ratings,
        fixed_supported_output_root=args.fixed_supported_output_root,
        master_map_path=args.master_map_path,
    )
    print("Wrote:")
    print(f"  {outputs.index_path}")
    for path in outputs.payload_paths:
        print(f"  {path}")
    return 0
