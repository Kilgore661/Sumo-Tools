"""Publication contracts for tracker History artifacts."""

from __future__ import annotations

from pathlib import Path

from src.infra.tracker import update_cycle
from src.infra.history_artifacts import history_from_year
from src.sumo_core.History import Date, History
from src.sumo_core.BasicPrimitives import Month, Year


def test_canonical_publish_also_refreshes_post_1988_zip(
    tmp_path: Path,
    monkeypatch,
) -> None:
    history = History()
    before = _date(1988, 11)
    first = _date(1989, 1)
    latest = _date(2026, 7)
    history[before] = "before"  # type: ignore[assignment]
    history[first] = "first"  # type: ignore[assignment]
    history[latest] = "latest"  # type: ignore[assignment]
    saved: list[tuple[History, str]] = []

    def save(history_to_save: History, path: str) -> None:
        saved.append((history_to_save, path))
        Path(path + ".zip").touch()

    monkeypatch.setattr(update_cycle, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(update_cycle, "save_history_with_annotations", save)

    published = update_cycle._publish_canonical_history(history, 1958, 2026)

    assert published is True
    assert [Path(path).name for _, path in saved] == [
        "1958_01 to 2026_11",
        "1989_01 to 2026_11",
    ]
    assert set(saved[0][0]) == {before, first, latest}
    assert set(saved[1][0]) == {first, latest}


def test_publish_does_not_duplicate_post_1988_artifact_before_1989(
    tmp_path: Path,
    monkeypatch,
) -> None:
    history = History()
    history[_date(1988, 11)] = "before"  # type: ignore[assignment]
    saved_paths: list[str] = []

    def save(_history: History, path: str) -> None:
        saved_paths.append(path)
        Path(path + ".zip").touch()

    monkeypatch.setattr(update_cycle, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(update_cycle, "save_history_with_annotations", save)

    assert update_cycle._publish_canonical_history(history, 1958, 1988) is True
    assert [Path(path).name for path in saved_paths] == ["1958_01 to 1988_11"]


def test_history_from_year_preserves_only_requested_date_domain() -> None:
    history = History()
    before = _date(1988, 11)
    first = _date(1989, 1)
    history[before] = "before"  # type: ignore[assignment]
    history[first] = "first"  # type: ignore[assignment]

    result = history_from_year(history, 1989)

    assert set(result) == {first}


def _date(year: int, month: int) -> Date:
    return Date(Year(year), Month(month))
