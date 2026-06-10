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
    _write_csv(result.output_dir / "warnings.csv", result.warnings)
    _write_review_form(result)
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


def _probable_entrypoint_rows(result: EntrypointAnalysisResult) -> list[ModuleIndexRecord]:
    return sorted(_program_kind_rows(result, "standalone_program"), key=lambda row: row.module)


def _imported_program_review_rows(result: EntrypointAnalysisResult) -> list[ModuleIndexRecord]:
    return sorted(
        _program_kind_rows(result, "imported_program"),
        key=lambda row: (row.program_subtype != "probable_library", row.module),
    )


def _warning_rows(result: EntrypointAnalysisResult) -> list[object]:
    return [row for row in result.warnings if row.severity == "warning"]


def _note_rows(result: EntrypointAnalysisResult) -> list[object]:
    return [row for row in result.warnings if row.severity == "note"]


def _write_review_form(result: EntrypointAnalysisResult) -> None:
    accounting = _module_type_accounting(result)
    probable_entrypoints = _probable_entrypoint_rows(result)
    imported_programs = _imported_program_review_rows(result)
    warning_count = len(_warning_rows(result))
    note_count = len(_note_rows(result))
    lines = [
        "# SDDA Entrypoint Review Form",
        "",
        f"Import root: `{result.import_root}`",
        "",
        "This generated form records human review of machine-identified entrypoint candidates.",
        "Check exactly one outcome for each reviewed module and add comments where useful.",
        "",
        "## Machine-written context",
        "",
        f"total_modules: {accounting['total_modules']}",
        f"library_modules: {accounting['library_modules']}",
        f"programs: {accounting['programs']}",
        f"  probable_entrypoints: {accounting['probable_entrypoints']}",
        f"  imported_programs_needing_review: {accounting['imported_programs_needing_review']}",
        f"    probable_library_modules: {accounting['probable_library_modules']}",
        f"    possible_entrypoints: {accounting['possible_entrypoints']}",
        f"resolution_notes: {note_count}",
        f"warnings: {warning_count}",
        "",
    ]
    if note_count:
        lines.extend(
            [
                "Resolution notes were generated. These usually document intentional import-root-relative resolutions; review `warnings.csv` if a classification looks surprising.",
                "",
            ]
        )
    if warning_count:
        lines.extend(
            [
                "Machine warnings were generated. Review `warnings.csv` and `summary.md` before recording final conclusions.",
                "",
            ]
        )
    lines.extend(
        [
            "## Overall human conclusion",
            "",
            "Use this section after reviewing the module-level entries below.",
            "",
            "Conclusion:",
            "",
            "> ",
            "",
            "True entrypoints:",
            "",
            "- ",
            "",
            "Modules reviewed as library-like:",
            "",
            "- ",
            "",
            "Modules still unclear:",
            "",
            "- ",
            "",
            "## Probable entrypoints",
            "",
            "These are standalone programs. They are probable entrypoints, but still need human confirmation.",
            "",
        ]
    )
    if not probable_entrypoints:
        lines.extend(["No standalone programs were found.", ""])
    for row in probable_entrypoints:
        lines.extend(_probable_entrypoint_section(row))

    lines.extend(
        [
            "## Imported programs needing review",
            "",
            "These are programs that are imported by at least one other indexed module.",
            "",
        ]
    )
    if not imported_programs:
        lines.extend(["No imported programs require review.", ""])
    for row in imported_programs:
        lines.extend(_imported_program_section(row))
    (result.output_dir / "entrypoint_review_form.md").write_text("\n".join(lines), encoding="utf-8")


def _probable_entrypoint_section(row: ModuleIndexRecord) -> list[str]:
    return [
        f"### `{row.module}`",
        "",
        f"Path: `{row.path}`",
        f"First non-declarative statement: line {row.first_non_declarative_line}, `{row.first_non_declarative_kind}`",
        f"Has main guard: `{row.has_main_guard}`",
        f"Is `__main__.py`: `{row.is_dunder_main}`",
        "",
        "- [ ] Reviewed as true entrypoint",
        "- [ ] Reviewed as not a true entrypoint",
        "- [ ] Still unclear",
        "",
        "Conclusion / comments:",
        "",
        "> ",
        "",
    ]


