from __future__ import annotations

from pathlib import Path

from .classifier import classify_module, has_main_guard, has_non_declarative_after_last_function, parse_python_file
from .models import EntrypointAnalysisResult, ModuleIndexRecord, ProgramEvidenceRecord, ReferenceRecord
from .module_index import build_module_index
from .references import extract_references, inbound_references_by_module


def analyse_entrypoints(import_root: Path, output_dir: Path | None = None) -> EntrypointAnalysisResult:
    module_index = build_module_index(import_root)
    evidence_by_module: dict[str, list[ProgramEvidenceRecord]] = {}
    has_main_guard_by_module: dict[str, bool] = {}
    non_declarative_after_last_function_by_module: dict[str, bool] = {}
    references: list[ReferenceRecord] = []
    parsed_trees = {}

    for module_name, module in sorted(module_index.items()):
        tree = parse_python_file(module.path)
        parsed_trees[module_name] = tree
        _, evidence = classify_module(module_name, module.path, tree, module.is_dunder_main)
        evidence_by_module[module_name] = evidence
        has_main_guard_by_module[module_name] = has_main_guard(tree)
        non_declarative_after_last_function_by_module[module_name] = has_non_declarative_after_last_function(tree)

    for module_name, tree in parsed_trees.items():
        references.extend(extract_references(module_name, tree, module_index))

    inbound_by_module = inbound_references_by_module(references)
    module_index_rows = [
        _module_index_row(
            module_name,
            module,
            evidence_by_module[module_name],
            inbound_by_module.get(module_name, []),
            has_main_guard_by_module[module_name],
            non_declarative_after_last_function_by_module[module_name],
        )
        for module_name, module in sorted(module_index.items())
    ]
    final_output_dir = output_dir or _default_output_dir()
    return EntrypointAnalysisResult(
        import_root=import_root,
        output_dir=final_output_dir,
        modules=list(module_index.values()),
        module_index_rows=module_index_rows,
        program_evidence=[row for rows in evidence_by_module.values() for row in rows],
        references=sorted(
            references,
            key=lambda row: (row.target_module, row.source_module, row.line, row.imported_name),
        ),
    )


def _module_index_row(
    module_name: str,
    module: object,
    evidence: list[ProgramEvidenceRecord],
    inbound_references: list[ReferenceRecord],
    has_main_guard_value: bool,
    non_declarative_after_last_function: bool,
) -> ModuleIndexRecord:
    module_kind = "program" if evidence else "library_module"
    program_kind = _program_kind(module_kind, inbound_references)
    first_evidence = min(evidence, key=lambda row: row.line) if evidence else None
    imported_by = ";".join(sorted({row.source_module for row in inbound_references}))
    return ModuleIndexRecord(
        module=module_name,
        path=str(getattr(module, "path")),
        module_kind=module_kind,
        program_kind=program_kind,
        program_subtype=_program_subtype(program_kind, non_declarative_after_last_function),
        inbound_reference_count=len({row.source_module for row in inbound_references}),
        imported_by=imported_by,
        first_non_declarative_line=first_evidence.line if first_evidence else 0,
        first_non_declarative_kind=first_evidence.statement_kind if first_evidence else "",
        has_main_guard=has_main_guard_value,
        is_dunder_main=getattr(module, "is_dunder_main"),
    )


def _program_kind(module_kind: str, inbound_references: list[ReferenceRecord]) -> str:
    if module_kind == "library_module":
        return ""
    if inbound_references:
        return "imported_program"
    return "standalone_program"


def _program_subtype(program_kind: str, non_declarative_after_last_function: bool) -> str:
    if program_kind != "imported_program":
        return ""
    if non_declarative_after_last_function:
        return "review"
    return "probable_library"


def _default_output_dir() -> Path:
    return Path("files") / "output" / "sdda" / "entrypoints"
