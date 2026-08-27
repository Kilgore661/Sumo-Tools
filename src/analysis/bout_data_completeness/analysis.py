"""Build literal-chii record-availability evidence from banzuke and hoshi data."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Mapping

from src.infra.get_bios.api import BioBashoDate
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .model import (
    AvailabilityAudit,
    BashoDivisionAvailabilityRow,
    ChiiAvailabilityRow,
    DivisionAvailabilitySummaryRow,
    SourceIdentity,
)
from .source import EXPECTED_HOSHI_SLOTS, load_rikishi_pages


DIVISION_ORDER = {
    "MAKUUCHI": 0,
    "JURYO": 1,
    "MAKUSHITA": 2,
    "SANDANME": 3,
    "JONIDAN": 4,
    "JONOKUCHI": 5,
}


def analyse_availability(
    history: History,
    *,
    history_source: SourceIdentity,
    bio_store_source: SourceIdentity,
    intai_by_rikishi: Mapping[RikId, BioBashoDate | None],
    bio_dir: Path,
    start: tuple[int, int] = (1958, 1),
    end: tuple[int, int] = (2026, 3),
) -> AvailabilityAudit:
    """Audit every literal chii-rikishi occurrence in the selected banzuke range."""

    dates = tuple(
        date for date in sorted(history) if start <= _date_key(date) <= end
    )
    if not dates:
        raise ValueError("Bout-data completeness audit selected no basho")

    required_bashos = defaultdict(set)
    for date in dates:
        for rikishi_id in history[date].banzuke.riks:
            required_bashos[rikishi_id].add(str(date))
    pages, page_source = load_rikishi_pages(bio_dir, required_bashos)

    chii_rows: list[ChiiAvailabilityRow] = []
    for date in dates:
        basho_label = str(date)
        banzuke = history[date].banzuke
        for rikishi_id in sorted(
            banzuke.riks,
            key=lambda item: (banzuke.rikchii[item].ordinal(), int(item)),
        ):
            try:
                hoshi = pages[rikishi_id][basho_label]
            except KeyError as error:
                raise ValueError(
                    f"Rikishi {int(rikishi_id)} is on the {basho_label} banzuke "
                    "but the cached Rikishi.aspx page has no matching career row"
                ) from error
            try:
                intai = intai_by_rikishi[rikishi_id]
            except KeyError as error:
                raise ValueError(
                    f"Rikishi {int(rikishi_id)} is on the {basho_label} banzuke "
                    "but is absent from the BioStore"
                ) from error
            chii = banzuke.rikchii[rikishi_id]
            chii_rows.append(
                ChiiAvailabilityRow(
                    basho=basho_label,
                    chii=str(chii),
                    chii_ordinal=chii.ordinal(),
                    division=division_for(chii).name,
                    rikishi_id=int(rikishi_id),
                    shikona=str(banzuke.rikshik[rikishi_id]),
                    recorded=hoshi.recorded,
                    complete=hoshi.complete,
                    retired=intai is not None and str(intai) == basho_label,
                    known_hoshi_symbol_count=hoshi.known_symbol_count,
                    empty_hoshi_symbol_count=hoshi.empty_symbol_count,
                    hoshi_slot_count=hoshi.slot_count,
                )
            )

    basho_division_rows = build_basho_division_rows(chii_rows)
    division_summary_rows = build_division_summary_rows(basho_division_rows)
    return AvailabilityAudit(
        first_basho=str(dates[0]),
        last_basho=str(dates[-1]),
        basho_count=len(dates),
        history_source=history_source,
        bio_store_source=bio_store_source,
        rikishi_page_source=page_source,
        chii_rows=tuple(chii_rows),
        basho_division_rows=basho_division_rows,
        division_summary_rows=division_summary_rows,
    )


def build_basho_division_rows(
    chii_rows: list[ChiiAvailabilityRow],
) -> tuple[BashoDivisionAvailabilityRow, ...]:
    """Classify each represented basho/division as none, partial or complete."""

    groups: dict[tuple[str, str], list[ChiiAvailabilityRow]] = defaultdict(list)
    for row in chii_rows:
        groups[(row.basho, row.division)].append(row)

    result = []
    for (basho, division), rows in groups.items():
        present = len(rows)
        with_any_records = sum(row.recorded for row in rows)
        complete_records = sum(row.complete for row in rows)
        partial_records = sum(row.recorded and not row.complete for row in rows)
        without_records = sum(not row.recorded for row in rows)
        retired_incomplete = sum(row.retired and not row.complete for row in rows)
        missing = sum(not row.complete and not row.retired for row in rows)
        eligible_rows = [row for row in rows if not row.retired]
        expected_day_records = EXPECTED_HOSHI_SLOTS * len(eligible_rows)
        known_day_records = sum(
            row.known_hoshi_symbol_count for row in eligible_rows
        )
        missing_day_records = expected_day_records - known_day_records
        if with_any_records == 0 and missing > 0:
            status = "none"
        elif missing == 0:
            status = "complete"
        else:
            status = "partial"
        result.append(
            BashoDivisionAvailabilityRow(
                basho=basho,
                division=division,
                chii_present=present,
                chii_with_any_records=with_any_records,
                chii_complete_records=complete_records,
                chii_partial_records=partial_records,
                chii_without_records=without_records,
                chii_retired_incomplete=retired_incomplete,
                chii_missing=missing,
                expected_day_records=expected_day_records,
                known_day_records=known_day_records,
                missing_day_records=missing_day_records,
                missing_day_record_percentage=_percentage(
                    missing_day_records, expected_day_records
                ),
                known_day_record_percentage=_percentage(
                    known_day_records, expected_day_records
                ),
                status=status,
            )
        )
    result.sort(key=lambda row: (row.basho, DIVISION_ORDER[row.division]))
    return tuple(result)


def build_division_summary_rows(
    rows: tuple[BashoDivisionAvailabilityRow, ...],
) -> tuple[DivisionAvailabilitySummaryRow, ...]:
    """Derive division milestones without imposing a completeness threshold."""

    by_division: dict[str, list[BashoDivisionAvailabilityRow]] = defaultdict(list)
    for row in rows:
        by_division[row.division].append(row)

    result = []
    for division in sorted(by_division, key=lambda item: DIVISION_ORDER[item]):
        division_rows = sorted(by_division[division], key=lambda row: row.basho)
        pre_1989_partial_density = _partial_density(
            row
            for row in division_rows
            if row.basho < "1989/01" and row.status == "partial"
        )
        all_partial_density = _partial_density(
            row for row in division_rows if row.status == "partial"
        )
        incomplete_indices = [
            index
            for index, row in enumerate(division_rows)
            if row.status != "complete"
        ]
        if not incomplete_indices:
            continuous_from = division_rows[0].basho
        elif incomplete_indices[-1] + 1 < len(division_rows):
            continuous_from = division_rows[incomplete_indices[-1] + 1].basho
        else:
            continuous_from = ""

        result.append(
            DivisionAvailabilitySummaryRow(
                division=division,
                first_basho_with_any_recorded_chii=_first_basho(
                    division_rows,
                    lambda row: row.chii_with_any_records > 0,
                ),
                first_basho_with_complete_records=_first_basho(
                    division_rows,
                    lambda row: row.status == "complete",
                ),
                last_basho_with_incomplete_records=(
                    division_rows[incomplete_indices[-1]].basho
                    if incomplete_indices
                    else ""
                ),
                continuous_complete_coverage_begins=continuous_from,
                basho_with_no_records=sum(row.status == "none" for row in division_rows),
                basho_with_partial_records=sum(
                    row.status == "partial" for row in division_rows
                ),
                basho_with_complete_records=sum(
                    row.status == "complete" for row in division_rows
                ),
                pre_1989_partial_expected_day_records=pre_1989_partial_density[0],
                pre_1989_partial_missing_day_records=pre_1989_partial_density[1],
                pre_1989_partial_missing_day_record_percentage=pre_1989_partial_density[2],
                pre_1989_partial_known_day_record_percentage=pre_1989_partial_density[3],
                all_partial_expected_day_records=all_partial_density[0],
                all_partial_missing_day_records=all_partial_density[1],
                all_partial_missing_day_record_percentage=all_partial_density[2],
                all_partial_known_day_record_percentage=all_partial_density[3],
            )
        )
    return tuple(result)


def division_for(chii: Chii) -> Division:
    """Return the six-division coordinate for one literal Chii."""

    if isinstance(chii.level, MSD):
        return Division.MAKUUCHI
    return chii.level


def _first_basho(rows, predicate) -> str:
    return next((row.basho for row in rows if predicate(row)), "")


def _partial_density(
    rows,
) -> tuple[int, int, float, float]:
    selected = tuple(rows)
    expected = sum(row.expected_day_records for row in selected)
    missing = sum(row.missing_day_records for row in selected)
    known = expected - missing
    return expected, missing, _percentage(missing, expected), _percentage(known, expected)


def _percentage(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 3) if denominator else 0.0


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)
