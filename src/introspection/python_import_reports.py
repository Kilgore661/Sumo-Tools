"""Report writers for Python import introspection outputs."""

from __future__ import annotations

import csv
from pathlib import Path

from src.introspection.python_import_model import ImportEdge, PythonModule


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write dictionaries to a UTF-8 CSV file with a stable header."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def module_import_summary(
    modules: list[PythonModule],
    edges: list[ImportEdge],
) -> dict[str, dict[str, set[str]]]:
    """Summarise importers and imported symbols by target module."""

    summary: dict[str, dict[str, set[str]]] = {
        module.module_name: {
            "imported_by_modules": set(),
            "imported_symbols": set(),
            "main_imported_by_modules": set(),
            "non_main_imported_by_modules": set(),
        }
        for module in modules
    }

    for edge in edges:
        target_module = edge.resolved_module
        if target_module not in summary:
            continue

        target = summary[target_module]
        target["imported_by_modules"].add(edge.importer_module)

        if edge.imported_symbol:
            target["imported_symbols"].add(edge.imported_symbol)
            if edge.imported_symbol == "main":
                target["main_imported_by_modules"].add(edge.importer_module)
            else:
                target["non_main_imported_by_modules"].add(edge.importer_module)

    return summary


def module_rows(modules: list[PythonModule], edges: list[ImportEdge]) -> list[dict[str, object]]:
    """Build summary rows for discovered modules."""

    summary = module_import_summary(modules, edges)
    rows: list[dict[str, object]] = []

    for module in modules:
        target = summary[module.module_name]
        importers = sorted(target["imported_by_modules"])
        rows.append(
            {
                "module_path": module.path.as_posix(),
                "module_name": module.module_name,
                "has_main_guard": module.has_main_guard,
                "defines_main": module.defines_main,
                "parse_status": module.parse_status,
                "parse_error": module.parse_error,
                "imported_by_count": len(importers),
                "imported_by_modules": ";".join(importers),
                "imported_symbols": ";".join(sorted(target["imported_symbols"])),
                "main_imported_by_modules": ";".join(sorted(target["main_imported_by_modules"])),
                "non_main_imported_by_modules": ";".join(
                    sorted(target["non_main_imported_by_modules"])
                ),
            }
        )
    return rows


def edge_rows(edges: list[ImportEdge]) -> list[dict[str, object]]:
    """Build CSV rows for import edges."""

    return [
        {
            "importer_path": edge.importer_path.as_posix(),
            "importer_module": edge.importer_module,
            "import_style": edge.import_style,
            "imported_module_text": edge.imported_module_text,
            "imported_symbol": edge.imported_symbol,
            "imported_alias": edge.imported_alias,
            "level": edge.level,
            "is_relative": edge.is_relative,
            "resolved_module": edge.resolved_module,
            "resolved_path": edge.resolved_path,
            "resolved_symbol_module": edge.resolved_symbol_module,
            "resolved_symbol_path": edge.resolved_symbol_path,
            "resolution_status": edge.resolution_status,
        }
        for edge in edges
    ]


def candidate_role(row: dict[str, object]) -> str:
    """Return a first-pass role label from import summary facts."""

    has_main_guard = row["has_main_guard"] is True
    imported_by_count = int(row["imported_by_count"])
    main_imported = bool(row["main_imported_by_modules"])
    non_main_imported = bool(row["non_main_imported_by_modules"])

    if has_main_guard and imported_by_count == 0:
        return "standalone_entry_candidate"
    if has_main_guard and non_main_imported:
        return "runnable_support_candidate"
    if has_main_guard and main_imported:
        return "main_imported_needs_review"
    if has_main_guard:
        return "runnable_imported_candidate"
    if imported_by_count > 0:
        return "support_module_candidate"
    return "orphan_non_runnable_candidate"


def needs_review(row: dict[str, object]) -> bool:
    """Return true when the first-pass classification needs human inspection."""

    role = candidate_role(row)
    return role in {
        "main_imported_needs_review",
        "runnable_imported_candidate",
        "orphan_non_runnable_candidate",
    }


def entry_candidate_rows(module_summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return compact rows for modules that expose a ``__main__`` execution surface."""

    rows: list[dict[str, object]] = []
    for row in module_summary_rows:
        if row["has_main_guard"] is not True:
            continue
        rows.append(
            {
                "module_path": row["module_path"],
                "module_name": row["module_name"],
                "defines_main": row["defines_main"],
                "imported_by_count": row["imported_by_count"],
                "imported_by_modules": row["imported_by_modules"],
                "main_imported_by_modules": row["main_imported_by_modules"],
                "non_main_imported_by_modules": row["non_main_imported_by_modules"],
                "candidate_role": candidate_role(row),
                "needs_review": needs_review(row),
            }
        )
    return rows


def imported_main_rows(edges: list[ImportEdge]) -> list[dict[str, object]]:
    """Return compact evidence rows for ``from x import main`` edges."""

    return [
        {
            "importer_path": edge.importer_path.as_posix(),
            "importer_module": edge.importer_module,
            "imported_module_text": edge.imported_module_text,
            "resolved_module": edge.resolved_module,
            "resolved_path": edge.resolved_path,
            "resolution_status": edge.resolution_status,
        }
        for edge in edges
        if edge.import_style == "from" and edge.imported_symbol == "main"
    ]


def write_reports(output_dir: Path, modules: list[PythonModule], edges: list[ImportEdge]) -> None:
    """Write raw evidence CSVs and compact review CSVs."""

    modules_csv = output_dir / "python_modules.csv"
    edges_csv = output_dir / "python_import_edges.csv"
    entry_candidates_csv = output_dir / "python_entry_candidates.csv"
    imported_main_csv = output_dir / "python_imported_main.csv"

    module_summary_rows = module_rows(modules, edges)

    write_csv(
        modules_csv,
        [
            "module_path",
            "module_name",
            "has_main_guard",
            "defines_main",
            "parse_status",
            "parse_error",
            "imported_by_count",
            "imported_by_modules",
            "imported_symbols",
            "main_imported_by_modules",
            "non_main_imported_by_modules",
        ],
        module_summary_rows,
    )
    write_csv(
        edges_csv,
        [
            "importer_path",
            "importer_module",
            "import_style",
            "imported_module_text",
            "imported_symbol",
            "imported_alias",
            "level",
            "is_relative",
            "resolved_module",
            "resolved_path",
            "resolved_symbol_module",
            "resolved_symbol_path",
            "resolution_status",
        ],
        edge_rows(edges),
    )
    write_csv(
        entry_candidates_csv,
        [
            "module_path",
            "module_name",
            "defines_main",
            "imported_by_count",
            "imported_by_modules",
            "main_imported_by_modules",
            "non_main_imported_by_modules",
            "candidate_role",
            "needs_review",
        ],
        entry_candidate_rows(module_summary_rows),
    )
    write_csv(
        imported_main_csv,
        [
            "importer_path",
            "importer_module",
            "imported_module_text",
            "resolved_module",
            "resolved_path",
            "resolution_status",
        ],
        imported_main_rows(edges),
    )
