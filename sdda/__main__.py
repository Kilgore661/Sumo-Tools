from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyse
from .reports import write_reports


def main() -> None:
    args = _parse_args()
    result = analyse(
        root_module=args.root_module,
        import_root=args.import_root,
        output_dir=args.output_dir,
    )
    write_reports(result)
    _print_summary(result)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Static Data-Dependency Analyser")
    parser.add_argument("root_module", help="Python module to analyse as the root command")
    parser.add_argument(
        "--import-root",
        type=Path,
        default=Path("."),
        help="Repository/import root used to resolve project modules",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated reports; defaults to files/output/sdda/{root_module}",
    )
    return parser.parse_args()


def _print_summary(result) -> None:
    print(f"Wrote {result.output_dir}")
    print(f"Project modules indexed: {len(result.modules)}")
    print(f"Reachable modules: {len(result.reachable_modules)}")
    print(f"Import records: {len(result.imports)}")
    print(f"Scopes: {len(result.scopes)}")
    print(f"Type facts: {len(result.type_facts)}")
    print(f"Value facts: {len(result.value_facts)}")
    print(f"Field facts: {len(result.field_facts)}")
    print(f"File uses: {len(result.file_uses)}")
    print(f"File use resolutions: {len(result.file_use_resolutions)}")
    print(f"Producer outputs: {len(result.producer_outputs)}")
    print(f"Unresolved records: {len(result.unresolved)}")


if __name__ == "__main__":
    main()
