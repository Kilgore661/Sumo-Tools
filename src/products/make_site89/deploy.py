"""Local filesystem and remote SFTP deployment for site89 output."""

from __future__ import annotations

import getpass
import json
import os
import posixpath
import shutil
from dataclasses import dataclass, replace
from pathlib import Path

from .models import BuildOutput


DEFAULT_DEPLOY_TARGETS_PATH = Path("distro/make_site89_targets.json")
VALID_DEPLOY_METHODS = frozenset(("win_copy", "sftp"))


@dataclass(frozen=True, kw_only=True)
class DeployTarget:
    name: str
    method: str
    location: str
    url: str = ""
    host: str | None = None
    user: str | None = None
    password_env: str | None = None
    password_required: bool = False
    password: str | None = None


@dataclass(frozen=True, kw_only=True)
class DeploymentPlan:
    default_targets: tuple[str, ...]
    targets: dict[str, DeployTarget]


@dataclass(frozen=True, kw_only=True)
class DeploymentResult:
    target_name: str
    method: str
    source_root: Path
    target_root: Path | str
    public_url: str
    file_count: int


def build_output_from_existing(output_root: Path) -> BuildOutput:
    entrypoint = output_root / "index.html"
    if not entrypoint.is_file():
        raise FileNotFoundError(f"Build output entrypoint not found: {entrypoint}")
    return BuildOutput(
        root=output_root,
        entrypoint=entrypoint,
        file_count=sum(1 for path in output_root.rglob("*") if path.is_file()),
    )


def load_deployment_plan(
    path: Path = DEFAULT_DEPLOY_TARGETS_PATH,
) -> DeploymentPlan:
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw_targets = raw.get("targets")
    if not isinstance(raw_targets, dict):
        raise ValueError(f"{path} must contain a 'targets' object")
    targets: dict[str, DeployTarget] = {}
    for name, config in raw_targets.items():
        if not isinstance(config, dict):
            raise ValueError(f"{path} target {name!r} must be an object")
        method = config.get("method") or config.get("transfer")
        if method not in VALID_DEPLOY_METHODS:
            raise ValueError(
                f"{path} target {name!r} method must be one of "
                f"{', '.join(sorted(VALID_DEPLOY_METHODS))}"
            )
        location = config.get("location") or config.get("root") or config.get("path")
        if not location:
            raise ValueError(f"{path} target {name!r} needs a location")
        host = config.get("host") or config.get("ip")
        user = config.get("user")
        if method == "sftp":
            missing = [
                field
                for field, value in (("host", host), ("user", user))
                if not value
            ]
            if missing:
                raise ValueError(
                    f"{path} target {name!r} needs {', '.join(missing)} for sftp"
                )
        targets[name] = DeployTarget(
            name=name,
            method=method,
            location=str(location),
            url=str(config.get("url") or ""),
            host=str(host) if host else None,
            user=str(user) if user else None,
            password_env=config.get("password_env"),
            password_required=bool(
                config.get("password_required", method == "sftp")
            ),
        )
    default_targets = tuple(raw.get("default_targets") or targets.keys())
    unknown = [name for name in default_targets if name not in targets]
    if unknown:
        raise ValueError(f"unknown default deploy target(s): {', '.join(unknown)}")
    return DeploymentPlan(default_targets=default_targets, targets=targets)


def select_deploy_targets(
    plan: DeploymentPlan,
    *,
    local_only: bool = False,
) -> tuple[DeployTarget, ...]:
    targets = tuple(plan.targets[name] for name in plan.default_targets)
    if local_only:
        targets = tuple(target for target in targets if target.method == "win_copy")
    if not targets:
        raise ValueError("no deploy targets selected")
    return targets


def deploy_targets(
    build_output: BuildOutput,
    targets: tuple[DeployTarget, ...],
) -> tuple[DeploymentResult, ...]:
    return tuple(deploy_target(build_output, target) for target in targets)


