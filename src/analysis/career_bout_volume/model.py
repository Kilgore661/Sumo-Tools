"""Immutable result and provenance models for career bout volume."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HistorySource:
    """The external source from which one probe History was loaded."""

    kind: str
    path: str
    sha256: str


@dataclass(frozen=True)
class RikishiBashoRow:
    """One rikishi's banzuke position and result evidence in one basho."""

    rikishi_id: int
    shikona: str
    basho: str
    chii: str
    chii_ordinal: int
    banzuke_size: int
    position_from_top: int
    position_from_bottom: int
    normalized_position: float
    recorded_results: int
    fought_bouts: int
    fought_wins: int
    fought_losses: int
    draws: int
    fusensho: int
    fusenpai: int


@dataclass(frozen=True)
class RikishiCareerRow:
    """Career-level aggregation used by the scatter chart."""

    rikishi_id: int
    shikona: str
    first_basho: str
    last_basho: str
    banzuke_appearances: int
    mean_normalized_position: float
    stdev_normalized_position: float
    sem_normalized_position: float
    ci95_normalized_position_low: float
    ci95_normalized_position_high: float
    best_normalized_position: float
    worst_normalized_position: float
    total_recorded_results: int
    total_fought_bouts: int
    total_fought_wins: int
    total_fought_losses: int
    total_draws: int
    total_fusensho: int
    total_fusenpai: int
    active: bool
    partial_start: bool
    primary_population: bool
    career_status: str


@dataclass(frozen=True)
class BoutProbabilityRow:
    """Empirical probability of reaching a bout threshold in one position band."""

    position_band: str
    position_low_inclusive: float
    position_high_exclusive: float | str
    career_count: int
    bout_threshold: int
    reaching_count: int
    empirical_probability: float
    ci95_low: float
    ci95_high: float


@dataclass(frozen=True)
class ProbeResult:
    """All derived rows for one History."""

    history_first_basho: str
    history_last_basho: str
    history_basho_count: int
    exception_count: int
    basho_rows: tuple[RikishiBashoRow, ...]
    career_rows: tuple[RikishiCareerRow, ...]


@dataclass(frozen=True)
class ProbeOutputs:
    """Files written for one timestamped probe run."""

    run_directory: Path
    manifest_json: Path
    rikishi_basho_csv: Path
    rikishi_careers_csv: Path
    scatter_html: Path
    bout_probability_csv: Path
    bout_probability_html: Path
