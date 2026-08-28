"""Direct parser publication keeps the post-1988 History zip synchronized."""

from __future__ import annotations

from pathlib import Path

from src.infra.parser import parser2
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.History import Date, History


def test_direct_full_history_parse_writes_full_and_post_1988_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    history = History()
    before = _date(1988, 11)
    first = _date(1989, 1)
    history[before] = "before"  # type: ignore[assignment]
    history[first] = "first"  # type: ignore[assignment]
    saved: list[tuple[History, str]] = []

    monkeypatch.setattr(parser2, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(parser2, "parse_range", lambda _start, _end: history)
    monkeypatch.setattr(
        parser2,
        "save_history_with_annotations",
        lambda value, path: saved.append((value, path)),
    )

    parser2.parse_and_save_history(1958, 2026)

    assert [Path(path).name for _, path in saved] == [
        "1958_01 to 2026_11",
        "1989_01 to 2026_11",
    ]
    assert set(saved[0][0]) == {before, first}
    assert set(saved[1][0]) == {first}


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))
