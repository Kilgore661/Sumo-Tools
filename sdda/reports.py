from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from .models import AnalysisResult, ImportRecord


def write_reports(result: AnalysisResult) -> None:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(result.output_dir / "module_index.csv", result.modules)
    _write_csv(result.output_dir / "imports.csv", result.imports)
    _write_module_graph(result.output_dir / "module_graph.csv", result.imports)
    _write_csv(result.output_dir / "scopes.csv", result.scopes)
    _write_csv(result.output_dir / "file_uses.csv", result.file_uses)
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
        f"File uses: {len(result.file_uses)}",
        f"Unresolved records: {len(result.unresolved)}",
        "",
        "## Reports",
        "",
        "```text",
        "module_index.csv",
        "imports.csv",
        "module_graph.csv",
        "scopes.csv",
        "file_uses.csv",
        "unresolved.csv",
        "summary.md",
        "```",
    ]
    (result.output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
