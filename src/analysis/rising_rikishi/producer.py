"""Build exploratory rising-rikishi Equelo delta CSVs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.analysis.equelo.api import EqueloLookup
from src.analysis.rising_rikishi.model import (
    BoutCounts,
    RatingEndpoints,
    RisingRow,
    RisingWindow,
)
from src.analysis.rising_rikishi.writer import OUTPUT_ROOT, output_path, write_rows
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import BoutResult


RATING_DECISIONS_TO_SKIP = {"fusen", "blank"}


def build_outputs(
    *,
    history: History,
    windows: Iterable[int],
    output_root: Path = OUTPUT_ROOT,
    all_end_basho: bool = False,
    equelo_lookup: EqueloLookup | None = None,
    shikona_store: FullShikonaStore | None = None,
) -> list[Path]:
    """Write rising-rikishi CSVs for selected end basho/window-size pairs."""

    dates = tuple(sorted(history.keys()))
    lookup = equelo_lookup if equelo_lookup is not None else EqueloLookup.load(history)
    full_shikona = shikona_store if shikona_store is not None else FullShikonaStore.from_sources(history)
    written: list[Path] = []

    for window_size in sorted(set(windows)):
        for end_index in output_end_indices(dates, window_size, all_end_basho):
            window = make_window(dates, end_index=end_index, window_size=window_size)
            rows = build_rows_for_window(
                history=history,
                equelo_lookup=lookup,
                shikona_store=full_shikona,
                window=window,
            )
            path = output_path(output_root, window)
            write_rows(rows, path)
            written.append(path)

    return written


def output_end_indices(
    dates: tuple[Date, ...],
    window_size: int,
    all_end_basho: bool,
) -> range:
    """Return end-date indices to produce for one window size."""

    if len(dates) < window_size:
        return range(0, 0)
    if all_end_basho:
        return range(window_size - 1, len(dates))
    return range(len(dates) - 1, len(dates))


def make_window(
    dates: tuple[Date, ...],
    *,
    end_index: int,
    window_size: int,
) -> RisingWindow:
    """Return the n-basho movement window ending at dates[end_index]."""

    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")
    first_index = end_index - window_size + 1
    if first_index < 0:
        raise ValueError("end_index does not allow a full movement window")
    movement_basho = dates[first_index : end_index + 1]
    return RisingWindow(end_basho=dates[end_index], movement_basho=movement_basho)


def build_rows_for_window(
    *,
    history: History,
    equelo_lookup: EqueloLookup,
    shikona_store: FullShikonaStore,
    window: RisingWindow,
) -> list[RisingRow]:
    """Return all eligible rikishi rows for one rising-rikishi window."""

    endpoints = (
        rating_endpoints(history, equelo_lookup, window, rikid)
        for rikid in eligible_rikishi(history, window)
    )
    rows = [
        make_row(
            history=history,
            shikona_store=shikona_store,
            window=window,
            endpoints=endpoint,
        )
        for endpoint in endpoints
        if endpoint is not None
    ]
    return sorted(rows, key=lambda row: (row.chii_ordinal, row.shikona, row.rik_id))


def eligible_rikishi(history: History, window: RisingWindow) -> tuple[RikId, ...]:
    """Return rikishi on the banzuke in every basho in the movement window."""

    present_sets = [history(date).banzuke.riks for date in window.movement_basho]
    if not present_sets:
        return ()
    return tuple(sorted(set.intersection(*map(set, present_sets)), key=int))


def rating_endpoints(
    history: History,
    equelo_lookup: EqueloLookup,
    window: RisingWindow,
    rikid: RikId,
) -> RatingEndpoints | None:
    """Return before-first-basho and after-end-basho ratings for one rikishi."""

    first_basho = window.first_basho
    end_basho = window.end_basho
    start_rating = equelo_lookup.before_ratings[first_basho].get(rikid)
    end_rating = equelo_lookup.after_ratings[end_basho].get(rikid)
    if start_rating is None or end_rating is None:
        return None

    chii = history(end_basho).banzuke.get_chii(rikid)
    if chii is None:
        return None

    return RatingEndpoints(
        rikid=rikid,
        chii=chii,
        start_rating=float(start_rating),
        end_rating=float(end_rating),
    )


def make_row(
    *,
    history: History,
    shikona_store: FullShikonaStore,
    window: RisingWindow,
    endpoints: RatingEndpoints,
) -> RisingRow:
    """Return one CSV row for one eligible rikishi/window."""

    counts = count_bouts(history, window, endpoints.rikid)
    delta = endpoints.end_rating - endpoints.start_rating
    bout_norm = delta / counts.rating_bouts if counts.rating_bouts else None

    return RisingRow(
        rik_id=int(endpoints.rikid),
        shikona=shikona_store.full_shikona(endpoints.rikid),
        chii=str(endpoints.chii),
        chii_ordinal=endpoints.chii.ordinal(),
        delta=format_float(delta),
        basho_norm=format_float(delta / window.size),
        num_bouts=counts.rating_bouts,
        bout_norm=format_float(bout_norm) if bout_norm is not None else "",
    )


def count_bouts(history: History, window: RisingWindow, rikid: RikId) -> BoutCounts:
    """Count rating-updating bouts involving rikid in a movement window."""

    rating_bouts = 0
    for date in window.movement_basho:
        for bout in iter_bouts(history(date).summary):
            if not bout_involves(bout, rikid):
                continue
            if bout.decision in RATING_DECISIONS_TO_SKIP:
                continue
            rating_bouts += 1
    return BoutCounts(rating_bouts=rating_bouts)


def iter_bouts(summary) -> Iterable[BoutResult]:
    """Yield each recorded bout result once from a basho summary."""

    for day in sorted(summary.keys()):
        daily = summary(day)
        for pair in sorted(daily.results_lookup.keys(), key=lambda item: (int(item[0]), int(item[1]))):
            yield daily.results_lookup[pair]


def bout_involves(bout: BoutResult, rikid: RikId) -> bool:
    """Return whether a bout result involves rikid."""

    return bout.rikishi1 == rikid or bout.rikishi2 == rikid


def format_float(value: float) -> str:
    """Format floating-point values for spreadsheet inspection."""

    return f"{value:.3f}"