def preflight_deploy_targets(
    targets: tuple[DeployTarget, ...],
) -> tuple[DeployTarget, ...]:
    """Resolve credentials and verify every remote connection before deploy."""

    return tuple(preflight_deploy_target(target) for target in targets)


def preflight_deploy_target(target: DeployTarget) -> DeployTarget:
    if target.method != "sftp":
        return target
    checked = resolve_sftp_password(target)
    transport = connect_sftp_transport(checked)
    transport.close()
    return checked


def deploy_target(
    build_output: BuildOutput,
    target: DeployTarget,
) -> DeploymentResult:
    if target.method == "win_copy":
        return deploy_win_copy(build_output, target)
    if target.method == "sftp":
        return deploy_sftp(build_output, target)
    raise ValueError(f"unsupported deploy method: {target.method}")


def deploy_win_copy(
    build_output: BuildOutput,
    deploy_target: DeployTarget,
) -> DeploymentResult:
    local_root = Path(deploy_target.location)
    _clear_local_root(local_root)
    for source in build_output.root.rglob("*"):
        if source.is_file():
            target = local_root / source.relative_to(build_output.root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    return DeploymentResult(
        target_name=deploy_target.name,
        method=deploy_target.method,
        source_root=build_output.root,
        target_root=local_root,
        public_url=deploy_target.url,
        file_count=build_output.file_count,
    )


def _clear_local_root(local_root: Path) -> None:
    local_root.mkdir(parents=True, exist_ok=True)
    for item in local_root.iterdir():
        if item.name.endswith(".swp"):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def resolve_sftp_password(target: DeployTarget) -> DeployTarget:
    """Return an SFTP target carrying its resolved password."""

    if target.password is not None:
        return target
    password = None
    if target.password_env:
        password = os.environ.get(target.password_env)
        if password:
            print(f"using {target.password_env} for {target.name} deployment")
    if password is None and target.password_required:
        password = getpass.getpass(
            f"SFTP password for {target.user}@{target.host}: "
        )
    return replace(target, password=password)


def connect_sftp_transport(target: DeployTarget):
    """Open an authenticated Paramiko transport for one target."""

    import paramiko

    transport = paramiko.Transport((target.host, 22))
    transport.connect(username=target.user, password=target.password)
    return transport


def _ensure_remote_dir(sftp, remote_dir: str) -> None:
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f"created {remote_dir}")


def _ensure_remote_tree(sftp, remote_dir: str) -> None:
    current = ""
    for part in (part for part in remote_dir.split("/") if part):
        current = f"{current}/{part}"
        _ensure_remote_dir(sftp, current)


def deploy_sftp(
    build_output: BuildOutput,
    target: DeployTarget,
) -> DeploymentResult:
    """Upload every generated file, without deleting unrelated remote files."""

    import paramiko

    target = resolve_sftp_password(target)
    transport = connect_sftp_transport(target)
    uploaded = 0
    progress_width = 0
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        _ensure_remote_tree(sftp, target.location)
        sources = tuple(
            path for path in build_output.root.rglob("*") if path.is_file()
        )
        uploads = tuple(
            (
                source,
                source.relative_to(build_output.root),
                posixpath.join(
                    target.location,
                    *source.relative_to(build_output.root).parts,
                ),
            )
            for source in sources
        )
        remote_dirs = dict.fromkeys(
            posixpath.dirname(remote_file) for _, _, remote_file in uploads
        )
        for remote_dir in remote_dirs:
            _ensure_remote_tree(sftp, remote_dir)
        total = len(uploads)
        for source, relative, remote_file in uploads:
            message = f"uploading {uploaded + 1}/{total}: {relative.as_posix()}"
            progress_width = max(progress_width, len(message))
            print(f"\r{message.ljust(progress_width)}", end="", flush=True)
            sftp.put(str(source), remote_file)
            uploaded += 1
        return DeploymentResult(
            target_name=target.name,
            method=target.method,
            source_root=build_output.root,
            target_root=target.location,
            public_url=target.url,
            file_count=uploaded,
        )
    finally:
        if progress_width:
            print()
        transport.close()
