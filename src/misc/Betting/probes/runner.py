"""Orchestrate a bounded sequence of connection places for one source."""

from __future__ import annotations

import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time as clock_time, timedelta
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from .connection import (
    ConnectionError,
    ExpressVpnController,
    Place,
    VpnLock,
    observe_exit_ip,
    resolve_places,
)
from .records import AttemptStore


@dataclass(frozen=True)
class AcquisitionResult:
    outcome: str
    detail: str = ""
    files: tuple[str, ...] = field(default_factory=tuple)

    @property
    def succeeded(self) -> bool:
        return self.outcome == "success"


@dataclass(frozen=True)
class ProbePlan:
    source: str
    target_date: date
    timezone: str
    selectors: tuple[str, ...]
    normal_window: bool


def normal_start_window(now: datetime) -> bool:
    local = now.timetz().replace(tzinfo=None)
    return clock_time(10, 0) <= local <= clock_time(22, 0)


def default_target_date(now: datetime) -> date:
    return now.date() + timedelta(days=1)


def print_plan(plan: ProbePlan) -> None:
    window = "normal" if plan.normal_window else "override"
    print(f"Source: {plan.source}")
    print(f"Target date: {plan.target_date.isoformat()}")
    print(f"Start-window mode: {window} ({plan.timezone})")
    print("Places: " + ", ".join(plan.selectors))


def run_probe(
    plan: ProbePlan,
    acquire: Callable[[Place, str, str], AcquisitionResult],
    *,
    records_dir: Path,
    lock_path: Path,
    controller_factory: Callable[[], ExpressVpnController] = ExpressVpnController,
    exit_ip_observer: Callable[[], str] = observe_exit_ip,
    now_function: Callable[[], datetime] | None = None,
) -> int:
    timezone = ZoneInfo(plan.timezone)
    now_function = now_function or (lambda: datetime.now(timezone))
    started = now_function()
    run_id = str(uuid.uuid4())
    store = AttemptStore(records_dir, plan.source, run_id)

    with VpnLock(lock_path):
        controller = controller_factory()
        catalogue = controller.catalogue()
        places = resolve_places(list(plan.selectors), catalogue)
        initial = controller.status()
        excluded = store.excluded_place_keys()
        store.write_manifest(
            {
                "run_id": run_id,
                "source": plan.source,
                "target_date": plan.target_date.isoformat(),
                "timezone": plan.timezone,
                "started_at": started.isoformat(),
                "normal_window": plan.normal_window,
                "places": [asdict(place) for place in places],
                "initial_connection": asdict(initial),
            }
        )
        result_code = 1
        consecutive_vpn_failures = 0
        try:
            for number, place in enumerate(places, start=1):
                attempt_started = now_function()
                if place.key in excluded:
                    print(
                        f"Attempt {number}/{len(places)}: {place.name} (known HTTP 451; skipped)",
                        file=sys.stderr,
                        flush=True,
                    )
                    store.append(
                        {
                            "attempted_at": attempt_started.isoformat(),
                            "finished_at": attempt_started.isoformat(),
                            "place": asdict(place),
                            "exit_ip": "",
                            "outcome": "known_451_skipped",
                            "detail": "A previous run recorded HTTP 451",
                            "files": [],
                            "target_date": plan.target_date.isoformat(),
                        }
                    )
                    continue
                print(
                    f"Attempt {number}/{len(places)}: {place.name}",
                    file=sys.stderr,
                    flush=True,
                )
                exit_ip = ""
                try:
                    try:
                        controller.ensure_place(place)
                    except ConnectionError as exc:
                        result = AcquisitionResult("vpn_failed", str(exc))
                    else:
                        try:
                            exit_ip = exit_ip_observer()
                        except ConnectionError as exc:
                            result = AcquisitionResult("network_not_ready", str(exc))
                        else:
                            print(f"  Exit IP: {exit_ip}", file=sys.stderr, flush=True)
                            result = acquire(place, exit_ip, run_id)
                except KeyboardInterrupt:
                    store.append(
                        {
                            "attempted_at": attempt_started.isoformat(),
                            "place": asdict(place),
                            "exit_ip": exit_ip,
                            "outcome": "cancelled",
                        }
                    )
                    result_code = 130
                    raise
                store.append(
                    {
                        "attempted_at": attempt_started.isoformat(),
                        "finished_at": now_function().isoformat(),
                        "place": asdict(place),
                        "exit_ip": exit_ip,
                        "outcome": result.outcome,
                        "detail": result.detail,
                        "files": list(result.files),
                        "target_date": plan.target_date.isoformat(),
                    }
                )
                print(f"  Result: {result.outcome}", file=sys.stderr, flush=True)
                if result.detail:
                    print(f"  Detail: {result.detail}", file=sys.stderr, flush=True)
                for path in result.files:
                    print(f"  Saved: {path}", file=sys.stderr, flush=True)
                if result.outcome == "vpn_failed":
                    consecutive_vpn_failures += 1
                    if consecutive_vpn_failures >= 3:
                        print(
                            "Three consecutive VPN control failures; aborting.",
                            file=sys.stderr,
                        )
                        result_code = 3
                        break
                else:
                    consecutive_vpn_failures = 0
                if result.succeeded:
                    result_code = 0
                    break
        finally:
            try:
                controller.restore(initial, catalogue)
                print("Restored initial VPN state.", file=sys.stderr)
            except ConnectionError as exc:
                print(f"Could not restore initial VPN state: {exc}", file=sys.stderr)
                if result_code != 130:
                    result_code = 3
        return result_code
