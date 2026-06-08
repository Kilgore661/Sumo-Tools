"""Report writing for data-flow introspection."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from src.introspection.data_flow_model import (
    ArtifactSummary,
    ArtifactUse,
    DataFlowGraph,
    artifact_summary_to_dict,
    artifact_use_to_dict,
    import_ref_to_dict,
    module_ref_to_dict,
)


UNRESOLVED_PATH_PREFIXES = (
    "build_output.",
    "output_root/",
    "root/",
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
        output_dir / "root_artifacts.csv",
        ["role", "artifact", "modules", "reason"],
        root_artifact_rows(graph),
    )
    write_csv(
        output_dir / "root_rule.csv",
        ["root_module", "command", "inputs", "outputs", "upstream_generated_prerequisites"],
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
        "upstream_generated_prerequisites": ";".join(upstream_generated_prerequisites(graph)),
    }


def root_command(graph: DataFlowGraph) -> str:
    """Return the command that invokes the analysed root module."""

    return f"python -m {graph.root_module}"


def root_package(graph: DataFlowGraph) -> str:
    """Return the package treated as owned by the root command."""

    if graph.root_module.endswith(".__main__"):
        return graph.root_module.removesuffix(".__main__")
    return graph.root_module.rsplit(".", 1)[0]


def is_root_module(graph: DataFlowGraph, module_name: str) -> bool:
    """Return true when ``module_name`` is part of the root command package."""

    package = root_package(graph)
    return module_name == package or module_name.startswith(f"{package}.")


def normalised_artifact(artifact: str) -> str:
    """Return a slash-normalised artifact path/expression."""

    return artifact.replace("\\", "/")


def is_makefile_ready_artifact(artifact: str) -> bool:
    """Return true when an artifact looks safe enough for a candidate Makefile rule."""

    normalised = normalised_artifact(artifact)
    if normalised.startswith(UNRESOLVED_PATH_PREFIXES):
        return False
    if "(" in normalised or ")" in normalised or "{" in normalised or "}" in normalised:
        return False
    return True


def root_output_uses(graph: DataFlowGraph) -> tuple[ArtifactUse, ...]:
    """Return concrete writes that look owned by the root command package."""

    return tuple(
        sorted(
            (
                use
                for use in graph.artifact_uses
                if use.action == "write"
                and use.artifact_kind == "concrete"
                and is_makefile_ready_artifact(use.artifact)
                and is_root_module(graph, use.module_name)
            ),
            key=lambda use: (use.artifact, use.module_name, use.line_number),
        )
    )


def unresolved_root_output_uses(graph: DataFlowGraph) -> tuple[ArtifactUse, ...]:
    """Return root-package writes not suitable for the candidate Makefile yet."""

    return tuple(
        sorted(
            (
                use
                for use in graph.artifact_uses
                if use.action == "write"
                and use.artifact_kind == "concrete"
                and not is_makefile_ready_artifact(use.artifact)
                and is_root_module(graph, use.module_name)
            ),
            key=lambda use: (use.artifact, use.module_name, use.line_number),
        )
    )


def rule_outputs(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return conservative candidate Makefile targets for the root command."""

    return tuple(sorted({use.artifact for use in root_output_uses(graph)}))


def has_same_producer_and_consumer(summary: ArtifactSummary) -> bool:
    """Return true for state-like artifacts read and written by the same module."""

    return bool(set(summary.producer_modules) & set(summary.consumer_modules))


def upstream_generated_summaries(graph: DataFlowGraph) -> tuple[ArtifactSummary, ...]:
    """Return generated prerequisites produced outside the root command package."""

    return tuple(
        summary
        for summary in graph.generated_prerequisites
        if not has_same_producer_and_consumer(summary)
        and any(not is_root_module(graph, module_name) for module_name in summary.producer_modules)
    )


