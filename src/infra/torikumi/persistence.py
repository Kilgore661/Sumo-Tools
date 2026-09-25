"""Deterministic JSON persistence for the current Future snapshot."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.sumo_core.BasicPrimitives import Day, Month, RikId, Year
from src.sumo_core.History import Date

from .model import Future, FutureBout, FutureDay


SCHEMA_VERSION = 1
DEFAULT_OUTPUT_ROOT = Path("files/output/torikumi")
DEFAULT_FUTURE_PATH = DEFAULT_OUTPUT_ROOT / "future.json"


def save_future(future: Future, path: Path = DEFAULT_FUTURE_PATH) -> Path:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "basho": str(future.date),
        "completed_through": (
            None if future.completed_through is None else int(future.completed_through)
        ),
        "generated_at": future.generated_at.isoformat(),
        "days": [
            {
                "day": int(day.day),
                "source_url": day.source_url,
                "downloaded_at": day.downloaded_at.isoformat(),
                "result_count": day.result_count,
                "bouts": [
                    {
                        "order": bout.order,
                        "east": int(bout.east),
                        "west": int(bout.west),
                        "east_shikona": bout.east_shikona,
                        "west_shikona": bout.west_shikona,
                    }
                    for bout in day.bouts
                ],
            }
            for day in future.days
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def load_future(path: Path = DEFAULT_FUTURE_PATH) -> Future:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported Future schema: {payload.get('schema_version')!r}")
    year_text, month_text = payload["basho"].split("/")
    date = Date(Year(int(year_text)), Month(int(month_text)))
    completed = payload.get("completed_through")
    return Future(
        date=date,
        completed_through=None if completed is None else Day(int(completed)),
        generated_at=datetime.fromisoformat(payload["generated_at"]),
        days=tuple(
            FutureDay(
                day=Day(int(raw_day["day"])),
                source_url=raw_day["source_url"],
                downloaded_at=datetime.fromisoformat(raw_day["downloaded_at"]),
                result_count=int(raw_day.get("result_count", 0)),
                bouts=tuple(
                    FutureBout(
                        order=int(raw_bout["order"]),
                        east=RikId(int(raw_bout["east"])),
                        west=RikId(int(raw_bout["west"])),
                        east_shikona=raw_bout.get("east_shikona"),
                        west_shikona=raw_bout.get("west_shikona"),
                    )
                    for raw_bout in raw_day["bouts"]
                ),
            )
            for raw_day in payload["days"]
        ),
    )

