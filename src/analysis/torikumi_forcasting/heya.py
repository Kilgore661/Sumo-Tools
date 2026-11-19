"""Typed access to forecasting-owned historical heya data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import Date


SCHEMA_VERSION = 1
DEFAULT_HEYA_INDEX = Path(
    "files/output/analysis/torikumi_forcasting/heya_index.json"
)


@dataclass(frozen=True)
class HeyaEntry:
    basho: Date
    rikid: RikId
    heya: str
    observed_days: tuple[int, ...]
    observation_count: int


@dataclass(frozen=True)
class HeyaIndex:
    entries: Mapping[tuple[Date, RikId], HeyaEntry]
    source: Mapping[str, object]

    def get(self, basho: Date, rikid: RikId) -> HeyaEntry | None:
        return self.entries.get((basho, rikid))

    def heya_at(self, basho: Date, rikid: RikId) -> str | None:
        entry = self.get(basho, rikid)
        return entry.heya if entry is not None else None


def load_heya_index(path: Path = DEFAULT_HEYA_INDEX) -> HeyaIndex:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            "unsupported heya index schema_version: "
            f"{raw.get('schema_version')!r}"
        )

    entries: dict[tuple[Date, RikId], HeyaEntry] = {}
    for record in raw.get("records", []):
        basho = _parse_basho(record["basho"])
        rikid = RikId(int(record["rikid"]))
        entry = HeyaEntry(
            basho=basho,
            rikid=rikid,
            heya=str(record["heya"]),
            observed_days=tuple(int(day) for day in record["observed_days"]),
            observation_count=int(record["observation_count"]),
        )
        key = (basho, rikid)
        if key in entries:
            raise ValueError(f"duplicate heya index record for {basho}, {rikid}")
        if entry.heya == "":
            raise ValueError(f"blank heya index record for {basho}, {rikid}")
        if entry.observation_count < len(entry.observed_days):
            raise ValueError(
                f"invalid observation count for {basho}, {rikid}: "
                f"{entry.observation_count} < {len(entry.observed_days)}"
            )
        entries[key] = entry

    source = raw.get("source", {})
    if not isinstance(source, dict):
        raise ValueError("heya index source must be an object")
    return HeyaIndex(
        entries=MappingProxyType(entries),
        source=MappingProxyType(source),
    )


def _parse_basho(value: str) -> Date:
    year, month = value.split("/")
    return Date.from_ints(int(year), int(month))
