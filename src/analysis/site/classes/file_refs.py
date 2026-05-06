"""File reference sorts for the public site model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True, kw_only=True)
class AssetRef:
    """
    Reference to a non-data supporting file.

    Examples include CSS, JavaScript, favicons, images, fonts, and local
    library files.
    """

    id: str
    source_path: Path
    output_path: PurePosixPath
    media_type: str | None = None


@dataclass(frozen=True, kw_only=True)
class DataRef:
    """
    Reference to a data file the page presents or consumes.

    Examples include CSV and JSON files containing analysed/project data.
    """

    id: str
    source_path: Path
    output_path: PurePosixPath
    media_type: str | None = None


@dataclass(frozen=True, kw_only=True)
class ViewRef:
    """
    Reference to a renderable view file.

    Examples include standalone HTML pages, HTML fragments, and templates.
    """

    id: str
    source_path: Path
    output_path: PurePosixPath | None = None
    media_type: str | None = "text/html"
