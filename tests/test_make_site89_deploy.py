import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

import src.products.make_site89.__main__ as site89_main
from src.products.make_site89.__main__ import build_parser
from src.products.make_site89.deploy import (
    DeployTarget,
    build_output_from_existing,
    deploy_sftp,
    deploy_targets,
    load_deployment_plan,
    preflight_deploy_target,
    select_deploy_targets,
)


def test_local_deployment_replaces_old_site_tree(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    server_root = tmp_path / "server" / "sumo-tools89"
    (output_root / "runtime").mkdir(parents=True)
    (output_root / "index.html").write_text("index", encoding="utf-8")
    (output_root / "runtime" / "site.js").write_text("runtime", encoding="utf-8")
    server_root.mkdir(parents=True)
    (server_root / "stale.txt").write_text("stale", encoding="utf-8")
    (server_root / "keep.swp").write_text("keep", encoding="utf-8")
    config_path = tmp_path / "targets.json"
    config_path.write_text(
        json.dumps(
            {
                "default_targets": ["local_apache"],
                "targets": {
                    "local_apache": {
                        "method": "win_copy",
                        "location": str(server_root),
                        "url": "http://server/sumo-tools89/",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    plan = load_deployment_plan(config_path)
    results = deploy_targets(
        build_output_from_existing(output_root),
        select_deploy_targets(plan, local_only=True),
    )

    assert len(results) == 1
    assert results[0].public_url == "http://server/sumo-tools89/"
    assert (server_root / "index.html").read_text(encoding="utf-8") == "index"
    assert (server_root / "runtime" / "site.js").read_text(encoding="utf-8") == "runtime"
    assert not (server_root / "stale.txt").exists()
    assert (server_root / "keep.swp").read_text(encoding="utf-8") == "keep"


def test_existing_build_requires_index(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="index.html"):
        build_output_from_existing(tmp_path)


def test_repository_target_is_separate_from_make_site2() -> None:
    plan = load_deployment_plan(Path("distro/make_site89_targets.json"))

    local = plan.targets["local_apache"]
    assert local.location == "A:/local/html/sumo-tools89"
    assert local.url == "http://192.168.0.146/sumo-tools89/"

    remote = plan.targets["remote_661"]
    assert remote.method == "sftp"
    assert remote.host == "www.661.org.uk"
    assert remote.user == "root"
    assert remote.location == "/var/www/html/sumo-tools89"
    assert remote.url == "http://68.66.241.105/sumo-tools89/"
    assert remote.password_env == "GEOLOCATION"
    assert remote.password_required
    assert plan.default_targets == ("local_apache", "remote_661")


def test_cli_accepts_make_site2_style_local_only_mode() -> None:
    args = build_parser().parse_args(["--local-only"])

    assert args.local_only


def test_local_only_filters_remote_before_password_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checked = []

    def preflight(targets):
        checked.extend(targets)
        return targets

    monkeypatch.setattr(site89_main, "preflight_deploy_targets", preflight)
    args = build_parser().parse_args(["--local-only"])

    targets = site89_main.prepare_deployment_targets(args)

    assert tuple(target.name for target in targets) == ("local_apache",)
    assert tuple(target.method for target in checked) == ("win_copy",)


def test_build_only_reports_its_own_elapsed_time(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = SimpleNamespace(
        entrypoint=tmp_path / "index.html",
        file_count=380,
    )
    monkeypatch.setattr(site89_main, "build_site", lambda **_kwargs: output)
    times = iter((10.0, 16.8))
    monkeypatch.setattr(site89_main, "time", lambda: next(times))

    site89_main.main(["--build-only"])

    assert "Built in 6.8s" in capsys.readouterr().out


def test_local_only_filters_configured_sftp_target(tmp_path: Path) -> None:
    config_path = tmp_path / "targets.json"
    config_path.write_text(
        json.dumps(
            {
                "default_targets": ["local", "remote"],
                "targets": {
                    "local": {
                        "method": "win_copy",
                        "location": str(tmp_path / "local"),
                    },
                    "remote": {
                        "method": "sftp",
                        "host": "example.test",
                        "user": "tester",
                        "location": "/remote/site",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    plan = load_deployment_plan(config_path)

    assert tuple(target.name for target in select_deploy_targets(plan)) == (
        "local",
        "remote",
    )
    assert tuple(
        target.name for target in select_deploy_targets(plan, local_only=True)
    ) == ("local",)


def test_sftp_preflight_uses_environment_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.products.make_site89 import deploy as site89_deploy

    connected: list[tuple[str, str]] = []

    class Transport:
        def __init__(self, target):
            self.target = target

        def connect(self, *, username: str, password: str) -> None:
            connected.append((username, password))

        def close(self) -> None:
            return None

    monkeypatch.setitem(sys.modules, "paramiko", SimpleNamespace(Transport=Transport))
    monkeypatch.setenv("TEST_SITE89_PASSWORD", "secret")

    checked = preflight_deploy_target(
        DeployTarget(
            name="remote",
            method="sftp",
            location="/remote/site",
            host="example.test",
            user="tester",
            password_env="TEST_SITE89_PASSWORD",
            password_required=True,
        )
    )

    assert checked.password == "secret"
    assert connected == [("tester", "secret")]


def test_sftp_uploads_generated_tree_without_remote_deletion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    uploaded: list[str] = []
    made: list[str] = []

    class Transport:
        def __init__(self, target):
            self.target = target

        def connect(self, *, username: str, password: str) -> None:
            return None

        def close(self) -> None:
            return None

    class SFTPClient:
        @classmethod
        def from_transport(cls, transport):
            return cls()

        def stat(self, remote_dir: str) -> None:
            if remote_dir == "/remote/site/runtime":
                raise FileNotFoundError

        def mkdir(self, remote_dir: str) -> None:
            made.append(remote_dir)

        def put(self, source: str, remote_file: str) -> None:
            uploaded.append(remote_file)

    paramiko = SimpleNamespace(Transport=Transport, SFTPClient=SFTPClient)
    monkeypatch.setitem(sys.modules, "paramiko", paramiko)
    output_root = tmp_path / "output"
    (output_root / "runtime").mkdir(parents=True)
    (output_root / "index.html").write_text("index", encoding="utf-8")
    (output_root / "runtime" / "site.js").write_text("js", encoding="utf-8")

    result = deploy_sftp(
        build_output_from_existing(output_root),
        DeployTarget(
            name="remote",
            method="sftp",
            location="/remote/site",
            host="example.test",
            user="tester",
            password="secret",
        ),
    )

    assert result.file_count == 2
    assert made == ["/remote/site/runtime"]
    assert uploaded == [
        "/remote/site/index.html",
        "/remote/site/runtime/site.js",
    ]
    console = capsys.readouterr().out
    assert "uploading 2/2: runtime/site.js" in console
    assert "created" not in console
