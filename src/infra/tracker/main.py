"""
Tracker main loop.

This module contains the top-level orchestration for maintaining the
canonical sumo dataset.

The tracker runs continuously. On each iteration it:

1. Determines the current basho scheduling window
2. Derives the current run state (DORMANT / READY)
3. Decides whether new data may exist and a run should be attempted
4. If so, determines the ordered list of requested (Date, Day) pairs
5. Enters ACTIVE state and runs the update cycle:
       scrape requested pairs
       -> parse requested pairs
       -> write canonical zip
6. Handles the outcome according to policy:
       - success -> record successful run for the day
       - scrape failure -> retry later
       - no new data -> do nothing
       - parser failure -> alert and terminate

The tracker is time-driven. It determines which (Date, Day) pairs should
now exist and requests them explicitly. It does not parse, validate, or
construct canonical History itself.

This module defines:
    - run(): the main loop
    - handle_update_result(): policy for update outcomes

All domain-specific work (planning, scraping, parsing, persistence) is
delegated to other modules.
"""

from datetime import date, datetime
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
)
from infra.tracker.tray import set_tray_state
from infra.tracker.types import RunState, TrackerRuntime, UpdateResult
from infra.tracker.update_cycle import run_update_cycle


def handle_update_result(
    result: UpdateResult,
    run_date: date,
    ledger: InMemoryLedger,
    runtime: TrackerRuntime,
) -> None:
    if result == UpdateResult.SUCCESS:
        ledger.record_success_for(run_date)
        print(f"[tracker] successful run recorded for {run_date.isoformat()}")
        runtime.state = RunState.READY
        set_tray_state(runtime.state)
        return

    if result == UpdateResult.SCRAPE_FAILED:
        print("[tracker] scrape failed; will retry later")
        runtime.state = RunState.READY
        set_tray_state(runtime.state)
        return

    if result == UpdateResult.NO_NEW_DATA:
        print("[tracker] no new canonical data produced")
        runtime.state = RunState.READY
        set_tray_state(runtime.state)
        return

    if result == UpdateResult.PARSER_FATAL_ERROR:
        alert_fatal("parser failed on valid input; tracker terminating")
        raise SystemExit(1)

    raise RuntimeError(f"Unhandled update result: {result!r}")


def run(config: TrackerConfig) -> None:
    ledger = InMemoryLedger()
    runtime = TrackerRuntime(state=RunState.DORMANT)

    while True:
        now = datetime.now()
        runtime.current_time = now
        runtime.current_window = get_basho_window(now, config)
        runtime.state = state_for(now, runtime.current_window)
        runtime.next_run_time = next_run_time(now, runtime.current_window, config)

        set_tray_state(runtime.state)

        if not time_when_new_data_may_exist(
            now,
            runtime.state,
            runtime.current_window,
            ledger,
        ):
            sleep(config.poll_interval_seconds)
            continue

        requested_date_days = get_requested_date_days(
            now,
            ledger,
            config,
        )

        if len(requested_date_days) == 0:
            print("[tracker] planner returned no requested date/day pairs")
            runtime.state = RunState.READY
            set_tray_state(runtime.state)
            sleep(config.poll_interval_seconds)
            continue

        runtime.state = RunState.ACTIVE
        set_tray_state(runtime.state)

        result = run_update_cycle(requested_date_days)

        handle_update_result(
            result,
            now.date(),
            ledger,
            runtime,
        )

        sleep(config.poll_interval_seconds)


if __name__ == "__main__":
    run(TrackerConfig())
