"""Report writing for data-flow introspection."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from src.introspection.data_flow_model import (
    DataFlowGraph,
    artifact_summary_to_dict,
    artifact_use_to_dict,
    import_ref_to_dict,
    module_ref_to_dict,
)


def write_data_flow_reports(graph: DataFlowGraph, output_dir: Path) -> None:
    """Persist data-flow JSON and CSV reports."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "data_flow.json").write_text(
        json.dumps(graph.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_csv(
        output_dir / "modules.csv",
        ["module_name", "path"],
        [module_ref_to_dict(module) for module in graph.modules],
    )
    write_csv(
        output_dir / "imports.csv",
        ["importer_module", "imported_module", "imported_name", "alias", "import_style", "line_number"],
        [import_ref_to_dict(import_ref) for import_ref in graph.imports],
    )
    write_csv(
        output_dir / "artifact_uses.csv",
        [
            "module_name",
            "distance_from_root",
            "scope",
            "action",
            "artifact",
            "artifact_kind",
            "evidence",
            "line_number",
            "confidence",
        ],
        [artifact_use_to_dict(use) for use in graph.artifact_uses],
    )
    write_csv(
        output_dir / "artifacts.csv",
        [
            "artifact",
            "artifact_kind",
            "read_count",
            "write_count",
            "glob_count",
            "producer_modules",
            "consumer_modules",
        ],
        [artifact_summary_to_dict(summary) for summary in graph.artifact_summaries],
    )
    write_csv(
        output_dir / "generated_prerequisites.csv",
        [
            "artifact",
            "artifact_kind",
            "read_count",
            "write_count",
            "glob_count",
            "producer_modules",
            "consumer_modules",
        ],
        [artifact_summary_to_dict(summary) for summary in graph.generated_prerequisites],
    )
    write_csv(
        output_dir / "root_rule.csv",
        ["root_module", "command", "inputs", "outputs", "generated_prerequisites"],
        [root_rule_row(graph)],
    )
    (output_dir / "Makefile.candidate").write_text(
        makefile_candidate(graph),
        encoding="utf-8",
    )
    write_csv(
        output_dir / "summary.csv",
        ["kind", "artifact"],
        [{"kind": "input", "artifact": artifact} for artifact in graph.input_artifacts]
        + [{"kind": "output", "artifact": artifact} for artifact in graph.output_artifacts]
        + [{"kind": "concrete_input", "artifact": artifact} for artifact in graph.concrete_input_artifacts]
        + [{"kind": "concrete_output", "artifact": artifact} for artifact in graph.concrete_output_artifacts],
    )


def root_rule_row(graph: DataFlowGraph) -> dict[str, object]:
    """Return the root command as one reviewable Makefile-rule row."""

    return {
        "root_module": graph.root_module,
        "command": root_command(graph),
        "inputs": ";".join(rule_inputs(graph)),
        "outputs": ";".join(rule_outputs(graph)),
        "generated_prerequisites": ";".join(summary.artifact for summary in graph.generated_prerequisites),
    }


def root_command(graph: DataFlowGraph) -> str:
    """Return the command that invokes the analysed root module."""

    return f"python -m {graph.root_module}"


def rule_inputs(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return candidate Makefile prerequisites for the root command."""

    return graph.concrete_input_artifacts or graph.input_artifacts


def rule_outputs(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return candidate Makefile targets for the root command."""

    return graph.concrete_output_artifacts or graph.output_artifacts


def makefile_candidate(graph: DataFlowGraph) -> str:
    """Return a reviewable Makefile fragment for the root command."""

    outputs = rule_outputs(graph)
    inputs = rule_inputs(graph)
    generated_prerequisites = tuple(summary.artifact for summary in graph.generated_prerequisites)

    lines = [
        f"# Candidate Makefile rule inferred from data flow for {graph.root_module}.",
        "# Review before use: this is evidence-backed, not authoritative.",
        "#",
        f"# Command: {root_command(graph)}",
        f"# Reachable modules: {len(graph.modules)}",
        f"# Artifact uses: {len(graph.artifact_uses)}",
        f"# Concrete inputs: {len(graph.concrete_input_artifacts)}",
        f"# Concrete outputs: {len(graph.concrete_output_artifacts)}",
    ]

    if generated_prerequisites:
        lines.extend(["#", "# Generated prerequisites consumed by reachable code:"])
        lines.extend(f"#   {artifact}" for artifact in generated_prerequisites)

    lines.append("")

    if not outputs:
        lines.extend(
            [
                f".PHONY: {make_target_name(graph.root_module)}",
                f"{make_target_name(graph.root_module)}: {make_continuation(inputs)}".rstrip(),
                f"\t{root_command(graph)}",
                "",
            ]
        )
        return "\n".join(lines)

    target_lines = make_rule_lines(outputs, inputs, root_command(graph))
    lines.extend(target_lines)
    return "\n".join(lines) + "\n"


def make_rule_lines(outputs: tuple[str, ...], inputs: tuple[str, ...], command: str) -> list[str]:
    """Return Makefile lines for one command with possibly many targets/prerequisites."""

    escaped_outputs = tuple(make_path_token(path) for path in outputs)
    escaped_inputs = tuple(make_path_token(path) for path in inputs)

    first_line = f"{' '.join(escaped_outputs)}:"
    if escaped_inputs:
        first_line += f" {make_continuation(escaped_inputs)}"

    return [first_line.rstrip(), f"\t{command}", ""]


def make_continuation(paths: tuple[str, ...]) -> str:
    """Return Makefile path list with readable continuations."""

    if not paths:
        return ""
    if len(paths) == 1:
        return make_path_token(paths[0])
    return " \\\n    ".join(make_path_token(path) for path in paths)


def make_path_token(path: str) -> str:
    """Return a path token escaped for simple Makefile syntax."""

    return path.replace("\\", "/").replace(" ", "\\ ")


def make_target_name(module_name: str) -> str:
    """Return a simple phony target name for a root module."""

    return module_name.replace(".", "-")


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    """Write dictionaries to CSV."""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
