"""Command-line entry point for the mojibake audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from mojibake.audit import audit_tree
from mojibake.findings import write_findings, write_summary


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    findings = sorted(
        audit_tree(root),
        key=lambda finding: (finding.path, finding.line, finding.kind, finding.detail),
    )
    write_findings(output_root / "findings.csv", findings)
    write_summary(output_root / "summary.csv", findings)
    print(f"wrote {len(findings)} findings to {output_root}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit UTF-8 boundaries and likely mojibake signatures."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root or subtree to audit. Defaults to the repo root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("files") / "output" / "mojibake_audit",
        help="Directory for CSV audit reports.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
