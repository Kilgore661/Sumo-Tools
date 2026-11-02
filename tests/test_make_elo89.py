from pathlib import Path

from src.products import build_elo89
from src.products.make_elo89.__main__ import (
    DEFAULT_DATA_BUNDLE,
    DEFAULT_OUTPUT_ROOT,
    build_parser,
)
from src.products.make_site89.deploy import load_deployment_plan


def test_make_elo89_defaults_are_independent() -> None:
    args = build_parser().parse_args(["--build-only", "--prod"])

    assert args.data_bundle == DEFAULT_DATA_BUNDLE
    assert args.data_bundle == Path("files/output/analysis/elo89_site_bundle")
    assert args.output == DEFAULT_OUTPUT_ROOT
    assert args.output.name == "make_elo89"
    assert args.output.name != "make_site89"


def test_make_elo89_local_target_is_independent() -> None:
    plan = load_deployment_plan(Path("distro/make_elo89_targets.json"))
    target = plan.targets["local_apache"]
    remote = plan.targets["remote_661"]

    assert target.location == "A:/local/html/sumo-elo89"
    assert target.url == "http://192.168.0.146/sumo-elo89/"
    assert "sumo-tools89" not in target.location
    assert plan.default_targets == ("local_apache", "remote_661")
    assert remote.method == "sftp"
    assert remote.host == "www.661.org.uk"
    assert remote.user == "root"
    assert remote.location == "/var/www/html/sumo-elo89"
    assert remote.url == "http://68.66.241.105/sumo-elo89/"
    assert remote.password_env == "GEOLOCATION"


def test_live_workflow_produces_independent_bundle_and_forwards_flags(
    monkeypatch,
    tmp_path: Path,
) -> None:
    full_history = object()
    selected_history = object()
    captured = {}
    forwarded = []
    monkeypatch.setattr(build_elo89, "get_history", lambda: full_history)
    monkeypatch.setattr(
        build_elo89,
        "history_from_year",
        lambda history, year: (
            captured.update(history=history, year=year) or selected_history
        ),
    )
    monkeypatch.setattr(
        build_elo89,
        "produce_site89_bundle",
        lambda **kwargs: captured.update(production=kwargs),
    )
    monkeypatch.setattr(build_elo89, "run_make_elo89", lambda argv: forwarded.extend(argv))
    monkeypatch.setattr(build_elo89, "DEFAULT_FUTURE_PATH", tmp_path / "absent.json")
    monkeypatch.setattr(build_elo89, "NEW_BANZUKE_JSON", tmp_path / "absent-banzuke.json")
    bundle = tmp_path / "elo89-bundle"
    output = tmp_path / "make_elo89"
    argv = [
        "--data-bundle",
        str(bundle),
        "--output",
        str(output),
        "--prod",
        "--build-only",
    ]

    build_elo89.main(argv)

    assert captured["history"] is full_history
    assert captured["year"] == 1989
    assert captured["production"]["history"] is selected_history
    assert captured["production"]["output_root"] == bundle
    assert captured["production"]["new_banzuke"] is None
    assert callable(captured["production"]["progress"])
    assert forwarded == argv


def test_no_build_skips_live_production(monkeypatch) -> None:
    monkeypatch.setattr(
        build_elo89,
        "get_history",
        lambda: (_ for _ in ()).throw(AssertionError("live store was accessed")),
    )
    monkeypatch.setattr(
        build_elo89,
        "produce_site89_bundle",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("bundle was produced")),
    )
    forwarded = []
    monkeypatch.setattr(build_elo89, "run_make_elo89", lambda argv: forwarded.extend(argv))

    build_elo89.main(["--no-build", "--local-only"])

    assert forwarded == ["--no-build", "--local-only"]
