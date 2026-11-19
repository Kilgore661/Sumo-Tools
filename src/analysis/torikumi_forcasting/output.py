"""Persist greedy torikumi-forecasting results."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .model import AnalysisResult, OutputPaths


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/torikumi_forcasting")


def write_outputs(
    result: AnalysisResult,
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
        failure_diagnostics_csv=run_directory / "failure_diagnostics.csv",
        report_md=run_directory / "report.md",
        manifest_json=run_directory / "manifest.json",
    )
    _write_cases(result, outputs.cases_csv)
    _write_exclusions(result, outputs.excluded_cases_csv)
    _write_pairs(result, outputs.forecast_pairs_csv)
    _write_heya_diagnostics(result, outputs.heya_diagnostics_csv)
    _write_failure_diagnostics(result, outputs.failure_diagnostics_csv)
    outputs.report_md.write_text(_render_report(result), encoding="utf-8")

    manifest = {
        "analysis": "torikumi_forcasting_greedy",
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
                if result.holdout_first_basho is not None
                else None
            ),
        },
        "contracts": {
            "population": "target-day published makuuchi participants",
            "standings": "W+FS through d-2 descending, then Chii ordinal",
            "prior_opponents": "scheduled regular pairs through d-1",
            "eligibility": "not prior opponents and not same heya",
            "missing_heya": "unique heya<rikid>",
            "matching": "literal greedy; first eligible remaining opponent; no backtracking",
            "family_restriction": "not represented",
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


def _write_cases(result: AnalysisResult, path: Path) -> None:
    fields = [
        "split", "basho", "day", "population_size", "actual_pair_count",
        "forecast_pair_count", "recovered_pairs", "pair_recovery_rate",
        "actual_unmatched", "forecast_unpaired", "unmatched_correct",
        "success", "exact", "synthetic_heya_count",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in result.cases:
            writer.writerow({
                "split": row.split,
                "basho": str(row.case.basho),
                "day": row.case.day,
                "population_size": len(row.case.standings),
                "actual_pair_count": len(row.case.actual_pairs),
                "forecast_pair_count": len(row.forecast.pairs),
                "recovered_pairs": row.recovered_pairs,
                "pair_recovery_rate": f"{row.pair_recovery_rate:.12f}",
                "actual_unmatched": _ids(row.case.actual_unmatched),
                "forecast_unpaired": _ids(item.rikid for item in row.forecast.unpaired),
                "unmatched_correct": _optional_bool(row.unmatched_correct),
                "success": int(row.forecast.success),
                "exact": int(row.exact),
                "synthetic_heya_count": sum(
                    item.synthetic_heya for item in row.case.standings
                ),
            })


def _write_exclusions(result: AnalysisResult, path: Path) -> None:
    fields = [
        "basho", "day", "population_size", "actual_unmatched_count",
        "parity_minimum", "reason",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in result.exclusions:
            writer.writerow({
                "basho": str(row.basho),
                "day": row.day,
                "population_size": row.population_size,
                "actual_unmatched_count": row.actual_unmatched_count,
                "parity_minimum": row.parity_minimum,
                "reason": row.reason,
            })


def _write_pairs(result: AnalysisResult, path: Path) -> None:
    fields = [
        "split", "basho", "day", "forecast_order", "east_id", "east_shikona",
        "east_chii", "east_wins", "east_heya", "east_synthetic_heya",
        "west_id", "west_shikona", "west_chii", "west_wins", "west_heya",
        "west_synthetic_heya", "actual_pair",
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
                    "east_id": int(pair.east.rikid),
                    "east_shikona": pair.east.shikona,
                    "east_chii": str(pair.east.chii),
                    "east_wins": pair.east.wins,
                    "east_heya": pair.east.heya,
                    "east_synthetic_heya": int(pair.east.synthetic_heya),
                    "west_id": int(pair.west.rikid),
                    "west_shikona": pair.west.shikona,
                    "west_chii": str(pair.west.chii),
                    "west_wins": pair.west.wins,
                    "west_heya": pair.west.heya,
                    "west_synthetic_heya": int(pair.west.synthetic_heya),
                    "actual_pair": int(pair.pair in case_result.case.actual_pairs),
                })


def _write_heya_diagnostics(result: AnalysisResult, path: Path) -> None:
    fields = ["split", "basho", "day", "rikid", "shikona", "assigned_heya"]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case_result in result.cases:
            for standing in case_result.case.standings:
                if standing.synthetic_heya:
                    writer.writerow({
                        "split": case_result.split,
                        "basho": str(case_result.case.basho),
                        "day": case_result.case.day,
                        "rikid": int(standing.rikid),
                        "shikona": standing.shikona,
                        "assigned_heya": standing.heya,
                    })


def _write_failure_diagnostics(result: AnalysisResult, path: Path) -> None:
    fields = [
        "split", "basho", "day", "forecast_success", "rikid", "shikona",
        "position", "wins", "chii", "heya", "candidate_rejections",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case_result in result.cases:
            standing_by_id = {row.rikid: row for row in case_result.case.standings}
            for diagnostic in case_result.forecast.diagnostics:
                standing = standing_by_id[diagnostic.rikishi]
                rejections = "; ".join(
                    f"{int(row.opponent)}:{'+'.join(row.reasons)}"
                    for row in diagnostic.rejections
                )
                writer.writerow({
                    "split": case_result.split,
                    "basho": str(case_result.case.basho),
                    "day": case_result.case.day,
                    "forecast_success": int(case_result.forecast.success),
                    "rikid": int(standing.rikid),
                    "shikona": standing.shikona,
                    "position": standing.position,
                    "wins": standing.wins,
                    "chii": str(standing.chii),
                    "heya": standing.heya,
                    "candidate_rejections": rejections,
                })


def _render_report(result: AnalysisResult) -> str:
    lines = [
        "# Greedy Torikumi Forecasting", "",
        "## Scope", "",
        f"- Completed basho: {result.included_basho_count:,}",
        f"- Selected range: {result.selected_first_basho} to {result.selected_last_basho}",
        f"- Target days: {result.first_day} to 15", "",
        f"- Excluded extra-cross-division cases: {len(result.exclusions):,}", "",
        "## Results", "",
        "| Split | Cases | Complete | Failures | Mean pair recovery | Exact cards | Odd cases | Correct unmatched |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for split in ("all", "development", "holdout"):
        rows = result.cases if split == "all" else tuple(
            row for row in result.cases if row.split == split
        )
        if not rows:
            continue
        complete = sum(row.forecast.success for row in rows)
        odd = [row for row in rows if row.case.actual_unmatched]
        lines.append(
            f"| {split} | {len(rows):,} | {complete:,} | {len(rows)-complete:,} | "
            f"{sum(row.pair_recovery_rate for row in rows)/len(rows):.3%} | "
            f"{sum(row.exact for row in rows):,} | {len(odd):,} | "
            f"{sum(row.unmatched_correct is True for row in odd):,} |"
        )

    lines.extend(["", "## By day", "", "| Day | Cases | Failures | Mean pair recovery | Exact cards |", "|---:|---:|---:|---:|---:|"])
    for day in range(result.first_day, 16):
        rows = [row for row in result.cases if row.case.day == day]
        lines.append(
            f"| {day} | {len(rows):,} | {sum(not row.forecast.success for row in rows):,} | "
            f"{sum(row.pair_recovery_rate for row in rows)/len(rows):.3%} | "
            f"{sum(row.exact for row in rows):,} |"
        )

    lines.extend([
        "", "## Exclusions by day", "",
        "| Day | Extra-cross-division cases |", "|---:|---:|",
    ])
    for day in range(result.first_day, 16):
        lines.append(
            f"| {day} | {sum(row.day == day for row in result.exclusions):,} |"
        )

    synthetic = sum(
        standing.synthetic_heya
        for row in result.cases
        for standing in row.case.standings
    )
    lines.extend([
        "", "## Diagnostics", "",
        f"- Synthetic-heya case appearances: {synthetic:,}",
        "- Greedy failures retain their partial pairs and list every unpaired rikishi in `failure_diagnostics.csv`.",
        "- This report evaluates the predeclared greedy baseline; it does not repair failures.", "",
    ])
    return "\n".join(lines)


def _manifest_counts(result: AnalysisResult) -> dict[str, object]:
    statuses = Counter("success" if row.forecast.success else "failure" for row in result.cases)
    return {
        "cases": len(result.cases),
        "excluded_extra_cross_division_cases": len(result.exclusions),
        "case_status": dict(sorted(statuses.items())),
        "forecast_pairs": sum(len(row.forecast.pairs) for row in result.cases),
        "recovered_pairs": sum(row.recovered_pairs for row in result.cases),
        "exact_cards": sum(row.exact for row in result.cases),
        "odd_population_cases": sum(bool(row.case.actual_unmatched) for row in result.cases),
        "correct_unmatched": sum(row.unmatched_correct is True for row in result.cases),
        "synthetic_heya_case_appearances": sum(
            standing.synthetic_heya
            for row in result.cases
            for standing in row.case.standings
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
        run_directory = output_root / timestamp.strftime("greedy_%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory
