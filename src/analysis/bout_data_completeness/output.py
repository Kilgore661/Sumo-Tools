"""Write CSV evidence, division findings and provenance for the audit."""

from __future__ import annotations

import csv
from dataclasses import asdict, fields
from datetime import datetime, timezone
import json
from pathlib import Path

from .model import AuditOutputs, AvailabilityAudit


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/bout_data_completeness")


def write_outputs(
    audit: AvailabilityAudit,
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> AuditOutputs:
    """Replace the declared output set with one internally consistent audit."""

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = AuditOutputs(
        output_root=output_root,
        chii_csv=output_root / "basho_chii_record_availability.csv",
        basho_division_csv=output_root / "basho_division_record_availability.csv",
        division_summary_csv=output_root / "division_record_availability_summary.csv",
        findings_md=output_root / "findings.md",
        manifest_json=output_root / "manifest.json",
    )
    _write_dataclass_csv(audit.chii_rows, outputs.chii_csv)
    _write_dataclass_csv(audit.basho_division_rows, outputs.basho_division_csv)
    _write_dataclass_csv(audit.division_summary_rows, outputs.division_summary_csv)
    outputs.findings_md.write_text(_build_findings(audit), encoding="utf-8")
    outputs.manifest_json.write_text(
        json.dumps(
            {
                "analysis": "bout_data_completeness",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "history": {
                    "first_basho": audit.first_basho,
                    "last_basho": audit.last_basho,
                    "basho_count": audit.basho_count,
                },
                "sources": {
                    "history": asdict(audit.history_source),
                    "bio_store": asdict(audit.bio_store_source),
                    "rikishi_pages": asdict(audit.rikishi_page_source),
                },
                "contracts": {
                    "atomic_domain": (
                        "one row for every literal chii-rikishi occurrence actually "
                        "present on each selected banzuke"
                    ),
                    "recorded": (
                        "the matching dated Rikishi.aspx career row contains at "
                        "least one non-empty hoshi symbol"
                    ),
                    "complete": (
                        "the matching dated Rikishi.aspx career row contains exactly "
                        "15 hoshi symbols and none is hoshi_empty"
                    ),
                    "retired": (
                        "the rikishi's parsed BioStore Intai date equals the basho"
                    ),
                    "missing": (
                        "the record is not complete and the rikishi's parsed "
                        "BioStore Intai date does not equal the basho"
                    ),
                    "absent_chii": "no row; an absent chii is not counted as missing",
                    "division_status": (
                        "none when every actual position is missing; complete when "
                        "none are missing; partial otherwise"
                    ),
                    "day_record_density": (
                        "each non-retired rikishi-basho contributes 15 expected daily "
                        "records; known and missing percentages exclude retirement-basho "
                        "rikishi from numerator and denominator"
                    ),
                    "partial_density": (
                        "division-summary density aggregates only basho whose division "
                        "status is partial, separately before 1989 and over all data"
                    ),
                    "continuous_complete_coverage": (
                        "earliest basho after the last incomplete basho, provided "
                        "every later selected basho is complete"
                    ),
                },
                "counts": {
                    "chii_rows": len(audit.chii_rows),
                    "basho_division_rows": len(audit.basho_division_rows),
                    "division_summary_rows": len(audit.division_summary_rows),
                },
                "outputs": {
                    "chii_csv": outputs.chii_csv.name,
                    "basho_division_csv": outputs.basho_division_csv.name,
                    "division_summary_csv": outputs.division_summary_csv.name,
                    "findings_md": outputs.findings_md.name,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return outputs


def _write_dataclass_csv(rows: tuple[object, ...], path: Path) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    field_names = tuple(field.name for field in fields(rows[0]))
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _build_findings(audit: AvailabilityAudit) -> str:
    lines = [
        "# Bout-data completeness by literal chii",
        "",
        "## Scope",
        "",
        f"Audited {audit.basho_count} basho from {audit.first_basho} through {audit.last_basho}.",
        "A position is complete when its matching cached Rikishi.aspx career row",
        "contains exactly 15 hoshi symbols and none is a hoshi_empty placeholder.",
        "Chii absent from a banzuke are ignored. An incomplete record whose BioStore",
        "Intai equals the basho is reported separately and does not count as missing;",
        "retirement is not otherwise inferred.",
        "",
        "## Division summary",
        "",
        "| Division | First any | Last incomplete | First complete | Continuous complete from | None | Partial | Complete |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in audit.division_summary_rows:
        lines.append(
            f"| {row.division} | {_display(row.first_basho_with_any_recorded_chii)} | "
            f"{_display(row.last_basho_with_incomplete_records)} | "
            f"{_display(row.first_basho_with_complete_records)} | "
            f"{_display(row.continuous_complete_coverage_begins)} | "
            f"{row.basho_with_no_records} | {row.basho_with_partial_records} | "
            f"{row.basho_with_complete_records} |"
        )

    lines.extend(
        (
            "",
            "## Density within partial basho",
            "",
            "Complete and no-record basho are excluded. Retirement-basho rikishi are",
            "excluded from both expected and missing daily-record counts.",
            "",
            "| Division | Pre-1989 missing / expected | Pre-1989 known | Pre-1989 missing | All missing / expected | All known | All missing |",
            "|---|---:|---:|---:|---:|---:|---:|",
        )
    )
    for row in audit.division_summary_rows:
        lines.append(
            f"| {row.division} | "
            f"{row.pre_1989_partial_missing_day_records:,} / "
            f"{row.pre_1989_partial_expected_day_records:,} | "
            f"{row.pre_1989_partial_known_day_record_percentage:.3f}% | "
            f"{row.pre_1989_partial_missing_day_record_percentage:.3f}% | "
            f"{row.all_partial_missing_day_records:,} / "
            f"{row.all_partial_expected_day_records:,} | "
            f"{row.all_partial_known_day_record_percentage:.3f}% | "
            f"{row.all_partial_missing_day_record_percentage:.3f}% |"
        )

    lines.extend(("", "## Partial basho", ""))
    partial = [row for row in audit.basho_division_rows if row.status == "partial"]
    if not partial:
        lines.append("None.")
    else:
        lines.extend(
            (
                "| Basho | Division | Any records | Complete | Partial | None | Retired incomplete | Present | Missing chii | Missing daily records | Daily records known |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            )
        )
        for row in partial:
            lines.append(
                f"| {row.basho} | {row.division} | {row.chii_with_any_records} | "
                f"{row.chii_complete_records} | {row.chii_partial_records} | "
                f"{row.chii_without_records} | {row.chii_retired_incomplete} | "
                f"{row.chii_present} | {row.chii_missing} | "
                f"{row.missing_day_records:,} / {row.expected_day_records:,} | "
                f"{row.known_day_record_percentage:.3f}% |"
            )
    lines.append("")
    return "\n".join(lines)


def _display(value: str) -> str:
    return value or "—"
