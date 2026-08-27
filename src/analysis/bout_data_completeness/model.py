"""Immutable evidence and output models for bout-data completeness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    """Identity of an external input consumed by the audit."""

    path: str
    sha256: str
    file_count: int
    kind: str = "files"


@dataclass(frozen=True, slots=True)
class ChiiAvailabilityRow:
    """Availability for one rikishi at one actual banzuke chii."""

    basho: str
    chii: str
    chii_ordinal: int
    division: str
    rikishi_id: int
    shikona: str
    recorded: bool
    complete: bool
    retired: bool
    known_hoshi_symbol_count: int
    empty_hoshi_symbol_count: int
    hoshi_slot_count: int


@dataclass(frozen=True, slots=True)
class BashoDivisionAvailabilityRow:
    """Availability counts for one represented division in one basho."""

    basho: str
    division: str
    chii_present: int
    chii_with_any_records: int
    chii_complete_records: int
    chii_partial_records: int
    chii_without_records: int
    chii_retired_incomplete: int
    chii_missing: int
    expected_day_records: int
    known_day_records: int
    missing_day_records: int
    missing_day_record_percentage: float
    known_day_record_percentage: float
    status: str


@dataclass(frozen=True, slots=True)
class DivisionAvailabilitySummaryRow:
    """Chronological availability milestones for one division."""

    division: str
    first_basho_with_any_recorded_chii: str
    first_basho_with_complete_records: str
    last_basho_with_incomplete_records: str
    continuous_complete_coverage_begins: str
    basho_with_no_records: int
    basho_with_partial_records: int
    basho_with_complete_records: int
    pre_1989_partial_expected_day_records: int
    pre_1989_partial_missing_day_records: int
    pre_1989_partial_missing_day_record_percentage: float
    pre_1989_partial_known_day_record_percentage: float
    all_partial_expected_day_records: int
    all_partial_missing_day_records: int
    all_partial_missing_day_record_percentage: float
    all_partial_known_day_record_percentage: float


@dataclass(frozen=True, slots=True)
class AvailabilityAudit:
    """All derived evidence for one selected History interval."""

    first_basho: str
    last_basho: str
    basho_count: int
    history_source: SourceIdentity
    bio_store_source: SourceIdentity
    rikishi_page_source: SourceIdentity
    chii_rows: tuple[ChiiAvailabilityRow, ...]
    basho_division_rows: tuple[BashoDivisionAvailabilityRow, ...]
    division_summary_rows: tuple[DivisionAvailabilitySummaryRow, ...]


@dataclass(frozen=True, slots=True)
class AuditOutputs:
    """Paths written by one audit run."""

    output_root: Path
    chii_csv: Path
    basho_division_csv: Path
    division_summary_csv: Path
    findings_md: Path
    manifest_json: Path
