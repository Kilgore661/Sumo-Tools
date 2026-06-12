from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OutputRootEvidenceRecord:
    module: str
    scope: str
    line: int
    action: str
    family_pattern: str
    candidate_output_root: str
    evidence_kind: str
    confidence: str
    raw_expression: str
    reason: str


@dataclass(frozen=True)
class ModuleOutputRootRecord:
    module: str
    output_root: str
    status: str
    confidence: str
    evidence_count: int
    shortest_root: str
    convention_root: str
    roots_seen: str
    reason: str

