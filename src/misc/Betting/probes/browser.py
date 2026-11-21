"""Launch an ordinary installed Chromium browser and attach through CDP."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


DEBUG_PORT_TIMEOUT_SECONDS = 10.0


def find_browser(channel: str) -> Path:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    program_files = Path(os.environ.get("PROGRAMFILES", ""))
    program_files_x86 = Path(os.environ.get("PROGRAMFILES(X86)", ""))
    if channel == "chrome":
        relative = Path("Google") / "Chrome" / "Application" / "chrome.exe"
        names = ("chrome", "google-chrome")
    else:
        relative = Path("Microsoft") / "Edge" / "Application" / "msedge.exe"
        names = ("msedge",)
    for candidate in (
        local_app_data / relative,
        program_files / relative,
        program_files_x86 / relative,
    ):
        if candidate.is_file():
            return candidate
    for name in names:
        discovered = shutil.which(name)
        if discovered:
            return Path(discovered)
    raise RuntimeError(f"Could not find an installed {channel} browser")


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _wait_for_debug_port(process: subprocess.Popen[bytes], port: int) -> None:
    url = f"http://127.0.0.1:{port}/json/version"
    deadline = time.monotonic() + DEBUG_PORT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("The browser exited before its debugging port opened")
        try:
            with urlopen(url, timeout=1):
                return
        except (URLError, OSError):
            time.sleep(0.2)
    raise RuntimeError(
        "The browser did not open its debugging port within "
        f"{DEBUG_PORT_TIMEOUT_SECONDS:g} seconds"
    )


def start_browser(
    browser_path: Path, profile_dir: Path, headed: bool
) -> tuple[subprocess.Popen[bytes], int]:
    port = _free_port()
    profile_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(browser_path),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir.resolve()}",
        "--no-first-run",
        "--no-default-browser-check",
        "--lang=en-GB",
        "--disable-session-crashed-bubble",
    ]
    if not headed:
        command.append("--headless=new")
    process = subprocess.Popen(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        _wait_for_debug_port(process, port)
    except RuntimeError:
        stop_browser(process)
        raise
    return process, port


def stop_browser(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def close_attached_browser(browser: Any | None, process: subprocess.Popen[bytes]) -> None:
    """Close the actual CDP browser, then its launched process tree if needed."""

    if browser is not None:
        try:
            session = browser.new_browser_cdp_session()
            session.send("Browser.close")
        except Exception:
            try:
                browser.close()
            except Exception:
                pass
    deadline = time.monotonic() + 3.0
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    stop_browser(process)
