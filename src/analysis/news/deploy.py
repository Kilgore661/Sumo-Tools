"""
Static asset deployment contract for the Banzuke Change Report.
"""

import os
from pathlib import Path
import posixpath
import shutil
import stat
import sys

import paramiko

from src.analysis.news.classes import PublicationRequest


HOST = "www.661.org.uk"
USER = "root"

LOCAL_ROOT = Path(r"A:/local/html/bcr")
LOCAL_DATA = LOCAL_ROOT / "data"
LOCAL_COMMON_STATIC = Path(__file__).resolve().parents[1] / "common" / "files"

REMOTE_ROOT = "/var/www/html/bcr"
REMOTE_DATA = posixpath.join(REMOTE_ROOT, "data")
REMOTE_COMMON = "/var/www/html/common/files"

STATIC_FILE_NAMES = (
    "index.html",
    "banzuke_change_report.css",
    "banzuke_change_report.js.txt",
)

REMOTE_ROOT_FILE_NAMES = (
    *STATIC_FILE_NAMES,
    "site_config.json",
)

COMMON_STATIC_FILE_NAMES = (
    "site-wide.css",
    "tool-layout.css",
)


def copy_static_assets(request: PublicationRequest) -> None:
    """
    Contract:
        request.static_dir contains the BCR HTML/CSS/JS assets and
        request.common_static_dir contains the shared lab CSS used by the BCR
        HTML.

        Copies the static browser app assets into the output tree.
    """

    request.output_root.mkdir(parents=True, exist_ok=True)
    request.common_output_dir.mkdir(parents=True, exist_ok=True)

    for name in STATIC_FILE_NAMES:
        shutil.copy2(request.static_dir / name, request.output_root / name)

    for name in COMMON_STATIC_FILE_NAMES:
        shutil.copy2(
            request.common_static_dir / name,
            request.common_output_dir / name,
        )


def ensure_remote_dir(sftp, remote_dir: str) -> None:
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f"Created: {remote_dir}")


def upload_file(sftp, local_file: Path, remote_file: str) -> None:
    sftp.put(str(local_file), remote_file)


def clear_remote_files(sftp, remote_dir: str) -> None:
    """
    Delete files only (not subdirectories) in remote_dir.
    """

    for item in sftp.listdir_attr(remote_dir):
        remote_path = posixpath.join(remote_dir, item.filename)

        if stat.S_ISREG(item.st_mode):
            sftp.remove(remote_path)


def deploy_static_files(sftp) -> None:
    """
    Contract:
        LOCAL_ROOT contains the published BCR root files.
        LOCAL_COMMON_STATIC contains shared lab CSS.

        Uploads BCR root files and shared CSS.
    """

    for name in REMOTE_ROOT_FILE_NAMES:
        local_file = LOCAL_ROOT / name
        remote_file = posixpath.join(REMOTE_ROOT, name)
        upload_file(sftp, local_file, remote_file)

    for name in COMMON_STATIC_FILE_NAMES:
        local_file = LOCAL_COMMON_STATIC / name
        remote_file = posixpath.join(REMOTE_COMMON, name)
        upload_file(sftp, local_file, remote_file)


def deploy_data_files(sftp) -> None:
    """
    Contract:
        LOCAL_DATA contains the BCR browser data files.

        Replaces remote data files with the current local publication data.
    """

    clear_remote_files(sftp, REMOTE_DATA)

    for local_file in LOCAL_DATA.iterdir():
        if local_file.is_file() and local_file.suffix.lower() in {".csv", ".json"}:
            remote_file = posixpath.join(REMOTE_DATA, local_file.name)
            upload_file(sftp, local_file, remote_file)


def main() -> None:
    """
    Contract:
        LOCAL_ROOT is the current local BCR publication tree produced by
        publisher.py.  MY_SFTP_PASS contains the deployment password.

        Uploads the static BCR app to the remote web root.
    """

    password = os.environ.get("MY_SFTP_PASS")

    if not password:
        print("Error: MY_SFTP_PASS environment variable is not set.")
        print('Try:\n$env:MY_SFTP_PASS = "whatever"')
        sys.exit(1)

    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=password)

    try:
        sftp = paramiko.SFTPClient.from_transport(transport)

        ensure_remote_dir(sftp, REMOTE_ROOT)
        ensure_remote_dir(sftp, REMOTE_DATA)
        ensure_remote_dir(sftp, posixpath.dirname(REMOTE_COMMON))
        ensure_remote_dir(sftp, REMOTE_COMMON)

        deploy_static_files(sftp)
        deploy_data_files(sftp)

        print("BCR remote deployment complete.")

    finally:
        transport.close()


if __name__ == "__main__":
    main()
