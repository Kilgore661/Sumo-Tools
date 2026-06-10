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
    _write_csv(result.output_dir / "call_edges.csv", result.call_edges)
    _write_csv(result.output_dir / "execution_call_slice.csv", result.execution_call_slice)
    _write_csv(result.output_dir / "execution_review_candidates.csv", result.execution_review_candidates)
    _write_csv(result.output_dir / "source_distribution_inputs.csv", result.source_distribution_inputs)
    _write_csv(result.output_dir / "call_argument_bindings.csv", result.call_argument_bindings)
    _write_csv(result.output_dir / "parameter_field_provenance.csv", result.parameter_field_provenance)
    _write_csv(result.output_dir / "parameter_file_provenance.csv", result.parameter_file_provenance)
    _write_csv(result.output_dir / "file_uses.csv", result.file_uses)
    _write_csv(result.output_dir / "file_use_resolution.csv", result.file_use_resolutions)
    _write_csv(result.output_dir / "producer_return_bindings.csv", result.producer_return_bindings)
    _write_csv(result.output_dir / "producer_write_bindings.csv", result.producer_write_bindings)
    _write_csv(result.output_dir / "producer_outputs.csv", result.producer_outputs)
    _write_csv(result.output_dir / "file_families.csv", result.file_families)
    _write_csv(result.output_dir / "file_family_evidence.csv", result.file_family_evidence)
    _write_csv(result.output_dir / "file_family_classification.csv", result.file_family_classification)
    _write_csv(result.output_dir / "distribution_candidates.csv", result.distribution_candidates)
    _write_csv(result.output_dir / "review_candidates.csv", result.review_candidates)
    _write_csv(result.output_dir / "unresolved.csv", result.unresolved)
    _write_summary(result)
    _write_source_distribution_summary(result)


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
        f"Call edges: {len(result.call_edges)}",
        f"Execution call slice: {len(result.execution_call_slice)}",
        f"Execution review candidates: {len(result.execution_review_candidates)}",
        f"Source distribution inputs: {len(result.source_distribution_inputs)}",
        f"Call argument bindings: {len(result.call_argument_bindings)}",
        f"Parameter field provenance: {len(result.parameter_field_provenance)}",
        f"Parameter file provenance: {len(result.parameter_file_provenance)}",
        f"File uses: {len(result.file_uses)}",
        f"File use resolutions: {len(result.file_use_resolutions)}",
        f"Producer return bindings: {len(result.producer_return_bindings)}",
        f"Producer write bindings: {len(result.producer_write_bindings)}",
        f"Producer outputs: {len(result.producer_outputs)}",
        f"File families: {len(result.file_families)}",
        f"File family evidence rows: {len(result.file_family_evidence)}",
        f"File family classifications: {len(result.file_family_classification)}",
        f"Distribution candidates: {len(result.distribution_candidates)}",
        f"Review candidates: {len(result.review_candidates)}",
        f"Unresolved records: {len(result.unresolved)}",
        "",
    ]
    lines.extend(_summary_block("Distribution decisions", _distribution_decisions(result)))
    lines.extend(_summary_block("File-family classifications", _file_family_classifications(result)))
    lines.extend(_summary_block("Execution review status", _execution_review_status(result)))
    lines.extend(_summary_block("Effective review priorities", _effective_review_priorities(result)))
    lines.extend(_summary_block("Source distribution buckets", _source_distribution_buckets(result)))
    lines.extend(_candidate_list_block("Include candidates", _include_candidates(result)))
    lines.extend(_candidate_list_block("High-priority review candidates", _high_review_candidates(result)))
    lines.extend(_execution_candidate_list_block("Effective high-priority review candidates", _effective_high_review_candidates(result)))
    lines.extend(_source_distribution_list_block("Repository source inputs", _source_distribution_bucket_rows(result, "repository_source_input")))
    lines.extend(_source_distribution_list_block("Precomputed artifact inputs", _source_distribution_bucket_rows(result, "precomputed_artifact_input")))
    lines.extend(_source_distribution_list_block("Mode-dependent source distribution review", _source_distribution_bucket_rows(result, "mode_dependent_review")))
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
            "call_edges.csv",
            "execution_call_slice.csv",
            "execution_review_candidates.csv",
            "source_distribution_inputs.csv",
            "source_distribution_summary.md",
            "call_argument_bindings.csv",
            "parameter_field_provenance.csv",
            "parameter_file_provenance.csv",
            "file_uses.csv",
            "file_use_resolution.csv",
            "producer_return_bindings.csv",
            "producer_write_bindings.csv",
            "producer_outputs.csv",
            "file_families.csv",
            "file_family_evidence.csv",
            "file_family_classification.csv",
            "distribution_candidates.csv",
            "review_candidates.csv",
            "unresolved.csv",
            "summary.md",
            "```",
        ]
    )
    (result.output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_source_distribution_summary(result: AnalysisResult) -> None:
    lines = [
        "# Source Distribution Summary",
        "",
        f"Root module: `{result.root_module}`",
        "",
        "## Bottom line",
        "",
        _bottom_line(result),
        "",
        "## Bucket counts",
        "",
    ]
    lines.extend(_summary_block_lines(_source_distribution_buckets(result)))
    lines.extend(
        [
            "## Repository source inputs",
            "",
            "These are concrete repository files/assets that should be included in a source distribution.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "repository_source_input")))
    lines.extend(
        [
            "## Precomputed artifact inputs",
            "",
            "These are required by the current product slice, but they live under `files/output/...`. The policy decision is `include_or_regenerate`.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "precomputed_artifact_input")))
    lines.extend(
        [
            "## Mode-dependent deployment inputs",
            "",
            "These are generated in normal build mode but externally supplied in deployment modes such as `--no-build`.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "mode_dependent_review")))
    lines.extend(
        [
            "## Runtime and state/control review",
            "",
            "These rows are execution-reachable state checks, existence checks, or runtime control paths rather than ordinary source inputs.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "state_or_control_review")))
    lines.extend(
        [
            "## Pipeline tree review",
            "",
            "These are variable output-tree globs that still need provenance clarification if the final packaging policy depends on them.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "pipeline_tree_review")))
    lines.extend(
        [
            "## Scoped output parameters",
            "",
            "These are output-location parameters, not source-distribution inputs.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "scoped_output_parameter")))
    lines.extend(
        [
            "## Unresolved non-execution parameter proxies",
            "",
            "These are scoped parameter families that are not represented as final concrete source inputs in this report. Important concrete families produced from parameter provenance appear in the sections above.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "unresolved_non_execution_parameter")))
    lines.extend(
        [
            "## Not in current execution slice",
            "",
            "These rows are conservative import-reachable evidence, but they are outside the current `make_site2` execution slice.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "not_in_execution_slice")))
    lines.extend(
        [
            "## Generated or intermediate outputs",
            "",
            "These rows are generated or intermediate outputs and are excluded from the source distribution input set.",
            "",
        ]
    )
    lines.extend(_source_distribution_rows(_source_distribution_bucket_rows(result, "generated_or_intermediate_output"), limit=30))
    if len(_source_distribution_bucket_rows(result, "generated_or_intermediate_output")) > 30:
        lines.extend(["", "Generated/intermediate output list truncated to 30 rows in this summary; see `source_distribution_inputs.csv` for the full list.", ""])
    lines.extend(
        [
            "## Policy notes",
            "",
            "- `repository_source_input` means include in the source distribution.",
            "- `precomputed_artifact_input` means the website product needs the artifact present, but the product policy can choose whether to include it, regenerate it, or package it separately.",
            "- `mode_dependent_review` means normal build mode and deployment/no-build mode have different assumptions.",
            "- `not_in_execution_slice` rows are retained as conservative evidence but are not blockers for the current product slice.",
            "",
        ]
    )
    (result.output_dir / "source_distribution_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _bottom_line(result: AnalysisResult) -> str:
    counts = _source_distribution_buckets(result)
    repository_count = counts.get("repository_source_input", 0)
    artifact_count = counts.get("precomputed_artifact_input", 0)
    mode_count = counts.get("mode_dependent_review", 0)
    state_count = counts.get("state_or_control_review", 0)
    pipeline_count = counts.get("pipeline_tree_review", 0)
    return (
        f"For the current `make_site2` execution slice, SDDA identifies {repository_count} repository source inputs "
        f"and {artifact_count} precomputed artifact inputs. There are {mode_count} mode-dependent deployment rows, "
        f"{state_count} state/control review rows, and {pipeline_count} pipeline-tree review rows. "
        "Generated/intermediate outputs are excluded, and import-reachable rows outside the execution slice are separated from the product-slice answer."
    )


def _distribution_decisions(result: AnalysisResult) -> Counter[str]:
    return Counter(row.distribution_decision for row in result.distribution_candidates)


def _file_family_classifications(result: AnalysisResult) -> Counter[str]:
    return Counter(row.classification for row in result.file_family_classification)


def _execution_review_status(result: AnalysisResult) -> Counter[str]:
    return Counter(row.execution_status for row in result.execution_review_candidates)


def _effective_review_priorities(result: AnalysisResult) -> Counter[str]:
    return Counter(row.effective_review_priority for row in result.execution_review_candidates)


def _source_distribution_buckets(result: AnalysisResult) -> Counter[str]:
    return Counter(row.source_distribution_bucket for row in result.source_distribution_inputs)


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


def _effective_high_review_candidates(result: AnalysisResult) -> list[object]:
    return sorted(
        [
            row
            for row in result.execution_review_candidates
            if row.effective_review_priority == "high"
        ],
        key=lambda row: row.family_pattern,
    )


def _source_distribution_bucket_rows(result: AnalysisResult, bucket: str) -> list[object]:
    return sorted(
        [row for row in result.source_distribution_inputs if row.source_distribution_bucket == bucket],
        key=lambda row: row.family_pattern,
    )


def _summary_block(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"## {title}", ""]
    lines.extend(_summary_block_lines(counts))
    return lines


def _summary_block_lines(counts: Counter[str]) -> list[str]:
    lines: list[str] = []
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


def _execution_candidate_list_block(title: str, rows: list[object]) -> list[str]:
    lines = [f"## {title}", ""]
    if not rows:
        lines.extend(["None", ""])
        return lines
    for row in rows:
        lines.append(
            f"- `{row.family_pattern}` ({row.classification}; {row.execution_status}; {row.classification_reason})"
        )
    lines.append("")
    return lines


def _source_distribution_list_block(title: str, rows: list[object]) -> list[str]:
    lines = [f"## {title}", ""]
    lines.extend(_source_distribution_rows(rows))
    return lines


def _source_distribution_rows(rows: list[object], limit: int | None = None) -> list[str]:
    if not rows:
        return ["None", ""]
    selected_rows = rows if limit is None else rows[:limit]
    lines = [
        f"- `{row.family_pattern}` ({row.source_distribution_decision}; {row.classification}; {row.reason})"
        for row in selected_rows
    ]
    lines.append("")
    return lines
