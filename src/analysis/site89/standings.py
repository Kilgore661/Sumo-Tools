"""Produce the established latest-window standings files into a supplied root."""

from __future__ import annotations

from pathlib import Path

from src.analysis.standings.multiple_basho import (
    get_multiple_basho_core,
    resolve_window_dates,
)
from src.analysis.standings.multiple_basho_view import get_multiple_basho_view
from src.analysis.standings.publisher import write_published_view_csv
from src.analysis.standings.publisher_reports import write_sidecar_json, write_site_config_json
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.History import History


WINDOWS = (1, 2, 3, 4, 5, 6, 12, 18, 24, 36, 60)
DIRECTION = "BACKWARDS"


def produce_standings(*, history: History, output_root: Path) -> tuple[Path, ...]:
    output_root.mkdir(parents=True, exist_ok=True)
    anchor = max(history)
    names = FullShikonaStore.from_sources(history)
    config = output_root / "site_config.json"
    write_site_config_json(config, anchor, DIRECTION, WINDOWS, 6, "makuuchi")
    paths = [config]
    token = str(anchor).replace("/", "_")
    for window in WINDOWS:
        selected = resolve_window_dates(history, anchor, DIRECTION, window)
        core = get_multiple_basho_core(history, selected)
        view = get_multiple_basho_view(
            history, core, full_shikona_store=names
        )
        stem = f"multiple basho standings view ({token}, {DIRECTION}, {window})"
        csv_path = output_root / f"{stem}.csv"
        json_path = output_root / f"{stem}.json"
        write_published_view_csv(view, csv_path, set(history(selected[-1]).banzuke.riks))
        write_sidecar_json(json_path, anchor, DIRECTION, window, selected)
        paths.extend((csv_path, json_path))
    return tuple(paths)
