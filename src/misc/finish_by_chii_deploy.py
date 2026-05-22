import os
from pathlib import Path
import posixpath
import sys

import paramiko


HOST = "www.661.org.uk"
USER = "root"

LOCAL_ROOT = Path(r"A:/local/html/finish_by_chii")
LOCAL_HTML = LOCAL_ROOT / "index.html"
LOCAL_AVERAGE_HTML = LOCAL_ROOT / "average.html"

REMOTE_ROOT = "/var/www/html/finish_by_chii"
REMOTE_HTML = posixpath.join(REMOTE_ROOT, "index.html")
REMOTE_AVERAGE_HTML = posixpath.join(REMOTE_ROOT, "average.html")


def ensure_remote_dir(sftp, remote_dir: str) -> None:
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f"Created: {remote_dir}")


def upload_file(sftp, local_file: Path, remote_file: str) -> None:
    sftp.put(str(local_file), remote_file)


def main() -> None:
    password = os.environ.get("GEOLOCATION")

    if not password:
        print("Error: GEOLOCATION environment variable is not set.")
        print('Try:\n$env:GEOLOCATION = "whatever"')
        sys.exit(1)

    local_remote_files = (
        (LOCAL_HTML, REMOTE_HTML),
        (LOCAL_AVERAGE_HTML, REMOTE_AVERAGE_HTML),
    )
    for local_file, _ in local_remote_files:
        if not local_file.exists():
            raise RuntimeError(f"Local HTML not found: {local_file}")

    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=password)

    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        ensure_remote_dir(sftp, REMOTE_ROOT)
        for local_file, remote_file in local_remote_files:
            upload_file(sftp, local_file, remote_file)
        print("Finish by Chii remote deployment complete.")

    finally:
        transport.close()


if __name__ == "__main__":
    main()
