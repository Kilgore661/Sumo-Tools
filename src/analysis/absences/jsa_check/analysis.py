"""Derive scheduling diagnostics and absence-window inference."""

from __future__ import annotations

from collections.abc import Mapping

from src.sumo_core.BasicEnums import Division, Outcome
from src.sumo_core.BasicPrimitives import Day, RikId
from src.sumo_core.History import Date, History
from src.sumo_core.Summary import Summary

from .model import (
    AbsenceInference,
    FinalRecord,
    JsaCheckResult,
    JsaCheckSummary,
    RikishiBashoWindowRow,
)


SUBSEK_DIVISIONS = frozenset(
    {
        Division.MAKUSHITA,
        Division.SANDANME,
        Division.JONIDAN,
        Division.JONOKUCHI,
    }
)
WINDOWS = (
    (1, 2),
    (3, 4),
    (5, 6),
    (7, 8),
    (9, 10),
    (11, 12),
    (13, 14, 15),
)
OUTCOME_CODES = {
    Outcome.W: "W",
    Outcome.L: "L",
    Outcome.FS: "FS",
    Outcome.FP: "FP",
    Outcome.DRAW: "d",
}


def analyse_absence_windows(
    history: History,
    final_records: Mapping[Date, Mapping[RikId, FinalRecord]],
    retirement_last_appearances: Mapping[RikId, str],
    *,
    start: tuple[int, int] = (1989, 1),
    end: tuple[int, int] | None = None,
) -> JsaCheckResult:
    """Return atomic evidence and a summary for the selected population."""

    dates = _complete_basho_dates(history, start=start, end=end)
    rows = tuple(
        row
        for date in dates
        for row in _analyse_basho(
            history,
            final_records,
            retirement_last_appearances,
            date,
        )
    )
    _require_dated_draws(rows)
    return JsaCheckResult(rows=rows, summary=_summarise(rows, dates))


def _require_dated_draws(rows: tuple[RikishiBashoWindowRow, ...]) -> None:
    """Reject History artefacts that omit draws recorded in final results."""

    mismatches = tuple(row for row in rows if not row.draws_reconcile)
    if mismatches:
        affected = ", ".join(
            f"{row.basho} rikishi {row.rikishi_id}" for row in mismatches
        )
        raise ValueError(
            "JSA Check requires a rebuilt History containing every dated draw; "
            f"draw counts do not reconcile for: {affected}"
        )


def _analyse_basho(
    history: History,
    final_records: Mapping[Date, Mapping[RikId, FinalRecord]],
    retirement_last_appearances: Mapping[RikId, str],
    date: Date,
) -> tuple[RikishiBashoWindowRow, ...]:
    """Derive one atomic row for every ranked sub-sekitori in a basho."""

    basho = history[date]
    banzuke = basho.banzuke
    selected_rikishi = {
        rikishi_id
        for rikishi_id, chii in banzuke.rikchii.items()
        if chii.level in SUBSEK_DIVISIONS
    }
    outcomes = _daily_outcomes(basho.summary, selected_rikishi)
    ordered_rikishi = sorted(
        selected_rikishi,
        key=lambda item: (banzuke.rikchii[item].ordinal(), int(item)),
    )
    return tuple(
        _derive_row(
            date=date,
            rikishi_id=rikishi_id,
            shikona=str(banzuke.rikshik[rikishi_id]),
            division=banzuke.rikchii[rikishi_id].level.name,
            chii=str(banzuke.rikchii[rikishi_id]),
            outcomes=outcomes[rikishi_id],
            final_record=final_records[date][rikishi_id],
            final_observed_basho=(
                retirement_last_appearances.get(rikishi_id) == str(date)
            ),
        )
        for rikishi_id in ordered_rikishi
    )