def _imported_program_section(row: ModuleIndexRecord) -> list[str]:
    return [
        f"### `{row.module}`",
        "",
        f"Path: `{row.path}`",
        f"Subtype hint: `{row.program_subtype or 'review'}`",
        f"Imported by: `{row.imported_by}`",
        f"First non-declarative statement: line {row.first_non_declarative_line}, `{row.first_non_declarative_kind}`",
        f"Has main guard: `{row.has_main_guard}`",
        f"Is `__main__.py`: `{row.is_dunder_main}`",
        "",
        "- [ ] Reviewed as library-like module",
        "- [ ] Reviewed as real entrypoint",
        "- [ ] Reviewed as obsolete / ignore",
        "- [ ] Still unclear",
        "",
        "Conclusion / comments:",
        "",
        "> ",
        "",
    ]


def _write_summary(result: EntrypointAnalysisResult) -> None:
    module_kind_counts = Counter(row.module_kind for row in result.module_index_rows)
    program_kind_counts = Counter(row.program_kind for row in result.module_index_rows if row.program_kind)
    imported_subtype_counts = Counter(
        row.program_subtype
        for row in result.module_index_rows
        if row.program_kind == "imported_program" and row.program_subtype
    )
    severity_counts = Counter(row.severity for row in result.warnings)
    warning_kind_counts = Counter(row.warning_kind for row in result.warnings)
    accounting = _module_type_accounting(result)
    lines = [
        "# SDDA Entrypoint Index Summary",
        "",
        f"Import root: `{result.import_root}`",
        f"Output directory: `{result.output_dir}`",
        "",
        "## Module type accounting",
        "",
        f"total_modules: {accounting['total_modules']}",
        "",
        f"library_modules: {accounting['library_modules']}",
        "",
        f"programs: {accounting['programs']}",
        f"  probable_entrypoints: {accounting['probable_entrypoints']}",
        f"  imported_programs_needing_review: {accounting['imported_programs_needing_review']}",
        f"    probable_library_modules: {accounting['probable_library_modules']}",
        f"    possible_entrypoints: {accounting['possible_entrypoints']}",
        "",
        "## Resolution notes and warnings",
        "",
    ]
    if result.warnings:
        lines.extend(_counter_lines(severity_counts))
        lines.extend(["### Kinds", ""])
        lines.extend(_counter_lines(warning_kind_counts))
        lines.extend(
            [
                "Review `warnings.csv` for details. Severity `note` usually records intentional import-root-relative resolution. Severity `warning` marks something that may affect classification and should be reviewed.",
                "",
            ]
        )
    else:
        lines.extend(["No resolution notes or warnings.", ""])
    lines.extend(["## Module kinds", ""])
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
            "warnings.csv",
            "entrypoint_review_form.md",
            "summary.md",
            "```",
            "",
            "## Notes",
            "",
            "A library module is a Python module whose top-level body is declarative only.",
            "A program is any Python module with non-declarative top-level code, including assignments and main guards.",
            "A standalone program is counted as a probable entrypoint.",
            "An imported program is a program that is imported by at least one other indexed module and needs human review.",
            "An imported program with subtype `probable_library` has no non-declarative top-level code after its final top-level function.",
            "An imported program counted as `possible_entrypoints` does not have the `probable_library` hint.",
            "When the import root is narrower than the repository root, absolute imports that start with that import root can be resolved to local indexed modules and reported in `warnings.csv` as resolution notes.",
            "Review outcomes and final conclusions can be recorded in `entrypoint_review_form.md`.",
            "",
        ]
    )
    (result.output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def _module_type_accounting(result: EntrypointAnalysisResult) -> dict[str, int]:
    total_modules = len(result.module_index_rows)
    library_modules = len(_library_rows(result))
    programs = len(_program_rows(result))
    probable_entrypoints = len(_program_kind_rows(result, "standalone_program"))
    imported_programs = _program_kind_rows(result, "imported_program")
    probable_library_modules = len(
        [row for row in imported_programs if row.program_subtype == "probable_library"]
    )
    possible_entrypoints = len(
        [row for row in imported_programs if row.program_subtype != "probable_library"]
    )
    return {
        "total_modules": total_modules,
        "library_modules": library_modules,
        "programs": programs,
        "probable_entrypoints": probable_entrypoints,
        "imported_programs_needing_review": len(imported_programs),
        "probable_library_modules": probable_library_modules,
        "possible_entrypoints": possible_entrypoints,
    }


def _counter_lines(counts: Counter[str]) -> list[str]:
    lines = [f"{name}: {count}" for name, count in sorted(counts.items())]
    lines.append("")
    return lines
