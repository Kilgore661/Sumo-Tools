"""Data classes for Basho Results Browser producer outputs."""

from __future__ import annotations

from dataclasses import dataclass


MISSING = "-"


@dataclass(frozen=True)
class BashoResultsIndexEntry:
    basho: str
    year: int
    month: int
    label: str
    status: str
    latest_day: int
    payload_path: str


@dataclass(frozen=True)
class BashoResultsIndex:
    schema: str
    generated_at: str
    default_basho: str
    entries: tuple[BashoResultsIndexEntry, ...]


@dataclass(frozen=True)
class BashoResultsRow:
    basho: str
    division_id: str
    division_label: str
    rikishi_id: str
    shikona: str
    graph_shikona: str
    chii: str
    chii_ordinal: str
    score: str
    previous_delta_direction: str
    previous_delta: str
    previous_result: str
    previous_chii: str
    previous_chii_ordinal: str
    previous_equelo: str
    equelo: str
    delta_equelo: str
    nu_chii: str
    nu_chii_ordinal: str

