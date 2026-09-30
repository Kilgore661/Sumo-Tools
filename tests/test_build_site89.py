from pathlib import Path

from src.products import build_site89


def test_live_store_workflow_produces_bundle_and_forwards_existing_flags(
    monkeypatch,
    tmp_path: Path,
) -> None:
    full_history = object()
    selected_history = object()
    captured = {}
    forwarded = []

    monkeypatch.setattr(build_site89, "get_history", lambda: full_history)
    monkeypatch.setattr(
        build_site89,
        "history_from_year",
        lambda history, year: (
            captured.update(history=history, year=year) or selected_history
        ),
    )
    monkeypatch.setattr(
        build_site89,
        "produce_site89_bundle",
        lambda **kwargs: captured.update(production=kwargs),
    )
    monkeypatch.setattr(
        build_site89,
        "run_make_site89",
        lambda argv: forwarded.extend(argv),
    )
    monkeypatch.setattr(
        build_site89,
        "DEFAULT_FUTURE_PATH",
        tmp_path / "absent-future.json",
    )

    bundle = tmp_path / "bundle"
    output = tmp_path / "site"
    argv = [
        "--data-bundle",
        str(bundle),
        "--output",
        str(output),
        "--build-only",
        "--prod",
    ]
    build_site89.main(argv)

    assert captured["history"] is full_history
    assert captured["year"] == 1989
    assert captured["production"]["history"] is selected_history
    assert captured["production"]["output_root"] == bundle
    assert captured["production"]["future"] is None
    assert forwarded == argv


def test_no_build_skips_live_store_and_bundle_production(monkeypatch) -> None:
    monkeypatch.setattr(
        build_site89,
        "get_history",
        lambda: (_ for _ in ()).throw(AssertionError("live store was accessed")),
    )
    monkeypatch.setattr(
        build_site89,
        "produce_site89_bundle",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("bundle was produced")),
    )
    forwarded = []
    monkeypatch.setattr(
        build_site89,
        "run_make_site89",
        lambda argv: forwarded.extend(argv),
    )

    build_site89.main(["--no-build", "--local-only"])

    assert forwarded == ["--no-build", "--local-only"]
