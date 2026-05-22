"""Manifest classes for chart Published Artefacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from .table_pa import DataSource, Note, Option, SortSpec, TablePA


@dataclass(frozen=True, kw_only=True)
class AxisSpec:
    id: str
    source_field: str | None = None
    label: str | None = None
    order_field: str | None = None
    order_values: tuple[str, ...] = ()
    minimum: int | float | None = None
    maximum: int | float | None = None
    tickformat: str | None = None


@dataclass(frozen=True, kw_only=True)
class TraceSpec:
    id: str
    label: str
    kind: Literal["bar", "stacked_bar", "line", "scatter"]
    x: str
    y: str
    group_by: str | None = None
    visible_by_default: bool = True
    error_y: tuple[str, str] | None = None


@dataclass(frozen=True, kw_only=True)
class ChartPA:
    id: str
    heading: str
    data_sources: tuple[DataSource, ...]
    traces: tuple[TraceSpec, ...]
    options: tuple[Option, ...] = ()
    primary_source: str | None = None
    x_axis: AxisSpec | None = None
    y_axis: AxisSpec | None = None
    default_trace: str | None = None
    notes: tuple[Note, ...] = ()
    renderer: str = "plotly_chart"
    consumes_options: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        option_ids = {option.id for option in self.options}
        source_ids = {source.id for source in self.data_sources}
        trace_ids = {trace.id for trace in self.traces}

        _require_unique("option", [option.id for option in self.options])
        _require_unique("data source", [source.id for source in self.data_sources])
        _require_unique("trace", [trace.id for trace in self.traces])
        _require_unique("note", [note.id for note in self.notes])

        if self.primary_source is not None and self.primary_source not in source_ids:
            raise ValueError(f"{self.id}: primary source {self.primary_source!r} is unknown")

        for source in self.data_sources:
            if source.option_id is not None and source.option_id not in option_ids:
                raise ValueError(
                    f"{self.id}: data source {source.id!r} refers to unknown "
                    f"option {source.option_id!r}"
                )

        if self.default_trace is not None and self.default_trace not in trace_ids:
            raise ValueError(f"{self.id}: default trace {self.default_trace!r} is unknown")

        for option_id in self.consumes_options:
            if option_id not in option_ids:
                raise ValueError(f"{self.id}: consumes unknown option {option_id!r}")

    def to_manifest_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True, kw_only=True)
class MultiViewItem:
    id: str
    label: str
    pa: ChartPA | TablePA


@dataclass(frozen=True, kw_only=True)
class MultiViewPA:
    id: str
    heading: str
    view_option: Option
    views: tuple[MultiViewItem, ...]
    renderer: str = "multi_view"
    notes: tuple[Note, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        _require_unique("view", [view.id for view in self.views])
        value_ids = {str(value.value) for value in self.view_option.values}
        view_ids = {view.id for view in self.views}
        if value_ids != view_ids:
            raise ValueError(
                f"{self.id}: view option values {sorted(value_ids)!r} do not "
                f"match views {sorted(view_ids)!r}"
            )
        if str(self.view_option.default) not in view_ids:
            raise ValueError(
                f"{self.id}: default view {self.view_option.default!r} is unknown"
            )
        for view in self.views:
            view.pa.validate()

    def to_manifest_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True, kw_only=True)
class EssayPA:
    id: str
    heading: str
    renderer: str = "prose"
    source_path: str | None = None
    body_html: str | None = None
    notes: tuple[Note, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.source_path is None and self.body_html is None:
            raise ValueError(f"{self.id}: essay PA needs source_path or body_html")
        if self.source_path is not None and self.body_html is not None:
            raise ValueError(f"{self.id}: essay PA must not define both source_path and body_html")

    def to_manifest_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True, kw_only=True)
class ExcludedPA:
    id: str
    heading: str
    reason: str
    previous_view_kind: str
    renderer: str = "excluded"
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.reason:
            raise ValueError(f"{self.id}: excluded PA needs a reason")

    def to_manifest_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


def _require_unique(kind: str, values: list[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        joined = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate {kind} id(s): {joined}")
