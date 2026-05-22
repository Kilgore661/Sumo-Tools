"""Manifest class for table Published Artefacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(frozen=True, kw_only=True)
class OptionValue:
    value: str | int | bool
    label: str


@dataclass(frozen=True, kw_only=True)
class Option:
    id: str
    label: str
    kind: Literal["boolean", "enum", "multi_enum", "integer", "float", "text"]
    default: str | int | float | bool | tuple[str, ...]
    values: tuple[OptionValue, ...] = ()
    control: str | None = None
    url_key: str | None = None


@dataclass(frozen=True, kw_only=True)
class DataSource:
    id: str
    path: str
    media_type: str
    label: str | None = None
    option_id: str | None = None
    option_value: str | int | bool | None = None
    metadata_path: str | None = None


@dataclass(frozen=True, kw_only=True)
class IndexedDataSource:
    id: str
    index_path: str
    index_media_type: str
    payload_path_field: str
    payload_media_type: str
    label: str | None = None


@dataclass(frozen=True, kw_only=True)
class SortSpec:
    column: str
    descending: bool
    role: str | None = None


@dataclass(frozen=True, kw_only=True)
class TableColumn:
    id: str
    heading: str
    source_field: str | None = None
    group: str | None = None
    sortable: bool = True
    sort_key: str | None = None
    sort_kind: str = "auto"
    formatter: str | None = None
    align: Literal["left", "center", "right"] = "left"
    always_visible: bool = False
    note: str | None = None
    link: str | None = None


@dataclass(frozen=True, kw_only=True)
class ColumnGroup:
    id: str
    heading: str
    columns: tuple[str, ...]
    always_visible: bool = False


@dataclass(frozen=True, kw_only=True)
class GroupVisibilityPreset:
    id: str
    label: str
    visible_groups: tuple[str, ...]
    default_sort: SortSpec | None = None


@dataclass(frozen=True, kw_only=True)
class TableSection:
    id: str
    heading: str
    source_field: str
    source_value: str
    order_by: str | None = None


@dataclass(frozen=True, kw_only=True)
class Note:
    id: str
    text: str
    placement: str = "below_table"
    applies_to: tuple[str, ...] = ("all",)
    format: Literal["text", "html"] = "text"


@dataclass(frozen=True, kw_only=True)
class TablePA:
    id: str
    heading: str
    data_sources: tuple[DataSource, ...]
    columns: tuple[TableColumn, ...]
    options: tuple[Option, ...] = ()
    primary_source: str | None = None
    sections: tuple[TableSection, ...] = ()
    column_groups: tuple[ColumnGroup, ...] = ()
    group_visibility_presets: tuple[GroupVisibilityPreset, ...] = ()
    default_sort: SortSpec | None = None
    notes: tuple[Note, ...] = ()
    renderer: str = "standard_table"
    consumes_options: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        option_ids = {option.id for option in self.options}
        source_ids = {source.id for source in self.data_sources}
        column_ids = {column.id for column in self.columns}
        group_ids = {group.id for group in self.column_groups}
        note_ids = {note.id for note in self.notes}

        self._require_unique("option", [option.id for option in self.options])
        self._require_unique("data source", [source.id for source in self.data_sources])
        self._require_unique("column", [column.id for column in self.columns])
        self._require_unique("column group", [group.id for group in self.column_groups])
        self._require_unique("note", [note.id for note in self.notes])

        if self.primary_source is not None and self.primary_source not in source_ids:
            raise ValueError(f"{self.id}: primary source {self.primary_source!r} is unknown")

        for source in self.data_sources:
            if source.option_id is not None and source.option_id not in option_ids:
                raise ValueError(
                    f"{self.id}: data source {source.id!r} refers to unknown "
                    f"option {source.option_id!r}"
                )

        for column in self.columns:
            if column.group is not None and column.group not in group_ids:
                raise ValueError(
                    f"{self.id}: column {column.id!r} refers to unknown group "
                    f"{column.group!r}"
                )
            if column.note is not None and column.note not in note_ids:
                raise ValueError(
                    f"{self.id}: column {column.id!r} refers to unknown note "
                    f"{column.note!r}"
                )

        for group in self.column_groups:
            for column_id in group.columns:
                if column_id not in column_ids:
                    raise ValueError(
                        f"{self.id}: group {group.id!r} refers to unknown "
                        f"column {column_id!r}"
                    )

        for preset in self.group_visibility_presets:
            for group_id in preset.visible_groups:
                if group_id not in group_ids:
                    raise ValueError(
                        f"{self.id}: preset {preset.id!r} refers to unknown "
                        f"group {group_id!r}"
                    )
            if preset.default_sort is not None:
                self._validate_sort(preset.default_sort)

        if self.default_sort is not None:
            self._validate_sort(self.default_sort)

        for option_id in self.consumes_options:
            if option_id not in option_ids:
                raise ValueError(f"{self.id}: consumes unknown option {option_id!r}")

    def to_manifest_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def _validate_sort(self, sort: SortSpec) -> None:
        columns = {column.id: column for column in self.columns}
        if sort.column not in columns:
            raise ValueError(f"{self.id}: sort column {sort.column!r} is unknown")
        if not columns[sort.column].sortable:
            raise ValueError(f"{self.id}: sort column {sort.column!r} is not sortable")

    @staticmethod
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


@dataclass(frozen=True, kw_only=True)
class IndexedTablePA:
    id: str
    heading: str
    indexed_source: IndexedDataSource
    selector_option: str
    columns: tuple[TableColumn, ...]
    options: tuple[Option, ...] = ()
    column_groups: tuple[ColumnGroup, ...] = ()
    group_visibility_presets: tuple[GroupVisibilityPreset, ...] = ()
    default_sort: SortSpec | None = None
    notes: tuple[Note, ...] = ()
    renderer: str = "indexed_table"
    consumes_options: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        option_ids = {option.id for option in self.options}
        column_ids = {column.id for column in self.columns}
        group_ids = {group.id for group in self.column_groups}
        note_ids = {note.id for note in self.notes}

        TablePA._require_unique("option", [option.id for option in self.options])
        TablePA._require_unique("column", [column.id for column in self.columns])
        TablePA._require_unique("column group", [group.id for group in self.column_groups])
        TablePA._require_unique("note", [note.id for note in self.notes])

        if self.selector_option not in option_ids:
            raise ValueError(
                f"{self.id}: selector option {self.selector_option!r} is unknown"
            )

        for column in self.columns:
            if column.group is not None and column.group not in group_ids:
                raise ValueError(
                    f"{self.id}: column {column.id!r} refers to unknown group "
                    f"{column.group!r}"
                )
            if column.note is not None and column.note not in note_ids:
                raise ValueError(
                    f"{self.id}: column {column.id!r} refers to unknown note "
                    f"{column.note!r}"
                )

        for group in self.column_groups:
            for column_id in group.columns:
                if column_id not in column_ids:
                    raise ValueError(
                        f"{self.id}: group {group.id!r} refers to unknown "
                        f"column {column_id!r}"
                    )

        for preset in self.group_visibility_presets:
            for group_id in preset.visible_groups:
                if group_id not in group_ids:
                    raise ValueError(
                        f"{self.id}: preset {preset.id!r} refers to unknown "
                        f"group {group_id!r}"
                    )
            if preset.default_sort is not None:
                self._validate_sort(preset.default_sort)

        if self.default_sort is not None:
            self._validate_sort(self.default_sort)

        for option_id in self.consumes_options:
            if option_id not in option_ids:
                raise ValueError(f"{self.id}: consumes unknown option {option_id!r}")

    def to_manifest_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def _validate_sort(self, sort: SortSpec) -> None:
        columns = {column.id: column for column in self.columns}
        if sort.column not in columns:
            raise ValueError(f"{self.id}: sort column {sort.column!r} is unknown")
        if not columns[sort.column].sortable:
            raise ValueError(f"{self.id}: sort column {sort.column!r} is not sortable")
