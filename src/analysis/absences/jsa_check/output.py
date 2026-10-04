"""Write atomic evidence and a specification-shaped experiment summary."""

from __future__ import annotations

import csv
from pathlib import Path

from .model import (
    JsaCheckOutputs,
    JsaCheckResult,
    JsaCheckRunMetadata,
    JsaCheckSummary,
)


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/absences/jsa_check")


def write_outputs(
    result: JsaCheckResult,
    *,
    metadata: JsaCheckRunMetadata,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> JsaCheckOutputs:
    """Write the complete declared output set for one experiment run."""

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = JsaCheckOutputs(
        output_root=output_root,
        rows_csv=output_root / "rikishi_basho_absence_inference.csv",
        summary_txt=output_root / "summary.txt",
    )
    _write_rows_csv(result, outputs.rows_csv)
    outputs.summary_txt.write_text(
        format_summary(result.summary, metadata),
        encoding="utf-8",
    )
    return outputs


def _write_rows_csv(result: JsaCheckResult, path: Path) -> None:
    """Write one inspectable row per rikishi-basho."""

    header = (
        "basho",
        "rikishi_id",
        "shikona",
        "division",
        "chii",
        "final_record",
        "recorded_wins",
        "recorded_losses",
        "recorded_absences",
        "recorded_draws",
        "opportunity_total",
        "final_observed_basho",
        *(f"day_{day:02d}" for day in range(1, 16)),
        "daily_outcomes_unique",
        *(f"window_{window}_outcome_count" for window in range(1, 8)),
        "empty_windows",
        "outcome_count",
        "dated_win_count",
        "dated_loss_count",
        "dated_draw_count",
        "empty_window_count",
        "excess_outcome_count",
        "jsa_observant",
        "wins_reconcile",
        "losses_reconcile",
        "draws_reconcile",
        "window_accounting_reconciles",
        "absence_inference",
        "assigned_absence_count",
        "assigned_absence_windows",
    )
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        for row in result.rows:
            writer.writerow(
                (
                    row.basho,
                    row.rikishi_id,
                    row.shikona,
                    row.division,
                    row.chii,
                    row.final_record,
                    row.recorded_wins,
                    row.recorded_losses,
                    row.recorded_absences,
                    row.recorded_draws,
                    row.opportunity_total,
                    row.final_observed_basho,
                    *row.daily_outcomes,
                    row.daily_outcomes_unique,
                    *row.window_outcome_counts,
                    _window_list(row.empty_windows),
                    row.outcome_count,
                    row.dated_win_count,
                    row.dated_loss_count,
                    row.dated_draw_count,
                    row.empty_window_count,
                    row.excess_outcome_count,
                    row.jsa_observant,
                    row.wins_reconcile,
                    row.losses_reconcile,
                    row.draws_reconcile,
                    row.window_accounting_reconciles,
                    row.absence_inference.value,
                    row.assigned_absence_count,
                    _window_list(row.assigned_absence_windows),
                )
            )


def format_summary(
    summary: JsaCheckSummary,
    metadata: JsaCheckRunMetadata,
) -> str:
    """Render diagnostics separately from the central inference result."""

    population = summary.rikishi_basho_count
    lines = [
        "Run metadata",
        "------------",
        f"Generated at: {metadata.generated_at}",
        f"History source: {metadata.history_source}",
        f"Final-record source: {metadata.final_records_source}",
        f"Retirement artifact: {metadata.retirement_source}",
        "",
        f"First basho: {summary.first_basho}",
        f"Last basho: {summary.last_basho}",
        f"Basho: {summary.basho_count:,}",
        f"Rikishi-basho records: {population:,}",
        "",
        "Source sanitation",
        "-----------------",
        "Daily outcomes unique: "
        + _count_percentage(summary.daily_unique_count, population),
        "Daily outcomes not unique: "
        + _count_percentage(summary.daily_not_unique_count, population),
        "",
        "Opportunity totals",
        "------------------",
        "Below 7: "
        + _count_percentage(summary.opportunity_total_below_7_count, population),
        "7: " + _count_percentage(summary.opportunity_total_7_count, population),
        "8: " + _count_percentage(summary.opportunity_total_8_count, population),
        "Above 8: "
        + _count_percentage(summary.opportunity_total_above_8_count, population),
        "Below 7 and final observed basho: "
        + _count_percentage(
            summary.short_record_final_observed_basho_count,
            population,
        ),
        "Below 7 and not final observed basho: "
        + _count_percentage(
            summary.short_record_not_final_observed_basho_count,
            population,
        ),
        "Records with draws: "
        + _count_percentage(summary.records_with_draws_count, population),
        "",
        "Dated-result reconciliation",
        "---------------------------",
        "Wins reconciled: "
        + _count_percentage(summary.wins_reconciled_count, population),
        "Wins not reconciled: "
        + _count_percentage(summary.wins_not_reconciled_count, population),
        "Losses reconciled: "
        + _count_percentage(summary.losses_reconciled_count, population),
        "Losses not reconciled: "
        + _count_percentage(summary.losses_not_reconciled_count, population),
        "Draws reconciled: "
        + _count_percentage(summary.draws_reconciled_count, population),
        "Draws not reconciled: "
        + _count_percentage(summary.draws_not_reconciled_count, population),
        "",
        "Scheduling shape",
        "----------------",
        "At most one outcome per window: "
        + _count_percentage(summary.observant_count, population),
        "At least one double-occupied window: "
        + _count_percentage(summary.non_observant_count, population),
        "Window accounting reconciled: "
        + _count_percentage(summary.window_accounting_reconciled_count, population),
        "Window accounting not reconciled: "
        + _count_percentage(
            summary.window_accounting_not_reconciled_count,
            population,
        ),
        "",
        "Absence inference",
        "-----------------",
        "Records with no absences: "
        + _count_percentage(summary.no_absences_count, population),
        "All positive absences assigned: "
        + _count_percentage(summary.all_absences_assigned_count, population),
        "Ambiguous positive-absence records: "
        + _count_percentage(summary.ambiguous_absence_windows_count, population),
        "Inconsistent absence/empty-window records: "
        + _count_percentage(summary.inconsistent_absence_windows_count, population),
        "Positive-absence records: "
        + _count_percentage(summary.positive_absence_record_count, population),
        f"Recorded absences: {summary.total_absence_count:,}",
        f"Absences assigned to windows: {summary.assigned_absence_count:,}",
        "Assigned absences: " + _optional_percentage(summary.assigned_absence_percentage),
        "",
    ]
    return "\n".join(lines)


def _window_list(windows: tuple[int, ...]) -> str:
    return ";".join(str(window) for window in windows)


def _count_percentage(count: int, denominator: int) -> str:
    return f"{count:,} ({100.0 * count / denominator:.6f}%)"


def _optional_percentage(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}%"
