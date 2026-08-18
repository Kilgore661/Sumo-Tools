from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from src.products.make_site2.deploy import (
    DeployTarget,
    build_output_from_existing,
    deploy_sftp,
    deploy_win_copy,
    preflight_deploy_target,
)


def test_build_output_from_existing_requires_index(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_output_from_existing(tmp_path)


def test_deploy_local_clean_copies_existing_output(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    local_root = tmp_path / "server" / "sumo-tools2"
    (output_root / "runtime").mkdir(parents=True)
    (output_root / "index.html").write_text("index", encoding="utf-8")
    (output_root / "runtime" / "site.js").write_text("runtime", encoding="utf-8")
    local_root.mkdir(parents=True)
    (local_root / "stale.txt").write_text("stale", encoding="utf-8")
    (local_root / "keep.swp").write_text("keep", encoding="utf-8")

    build_output = build_output_from_existing(output_root)
    result = deploy_win_copy(
        build_output,
        DeployTarget(
            name="local",
            method="win_copy",
            location=str(local_root),
            url="http://server/sumo-tools2/",
        ),
    )

    assert result.file_count == 2
    assert result.public_url == "http://server/sumo-tools2/"
    assert (local_root / "index.html").read_text(encoding="utf-8") == "index"
    assert (local_root / "runtime" / "site.js").read_text(encoding="utf-8") == "runtime"
    assert not (local_root / "stale.txt").exists()
    assert (local_root / "keep.swp").read_text(encoding="utf-8") == "keep"


def test_remote_deploy_wrong_password_warns_and_exits_normally(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from src.products.make_site2 import deploy as make_site2_deploy

    class AuthenticationException(Exception):
        pass

    class Transport:
        def __init__(self, target):
            self.target = target

        def connect(self, *, username: str, password: str) -> None:
            raise AuthenticationException

    paramiko = SimpleNamespace(
        Transport=Transport,
        ssh_exception=SimpleNamespace(AuthenticationException=AuthenticationException),
    )
    output_root = tmp_path / "output"
    output_root.mkdir()
    (output_root / "index.html").write_text("index", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "paramiko", paramiko)
    monkeypatch.setattr(make_site2_deploy.getpass, "getpass", lambda prompt: "wrong")
    build_output = build_output_from_existing(output_root)

    with pytest.raises(SystemExit) as exc_info:
        deploy_sftp(
            build_output,
            DeployTarget(
                name="remote",
                method="sftp",
                location="/remote/sumo-tools2",
                host="example.test",
                user="tester",
                password_required=True,
            ),
        )

    assert exc_info.value.code == 0
    assert "Warning! Warning! Dr. Smith! Intruder alert!" in capsys.readouterr().out


def test_remote_preflight_auth_reuses_resolved_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.products.make_site2 import deploy as make_site2_deploy

    connected_passwords: list[str] = []

    class Transport:
        def __init__(self, target):
            self.target = target

        def connect(self, *, username: str, password: str) -> None:
            connected_passwords.append(password)

        def close(self) -> None:
            return None

    paramiko = SimpleNamespace(
        Transport=Transport,
        ssh_exception=SimpleNamespace(AuthenticationException=Exception),
    )
    monkeypatch.setitem(sys.modules, "paramiko", paramiko)
    monkeypatch.setattr(make_site2_deploy.getpass, "getpass", lambda prompt: "checked")

    checked_config = preflight_deploy_target(
        DeployTarget(
            name="remote",
            method="sftp",
            location="/remote/sumo-tools2",
            host="example.test",
            user="tester",
            password_required=True,
        )
    )

    assert checked_config.password == "checked"
    assert connected_passwords == ["checked"]


def test_remote_deploy_reports_upload_progress(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    uploaded: list[str] = []

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
            return None

        def put(self, source: str, remote_file: str) -> None:
            uploaded.append(remote_file)

    paramiko = SimpleNamespace(
        Transport=Transport,
        SFTPClient=SFTPClient,
        ssh_exception=SimpleNamespace(AuthenticationException=Exception),
    )
    output_root = tmp_path / "output"
    (output_root / "runtime").mkdir(parents=True)
    (output_root / "index.html").write_text("index", encoding="utf-8")
    (output_root / "runtime" / "site.js").write_text("runtime", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "paramiko", paramiko)
    build_output = build_output_from_existing(output_root)

    result = deploy_sftp(
        build_output,
        DeployTarget(
            name="remote",
            method="sftp",
            location="/remote/sumo-tools2",
            host="example.test",
            user="tester",
            password="right",
        ),
    )

    output = capsys.readouterr().out
    assert "uploading 1/2:" in output
    assert "uploading 2/2:" in output
    assert result.file_count == 2
    assert uploaded == [
        "/remote/sumo-tools2/index.html",
        "/remote/sumo-tools2/runtime/site.js",
    ]
