from pathlib import Path

from src.products import build_site89


def test_live_store_workflow_produces_bundle_and_forwards_existing_flags(
    monkeypatch,
    tmp_path: Path,
    capsys,
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
        lambda argv, *, prepared_targets: forwarded.extend(argv),
    )
    monkeypatch.setattr(
        build_site89,
        "DEFAULT_FUTURE_PATH",
        tmp_path / "absent-future.json",
    )
    monkeypatch.setattr(
        build_site89,
        "NEW_BANZUKE_JSON",
        tmp_path / "absent-banzuke.json",
    )
    times = iter((100.0, 206.4))
    monkeypatch.setattr(build_site89, "time", lambda: next(times))

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
    assert captured["production"]["new_banzuke"] is None
    assert forwarded == argv
    assert "Complete run after 106.4s" in capsys.readouterr().out


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
        lambda argv, *, prepared_targets: forwarded.extend(argv),
    )

    build_site89.main(["--no-build", "--local-only"])

    assert forwarded == ["--no-build", "--local-only"]


def test_deployment_preflight_happens_before_live_store_work(monkeypatch) -> None:
    events = []
    prepared_targets = (object(),)

    monkeypatch.setattr(
        build_site89,
        "prepare_deployment_targets",
        lambda args: events.append("preflight") or prepared_targets,
    )
    monkeypatch.setattr(
        build_site89,
        "get_history",
        lambda: events.append("history") or object(),
    )
    monkeypatch.setattr(build_site89, "history_from_year", lambda *_args: object())
    monkeypatch.setattr(build_site89, "produce_site89_bundle", lambda **_kwargs: None)
    monkeypatch.setattr(
        build_site89,
        "run_make_site89",
        lambda _argv, *, prepared_targets: events.append(
            ("build", prepared_targets)
        ),
    )

    build_site89.main([])

    assert events[:2] == ["preflight", "history"]
    assert events[-1] == ("build", prepared_targets)
