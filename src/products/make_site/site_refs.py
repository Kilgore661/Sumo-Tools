"""File-reference helpers for the public site definition."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from .classes import AssetRef, DataRef, ViewRef


def asset(
    id: str,
    source_path: Path,
    output_path: str,
    media_type: str,
) -> AssetRef:
    return AssetRef(
        id=id,
        source_path=source_path,
        output_path=PurePosixPath(output_path),
        media_type=media_type,
    )


def data(
    id: str,
    source_path: Path,
    output_path: str,
    media_type: str,
) -> DataRef:
    return DataRef(
        id=id,
        source_path=source_path,
        output_path=PurePosixPath(output_path),
        media_type=media_type,
    )


def data_media_type(source_path: Path) -> str:
    return {
        ".csv": "text/csv",
        ".json": "application/json",
    }[source_path.suffix]


def published_data_refs(
    source_dir: Path,
    output_dir: str,
    id_prefix: str,
) -> tuple[DataRef, ...]:
    return tuple(
        data(
            id=f"{id_prefix}_{source_path.stem}",
            source_path=source_path,
            output_path=str(PurePosixPath(output_dir) / source_path.name),
            media_type=data_media_type(source_path),
        )
        for source_path in sorted(source_dir.iterdir())
        if source_path.suffix in {".csv", ".json"}
    )


def view(
    id: str,
    source_path: Path,
    media_type: str = "text/html",
) -> ViewRef:
    return ViewRef(
        id=id,
        source_path=source_path,
        media_type=media_type,
    )
