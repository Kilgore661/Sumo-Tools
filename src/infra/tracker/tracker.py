"""
Tracker main loop.

This module contains the top-level orchestration for maintaining the
sumo data store.

The tracker runs continuously. On each iteration it:

1. Determines the current basho scheduling window
2. Derives the current run state (DORMANT / READY)
3. Decides whether new data may exist and a run should be attempted
4. If so, determines the ordered list of required BashoDayRefs
5. Enters ACTIVE state and runs the update cycle:
       compute required BashoDayRefs
       -> run update cycle (download/rebuild/publish/live store as needed)
       -> rebuild canonical History (parse source files)
       -> write canonical zip
       -> refresh live store
6. Handles the outcome according to policy:
       - success -> record successful run for the day
       - download failure -> enter RECOVERY and retry later
       - rebuild / publish / live-store failure -> alert and terminate
       - no new data -> do nothing

Immediate mode:
    If started with --now, the tracker performs one update cycle
    immediately at startup, bypassing the normal time-window gate.
    This is intended for repair / catch-up runs.

Test mode:
    If started with --test, the tracker uses a scaled clock instead of
    real time.

    Additional test-mode options:
        --date YYYY/MM/DD   simulated start date
        --time HH:MM        simulated start time
        --rate FLOAT        real seconds per simulated day

The tracker is time-driven. It determines the full set of BashoDayRefs that
should exist as of now and supplies this set to the update cycle; the retrieval
component then decides which corresponding artifacts must actually be fetched.
It does not parse, validate, or construct canonical History itself.

This module defines:
    - run(): the main loop
    - handle_update_result(): policy for update outcomes

All domain-specific work (planning, downloading, parsing, persistence,
live store refresh) is delegated to other modules.
"""

import argparse
from datetime import date, datetime
from time import sleep

from .alert import alert_fatal
from .config import TrackerConfig
from .ledger import InMemoryLedger
from .planner import get_requested_date_days
from .schedule import (
    get_basho_window,
    next_run_time,
    state_for,
    time_when_new_data_may_exist,
    within_window,
)
from .tray import set_tray_state
from .types import (
    RunState,
    TrackerRuntime,
    UpdateResult,
    RealClock,
    ScaledClock,
)
from .update_cycle import run_update_cycle
from ..live_store.LiveStore import LiveStore, get_store
from ..live_store.config import VERSION
from ..live_store.api import write_published_name, clear_published_name


def handle_update_result(
    runtime: TrackerRuntime,
    result: UpdateResult,
    run_date: date,
    ledger: InMemoryLedger,
) -> None:
    """
    Update tracker runtime and side effects based on one cycle result.

    Policy:
    - SUCCESS records a successful run for the day and returns the tracker to READY.
    - RETRIEVAL_FAILED enters RECOVERY.
    - NO_NEW_DATA records the day and enters READY.
    - All other failure results are fatal.
    """
    match result:
        case UpdateResult.SUCCESS:
            ledger.record_success_for(run_date)
            runtime.state = RunState.READY

        case UpdateResult.RETRIEVAL_FAILED:
            runtime.state = RunState.RECOVERY

        case UpdateResult.NO_NEW_DATA:
            ledger.record_success_for(run_date)
            runtime.state = RunState.READY

        case (
            UpdateResult.REBUILD_FAILED
            | UpdateResult.PUBLISH_FAILED
            | UpdateResult.LIVE_STORE_FAILED
        ):
            alert_fatal(f"Tracker update cycle failed fatally: {result.name}")
            raise RuntimeError(f"Fatal update cycle failure: {result.name}")

        case _:
            raise RuntimeError(f"Unhandled UpdateResult: {result!r}")


def _run_one_cycle_now(
    now: datetime,
    config: TrackerConfig,
    ledger: InMemoryLedger,
    runtime: TrackerRuntime,
    *,
    live_store: LiveStore,
    reason: str,
) -> None:
    """
    Run one update cycle immediately.
    """
    print(f"[tracker] starting update cycle ({reason})")

    requested_basho_days = get_requested_date_days(
        now,
        ledger,
        config,
    )

    if len(requested_basho_days) == 0:
        print("[tracker] planner returned no required BashoDayRefs")
        handle_update_result(
            runtime,
            UpdateResult.NO_NEW_DATA,
            now.date(),
            ledger,
        )
        return

    runtime.state = RunState.ACTIVE
    set_tray_state(runtime.state, now)

    result = run_update_cycle(requested_basho_days, live_store)

    handle_update_result(
        runtime,
        result,
        now.date(),
        ledger,
    )
    set_tray_state(runtime.state, now)


def _effective_poll_interval_seconds(
    config: TrackerConfig,
    *,
    test_mode: bool,
    real_seconds_per_simulated_day: float,
) -> float:
    """
    Return the sleep interval to use in the main loop.

    In normal mode, use the configured poll interval unchanged.

    In test mode, derive a shorter interval from the time scale so that
    the tracker samples several times per simulated day.
    """
    if not test_mode:
        return config.poll_interval_seconds

    # Four checks per simulated day, but do not spin too fast.
    return max(0.05, real_seconds_per_simulated_day / 4.0)


