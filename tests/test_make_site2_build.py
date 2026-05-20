from pathlib import Path

import pytest

from src.products.make_site2 import build as make_site2_build


def test_make_site2_build_uses_live_store_when_no_history_zip_is_given(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    live_history = object()
    captured: dict[str, object] = {}

    monkeypatch.setattr(make_site2_build, "get_history", lambda: live_history)
    monkeypatch.setattr(
        make_site2_build,
        "load_history_from_zip",
        lambda path: pytest.fail("zip loader should not be used"),
    )
    monkeypatch.setattr(
        make_site2_build,
        "build_basho_results_data_output",
        lambda **kwargs: captured.update(kwargs),
    )

    make_site2_build.build_site(output_root=tmp_path)

    assert captured["history"] is live_history


def test_make_site2_build_uses_history_zip_when_given(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    zip_history = object()
    captured: dict[str, object] = {}
    history_zip = Path("history.zip")

    monkeypatch.setattr(
        make_site2_build,
        "get_history",
        lambda: pytest.fail("live store should not be used"),
    )
    monkeypatch.setattr(
        make_site2_build,
        "load_history_from_zip",
        lambda path: zip_history if path == history_zip else pytest.fail(str(path)),
    )
    monkeypatch.setattr(
        make_site2_build,
        "build_basho_results_data_output",
        lambda **kwargs: captured.update(kwargs),
    )

    make_site2_build.build_site(output_root=tmp_path, history_zip=history_zip)

    assert captured["history"] is zip_history


def test_make_site2_build_rejects_history_and_history_zip_together(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="either history or history_zip"):
        make_site2_build.build_site(
            output_root=tmp_path,
            history=object(),
            history_zip=Path("history.zip"),
        )
