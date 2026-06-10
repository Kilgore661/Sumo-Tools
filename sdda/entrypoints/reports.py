from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .models import EntrypointAnalysisResult, ModuleIndexRecord


def write_reports(result: EntrypointAnalysisResult) -> None:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(result.output_dir / "module_index.csv", result.module_index_rows)
    _write_csv(result.output_dir / "programs.csv", _program_rows(result))
    _write_csv(result.output_dir / "standalone_programs.csv", _program_kind_rows(result, "standalone_program"))
    _write_csv(result.output_dir / "imported_programs.csv", _program_kind_rows(result, "imported_program"))
    _write_csv(result.output_dir / "library_modules.csv", _library_rows(result))
    _write_csv(result.output_dir / "program_evidence.csv", result.program_evidence)
    _write_csv(result.output_dir / "module_references.csv", result.references)
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


def _program_rows(result: EntrypointAnalysisResult) -> list[ModuleIndexRecord]:
    return [row for row in result.module_index_rows if row.module_kind == "program"]


def _library_rows(result: EntrypointAnalysisResult) -> list[ModuleIndexRecord]:
    return [row for row in result.module_index_rows if row.module_kind == "library_module"]


def _program_kind_rows(result: EntrypointAnalysisResult, program_kind: str) -> list[ModuleIndexRecord]:
    return [row for row in result.module_index_rows if row.program_kind == program_kind]


def _write_summary(result: EntrypointAnalysisResult) -> None:
    module_kind_counts = Counter(row.module_kind for row in result.module_index_rows)
    program_kind_counts = Counter(row.program_kind for row in result.module_index_rows if row.program_kind)
    imported_subtype_counts = Counter(
        row.program_subtype
        for row in result.module_index_rows
        if row.program_kind == "imported_program" and row.program_subtype
    )
    lines = [
        "# SDDA Entrypoint Index Summary",
        "",
        f"Import root: `{result.import_root}`",
        f"Output directory: `{result.output_dir}`",
        "",
        "## Module kinds",
        "",
    ]
    lines.extend(_counter_lines(module_kind_counts))
    lines.extend(["## Program kinds", ""])
    lines.extend(_counter_lines(program_kind_counts))
    lines.extend(["## Imported program subtypes", ""])
    lines.extend(_counter_lines(imported_subtype_counts))
    lines.extend(
        [
            "## Reports",
            "",
            "```text",
            "module_index.csv",
            "programs.csv",
            "standalone_programs.csv",
            "imported_programs.csv",
            "library_modules.csv",
            "program_evidence.csv",
            "module_references.csv",
            "summary.md",
            "```",
            "",
            "## Notes",
            "",
            "A library module is a Python module whose top-level body is declarative only.",
            "A program is any Python module with non-declarative top-level code, including assignments and main guards.",
            "A standalone program is not imported by another indexed module.",
            "An imported program is a program that is imported by at least one other indexed module and needs human review.",
            "An imported program with subtype `probable_library` has no non-declarative top-level code after its final top-level function.",
            "",
        ]
    )
    (result.output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def _counter_lines(counts: Counter[str]) -> list[str]:
    lines = [f"{name}: {count}" for name, count in sorted(counts.items())]
    lines.append("")
    return lines