def _derive_row(
    *,
    date: Date,
    rikishi_id: RikId,
    shikona: str,
    division: str,
    chii: str,
    outcomes: Mapping[int, list[str]],
    final_record: FinalRecord,
    final_observed_basho: bool,
) -> RikishiBashoWindowRow:
    """Transform source facts into diagnostics and one inference result."""

    daily_outcomes = tuple(
        ";".join(outcomes[day]) if outcomes[day] else "."
        for day in range(1, 16)
    )
    daily_outcomes_unique = all(len(outcomes[day]) <= 1 for day in range(1, 16))
    window_counts = tuple(
        sum(len(outcomes[day]) for day in window)
        for window in WINDOWS
    )
    empty_windows = tuple(
        index
        for index, count in enumerate(window_counts, start=1)
        if count == 0
    )
    outcome_codes = tuple(
        code
        for day in range(1, 16)
        for code in outcomes[day]
    )
    dated_win_count = sum(code in {"W", "FS"} for code in outcome_codes)
    dated_loss_count = sum(code in {"L", "FP"} for code in outcome_codes)
    dated_draw_count = sum(code == "d" for code in outcome_codes)
    excess_outcome_count = sum(max(0, count - 1) for count in window_counts)
    inference, assigned_count, assigned_windows = _infer_absences(
        final_record.absences,
        empty_windows,
    )
    expected_empty_windows = (
        final_record.absences
        + excess_outcome_count
        - (final_record.opportunity_total - len(WINDOWS))
    )

    return RikishiBashoWindowRow(
        basho=str(date),
        rikishi_id=int(rikishi_id),
        shikona=shikona,
        division=division,
        chii=chii,
        final_record=final_record.source_text,
        recorded_wins=final_record.wins,
        recorded_losses=final_record.losses,
        recorded_absences=final_record.absences,
        recorded_draws=final_record.draws,
        opportunity_total=final_record.opportunity_total,
        final_observed_basho=final_observed_basho,
        daily_outcomes=daily_outcomes,
        daily_outcomes_unique=daily_outcomes_unique,
        window_outcome_counts=window_counts,
        empty_windows=empty_windows,
        outcome_count=len(outcome_codes),
        dated_win_count=dated_win_count,
        dated_loss_count=dated_loss_count,
        dated_draw_count=dated_draw_count,
        empty_window_count=len(empty_windows),
        excess_outcome_count=excess_outcome_count,
        jsa_observant=excess_outcome_count == 0,
        wins_reconcile=final_record.wins == dated_win_count,
        losses_reconcile=final_record.losses == dated_loss_count,
        draws_reconcile=final_record.draws == dated_draw_count,
        window_accounting_reconciles=(
            len(empty_windows) == expected_empty_windows
        ),
        absence_inference=inference,
        assigned_absence_count=assigned_count,
        assigned_absence_windows=assigned_windows,
    )


def _infer_absences(
    recorded_absences: int,
    empty_windows: tuple[int, ...],
) -> tuple[AbsenceInference, int, tuple[int, ...]]:
    """Classify exactly what the absence count and empty windows imply."""

    empty_window_count = len(empty_windows)
    if recorded_absences == 0:
        return AbsenceInference.NO_ABSENCES, 0, ()
    if empty_window_count == recorded_absences:
        return AbsenceInference.ALL_ASSIGNED, recorded_absences, empty_windows
    if empty_window_count > recorded_absences:
        return AbsenceInference.AMBIGUOUS, 0, ()
    return AbsenceInference.INCONSISTENT, 0, ()


