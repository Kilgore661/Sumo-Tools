from __future__ import annotations

from .analysis import analyse_output_roots
from .reports import OUTPUT_DIR, write_reports


def main() -> None:
    evidence, module_roots = analyse_output_roots()
    write_reports(evidence, module_roots)
    print(f"Wrote {OUTPUT_DIR}")
    print(f"Evidence rows: {len(evidence)}")
    print(f"Modules indexed: {len(module_roots)}")
    print(f"Known output roots: {sum(row.status == 'known' for row in module_roots)}")


if __name__ == "__main__":
    main()
