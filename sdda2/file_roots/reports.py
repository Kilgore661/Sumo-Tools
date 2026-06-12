from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .models import FileEffectRootRecord, ModuleFileRootRecord

OUTPUT_DIR = Path("files") / "output" / "sdda2" / "file_roots"


def write_reports(
    effects: list[FileEffectRootRecord],
    module_roots: list[ModuleFileRootRecord],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT_DIR / "file_effect_roots.csv", effects)
    _write_csv(OUTPUT_DIR / "module_file_roots.csv", module_roots)
    _write_summary(OUTPUT_DIR / "summary.csv", effects, module_roots)


def _write_csv(path: Path, rows: list[object]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    dict_rows = [asdict(row) for row in rows]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dict_rows[0]))
        writer.writeheader()
        writer.writerows(dict_rows)


def _write_summary(
    path: Path,
    effects: list[FileEffectRootRecord],
    module_roots: list[ModuleFileRootRecord],
) -> None:
    normalisation_counts = Counter(row.normalisation_status for row in effects)
    unresolved = normalisation_counts["unresolved"]
    normalised = normalisation_counts["normalised_file_path"] + normalisation_counts["normalised_file_template"]
    rows = [
        {"metric": "file_effect_rows", "value": str(len(effects))},
        {"metric": "normalised_file_path_rows", "value": str(normalised)},
        {"metric": "unnormalised_path_expression_rows", "value": str(unresolved)},
        {"metric": "module_root_rows", "value": str(len(module_roots))},
        {"metric": "known_module_root_rows", "value": str(sum(row.status == "known" for row in module_roots))},
        {"metric": "not_known_module_rows", "value": str(sum(row.status == "not_known" for row in module_roots))},
    ]
    rows.extend(
        {"metric": f"normalisation:{key}", "value": str(value)}
        for key, value in sorted(normalisation_counts.items())
    )
    rows.extend(
        {"metric": f"direction:{key}", "value": str(value)}
        for key, value in sorted(Counter(row.direction for row in effects).items())
    )
    rows.extend(
        {"metric": f"shape:{key}", "value": str(value)}
        for key, value in sorted(Counter(row.shape for row in effects).items())
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rows)