def _summarise(
    rows: tuple[RikishiBashoWindowRow, ...],
    dates: tuple[Date, ...],
) -> JsaCheckSummary:
    """Aggregate diagnostics and inference classifications independently."""

    population = len(rows)
    observant_count = sum(row.jsa_observant for row in rows)
    non_observant_count = population - observant_count
    total_absences = sum(row.recorded_absences for row in rows)
    assigned_absences = sum(row.assigned_absence_count for row in rows)
    return JsaCheckSummary(
        first_basho=str(dates[0]),
        last_basho=str(dates[-1]),
        basho_count=len(dates),
        rikishi_basho_count=population,
        daily_unique_count=sum(row.daily_outcomes_unique for row in rows),
        daily_not_unique_count=sum(not row.daily_outcomes_unique for row in rows),
        opportunity_total_below_7_count=sum(
            row.opportunity_total < 7 for row in rows
        ),
        opportunity_total_7_count=sum(row.opportunity_total == 7 for row in rows),
        opportunity_total_8_count=sum(row.opportunity_total == 8 for row in rows),
        opportunity_total_above_8_count=sum(
            row.opportunity_total > 8 for row in rows
        ),
        short_record_final_observed_basho_count=sum(
            row.opportunity_total < 7 and row.final_observed_basho for row in rows
        ),
        short_record_not_final_observed_basho_count=sum(
            row.opportunity_total < 7 and not row.final_observed_basho for row in rows
        ),
        records_with_draws_count=sum(row.recorded_draws > 0 for row in rows),
        wins_reconciled_count=sum(row.wins_reconcile for row in rows),
        wins_not_reconciled_count=sum(not row.wins_reconcile for row in rows),
        losses_reconciled_count=sum(row.losses_reconcile for row in rows),
        losses_not_reconciled_count=sum(not row.losses_reconcile for row in rows),
        draws_reconciled_count=sum(row.draws_reconcile for row in rows),
        draws_not_reconciled_count=sum(not row.draws_reconcile for row in rows),
        observant_count=observant_count,
        non_observant_count=non_observant_count,
        observant_percentage=_percentage(observant_count, population),
        non_observant_percentage=_percentage(non_observant_count, population),
        window_accounting_reconciled_count=sum(
            row.window_accounting_reconciles for row in rows
        ),
        window_accounting_not_reconciled_count=sum(
            not row.window_accounting_reconciles for row in rows
        ),
        no_absences_count=_inference_count(rows, AbsenceInference.NO_ABSENCES),
        all_absences_assigned_count=_inference_count(
            rows,
            AbsenceInference.ALL_ASSIGNED,
        ),
        ambiguous_absence_windows_count=_inference_count(
            rows,
            AbsenceInference.AMBIGUOUS,
        ),
        inconsistent_absence_windows_count=_inference_count(
            rows,
            AbsenceInference.INCONSISTENT,
        ),
        positive_absence_record_count=sum(row.recorded_absences > 0 for row in rows),
        total_absence_count=total_absences,
        assigned_absence_count=assigned_absences,
        assigned_absence_percentage=(
            _percentage(assigned_absences, total_absences)
            if total_absences
            else None
        ),
    )


def _inference_count(
    rows: tuple[RikishiBashoWindowRow, ...],
    inference: AbsenceInference,
) -> int:
    return sum(row.absence_inference is inference for row in rows)


def _complete_basho_dates(
    history: History,
    *,
    start: tuple[int, int],
    end: tuple[int, int] | None,
) -> tuple[Date, ...]:
    """Select the complete prefix of the requested History interval."""

    candidates = tuple(
        date
        for date in sorted(history)
        if _date_key(date) >= start and (end is None or _date_key(date) <= end)
    )
    complete_indices = [
        index for index, date in enumerate(candidates) if Day(15) in history[date].summary
    ]
    if not complete_indices:
        raise ValueError("JSA Check selected no complete basho")
    selected = candidates[: complete_indices[-1] + 1]
    incomplete = [
        str(date) for date in selected if Day(15) not in history[date].summary
    ]
    if incomplete:
        raise ValueError(
            "JSA Check found incomplete historical basho before its last complete "
            f"basho: {', '.join(incomplete)}"
        )
    return selected


def _daily_outcomes(
    summary: Summary,
    selected_rikishi: set[RikId],
) -> dict[RikId, dict[int, list[str]]]:
    """Index every selected rikishi's recorded outcomes by basho day."""

    result = {
        rikishi_id: {day: [] for day in range(1, 16)}
        for rikishi_id in selected_rikishi
    }
    for day in range(1, 16):
        for bout in summary[Day(day)].results_lookup.values():
            if bout.rikishi1 in selected_rikishi:
                result[bout.rikishi1][day].append(OUTCOME_CODES[bout.outcome1])
            if bout.rikishi2 in selected_rikishi:
                result[bout.rikishi2][day].append(OUTCOME_CODES[bout.outcome2])
    return result


def _percentage(numerator: int, denominator: int) -> float:
    return 100.0 * numerator / denominator


def _date_key(date: Date) -> tuple[int, int]:
    return int(date.year), int(date.month)
