"""Local-server and remote deployment for make_site2 output."""

from __future__ import annotations

import getpass
import os
import posixpath
import shutil
from dataclasses import dataclass, replace
from pathlib import Path

from .models import BuildOutput


HOST = "www.661.org.uk"
USER = "root"
LOCAL_ROOT = Path("A:/local/html/sumo-tools2")
LOCAL_URL = "http://192.168.0.6/sumo-tools2/"
REMOTE_ROOT = "/var/www/html/sumo-tools2"
REMOTE_URL = "http://68.66.241.105/sumo-tools2/"


@dataclass(frozen=True, kw_only=True)
class DeploymentConfig:
    local_root: Path = LOCAL_ROOT
    local_url: str = LOCAL_URL
    remote_root: str = REMOTE_ROOT
    remote_url: str = REMOTE_URL
    remote_host: str = HOST
    remote_user: str = USER
    remote_password: str | None = None


@dataclass(frozen=True, kw_only=True)
class DeploymentResult:
    mode: str
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


def deploy_local(
    build_output: BuildOutput,
    deployment_config: DeploymentConfig,
) -> DeploymentResult:
    local_root = deployment_config.local_root
    clear_local_root(local_root)
    for source in build_output.root.rglob("*"):
        if source.is_file():
            target = local_root / source.relative_to(build_output.root)
            copy_file(source, target)
    return DeploymentResult(
        mode="local",
        source_root=build_output.root,
        target_root=local_root,
        public_url=deployment_config.local_url,
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


def get_password() -> str:
    password = os.environ.get("GEOLOCATION")
    if password:
        print("using GEOLOCATION for remote deployment")
        return password
    return getpass.getpass("SFTP password: ")


def resolve_remote_password(deployment_config: DeploymentConfig) -> str:
    if deployment_config.remote_password is not None:
        return deployment_config.remote_password
    return get_password()


def connect_remote_transport(deployment_config: DeploymentConfig):
    import paramiko

    password = resolve_remote_password(deployment_config)
    transport = paramiko.Transport((deployment_config.remote_host, 22))
    try:
        transport.connect(
            username=deployment_config.remote_user,
            password=password,
        )
    except paramiko.ssh_exception.AuthenticationException:
        print("Warning! Warning! Dr. Smith! Intruder alert!")
        raise SystemExit(0)
    return transport


def preflight_remote_auth(deployment_config: DeploymentConfig) -> DeploymentConfig:
    password = resolve_remote_password(deployment_config)
    config_with_password = replace(deployment_config, remote_password=password)
    transport = connect_remote_transport(config_with_password)
    transport.close()
    return config_with_password


def deploy_remote(
    build_output: BuildOutput,
    deployment_config: DeploymentConfig,
) -> DeploymentResult:
    import paramiko

    transport = connect_remote_transport(deployment_config)
    count = 0
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        ensure_remote_tree(sftp, deployment_config.remote_root)
        sources = tuple(path for path in build_output.root.rglob("*") if path.is_file())
        total = len(sources)
        for source in sources:
            relative = source.relative_to(build_output.root)
            remote_file = posixpath.join(
                deployment_config.remote_root,
                *relative.parts,
            )
            print(f"uploading {count + 1}/{total}: {relative.as_posix()}")
            ensure_remote_tree(sftp, posixpath.dirname(remote_file))
            sftp.put(str(source), remote_file)
            count += 1
        return DeploymentResult(
            mode="remote",
            source_root=build_output.root,
            target_root=deployment_config.remote_root,
            public_url=deployment_config.remote_url,
            file_count=count,
        )
    finally:
        transport.close()