def state_artifact_summaries(graph: DataFlowGraph) -> tuple[ArtifactSummary, ...]:
    """Return artifacts that reachable code both reads and writes as state."""

    return tuple(
        summary
        for summary in graph.generated_prerequisites
        if has_same_producer_and_consumer(summary)
    )


def upstream_generated_prerequisites(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return artifact names for upstream generated prerequisites."""

    return tuple(summary.artifact for summary in upstream_generated_summaries(graph))


def state_artifacts(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return artifact names for state files consumed by the root command."""

    return tuple(summary.artifact for summary in state_artifact_summaries(graph))


def producer_modules_for_artifact(graph: DataFlowGraph, artifact: str) -> tuple[str, ...]:
    """Return modules that write ``artifact``."""

    return tuple(
        sorted(
            {
                use.module_name
                for use in graph.artifact_uses
                if use.artifact == artifact and use.action == "write"
            }
        )
    )


def is_root_output_artifact(graph: DataFlowGraph, artifact: str) -> bool:
    """Return true when ``artifact`` is one of the candidate root outputs."""

    return artifact in set(rule_outputs(graph))


def is_upstream_generated_artifact(graph: DataFlowGraph, artifact: str) -> bool:
    """Return true when ``artifact`` is produced outside the root package and consumed within reach."""

    return artifact in set(upstream_generated_prerequisites(graph))


def upstream_producer_modules(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return modules that produce upstream generated prerequisites."""

    return tuple(
        sorted(
            {
                module_name
                for summary in upstream_generated_summaries(graph)
                for module_name in summary.producer_modules
            }
        )
    )


def is_root_output_self_inspection(graph: DataFlowGraph, use: ArtifactUse) -> bool:
    """Return true when a read/glob appears to inspect the root output directory."""

    artifact = normalised_artifact(use.artifact).removesuffix("*").rstrip("/")
    return any(normalised_artifact(output).startswith(f"{artifact}/") for output in rule_outputs(graph))


def external_input_uses(graph: DataFlowGraph) -> tuple[ArtifactUse, ...]:
    """Return concrete reads/globs that are plausible root prerequisites."""

    upstream_producers = set(upstream_producer_modules(graph))
    return tuple(
        sorted(
            (
                use
                for use in graph.artifact_uses
                if use.action in {"read", "glob"}
                and use.artifact_kind == "concrete"
                and is_makefile_ready_artifact(use.artifact)
                and not is_root_output_artifact(graph, use.artifact)
                and not is_root_output_self_inspection(graph, use)
                and not producer_modules_for_artifact(graph, use.artifact)
                and use.module_name not in upstream_producers
            ),
            key=lambda use: (use.artifact, use.module_name, use.line_number),
        )
    )


def upstream_input_uses(graph: DataFlowGraph) -> tuple[ArtifactUse, ...]:
    """Return inputs that belong to upstream generated-prerequisite producers."""

    upstream_producers = set(upstream_producer_modules(graph))
    return tuple(
        sorted(
            (
                use
                for use in graph.artifact_uses
                if use.action in {"read", "glob"}
                and use.artifact_kind == "concrete"
                and is_makefile_ready_artifact(use.artifact)
                and use.module_name in upstream_producers
                and not producer_modules_for_artifact(graph, use.artifact)
            ),
            key=lambda use: (use.artifact, use.module_name, use.line_number),
        )
    )


def unresolved_input_uses(graph: DataFlowGraph) -> tuple[ArtifactUse, ...]:
    """Return concrete reads/globs whose paths still contain unresolved variables."""

    return tuple(
        sorted(
            (
                use
                for use in graph.artifact_uses
                if use.action in {"read", "glob"}
                and use.artifact_kind == "concrete"
                and not is_makefile_ready_artifact(use.artifact)
            ),
            key=lambda use: (use.artifact, use.module_name, use.line_number),
        )
    )


def rule_inputs(graph: DataFlowGraph) -> tuple[str, ...]:
    """Return conservative candidate Makefile prerequisites for the root command."""

    external_inputs = {use.artifact for use in external_input_uses(graph)}
    upstream_inputs = set(upstream_generated_prerequisites(graph))
    state_inputs = set(state_artifacts(graph))
    return tuple(sorted(external_inputs | upstream_inputs | state_inputs))


def root_artifact_rows(graph: DataFlowGraph) -> list[dict[str, object]]:
    """Return Makefile-facing artifact classification rows."""

    rows: list[dict[str, object]] = []
    for artifact in rule_outputs(graph):
        modules = tuple(
            sorted(
                {
                    use.module_name
                    for use in root_output_uses(graph)
                    if use.artifact == artifact
                }
            )
        )
        rows.append(
            {
                "role": "root_output",
                "artifact": artifact,
                "modules": ";".join(modules),
                "reason": "concrete write by module in root package",
            }
        )

    for use in unresolved_root_output_uses(graph):
        rows.append(
            {
                "role": "unresolved_root_output",
                "artifact": use.artifact,
                "modules": use.module_name,
                "reason": "root-package write but path contains unresolved variable-like prefix",
            }
        )

    for summary in upstream_generated_summaries(graph):
        rows.append(
            {
                "role": "upstream_generated_prerequisite",
                "artifact": summary.artifact,
                "modules": ";".join(summary.producer_modules),
                "reason": "consumed by reachable code but produced outside root package",
            }
        )

    for summary in state_artifact_summaries(graph):
        rows.append(
            {
                "role": "state_artifact",
                "artifact": summary.artifact,
                "modules": ";".join(summary.producer_modules),
                "reason": "same reachable module reads and writes this artifact",
            }
        )

    for use in external_input_uses(graph):
        rows.append(
            {
                "role": "external_input",
                "artifact": use.artifact,
                "modules": use.module_name,
                "reason": f"{use.action} with no reachable producer",
            }
        )

    for use in upstream_input_uses(graph):
        rows.append(
            {
                "role": "upstream_input",
                "artifact": use.artifact,
                "modules": use.module_name,
                "reason": f"{use.action} by upstream prerequisite producer",
            }
        )

    for use in unresolved_input_uses(graph):
        rows.append(
            {
                "role": "unresolved_input",
                "artifact": use.artifact,
                "modules": use.module_name,
                "reason": f"{use.action} path contains unresolved variable-like prefix",
            }
        )

    return sorted(rows, key=lambda row: (str(row["role"]), str(row["artifact"]), str(row["modules"])))


def makefile_candidate(graph: DataFlowGraph) -> str:
    """Return a reviewable Makefile fragment for the root command."""

    outputs = rule_outputs(graph)
    inputs = rule_inputs(graph)
    upstream_prerequisites = upstream_generated_prerequisites(graph)
    state_inputs = state_artifacts(graph)

    lines = [
        f"# Candidate Makefile rule inferred from data flow for {graph.root_module}.",
        "# Review before use: this is evidence-backed, not authoritative.",
        "#",
        f"# Command: {root_command(graph)}",
        f"# Root package: {root_package(graph)}",
        f"# Reachable modules: {len(graph.modules)}",
        f"# Artifact uses: {len(graph.artifact_uses)}",
        f"# Candidate root outputs: {len(outputs)}",
        f"# Candidate root inputs: {len(inputs)}",
    ]

    if upstream_prerequisites:
        lines.extend(["#", "# Upstream generated prerequisites consumed by reachable code:"])
        lines.extend(f"#   {artifact}" for artifact in upstream_prerequisites)

    if state_inputs:
        lines.extend(["#", "# State artifacts read by reachable code:"])
        lines.extend(f"#   {artifact}" for artifact in state_inputs)

    lines.extend(
        [
            "#",
            "# See root_artifacts.csv for the classification behind this rule.",
            "",
        ]
    )

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
