from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .models import AnalysisResult, DistributionCandidateRecord, ImportRecord


def write_reports(result: AnalysisResult) -> None:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(result.output_dir / "module_index.csv", result.modules)
    _write_csv(result.output_dir / "imports.csv", result.imports)
    _write_module_graph(result.output_dir / "module_graph.csv", result.imports)
    _write_csv(result.output_dir / "scopes.csv", result.scopes)
    _write_csv(result.output_dir / "type_facts.csv", result.type_facts)
    _write_csv(result.output_dir / "value_facts.csv", result.value_facts)
    _write_csv(result.output_dir / "field_facts.csv", result.field_facts)
    _write_csv(result.output_dir / "file_uses.csv", result.file_uses)
    _write_csv(result.output_dir / "file_families.csv", result.file_families)
    _write_csv(result.output_dir / "file_family_evidence.csv", result.file_family_evidence)
    _write_csv(result.output_dir / "file_family_classification.csv", result.file_family_classification)
    _write_csv(result.output_dir / "distribution_candidates.csv", result.distribution_candidates)
    _write_csv(result.output_dir / "unresolved.csv", result.unresolved)
    _write_summary(result)


def _write_csv(path: Path, rows: list[object]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    dict_rows = [asdict(row) for row in rows]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dict_rows[0]))
        writer.writeheader()
        writer.writerows(dict_rows)


def _write_module_graph(path: Path, imports: list[ImportRecord]) -> None:
    edges = [
        {
            "source_module": record.source_module,
            "target_module": record.target_module,
            "resolved": record.resolved,
            "reason": record.reason,
        }
        for record in imports
    ]
    if not edges:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(edges[0]))
        writer.writeheader()
        writer.writerows(edges)


def _write_summary(result: AnalysisResult) -> None:
    lines = [
        "# SDDA Summary",
        "",
        f"Root module: `{result.root_module}`",
        f"Import root: `{result.import_root}`",
        f"Output directory: `{result.output_dir}`",
        "",
        "## Counts",
        "",
        f"Project modules indexed: {len(result.modules)}",
        f"Reachable modules: {len(result.reachable_modules)}",
        f"Import records: {len(result.imports)}",
        f"Scopes: {len(result.scopes)}",
        f"Type facts: {len(result.type_facts)}",
        f"Value facts: {len(result.value_facts)}",
        f"Field facts: {len(result.field_facts)}",
        f"File uses: {len(result.file_uses)}",
        f"File families: {len(result.file_families)}",
        f"File family evidence rows: {len(result.file_family_evidence)}",
        f"File family classifications: {len(result.file_family_classification)}",
        f"Distribution candidates: {len(result.distribution_candidates)}",
        f"Unresolved records: {len(result.unresolved)}",
        "",
    ]
    lines.extend(_summary_block("Distribution decisions", _distribution_decisions(result)))
    lines.extend(_summary_block("File-family classifications", _file_family_classifications(result)))
    lines.extend(_candidate_list_block("Include candidates", _include_candidates(result)))
    lines.extend(_candidate_list_block("High-priority review candidates", _high_review_candidates(result)))
    lines.extend(
        [
            "## Reports",
            "",
            "```text",
            "module_index.csv",
            "imports.csv",
            "module_graph.csv",
            "scopes.csv",
            "type_facts.csv",
            "value_facts.csv",
            "field_facts.csv",
            "file_uses.csv",
            "file_families.csv",
            "file_family_evidence.csv",
            "file_family_classification.csv",
            "distribution_candidates.csv",
            "unresolved.csv",
            "summary.md",
            "```",
        ]
    )
    (result.output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _distribution_decisions(result: AnalysisResult) -> Counter[str]:
    return Counter(row.distribution_decision for row in result.distribution_candidates)


def _file_family_classifications(result: AnalysisResult) -> Counter[str]:
    return Counter(row.classification for row in result.file_family_classification)


def _include_candidates(result: AnalysisResult) -> list[DistributionCandidateRecord]:
    return sorted(
        [row for row in result.distribution_candidates if row.distribution_decision == "include"],
        key=lambda row: row.family_pattern,
    )


def _high_review_candidates(result: AnalysisResult) -> list[DistributionCandidateRecord]:
    return sorted(
        [
            row
            for row in result.distribution_candidates
            if row.distribution_decision == "review" and row.review_priority == "high"
        ],
        key=lambda row: row.family_pattern,
    )


def _summary_block(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"## {title}", ""]
    for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"{name}: {count}")
    lines.append("")
    return lines


def _candidate_list_block(title: str, rows: list[DistributionCandidateRecord]) -> list[str]:
    lines = [f"## {title}", ""]
    if not rows:
        lines.extend(["None", ""])
        return lines
    for row in rows:
        lines.append(f"- `{row.family_pattern}` ({row.classification}; {row.actions})")
    lines.append("")
    return lines
