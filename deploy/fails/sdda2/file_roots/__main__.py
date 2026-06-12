from __future__ import annotations

from .analysis import analyse_file_roots
from .reports import OUTPUT_DIR, write_reports


def main() -> None:
    effects, module_roots = analyse_file_roots()
    write_reports(effects, module_roots)
    print(f"Wrote {OUTPUT_DIR}")
    print(f"File effect rows: {len(effects)}")
    print(f"Module root rows: {len(module_roots)}")
    print(f"Known module root rows: {sum(row.status == 'known' for row in module_roots)}")


if __name__ == "__main__":
    main()
