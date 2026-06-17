"""UTF-8 and mojibake-marker scanning."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import MOJIBAKE_MARKERS, THIS_TOOL_PATH
from .findings import Finding


def audit_utf8_bytes(path: Path, relative_path: str) -> Iterable[Finding]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        yield Finding(
            path=relative_path,
            line=0,
            kind="non_utf8_text_candidate",
            detail=str(error),
            evidence="",
        )
        return
    if relative_path == THIS_TOOL_PATH:
        return
    yield from scan_mojibake_markers(relative_path, text)


def scan_mojibake_markers(relative_path: str, text: str) -> Iterable[Finding]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for marker in MOJIBAKE_MARKERS:
            if marker in line:
                yield Finding(
                    path=relative_path,
                    line=line_number,
                    kind="mojibake_marker",
                    detail=printable_marker(marker),
                    evidence=line.strip()[:160],
                )


def printable_marker(marker: str) -> str:
    if marker == "\ufffd":
        return "replacement_character"
    return marker
