"""Typed evidence, diagnostics and inference results for JSA Check."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AbsenceInference(Enum):
    """What the final absence count and empty windows allow us to infer."""

    NO_ABSENCES = "no_absences"
    ALL_ASSIGNED = "all_absences_assigned"
    AMBIGUOUS = "ambiguous_absence_windows"
    INCONSISTENT = "absence_count_exceeds_empty_windows"


@dataclass(frozen=True, slots=True)
class FinalRecord:
    """One independently published SumoDB final basho record."""

    source_text: str
    wins: int
    losses: int
    absences: int
    draws: int

    @property
    def opportunity_total(self) -> int:
        """Return wins + losses + absences + draws."""

        return self.wins + self.losses + self.absences + self.draws


@dataclass(frozen=True, slots=True)
class RikishiBashoWindowRow:
    """Atomic diagnostics and absence inference for one rikishi-basho."""

    basho: str
    rikishi_id: int
    shikona: str
    division: str
    chii: str
    final_record: str
    recorded_wins: int
    recorded_losses: int
    recorded_absences: int
    recorded_draws: int
    opportunity_total: int
    final_observed_basho: bool
    daily_outcomes: tuple[str, ...]
    daily_outcomes_unique: bool
    window_outcome_counts: tuple[int, ...]
    empty_windows: tuple[int, ...]
    outcome_count: int
    dated_win_count: int
    dated_loss_count: int
    dated_draw_count: int
    empty_window_count: int
    excess_outcome_count: int
    jsa_observant: bool
    wins_reconcile: bool
    losses_reconcile: bool
    draws_reconcile: bool
    window_accounting_reconciles: bool
    absence_inference: AbsenceInference
    assigned_absence_count: int
    assigned_absence_windows: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class JsaCheckSummary:
    """Population-level diagnostics and absence-inference results."""

    first_basho: str
    last_basho: str
    basho_count: int
    rikishi_basho_count: int
    daily_unique_count: int
    daily_not_unique_count: int
    opportunity_total_below_7_count: int
    opportunity_total_7_count: int
    opportunity_total_8_count: int
    opportunity_total_above_8_count: int
    short_record_final_observed_basho_count: int
    short_record_not_final_observed_basho_count: int
    records_with_draws_count: int
    wins_reconciled_count: int
    wins_not_reconciled_count: int
    losses_reconciled_count: int
    losses_not_reconciled_count: int
    draws_reconciled_count: int
    draws_not_reconciled_count: int
    observant_count: int
    non_observant_count: int
    observant_percentage: float
    non_observant_percentage: float
    window_accounting_reconciled_count: int
    window_accounting_not_reconciled_count: int
    no_absences_count: int
    all_absences_assigned_count: int
    ambiguous_absence_windows_count: int
    inconsistent_absence_windows_count: int
    positive_absence_record_count: int
    total_absence_count: int
    assigned_absence_count: int
    assigned_absence_percentage: float | None


@dataclass(frozen=True, slots=True)
class JsaCheckResult:
    """Complete in-memory result of the experiment."""

    rows: tuple[RikishiBashoWindowRow, ...]
    summary: JsaCheckSummary


@dataclass(frozen=True, slots=True)
class JsaCheckRunMetadata:
    """Provenance for one persisted experiment run."""

    generated_at: str
    history_source: str
    final_records_source: str
    retirement_source: str


@dataclass(frozen=True, slots=True)
class JsaCheckOutputs:
    """Files written by the experiment."""

    output_root: Path
    rows_csv: Path
    summary_txt: Path
