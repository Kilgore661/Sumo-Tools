"""Semantic UI model for make_site2.

This is the layer make_site2 exists to make explicit. Renderers consume these
objects; they do not decide what public pages, filters, panels, or artifacts are.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .publication_model import NavigationItem


ControlKind = Literal["select", "checkbox"]


@dataclass(frozen=True, kw_only=True)
class NavigationCollapseControl:
    enabled: bool
    storage_key: str


@dataclass(frozen=True, kw_only=True)
class NavigationBar:
    heading: str
    navigation_tree: tuple[NavigationItem, ...]
    collapse_control: NavigationCollapseControl


@dataclass(frozen=True, kw_only=True)
class FilterValue:
    value: str
    label: str


@dataclass(frozen=True, kw_only=True)
class FilterValuesSource:
    source: str
    field: str
    label_field: str
    order_field: str
    partition_filter: str | None = None
    partition_field: str | None = None
    partition_normalizer: str | None = None


@dataclass(frozen=True, kw_only=True)
class Filter:
    id: str
    label: str
    control: ControlKind
    default: str | bool
    url_key: str
    values: tuple[FilterValue, ...] = ()
    values_source: FilterValuesSource | None = None


@dataclass(frozen=True, kw_only=True)
class FilterSection:
    filters: tuple[Filter, ...]


@dataclass(frozen=True, kw_only=True)
class PA:
    artifact_id: str


@dataclass(frozen=True, kw_only=True)
class Notes:
    note_ids: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class PAPanel:
    pa: PA
    notes: Notes


@dataclass(frozen=True, kw_only=True)
class Contents:
    filter_section: FilterSection | None
    pa_panel: PAPanel


@dataclass(frozen=True, kw_only=True)
class Heading:
    title: str
    summary: str


@dataclass(frozen=True, kw_only=True, init=False)
class ContentPanel:
    page_id: str
    heading: Heading
    contents: Contents

    def __init__(
        self,
        *,
        page_id: str,
        heading: Heading,
        contents: Contents,
        grammar: str | None = None,
    ) -> None:
        """Construct a content panel.

        ``grammar`` is accepted temporarily while repeated site-manifest panel
        declarations are migrated from their former ``grammar="G1"`` spelling.
        It is not model state and is not serialized into the public UI manifest.
        """

        if grammar not in (None, "G1"):
            raise ValueError(f"Unsupported legacy content grammar: {grammar!r}")
        object.__setattr__(self, "page_id", page_id)
        object.__setattr__(self, "heading", heading)
        object.__setattr__(self, "contents", contents)


@dataclass(frozen=True, kw_only=True)
class PublicSiteShell:
    navigation_bar: NavigationBar
    content_panels: tuple[ContentPanel, ...]


def G1Contents(
    *,
    filter_section: FilterSection,
    pa: PA,
    note_ids: tuple[str, ...] = (),
) -> Contents:
    """Temporary construction adapter for legacy site-manifest declarations.

    The returned model is the active ``Contents -> FilterSection? . PAPanel``
    structure. Empty legacy filter sections are converted to absent optional
    filter sections; Notes are explicitly owned by ``PAPanel``.
    """

    return Contents(
        filter_section=filter_section if filter_section.filters else None,
        pa_panel=PAPanel(pa=pa, notes=Notes(note_ids=note_ids)),
    )
