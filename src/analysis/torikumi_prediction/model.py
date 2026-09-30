"""Data contracts for the torikumi-prediction analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.Chii import Chii


Level = MSD | Division


@dataclass(frozen=True)
class BanzukeClass:
    """A side-free semantic rank class used by the analysis."""

    level: Level
    number: int | None

    @classmethod
    def from_chii(cls, chii: Chii) -> "BanzukeClass":
        number = chii.number if chii.level in {
            MSD.MAEGASHIRA,
            Division.JURYO,
            Division.MAKUSHITA,
            Division.SANDANME,
            Division.JONIDAN,
            Division.JONOKUCHI,
        } else None
        return cls(chii.level, number)

    @property
    def label(self) -> str:
        abbreviation = self.level.as_abbreviation()
        return abbreviation if self.number is None else f"{abbreviation}{self.number}"

    @property
    def division(self) -> Division:
        return Division.MAKUUCHI if isinstance(self.level, MSD) else self.level

    @property
    def sort_key(self) -> tuple[int, int]:
        if isinstance(self.level, MSD):
            level_index = list(MSD).index(self.level)
        else:
            level_index = len(MSD) + list(Division).index(self.level) - 1
        return level_index, self.number or 0


@dataclass(frozen=True)
class Observation:
    basho: str
    day: int
    focal_id: int
    focal_chii: str
    focal_class: str
    focal_division: str
    opponent_id: int
    opponent_chii: str
    opponent_class: str
    opponent_division: str
    wins_before: int
    losses_before: int
    bouts_before: int
    bout_number: int
    cross_division: bool
    fusen: bool
    focal_roster_position: int
    opponent_roster_position: int | None
    roster_position_delta: int | None


@dataclass(frozen=True)
class ClassDayRow:
    focal_division: str
    focal_class: str
    day: int
    opponent_class: str
    observations: int
    focal_total: int
    probability: float


@dataclass(frozen=True)
class ClassDayWinsRow:
    focal_division: str
    focal_class: str
    day: int
    wins_before: int
    opponent_class: str
    observations: int
    focal_total: int
    probability: float


@dataclass(frozen=True)
class ClassRecordRow:
    focal_division: str
    focal_class: str
    day: int
    wins_before: int
    losses_before: int
    bouts_before: int
    bout_number: int
    opponent_class: str
    observations: int
    focal_total: int
    probability: float


@dataclass(frozen=True)
class OverallClassRow:
    focal_division: str
    focal_class: str
    opponent_class: str
    observations: int
    focal_total: int
    probability: float


@dataclass(frozen=True)
class Diagnostic:
    kind: str
    basho: str
    day: int | None
    rikishi1: int | None
    rikishi2: int | None
    detail: str


@dataclass(frozen=True)
class AnalysisResult:
    history_first_basho: str
    history_last_basho: str
    history_basho_count: int
    included_first_basho: str
    included_last_basho: str
    included_basho_count: int
    excluded_incomplete_basho_count: int
    scheduled_bout_count: int
    observations: tuple[Observation, ...]
    class_by_day: tuple[ClassDayRow, ...]
    class_by_day_wins: tuple[ClassDayWinsRow, ...]
    class_by_record: tuple[ClassRecordRow, ...]
    overall_class: tuple[OverallClassRow, ...]
    diagnostics: tuple[Diagnostic, ...]


@dataclass(frozen=True)
class OutputPaths:
    run_directory: Path
    observations_csv: Path
    class_by_day_csv: Path
    class_by_day_wins_csv: Path
    class_by_record_csv: Path
    overall_class_csv: Path
    diagnostics_csv: Path
    manifest_json: Path
