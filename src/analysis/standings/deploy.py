# deploy.py
import os, sys
from pathlib import Path
import posixpath
import stat
import paramiko

HOST = "www.661.org.uk"
USER = "root"

REMOTE_ROOT = "/var/www/html/standings"
REMOTE_DATA = posixpath.join(REMOTE_ROOT, "data")
REMOTE_COMMON = "/var/www/html/common/files"
from .config import PUBLISHER_LATEST_DATA as LOCAL_DATA

# Local project paths
BASE_DIR = Path(__file__).resolve().parent
LOCAL_STATIC = BASE_DIR / "files"
LOCAL_COMMON_STATIC = BASE_DIR.parent / "common" / "files"


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
    for name in ["index.html", "standings.css", "standings.js.txt"]:
        local_file = LOCAL_STATIC / name
        remote_file = posixpath.join(REMOTE_ROOT, name)
        upload_file(sftp, local_file, remote_file)

    for name in ["site-wide.css", "tool-layout.css"]:
        local_file = LOCAL_COMMON_STATIC / name
        remote_file = posixpath.join(REMOTE_COMMON, name)
        upload_file(sftp, local_file, remote_file)


def deploy_data_files(sftp) -> None:
    clear_remote_files(sftp, REMOTE_DATA)

    for local_file in LOCAL_DATA.iterdir():
        if local_file.is_file() and local_file.suffix.lower() in {".csv", ".json"}:
            remote_file = posixpath.join(REMOTE_DATA, local_file.name)
            upload_file(sftp, local_file, remote_file)


def main():
    password = os.environ.get('MY_SFTP_PASS')
    if not password:
        print("❌ Error: MY_SFTP_PASS environment variable is not set.")
        print('Try:\n$env:MY_SFTP_PASS = "whatever"' )
        sys.exit(1)

    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=password)

    try:
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Ensure remote structure exists
        ensure_remote_dir(sftp, REMOTE_ROOT)
        ensure_remote_dir(sftp, REMOTE_DATA)
        ensure_remote_dir(sftp, posixpath.dirname(REMOTE_COMMON))
        ensure_remote_dir(sftp, REMOTE_COMMON)

        # Copy static site files
        deploy_static_files(sftp)

        # Copy data files
        deploy_data_files(sftp)

        print("Remote deployment complete.")

    finally:
        transport.close()


if __name__ == "__main__":
    main()
