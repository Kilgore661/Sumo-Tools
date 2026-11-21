"""Small Betting-owned boundary around the ExpressVPN Windows CLI."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


LOCATION_PATTERN = re.compile(r"^\s+(.+?)\s+(\d+)\s*$")
CONNECTED_PREFIX = "Connected to "
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class ConnectionError(RuntimeError):
    """A bounded VPN or route operation failed."""


@dataclass(frozen=True)
class Place:
    key: str
    name: str
    location_id: int | None = None

    @classmethod
    def direct(cls) -> "Place":
        return cls("direct", "Direct")

    @classmethod
    def vpn(cls, location_id: int, name: str) -> "Place":
        return cls(f"expressvpn:{location_id}", name, location_id)


@dataclass(frozen=True)
class ConnectionState:
    connected: bool
    location_name: str | None = None
    raw: str = ""


def _run(command: list[str], timeout: float) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConnectionError(f"Command timed out: {' '.join(command)}") from exc
    except OSError as exc:
        raise ConnectionError(f"Could not run {command[0]}: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or str(result.returncode)
        raise ConnectionError(f"Command failed: {detail}")
    return result.stdout.strip() or result.stderr.strip()


def find_expressvpn_cli() -> Path:
    candidates: list[Path] = []
    override = os.environ.get("EXPRESSVPN_CLI")
    if override:
        candidates.append(Path(override))
    for variable in ("ProgramFiles(x86)", "ProgramFiles"):
        root = os.environ.get(variable)
        if root:
            candidates.append(
                Path(root) / "ExpressVPN" / "services" / "ExpressVPN.CLI.exe"
            )
    candidates.append(
        Path(r"C:\Program Files (x86)\ExpressVPN\services\ExpressVPN.CLI.exe")
    )
    discovered = shutil.which("ExpressVPN.CLI.exe")
    if discovered:
        candidates.append(Path(discovered))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ConnectionError("ExpressVPN CLI was not found; set EXPRESSVPN_CLI")


class ExpressVpnController:
    def __init__(self, cli_path: Path | None = None) -> None:
        self.cli_path = cli_path or find_expressvpn_cli()

    def command(self, *arguments: str, timeout: float = 30.0) -> str:
        return _run([str(self.cli_path), *arguments], timeout)

    def status(self, timeout: float = 5.0) -> ConnectionState:
        raw = self.command("status", timeout=timeout).strip()
        if raw.startswith(CONNECTED_PREFIX):
            return ConnectionState(True, raw[len(CONNECTED_PREFIX) :].strip(), raw)
        if raw.casefold() == "not connected":
            return ConnectionState(False, None, raw)
        raise ConnectionError(f"Unrecognised ExpressVPN status: {raw}")

    def catalogue(self) -> dict[int, str]:
        result: dict[int, str] = {}
        for line in self.command("list").splitlines():
            match = LOCATION_PATTERN.match(line)
            if match:
                result[int(match.group(2))] = match.group(1).strip()
        if not result:
            raise ConnectionError("ExpressVPN returned no recognisable locations")
        return result

    def _wait_for(self, place: Place, timeout: float = 15.0) -> ConnectionState:
        deadline = time.monotonic() + timeout
        last: ConnectionState | None = None
        while time.monotonic() < deadline:
            last = self.status()
            if place.location_id is None and not last.connected:
                return last
            if (
                place.location_id is not None
                and last.connected
                and last.location_name
                and last.location_name.casefold() == place.name.casefold()
            ):
                return last
            time.sleep(0.5)
        detail = last.raw if last else "unknown"
        raise ConnectionError(f"Could not establish {place.name}; last state: {detail}")

    def ensure_direct(self) -> ConnectionState:
        state = self.status()
        if state.connected:
            self.command("disconnect")
        return self._wait_for(Place.direct())

    def ensure_place(self, place: Place) -> ConnectionState:
        if place.location_id is None:
            return self.ensure_direct()
        state = self.status()
        if state.connected and state.location_name.casefold() == place.name.casefold():
            return state
        if state.connected:
            self.command("disconnect")
            self._wait_for(Place.direct())
        try:
            self.command("connect", str(place.location_id))
        except ConnectionError as exc:
            # A timed-out CLI command can still complete in the service.
            try:
                return self._wait_for(place, timeout=5.0)
            except ConnectionError:
                raise exc
        return self._wait_for(place)

    def restore(self, initial: ConnectionState, catalogue: dict[int, str]) -> None:
        if not initial.connected:
            self.ensure_direct()
            return
        match = next(
            (
                Place.vpn(location_id, name)
                for location_id, name in catalogue.items()
                if initial.location_name
                and name.casefold() == initial.location_name.casefold()
            ),
            None,
        )
        if match is None:
            raise ConnectionError(
                f"Initial location is no longer in the catalogue: {initial.location_name}"
            )
        self.ensure_place(match)


def resolve_places(selectors: list[str], catalogue: dict[int, str]) -> list[Place]:
    places: list[Place] = []
    for selector in selectors:
        if selector.casefold() in {"direct", "none"}:
            places.append(Place.direct())
            continue
        if not selector.isdecimal() or int(selector) not in catalogue:
            raise ConnectionError(f"Unknown ExpressVPN place: {selector}")
        location_id = int(selector)
        places.append(Place.vpn(location_id, catalogue[location_id]))
    return places


def observe_exit_ip(timeout: float = 15.0) -> str:
    providers = ("https://api.ipify.org", "https://icanhazip.com")
    deadline = time.monotonic() + timeout
    last_error = "no provider attempted"
    while time.monotonic() < deadline:
        for url in providers:
            remaining = max(0.1, deadline - time.monotonic())
            try:
                request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(request, timeout=min(5.0, remaining)) as response:
                    value = response.read(128).decode("ascii", errors="replace").strip()
                if value:
                    return value
            except (URLError, OSError, UnicodeError) as exc:
                last_error = str(exc)
        time.sleep(0.5)
    raise ConnectionError(f"Could not observe an exit IP: {last_error}")


class VpnLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.fd: int | None = None

    def __enter__(self) -> "VpnLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ConnectionError(f"Another Betting probe owns {self.path}") from exc
        os.write(self.fd, str(os.getpid()).encode("ascii"))
        return self

    def __exit__(self, *_args) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
