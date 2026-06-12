from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .models import ModuleOutputRootRecord, OutputRootEvidenceRecord

OUTPUT_DIR = Path("files") / "output" / "sdda2" / "output_root"


def write_reports(
    evidence: list[OutputRootEvidenceRecord],
    module_roots: list[ModuleOutputRootRecord],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT_DIR / "output_root_evidence.csv", evidence)
    _write_csv(OUTPUT_DIR / "module_output_roots.csv", module_roots)
    _write_summary(OUTPUT_DIR / "summary.csv", evidence, module_roots)


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
    evidence: list[OutputRootEvidenceRecord],
    module_roots: list[ModuleOutputRootRecord],
) -> None:
    rows = [
        {"metric": "evidence_rows", "value": str(len(evidence))},
        {"metric": "modules_indexed", "value": str(len(module_roots))},
        {"metric": "modules_with_known_output_root", "value": str(sum(row.status == "known" for row in module_roots))},
        {"metric": "modules_not_known", "value": str(sum(row.status == "not_known" for row in module_roots))},
    ]
    rows.extend(
        {"metric": f"confidence:{key}", "value": str(value)}
        for key, value in sorted(Counter(row.confidence for row in module_roots).items())
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rows)

