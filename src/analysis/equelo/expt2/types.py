from pdb import set_trace

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypeAlias

from ....sumo_core.Chii import Chii


ChiiRatings: TypeAlias = dict[Chii, float]
ProbeSet: TypeAlias = list[Chii]
ProbeCounts: TypeAlias = dict[Chii, int]
BashoStartRatingsByChii: TypeAlias = dict[Chii, list[float]]


@dataclass(frozen=True)
class AggregateResult:
    mean_by_chii: ChiiRatings
    count_by_chii: ProbeCounts


@dataclass(frozen=True)
class NormalisationResult:
    mu: ChiiRatings
    shift: float


@dataclass(frozen=True)
class IterationDiagnosticsRow:
    iteration: int
    delta: float
    shift: float
    iter_seconds: float
    probe_values: dict[Chii, float]
    probe_counts: dict[Chii, int]


class IterationDiagnosticsSink(Protocol):
    def record(self, row: IterationDiagnosticsRow) -> None: ...
    def finalise(self) -> Path | None: ...


@dataclass(frozen=True)
class SolveResult:
    mu: ChiiRatings
    converged: bool
    iterations: int
    final_delta: float
    output_csv_path: Path | None
    stats_csv_path: Path | None
    diagnostics_path: Path | None
    calibration_output_csv_path: Path | None = None
    calibration_stats_csv_path: Path | None = None
