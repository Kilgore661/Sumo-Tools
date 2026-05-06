"""
Deploy the sandbox Sumo Lab site.

The workflow mirrors the existing analysis deploy scripts:

1. Build the static site into files/output/site.
2. Copy that persisted output tree to A:/local/html/site.
3. Upload that local tree to the remote web root.
"""

from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import posixpath
import shutil

from .sandbox_builder import DEFAULT_OUTPUT_ROOT, build_site


HOST = "www.661.org.uk"
USER = "root"

LOCAL_ROOT = Path("A:/local/html/site")
REMOTE_ROOT = "/var/www/html/site"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, locally deploy, and remotely deploy the sandbox site."
    )
    parser.add_argument(
        "--build-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Persisted site output directory to build and deploy from.",
    )
    parser.add_argument(
        "--local-root",
        type=Path,
        default=LOCAL_ROOT,
        help="Local web directory to receive the deployable site.",
    )
    parser.add_argument(
        "--remote-root",
        default=REMOTE_ROOT,
        help="Remote web root to receive the deployable site.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Build and copy to A:, but do not upload remotely.",
    )
    parser.add_argument(
        "--remote-only",
        action="store_true",
        help="Upload the existing local deployment tree without rebuilding or copying.",
    )
    return parser


def clear_local_dir(path: Path) -> None:
    if path.drive and not Path(path.drive + "\\").exists():
        raise FileNotFoundError(
            f"Local deployment drive is not available: {path.drive}\\"
        )

    path.mkdir(parents=True, exist_ok=True)

    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def copy_tree(source_root: Path, target_root: Path) -> None:
    if not source_root.is_dir():
        raise FileNotFoundError(f"Build output does not exist: {source_root}")

    clear_local_dir(target_root)

    for source in source_root.rglob("*"):
        if not source.is_file():
            continue

        target = target_root / source.relative_to(source_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def ensure_remote_dir(sftp, remote_dir: str) -> None:
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f"Created: {remote_dir}")


def ensure_remote_tree(sftp, remote_dir: str) -> None:
    parts = [part for part in remote_dir.split("/") if part]
    current = ""

    for part in parts:
        current = f"{current}/{part}"
        ensure_remote_dir(sftp, current)


def upload_file(sftp, local_file: Path, remote_file: str) -> None:
    sftp.put(str(local_file), remote_file)


def upload_tree(sftp, local_root: Path, remote_root: str) -> int:
    ensure_remote_tree(sftp, remote_root)
    count = 0

    for local_file in local_root.rglob("*"):
        if not local_file.is_file():
            continue

        relative = local_file.relative_to(local_root)
        remote_file = posixpath.join(remote_root, *relative.parts)
        ensure_remote_tree(sftp, posixpath.dirname(remote_file))
        upload_file(sftp, local_file, remote_file)
        count += 1

    return count


def get_password() -> str:
    password = os.environ.get("MY_SFTP_PASS")
    if password:
        print("Using MY_SFTP_PASS for remote deployment.")
        return password

    print("MY_SFTP_PASS is not set; prompting for remote deployment password.")
    password = getpass.getpass("SFTP password: ")

    if not password:
        raise ValueError("No SFTP password supplied.")

    return password


def deploy_remote(local_root: Path, remote_root: str) -> int:
    import paramiko

    if not local_root.is_dir():
        raise FileNotFoundError(f"Local deployment tree does not exist: {local_root}")

    password = get_password()
    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=password)

    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        count = upload_tree(sftp, local_root, remote_root)
        sftp.stat(posixpath.join(remote_root, "index.html"))
        return count
    finally:
        transport.close()


def main() -> None:
    args = _build_parser().parse_args()
    if args.local_only and args.remote_only:
        raise ValueError("--local-only and --remote-only cannot be used together.")

    build_root = args.build_root.resolve()
    local_root = args.local_root.resolve()

    if not args.remote_only:
        build_site(build_root)
        copy_tree(build_root, local_root)

        print(f"Sandbox site built: {build_root}")
        print(f"Sandbox site locally deployed: {local_root}")

    if args.local_only:
        return

    remote_count = deploy_remote(local_root, args.remote_root)
    print(
        f"Sandbox site remotely deployed: {remote_count} files "
        f"to {HOST}:{args.remote_root}"
    )
    print(f"https://www.661.org.uk{args.remote_root.removeprefix('/var/www/html')}/")


if __name__ == "__main__":
    main()
