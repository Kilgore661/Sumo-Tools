"""Produce maximum observed Elo-89 day-end ratings."""

from __future__ import annotations

from pathlib import Path

from src.analysis.elo89.api import Elo89Artifacts
from src.infra.get_bios.FullShikonaStore import FullShikonaStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History

from .common import write_csv


def produce_highest_rating(
    *, history: History, ratings: Elo89Artifacts, output_root: Path
) -> Path:
    records: dict[RikId, tuple[float, str, int]] = {}
    represented = {str(date) for date in history}
    for date in sorted(ratings.day_end_ratings):
        if date not in represented:
            continue
        for day_text in sorted(ratings.day_end_ratings[date], key=int):
            for rid_text, raw in ratings.day_end_ratings[date][day_text].items():
                rid = RikId(int(rid_text))
                value = float(raw)
                if rid not in records or value > records[rid][0]:
                    records[rid] = value, date, int(day_text)
    names = FullShikonaStore.from_sources(history)
    latest = history(max(history))
    ranked = sorted(records.items(), key=lambda item: (-item[1][0], item[1][1], item[1][2], int(item[0])))
    rows = []
    for position, (rid, (rating, date, day)) in enumerate(ranked, start=1):
        state = history(next(key for key in history if str(key) == date))
        chii = state.banzuke.rikchii.get(rid)
        rows.append(
            {
                "position": position,
                "rikishi_id": int(rid),
                "shikona": names.full_shikona(rid),
                "active": rid in latest.banzuke.riks,
                "chii": "" if chii is None else str(chii),
                "chii_ordinal": "" if chii is None else chii.ordinal(),
                "rating": f"{rating:.3f}",
                "date": f"{date}/{day:02d}",
            }
        )
    return write_csv(output_root / "highest_rating.csv", rows)
