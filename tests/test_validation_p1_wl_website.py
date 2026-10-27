from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.products.make_site89.models import BuildOutput
from src.validation.kimarite.p1_wl_website import runner


def test_build_is_kimarite_owned_and_uses_unchanged_assembler(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    bundle_root, bundle, prior_sha256 = _bundle_fixture(tmp_path)
    captured = {}

    monkeypatch.setattr(runner, "load_site_data_bundle", lambda path: bundle)

    def fake_build_site(*, data_bundle, output_root, cache_mode):
        captured.update(
            data_bundle=data_bundle,
            output_root=output_root,
            cache_mode=cache_mode,
        )
        output_root.mkdir(parents=True)
        entrypoint = output_root / "index.html"
        entrypoint.write_text("<html>P1-WL</html>", encoding="utf-8")
        return BuildOutput(root=output_root, entrypoint=entrypoint, file_count=1)

    monkeypatch.setattr(runner, "build_site", fake_build_site)
    output = tmp_path / "website-run"

    result = runner.build_p1_wl_website(
        data_bundle=bundle_root,
        output_root=output,
        expected_prior_sha256=prior_sha256,
    )

    assert result == output
    assert captured == {
        "data_bundle": bundle_root.resolve(),
        "output_root": output / "site",
        "cache_mode": "dev",
    }
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "complete"
    assert manifest["ownership"] == {
        "orchestrator": "src.validation.kimarite.p1_wl_website",
        "assembler_dependency": "src.products.make_site89.build.build_site",
        "deployment_invoked": False,
    }
    assert manifest["input"]["accepted_prior_sha256"] == prior_sha256
    assert manifest["input"]["copied_prior_pair_count"] == 1
    assert manifest["output"]["file_count"] == 1
    assert manifest["output"]["reported_file_count"] == 1
    assert manifest["output"]["entrypoint"] == "site/index.html"
    console = capsys.readouterr().out
    assert "py -m http.server 8766" in console
    assert "http://localhost:8766/" in console


def test_rejects_bundle_with_wrong_prior_before_build(
    monkeypatch, tmp_path: Path
) -> None:
    bundle_root, bundle, _prior_sha256 = _bundle_fixture(tmp_path)
    monkeypatch.setattr(runner, "load_site_data_bundle", lambda path: bundle)
    built = False

    def unexpected_build(**kwargs):
        nonlocal built
        built = True

    monkeypatch.setattr(runner, "build_site", unexpected_build)
    output = tmp_path / "website-run"

    with pytest.raises(ValueError, match="accepted P1-WL prior"):
        runner.build_p1_wl_website(
            data_bundle=bundle_root,
            output_root=output,
            expected_prior_sha256="0" * 64,
        )

    assert built is False
    assert not output.exists()


def test_refuses_to_overwrite_existing_run(tmp_path: Path) -> None:
    output = tmp_path / "website-run"
    output.mkdir()

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        runner.build_p1_wl_website(
            data_bundle=tmp_path / "unused",
            output_root=output,
        )


def _bundle_fixture(tmp_path: Path):
    root = (tmp_path / "candidate").resolve()
    rating_root = root / "sources/elo89"
    rating_root.mkdir(parents=True)
    prior_path = rating_root / "prior.csv"
    prior_path.write_text("rank_pair,ordinal,rating\nM1,10000,2300\n", encoding="utf-8")
    prior_sha256 = hashlib.sha256(prior_path.read_bytes()).hexdigest()
    rating_manifest = {
        "model_id": "elo-89",
        "prior": {
            "copied_to": "prior.csv",
            "source_sha256": prior_sha256,
            "pair_count": 1,
        },
    }
    (rating_root / "manifest.json").write_text(
        json.dumps(rating_manifest), encoding="utf-8"
    )
    bundle_manifest = {
        "schema_version": 1,
        "model_id": "elo-89",
        "history": {"start": "1989/01", "end": "2026/09"},
        "rating_run": "sources/elo89/manifest.json",
        "artifacts": [],
    }
    (root / "manifest.json").write_text(
        json.dumps(bundle_manifest), encoding="utf-8"
    )
    bundle = SimpleNamespace(
        root=root,
        history_start="1989/01",
        history_end="2026/09",
        artifacts=(),
        manifest=bundle_manifest,
    )
    return root, bundle, prior_sha256
