"""
Tracker main loop.

This module contains the top-level orchestration for maintaining the
canonical sumo dataset and its mandatory downstream products.

The tracker runs continuously. On each iteration it:

1. Determines the current basho scheduling window
2. Derives the current run state (DORMANT / READY)
3. Decides whether new data may exist and a run should be attempted
4. If so, determines the ordered list of requested BashoDayRefs
5. Enters ACTIVE state and runs the update cycle:
       scrape requested pairs
       -> parse requested pairs
       -> write canonical zip
       -> refresh cache
       -> run required analysis/products
6. Handles the outcome according to policy:
       - success -> record successful run for the day
       - download failure -> enter RECOVERY and retry later
       - parser/cache/analysis failure -> alert and terminate
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

The tracker is time-driven. It determines which BashoDayRefs should
now exist and requests them explicitly. It does not parse, validate, or
construct canonical History itself.

This module defines:
    - run(): the main loop
    - handle_update_result(): policy for update outcomes

All domain-specific work (planning, scraping, parsing, persistence,
cache refresh, analysis) is delegated to other modules.
"""

import argparse
import time
from datetime import date, datetime, timedelta
from time import sleep

from infra.tracker.alert import alert_fatal
from infra.tracker.config import TrackerConfig
from infra.tracker.ledger import InMemoryLedger
from infra.tracker.planner import get_requested_date_days
from infra.tracker.schedule import (
    get_basho_window,
    next_run_time,
    state_for,
    time_when_new_data_may_exist,
    within_window,
)
from infra.tracker.tray import set_tray_state
from infra.tracker.types import RunState, TrackerRuntime, UpdateResult
from infra.tracker.update_cycle import run_update_cycle

from .Clocks import RealClock, ScaledClock

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
    - NO_NEW_DATA makes no state change.
    - All other failure results are fatal.
    """
    match result:
        case UpdateResult.SUCCESS:
            ledger.record_success_for(run_date)
            runtime.state = RunState.READY

        case UpdateResult.RETRIEVAL_FAILED:
            runtime.state = RunState.RECOVERY

        case UpdateResult.NO_NEW_DATA:
            pass

        case (
            UpdateResult.REBUILD_FAILED
            | UpdateResult.PUBLISH_FAILED
            | UpdateResult.CACHE_FAILED
            | UpdateResult.ANALYSIS_FAILED
            | UpdateResult.DERIVED_ARTIFACTS_MISSING
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
        print("[tracker] planner returned no requested BashoDayRefs")
        handle_update_result(
            runtime,
            UpdateResult.NO_NEW_DATA,
            now.date(),
            ledger,
        )
        return

    runtime.state = RunState.ACTIVE
    set_tray_state(runtime.state, now)

    result = run_update_cycle(requested_basho_days)

    handle_update_result(
        runtime,
        result,
        now.date(),
        ledger,
    )


def _effective_poll_interval_seconds(
    config: TrackerConfig,
    *,
    test_mode: bool,
    real_seconds_per_simulated_day: float
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


def run(
    config: TrackerConfig,
    *,
    immediate: bool = False,
    clock=None,
    poll_interval_seconds: float
) -> None:
    """
    Run the tracker main loop.
    """
    if clock is None:
        clock = RealClock()

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
            reason="scheduled",
        )

        sleep(poll_interval_seconds)

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
