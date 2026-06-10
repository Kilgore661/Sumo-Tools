from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyse_entrypoints
from .reports import write_reports


def main() -> None:
    args = _parse_args()
    result = analyse_entrypoints(import_root=args.import_root)
    write_reports(result)
    _print_summary(result)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SDDA repository entrypoint index")
    parser.add_argument(
        "--import-root",
        type=Path,
        default=Path("."),
        help="Repository/import root used to resolve project modules",
    )
    return parser.parse_args()


def _print_summary(result) -> None:
    program_rows = [row for row in result.module_index_rows if row.module_kind == "program"]
    standalone_rows = [row for row in result.module_index_rows if row.program_kind == "standalone_program"]
    command_like_rows = [row for row in standalone_rows if row.standalone_subtype == "command_like"]
    weak_entrypoint_rows = [
        row for row in standalone_rows if row.standalone_subtype == "weak_entrypoint_signal"
    ]
    imported_rows = [row for row in result.module_index_rows if row.program_kind == "imported_program"]
    library_rows = [row for row in result.module_index_rows if row.module_kind == "library_module"]
    resolution_notes = [row for row in result.warnings if row.severity == "note"]
    warnings = [row for row in result.warnings if row.severity == "warning"]
    print(f"Wrote {result.output_dir}")
    print(f"Modules indexed: {len(result.module_index_rows)}")
    print(f"Library modules: {len(library_rows)}")
    print(f"Programs: {len(program_rows)}")
    print(f"Standalone programs: {len(standalone_rows)}")
    print(f"  Command-like: {len(command_like_rows)}")
    print(f"  Weak entrypoint signal: {len(weak_entrypoint_rows)}")
    print(f"Imported programs: {len(imported_rows)}")
    print(f"References: {len(result.references)}")
    print(f"Resolution notes: {len(resolution_notes)}")
    print(f"Warnings: {len(warnings)}")


if __name__ == "__main__":
    main()
