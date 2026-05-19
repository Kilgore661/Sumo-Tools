"""Data-output layer for make_site2."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from src.analysis.sumo_history.basho_results.build import (
    build_index,
    build_payload_rows,
)
from src.analysis.sumo_history.basho_results.dates import represented_dates
from src.analysis.sumo_history.basho_results.ratings import RatingLookup
from src.analysis.sumo_history.basho_results.reports import write_index, write_payload
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


BASHO_RESULTS_ROUTE_DATA_DIR = Path("sumo-history") / "basho-results" / "data"


@dataclass(frozen=True, kw_only=True)
class BashoResultsDataOutput:
    index_path: Path
    payload_paths: tuple[Path, ...]


def load_history_from_zip(path: Path) -> History:
    """Load a History from a zip-backed annotated serialisation."""

    zipless = path.with_suffix("") if path.suffix == ".zip" else path
    return load_history_with_annotations(str(zipless))


def build_basho_results_data_output(
    *,
    history_zip: Path,
    output_root: Path,
    payload_mode: str = "all",
) -> BashoResultsDataOutput:
    """Build BRB index and CSV payloads into the make_site2 output tree."""

    if payload_mode not in {"all", "latest", "none"}:
        raise ValueError(f"Unsupported BRB payload mode: {payload_mode!r}")

    history = load_history_from_zip(history_zip)
    dates = represented_dates(history)
    if not dates:
        raise ValueError(f"No represented basho dates found in {history_zip}")

    route_data_root = output_root / BASHO_RESULTS_ROUTE_DATA_DIR
    if route_data_root.exists():
        shutil.rmtree(route_data_root)
    route_data_root.mkdir(parents=True, exist_ok=True)

    index = build_index(history)
    index_path = write_index(index, route_data_root)

    if payload_mode == "none":
        payload_dates = ()
    elif payload_mode == "latest":
        payload_dates = (dates[-1],)
    else:
        payload_dates = dates

    ratings = RatingLookup.load()
    payload_paths = tuple(
        write_payload(
            date,
            build_payload_rows(history=history, date=date, ratings=ratings),
            route_data_root,
        )
        for date in payload_dates
    )

    return BashoResultsDataOutput(
        index_path=index_path,
        payload_paths=payload_paths,
    )
