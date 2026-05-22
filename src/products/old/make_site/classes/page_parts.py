"""Page-part sorts for the public site model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .file_refs import DataRef, ViewRef


class OptionKind(StrEnum):
    """Supported abstract option kinds."""

    BOOLEAN = "boolean"
    ENUM = "enum"
    FLOAT = "float"
    INTEGER = "integer"
    MULTI_ENUM = "multi_enum"
    TEXT = "text"


@dataclass(frozen=True, kw_only=True)
class OptionValue:
    """One selectable value for an option."""

    value: str
    label: str


@dataclass(frozen=True, kw_only=True)
class OptionSpec:
    """Abstract definition of one page option."""

    id: str
    label: str
    kind: OptionKind
    default: str | int | float | bool
    values: tuple[OptionValue, ...] = ()


@dataclass(frozen=True, kw_only=True)
class OptionsModel:
    """Abstract definition of the states/parameters a page exposes."""

    options: tuple[OptionSpec, ...]


@dataclass(frozen=True, kw_only=True)
class ViewSpec:
    """Base sort for page body/view specifications."""


@dataclass(frozen=True, kw_only=True)
class StandaloneHtmlView(ViewSpec):
    """A complete HTML page used as the page view."""

    source: ViewRef


@dataclass(frozen=True, kw_only=True)
class PlotlyJsonView(ViewSpec):
    """A Plotly view rendered from chart data/config files."""

    data: DataRef
    template: str
    config: DataRef


@dataclass(frozen=True, kw_only=True)
class TableAppView(ViewSpec):
    """An interactive table-style browser page."""

    entrypoint: ViewRef


@dataclass(frozen=True, kw_only=True)
class EssayView(ViewSpec):
    """A prose/explanatory page."""

    source: ViewRef


@dataclass(frozen=True, kw_only=True)
class CustomView(ViewSpec):
    """Escape hatch for page views not yet covered by a specific view sort."""

    kind: str
