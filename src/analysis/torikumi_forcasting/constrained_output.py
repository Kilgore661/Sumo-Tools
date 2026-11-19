"""Persist constrained-matching torikumi forecasts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .constrained import allowed_opponent_counts, prohibited_edges
from .model import ConstrainedAnalysisResult, OutputPaths
from .output import DEFAULT_OUTPUT_ROOT


def write_constrained_outputs(
    result: ConstrainedAnalysisResult,
    *,
    sources: dict[str, object],
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    generated_at: datetime | None = None,
) -> OutputPaths:
    timestamp, run_directory = _create_run_directory(output_root, generated_at)
    outputs = OutputPaths(
        run_directory=run_directory,
        cases_csv=run_directory / "cases.csv",
        excluded_cases_csv=run_directory / "excluded_cases.csv",
        forecast_pairs_csv=run_directory / "forecast_pairs.csv",
        heya_diagnostics_csv=run_directory / "heya_diagnostics.csv",
        failure_diagnostics_csv=run_directory / "infeasibility_diagnostics.csv",
        report_md=run_directory / "report.md",
        manifest_json=run_directory / "manifest.json",
    )
    _write_cases(result, outputs.cases_csv)
    _write_exclusions(result, outputs.excluded_cases_csv)
    _write_pairs(result, outputs.forecast_pairs_csv)
    _write_heya_diagnostics(result, outputs.heya_diagnostics_csv)
    _write_infeasibility_diagnostics(result, outputs.failure_diagnostics_csv)
    outputs.report_md.write_text(_render_report(result), encoding="utf-8")
    manifest = {
        "analysis": "torikumi_forcasting_constrained",
        "status": "complete",
        "generated_at_utc": timestamp.isoformat(),
        "sources": sources,
        "selection": {
            "selected_first_basho": str(result.selected_first_basho),
            "selected_last_basho": str(result.selected_last_basho),
            "included_completed_basho": result.included_basho_count,
            "excluded_incomplete_basho": result.excluded_incomplete_basho_count,
            "first_day": result.first_day,
            "last_day": 15,
            "holdout_first_basho": (
                str(result.holdout_first_basho)
                if result.holdout_first_basho is not None else None
            ),
        },
        "contracts": {
            "population": "target-day published makuuchi participants",
            "standings": "W+FS through d-2 descending, then Chii ordinal",
            "eligibility": "not prior opponents and not same heya",
            "objective": "minimum sum of absolute standings-position distances",
            "unmatched": "zero cost; count fixed to population parity",
            "acceptance": "CP-SAT OPTIMAL only",
            "equal_optima": "one solution reported; no secondary preference",
        },
        "counts": _manifest_counts(result),
        "outputs": {
            field: getattr(outputs, field).name
            for field in outputs.__dataclass_fields__
            if field != "run_directory"
        },
    }
    outputs.manifest_json.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return outputs


def _write_cases(result: ConstrainedAnalysisResult, path: Path) -> None:
    fields = [
        "split", "basho", "day", "status", "population_size",
        "actual_pair_count", "forecast_pair_count", "recovered_pairs",
        "pair_recovery_rate", "actual_unmatched", "forecast_unmatched",
        "unmatched_correct", "exact", "objective_cost",
        "best_objective_bound", "solve_seconds", "synthetic_heya_count",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in result.cases:
            writer.writerow({
                "split": row.split,
                "basho": str(row.case.basho),
                "day": row.case.day,
                "status": row.forecast.status,
                "population_size": len(row.case.standings),
                "actual_pair_count": len(row.case.actual_pairs),
                "forecast_pair_count": len(row.forecast.pairs),
                "recovered_pairs": row.recovered_pairs,
                "pair_recovery_rate": f"{row.pair_recovery_rate:.12f}",
                "actual_unmatched": _ids(row.case.actual_unmatched),
                "forecast_unmatched": _ids(item.rikid for item in row.forecast.unpaired),
                "unmatched_correct": _optional_bool(row.unmatched_correct),
                "exact": int(row.exact),
                "objective_cost": row.forecast.objective_cost,
                "best_objective_bound": row.forecast.best_objective_bound,
                "solve_seconds": f"{row.forecast.solve_seconds:.9f}",
                "synthetic_heya_count": sum(
                    item.synthetic_heya for item in row.case.standings
                ),
            })


def _write_exclusions(result: ConstrainedAnalysisResult, path: Path) -> None:
    fields = [
        "basho", "day", "population_size", "actual_unmatched_count",
        "parity_minimum", "reason",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in result.exclusions:
            writer.writerow({
                "basho": str(row.basho), "day": row.day,
                "population_size": row.population_size,
                "actual_unmatched_count": row.actual_unmatched_count,
                "parity_minimum": row.parity_minimum, "reason": row.reason,
            })


def _write_pairs(result: ConstrainedAnalysisResult, path: Path) -> None:
    fields = [
        "split", "basho", "day", "forecast_order", "east_id", "east_shikona",
        "east_chii", "east_wins", "east_heya", "west_id", "west_shikona",
        "west_chii", "west_wins", "west_heya", "pair_cost", "actual_pair",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case_result in result.cases:
            for order, pair in enumerate(case_result.forecast.pairs, start=1):
                writer.writerow({
                    "split": case_result.split,
                    "basho": str(case_result.case.basho),
                    "day": case_result.case.day,
                    "forecast_order": order,
                    "east_id": int(pair.east.rikid), "east_shikona": pair.east.shikona,
                    "east_chii": str(pair.east.chii), "east_wins": pair.east.wins,
                    "east_heya": pair.east.heya,
                    "west_id": int(pair.west.rikid), "west_shikona": pair.west.shikona,
                    "west_chii": str(pair.west.chii), "west_wins": pair.west.wins,
                    "west_heya": pair.west.heya,
                    "pair_cost": abs(pair.east.position - pair.west.position),
                    "actual_pair": int(pair.pair in case_result.case.actual_pairs),
                })


def _write_heya_diagnostics(result: ConstrainedAnalysisResult, path: Path) -> None:
    fields = ["split", "basho", "day", "rikid", "shikona", "assigned_heya"]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case_result in result.cases:
            for standing in case_result.case.standings:
                if standing.synthetic_heya:
                    writer.writerow({
                        "split": case_result.split, "basho": str(case_result.case.basho),
                        "day": case_result.case.day, "rikid": int(standing.rikid),
                        "shikona": standing.shikona, "assigned_heya": standing.heya,
                    })


def _write_infeasibility_diagnostics(
    result: ConstrainedAnalysisResult, path: Path
) -> None:
    fields = [
        "split", "basho", "day", "rikid", "shikona",
        "allowed_opponent_count", "prohibited_edges",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in result.cases:
            if row.forecast.status != "INFEASIBLE":
                continue
            counts = allowed_opponent_counts(row.case)
            prohibited = list(prohibited_edges(row.case))
            by_rikishi = {standing.rikid: [] for standing in row.case.standings}
            for first, second, reasons in prohibited:
                detail = f"{int(first)}-{int(second)}:{'+'.join(reasons)}"
                by_rikishi[first].append(detail)
                by_rikishi[second].append(detail)
            for standing in row.case.standings:
                writer.writerow({
                    "split": row.split, "basho": str(row.case.basho),
                    "day": row.case.day, "rikid": int(standing.rikid),
                    "shikona": standing.shikona,
                    "allowed_opponent_count": counts[standing.rikid],
                    "prohibited_edges": "; ".join(by_rikishi[standing.rikid]),
                })


def _render_report(result: ConstrainedAnalysisResult) -> str:
    lines = [
        "# Constrained Torikumi Forecasting", "", "## Scope", "",
        f"- Completed basho: {result.included_basho_count:,}",
        f"- Selected range: {result.selected_first_basho} to {result.selected_last_basho}",
        f"- Target days: {result.first_day} to 15",
        f"- Excluded extra-cross-division cases: {len(result.exclusions):,}", "",
        "## Results", "",
        "| Split | Cases | Optimal | Mean pair recovery | Exact cards | Odd cases | Correct unmatched | Mean solve ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in ("all", "development", "holdout"):
        rows = result.cases if split == "all" else tuple(
            row for row in result.cases if row.split == split
        )
        if not rows:
            continue
        odd = [row for row in rows if row.case.actual_unmatched]
        lines.append(
            f"| {split} | {len(rows):,} | {sum(row.forecast.status == 'OPTIMAL' for row in rows):,} | "
            f"{sum(row.pair_recovery_rate for row in rows)/len(rows):.3%} | "
            f"{sum(row.exact for row in rows):,} | {len(odd):,} | "
            f"{sum(row.unmatched_correct is True for row in odd):,} | "
            f"{1000*sum(row.forecast.solve_seconds for row in rows)/len(rows):.3f} |"
        )
    lines.extend([
        "", "## By day", "",
        "| Day | Cases | Mean pair recovery | Exact cards | Mean objective |",
        "|---:|---:|---:|---:|---:|",
    ])
    for day in range(result.first_day, 16):
        rows = [row for row in result.cases if row.case.day == day]
        if not rows:
            continue
        lines.append(
            f"| {day} | {len(rows):,} | "
            f"{sum(row.pair_recovery_rate for row in rows)/len(rows):.3%} | "
            f"{sum(row.exact for row in rows):,} | "
            f"{sum(row.forecast.objective_cost or 0 for row in rows)/len(rows):.3f} |"
        )
    lines.extend([
        "", "## Diagnostics", "",
        f"- Infeasible cases: {sum(row.forecast.status == 'INFEASIBLE' for row in result.cases):,}",
        f"- Maximum solve time: {max((row.forecast.solve_seconds for row in result.cases), default=0):.6f} seconds",
        "- Only solutions proved optimal by CP-SAT are included.", "",
    ])
    return "\n".join(lines)


def _manifest_counts(result: ConstrainedAnalysisResult) -> dict[str, object]:
    statuses = Counter(row.forecast.status for row in result.cases)
    return {
        "cases": len(result.cases),
        "solver_status": dict(sorted(statuses.items())),
        "excluded_extra_cross_division_cases": len(result.exclusions),
        "forecast_pairs": sum(len(row.forecast.pairs) for row in result.cases),
        "recovered_pairs": sum(row.recovered_pairs for row in result.cases),
        "exact_cards": sum(row.exact for row in result.cases),
        "correct_unmatched": sum(row.unmatched_correct is True for row in result.cases),
        "total_solve_seconds": sum(row.forecast.solve_seconds for row in result.cases),
        "maximum_solve_seconds": max(
            (row.forecast.solve_seconds for row in result.cases), default=0
        ),
    }


def _ids(values) -> str:
    return ";".join(str(int(value)) for value in values)


def _optional_bool(value: bool | None) -> str:
    return "" if value is None else str(int(value))


def _create_run_directory(
    output_root: Path, generated_at: datetime | None
) -> tuple[datetime, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = (generated_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    timestamp = timestamp.replace(microsecond=0)
    while True:
        run_directory = output_root / timestamp.strftime("constrained_%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory
