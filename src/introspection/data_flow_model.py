"""Shared data models for data-flow introspection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModuleRef:
    """A Python module discovered below the import root."""

    module_name: str
    path: Path


@dataclass(frozen=True)
class ImportRef:
    """One internal import edge discovered in source code."""

    importer_module: str
    imported_module: str
    imported_name: str
    alias: str
    import_style: str
    line_number: int


@dataclass(frozen=True)
class ArtifactUse:
    """One piece of evidence that a module reads or writes a file-like artifact."""

    module_name: str
    distance_from_root: int
    scope: str
    action: str
    artifact: str
    artifact_kind: str
    evidence: str
    line_number: int
    confidence: str


@dataclass(frozen=True)
class ArtifactSummary:
    """Aggregated evidence for one artifact."""

    artifact: str
    artifact_kind: str
    read_count: int
    write_count: int
    glob_count: int
    producer_modules: tuple[str, ...]
    consumer_modules: tuple[str, ...]


@dataclass(frozen=True)
class DataFlowGraph:
    """Data-flow evidence reachable from one root module."""

    root_module: str
    modules: tuple[ModuleRef, ...]
    imports: tuple[ImportRef, ...]
    artifact_uses: tuple[ArtifactUse, ...]

    @property
    def direct_artifact_uses(self) -> tuple[ArtifactUse, ...]:
        """Return artifact uses from the root module only."""

        return tuple(use for use in self.artifact_uses if use.distance_from_root == 0)

    @property
    def transitive_artifact_uses(self) -> tuple[ArtifactUse, ...]:
        """Return artifact uses from modules reachable from the root."""

        return tuple(use for use in self.artifact_uses if use.distance_from_root > 0)

    @property
    def input_artifacts(self) -> tuple[str, ...]:
        """Return unique read/glob artifacts."""

        return tuple(sorted({use.artifact for use in self.artifact_uses if use.action in {"read", "glob"}}))

    @property
    def output_artifacts(self) -> tuple[str, ...]:
        """Return unique written artifacts."""

        return tuple(sorted({use.artifact for use in self.artifact_uses if use.action == "write"}))

    @property
    def concrete_input_artifacts(self) -> tuple[str, ...]:
        """Return concrete read/glob artifacts."""

        return tuple(
            sorted(
                {
                    use.artifact
                    for use in self.artifact_uses
                    if use.action in {"read", "glob"} and use.artifact_kind == "concrete"
                }
            )
        )

    @property
    def concrete_output_artifacts(self) -> tuple[str, ...]:
        """Return concrete written artifacts."""

        return tuple(
            sorted(
                {
                    use.artifact
                    for use in self.artifact_uses
                    if use.action == "write" and use.artifact_kind == "concrete"
                }
            )
        )

    @property
    def artifact_summaries(self) -> tuple[ArtifactSummary, ...]:
        """Return producer/consumer summaries for each artifact."""

        return tuple(build_artifact_summaries(self.artifact_uses))

    @property
    def generated_prerequisites(self) -> tuple[ArtifactSummary, ...]:
        """Return artifacts that are both produced and consumed in reachable code."""

        return tuple(
            summary
            for summary in self.artifact_summaries
            if summary.write_count > 0 and (summary.read_count > 0 or summary.glob_count > 0)
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "root_module": self.root_module,
            "modules": [module_ref_to_dict(module) for module in self.modules],
            "imports": [import_ref_to_dict(import_ref) for import_ref in self.imports],
            "artifact_uses": [artifact_use_to_dict(use) for use in self.artifact_uses],
            "artifacts": [artifact_summary_to_dict(summary) for summary in self.artifact_summaries],
            "generated_prerequisites": [
                artifact_summary_to_dict(summary) for summary in self.generated_prerequisites
            ],
            "input_artifacts": list(self.input_artifacts),
            "output_artifacts": list(self.output_artifacts),
            "concrete_input_artifacts": list(self.concrete_input_artifacts),
            "concrete_output_artifacts": list(self.concrete_output_artifacts),
        }


def module_ref_to_dict(module: ModuleRef) -> dict[str, object]:
    """Return a JSON-serialisable module row."""

    return {"module_name": module.module_name, "path": module.path.as_posix()}


def import_ref_to_dict(import_ref: ImportRef) -> dict[str, object]:
    """Return a JSON-serialisable import row."""

    return {
        "importer_module": import_ref.importer_module,
        "imported_module": import_ref.imported_module,
        "imported_name": import_ref.imported_name,
        "alias": import_ref.alias,
        "import_style": import_ref.import_style,
        "line_number": import_ref.line_number,
    }


def artifact_use_to_dict(use: ArtifactUse) -> dict[str, object]:
    """Return a JSON-serialisable artifact-use row."""

    return {
        "module_name": use.module_name,
        "distance_from_root": use.distance_from_root,
        "scope": use.scope,
        "action": use.action,
        "artifact": use.artifact,
        "artifact_kind": use.artifact_kind,
        "evidence": use.evidence,
        "line_number": use.line_number,
        "confidence": use.confidence,
    }


def artifact_summary_to_dict(summary: ArtifactSummary) -> dict[str, object]:
    """Return a JSON-serialisable artifact summary row."""

    return {
        "artifact": summary.artifact,
        "artifact_kind": summary.artifact_kind,
        "read_count": summary.read_count,
        "write_count": summary.write_count,
        "glob_count": summary.glob_count,
        "producer_modules": ";".join(summary.producer_modules),
        "consumer_modules": ";".join(summary.consumer_modules),
    }


def build_artifact_summaries(uses: tuple[ArtifactUse, ...]) -> list[ArtifactSummary]:
    """Aggregate artifact uses into producer/consumer summaries."""

    by_artifact: dict[str, list[ArtifactUse]] = {}
    for use in uses:
        by_artifact.setdefault(use.artifact, []).append(use)

    summaries: list[ArtifactSummary] = []
    for artifact, artifact_uses in sorted(by_artifact.items()):
        read_uses = [use for use in artifact_uses if use.action == "read"]
        write_uses = [use for use in artifact_uses if use.action == "write"]
        glob_uses = [use for use in artifact_uses if use.action == "glob"]
        kinds = {use.artifact_kind for use in artifact_uses}
        artifact_kind = "concrete" if kinds == {"concrete"} else ";".join(sorted(kinds))
        summaries.append(
            ArtifactSummary(
                artifact=artifact,
                artifact_kind=artifact_kind,
                read_count=len(read_uses),
                write_count=len(write_uses),
                glob_count=len(glob_uses),
                producer_modules=tuple(sorted({use.module_name for use in write_uses})),
                consumer_modules=tuple(sorted({use.module_name for use in read_uses + glob_uses})),
            )
        )
    return summaries
