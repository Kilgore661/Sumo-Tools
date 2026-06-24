"""Core public-site model for make_site2.

This is copied forward from the useful upper half of make_site, with the old
ViewSpec/rendering boundary removed. Pages stop at site-facing artifact/data
references so the next step can resolve them into the Publication UI Model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Mapping


class PageStatus(StrEnum):
    """Publication status used by build planning."""

    PROMOTED = "promoted"
    CANDIDATE = "candidate"
    RESEARCH = "research"
    DIAGNOSTIC = "diagnostic"
    LEGACY = "legacy"
    SUPERSEDED = "superseded"
    EXCLUDED = "excluded"


@dataclass(frozen=True, kw_only=True)
class SiteBuildConfig:
    """Build/deploy context for a generated site."""

    base_route: str
    output_root: Path
    build_mode: str = "production"
    cache_mode: str = "dev"
    cache_bust_param: str = "cb"


@dataclass(frozen=True, kw_only=True)
class BuildOutput:
    """Completed static output tree ready for deployment."""

    root: Path
    entrypoint: Path
    file_count: int


@dataclass(frozen=True)
class NavigationTree:
    """Recursive subject-led navigation tree."""

    id: str
    label: str
    slug: str
    children: tuple["NavigationTree", ...] = ()
    page_id: str | None = None
    href: str | None = None


@dataclass(frozen=True, kw_only=True)
class ArtifactRef:
    """Site-facing reference to an analytical artifact.

    The referenced producer data is not rendered here. This is the object that
    later crosses the key seam into a Publication UI Model.
    """

    id: str
    kind: str
    producer: str | None = None


@dataclass(frozen=True, kw_only=True)
class DataRef:
    """Reference to site-facing data required by a page/artifact."""

    id: str
    path: Path | str
    media_type: str = "application/json"


@dataclass(frozen=True, kw_only=True)
class PageDefinition:
    """Public page known to the site before publication planning."""

    id: str
    title: str
    summary: str
    artifact: ArtifactRef
    status: PageStatus
    data: tuple[DataRef, ...] = ()


@dataclass(frozen=True, kw_only=True)
class PageRegistry:
    """Finite mapping from page ids to page definitions."""

    pages: Mapping[str, PageDefinition]


@dataclass(frozen=True, kw_only=True)
class SiteDefinition:
    """Declared public-site model."""

    id: str
    title: str
    navigation: NavigationTree
    research_navigation: NavigationTree
    pages: PageRegistry
