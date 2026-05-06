"""Local and remote deployment for the generated static site."""

from __future__ import annotations

import getpass
import os
import posixpath
import shutil
from pathlib import Path

from .filesystem import copy_file


HOST = "www.661.org.uk"
USER = "root"
LOCAL_ROOT = Path("A:/local/html/sumo-tools")
REMOTE_ROOT = "/var/www/html/sumo-tools"


def deploy_local(output_root: Path, local_root: Path) -> None:
    clear_local_root(local_root)
    for source in output_root.rglob("*"):
        if source.is_file():
            target = local_root / source.relative_to(output_root)
            copy_file(source, target)


def clear_local_root(local_root: Path) -> None:
    local_root.mkdir(parents=True, exist_ok=True)
    for item in local_root.iterdir():
        if item.name.endswith(".swp"):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


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
    password = os.environ.get("MY_SFTP_PASS")
    if password:
        print("using MY_SFTP_PASS for remote deployment")
        return password
    return getpass.getpass("SFTP password: ")


def deploy_remote(local_root: Path, remote_root: str) -> int:
    import paramiko

    password = get_password()
    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=password)
    count = 0
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        ensure_remote_tree(sftp, remote_root)
        for source in local_root.rglob("*"):
            if source.is_file():
                relative = source.relative_to(local_root)
                remote_file = posixpath.join(remote_root, *relative.parts)
                ensure_remote_tree(sftp, posixpath.dirname(remote_file))
                sftp.put(str(source), remote_file)
                count += 1
        return count
    finally:
        transport.close()