def _fatal_recovery_message(now: datetime, runtime: TrackerRuntime) -> str:
    """
    Return the fatal message used when the active window closes while the
    tracker is still in RECOVERY.
    """
    window = runtime.current_window

    return (
        "active basho window closed while required maintained state is still unresolved; "
        f"recovery did not complete by {window.basho_end.isoformat(sep=' ')} "
        f"(now={now.isoformat(sep=' ')})"
    )


def _initialise_live_store() -> LiveStore:
    """
    Establish and return a usable live store before entering the tracker FSM.

    If no live store is present, bootstrap it from the canonical zip.
    In either case, advertise the current store name.

    The returned LiveStore object must be retained by the tracker for the
    lifetime of the process so that its owning shared-memory handle remains
    alive.
    """
    store = LiveStore(f"history{VERSION}")

    if not store.exists():
        store = get_store()

    write_published_name(store.name)
    return store


def run(
    config: TrackerConfig,
    *,
    immediate: bool = False,
    clock=None,
    poll_interval_seconds: float,
) -> None:
    """
    Run the tracker main loop.
    """
    if clock is None:
        clock = RealClock()

    clear_published_name()
    live_store = _initialise_live_store()

    try:
        ledger = InMemoryLedger()

        now = clock.now()
        current_window = get_basho_window(now, config)

        runtime = TrackerRuntime(
            state=state_for(now, current_window),
            current_time=now,
            current_window=current_window,
            next_run_time=next_run_time(now, current_window, config),
        )

        if immediate:
            _run_one_cycle_now(
                now,
                config,
                ledger,
                runtime,
                live_store=live_store,
                reason="immediate",
            )

        while True:
            now = clock.now()
            runtime.current_time = now
            runtime.current_window = get_basho_window(now, config)
            runtime.next_run_time = next_run_time(now, runtime.current_window, config)

            if not within_window(now, runtime.current_window):
                if runtime.state == RunState.RECOVERY:
                    alert_fatal(_fatal_recovery_message(now, runtime))
                    raise SystemExit(1)
                runtime.state = RunState.DORMANT
            else:
                if runtime.state not in (RunState.ACTIVE, RunState.RECOVERY):
                    runtime.state = state_for(now, runtime.current_window)

            set_tray_state(runtime.state, now)

            if not time_when_new_data_may_exist(
                now,
                runtime.state,
                runtime.current_window,
                ledger,
            ):
                sleep(poll_interval_seconds)
                continue

            _run_one_cycle_now(
                now,
                config,
                ledger,
                runtime,
                live_store=live_store,
                reason="scheduled",
            )

            sleep(poll_interval_seconds)

    finally:
        try:
            live_store.close()
        finally:
            clear_published_name()


def _parse_date(date_text: str) -> datetime.date:
    """
    Parse YYYY/MM/DD into a date.
    """
    return datetime.strptime(date_text, "%Y/%m/%d").date()


def _parse_time(time_text: str) -> datetime.time:
    """
    Parse HH:MM into a time.
    """
    return datetime.strptime(time_text, "%H:%M").time()


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run the basho tracker")

    parser.add_argument(
        "--now",
        action="store_true",
        help="Run one update cycle immediately at startup, then continue normally",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with a simulated clock",
    )

    parser.add_argument(
        "--date",
        default="2026/03/07",
        help="Simulated start date in YYYY/MM/DD format (test mode only)",
    )

    parser.add_argument(
        "--time",
        default="09:00",
        help="Simulated start time in HH:MM format (test mode only)",
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=20.0 / 15.0,
        help="Real seconds per simulated day (test mode only)",
    )

    return parser.parse_args()


def _make_clock_and_poll_interval(
    args: argparse.Namespace,
    config: TrackerConfig,
):
    """
    Construct the clock and poll interval from CLI arguments.
    """
    if not args.test:
        return RealClock(), config.poll_interval_seconds

    start_date = _parse_date(args.date)
    start_time = _parse_time(args.time)
    simulated_start = datetime.combine(start_date, start_time)

    clock = ScaledClock(
        simulated_start=simulated_start,
        real_seconds_per_simulated_day=args.rate,
    )

    poll_interval_seconds = _effective_poll_interval_seconds(
        config,
        test_mode=True,
        real_seconds_per_simulated_day=args.rate,
    )

    print(
        "[tracker] test mode:"
        f" start={simulated_start.isoformat(sep=' ')}"
        f", rate={args.rate} real seconds/day"
        f", poll={poll_interval_seconds:.3f}s"
    )

    return clock, poll_interval_seconds


if __name__ == "__main__":
    args = _parse_args()
    config = TrackerConfig()
    clock, poll_interval_seconds = _make_clock_and_poll_interval(args, config)
    run(
        config,
        immediate=args.now,
        clock=clock,
        poll_interval_seconds=poll_interval_seconds,
    )
