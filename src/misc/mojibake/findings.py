"""Finding model and report writers for the mojibake audit."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class Finding:
    path: str
    line: int
    kind: str
    detail: str
    evidence: str


def write_findings(path: Path, findings: list[Finding]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=("path", "line", "kind", "detail", "evidence"),
        )
        writer.writeheader()
        for finding in findings:
            writer.writerow(
                {
                    "path": finding.path,
                    "line": finding.line,
                    "kind": finding.kind,
                    "detail": finding.detail,
                    "evidence": finding.evidence,
                }
            )


def write_summary(path: Path, findings: list[Finding]) -> None:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=("kind", "count"))
        writer.writeheader()
        for kind, count in sorted(counts.items()):
            writer.writerow({"kind": kind, "count": count})
