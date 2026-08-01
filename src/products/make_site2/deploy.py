"""Local-server and remote deployment for make_site2 output."""

from __future__ import annotations

import getpass
import json
import os
import posixpath
import shutil
from dataclasses import dataclass, replace
from pathlib import Path

from .models import BuildOutput


DEFAULT_DEPLOY_TARGETS_PATH = Path("distro/make_site2_targets.json")
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
    """Describe an existing generated output tree for no-build deployment."""

    entrypoint = output_root / "index.html"
    if not entrypoint.is_file():
        raise FileNotFoundError(f"Build output entrypoint not found: {entrypoint}")
    return BuildOutput(
        root=output_root,
        entrypoint=entrypoint,
        file_count=count_files(output_root),
    )


def count_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file())


def load_deployment_plan(path: Path = DEFAULT_DEPLOY_TARGETS_PATH) -> DeploymentPlan:
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    raw_targets = raw.get("targets")
    if not isinstance(raw_targets, dict):
        raise ValueError(f"{path} must contain a 'targets' object")
    targets = {
        name: make_deploy_target(name, target_config, path)
        for name, target_config in raw_targets.items()
    }
    default_targets = tuple(raw.get("default_targets") or targets.keys())
    for name in default_targets:
        if name not in targets:
            raise ValueError(f"{path} default target {name!r} is not defined")
    return DeploymentPlan(default_targets=default_targets, targets=targets)


def make_deploy_target(
    name: str,
    target_config: object,
    path: Path,
) -> DeployTarget:
    if not isinstance(target_config, dict):
        raise ValueError(f"{path} target {name!r} must be an object")
    method = target_config.get("method") or target_config.get("transfer")
    if method not in VALID_DEPLOY_METHODS:
        raise ValueError(
            f"{path} target {name!r} method must be one of "
            f"{', '.join(sorted(VALID_DEPLOY_METHODS))}"
        )
    location = (
        target_config.get("location")
        or target_config.get("root")
        or target_config.get("path")
    )
    if not location:
        raise ValueError(f"{path} target {name!r} needs a location")
    host = target_config.get("host") or target_config.get("ip")
    user = target_config.get("user")
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
    return DeployTarget(
        name=name,
        method=method,
        location=str(location),
        url=str(target_config.get("url") or target_config.get("public_url") or ""),
        host=str(host) if host else None,
        user=str(user) if user else None,
        password_env=target_config.get("password_env"),
        password_required=bool(
            target_config.get("password_required", method == "sftp")
        ),
    )


def select_deploy_targets(
    plan: DeploymentPlan,
    requested_names: tuple[str, ...] = (),
    *,
    local_only: bool = False,
) -> tuple[DeployTarget, ...]:
    names = requested_names or plan.default_targets
    unknown = [name for name in names if name not in plan.targets]
    if unknown:
        raise ValueError(f"unknown deploy target(s): {', '.join(unknown)}")
    targets = tuple(plan.targets[name] for name in names)
    if local_only:
        targets = tuple(target for target in targets if target.method == "win_copy")
    if not targets:
        raise ValueError("no deploy targets selected")
    return targets


def preflight_deploy_targets(
    deploy_targets: tuple[DeployTarget, ...],
) -> tuple[DeployTarget, ...]:
    return tuple(preflight_deploy_target(target) for target in deploy_targets)


def preflight_deploy_target(deploy_target: DeployTarget) -> DeployTarget:
    if deploy_target.method != "sftp":
        return deploy_target
    target_with_password = resolve_sftp_password(deploy_target)
    transport = connect_sftp_transport(target_with_password)
    transport.close()
    return target_with_password


def deploy_target(
    build_output: BuildOutput,
    deploy_target: DeployTarget,
) -> DeploymentResult:
    if deploy_target.method == "win_copy":
        return deploy_win_copy(build_output, deploy_target)
    if deploy_target.method == "sftp":
        return deploy_sftp(build_output, deploy_target)
    raise ValueError(f"unsupported deploy method: {deploy_target.method}")


def deploy_win_copy(
    build_output: BuildOutput,
    deploy_target: DeployTarget,
) -> DeploymentResult:
    local_root = Path(deploy_target.location)
    clear_local_root(local_root)
    for source in build_output.root.rglob("*"):
        if source.is_file():
            target = local_root / source.relative_to(build_output.root)
            copy_file(source, target)
    return DeploymentResult(
        target_name=deploy_target.name,
        method=deploy_target.method,
        source_root=build_output.root,
        target_root=local_root,
        public_url=deploy_target.url,
        file_count=build_output.file_count,
    )


def clear_local_root(local_root: Path) -> None:
    local_root.mkdir(parents=True, exist_ok=True)
    for item in local_root.iterdir():
        if item.name.endswith(".swp"):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def ensure_remote_dir(sftp, remote_dir: str) -> None:
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f"created {remote_dir}")


def ensure_remote_tree(sftp, remote_dir: str) -> None:
    parts = [part for part in remote_dir.split("/") if part]
    current = ""
    for part in parts:
        current = f"{current}/{part}"
        ensure_remote_dir(sftp, current)


def resolve_sftp_password(deploy_target: DeployTarget) -> DeployTarget:
    if deploy_target.password is not None:
        return deploy_target
    password = None
    if deploy_target.password_env:
        password = os.environ.get(deploy_target.password_env)
        if password:
            print(
                f"using {deploy_target.password_env} for "
                f"{deploy_target.name} deployment"
            )
    if password is None and deploy_target.password_required:
        prompt = f"SFTP password for {deploy_target.user}@{deploy_target.host}: "
        password = getpass.getpass(prompt)
    return replace(deploy_target, password=password)


def connect_sftp_transport(deploy_target: DeployTarget):
    import paramiko

    transport = paramiko.Transport((deploy_target.host, 22))
    try:
        transport.connect(
            username=deploy_target.user,
            password=deploy_target.password,
        )
    except paramiko.ssh_exception.AuthenticationException:
        print("Warning! Warning! Dr. Smith! Intruder alert!")
        raise SystemExit(0)
    return transport


def deploy_sftp(
    build_output: BuildOutput,
    deploy_target: DeployTarget,
) -> DeploymentResult:
    import paramiko

    deploy_target = resolve_sftp_password(deploy_target)
    transport = connect_sftp_transport(deploy_target)
    count = 0
    progress_width = 0
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        ensure_remote_tree(sftp, deploy_target.location)
        sources = tuple(path for path in build_output.root.rglob("*") if path.is_file())
        total = len(sources)
        uploads = tuple(
            (
                source,
                source.relative_to(build_output.root),
                posixpath.join(
                    deploy_target.location,
                    *source.relative_to(build_output.root).parts,
                ),
            )
            for source in sources
        )
        remote_dirs = dict.fromkeys(
            posixpath.dirname(remote_file)
            for _, _, remote_file in uploads
        )
        for remote_dir in remote_dirs:
            ensure_remote_tree(sftp, remote_dir)
        for source, relative, remote_file in uploads:
            message = f"uploading {count + 1}/{total}: {relative.as_posix()}"
            progress_width = max(progress_width, len(message))
            print(f"\r{message.ljust(progress_width)}", end="", flush=True)
            sftp.put(str(source), remote_file)
            count += 1
        return DeploymentResult(
            target_name=deploy_target.name,
            method=deploy_target.method,
            source_root=build_output.root,
            target_root=deploy_target.location,
            public_url=deploy_target.url,
            file_count=count,
        )
    finally:
        if progress_width:
            print()
        transport.close()
