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
        output_dir / "summary.csv",
        ["kind", "artifact"],
        [{"kind": "input", "artifact": artifact} for artifact in graph.input_artifacts]
        + [{"kind": "output", "artifact": artifact} for artifact in graph.output_artifacts]
        + [{"kind": "concrete_input", "artifact": artifact} for artifact in graph.concrete_input_artifacts]
        + [{"kind": "concrete_output", "artifact": artifact} for artifact in graph.concrete_output_artifacts],
    )


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    """Write dictionaries to CSV."""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
