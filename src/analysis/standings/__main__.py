import argparse
import sys
from datetime import datetime
from time import perf_counter

from src.analysis.standings.Tee import Tee
from src.analysis.standings.get_standings import (
    compute_standings,
    load_or_create_totals_cache,
    resolve_date,
    resolve_window_dates,
)
from src.analysis.standings.reports import (
    copy_log_to_latest,
    copy_to_latest,
    ensure_output_dir,
    ensure_run_output_dir,
    run_log_file,
    standings_run_file,
    write_standings_csv,
)
from src.infra.live_store.api import get_history


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute sumo standings from History.")
    parser.add_argument("--date", help="Basho date YYYY/MM")
    parser.add_argument(
        "--direction",
        choices=["BACKWARDS", "FORWARDS"],
        default="BACKWARDS",
        help="Window direction relative to --date",
    )
    parser.add_argument(
        "--num-basho",
        type=int,
        default=1,
        help="Number of basho in the standings window",
    )
    parser.add_argument(
        "--wins",
        choices=["real", "all"],
        default="real",
        help="Primary ranking key",
    )
    return parser.parse_args()


def main() -> None:
    ensure_output_dir()

    run_dt = datetime.now()
    run_stamp = run_dt.strftime("%Y-%m-%d %H-%M-%S")
    ensure_run_output_dir(run_stamp)

    original_stdout = sys.stdout
    run_log = run_log_file(run_stamp)

    with run_log.open("w", encoding="utf-8") as log_file:
        tee = Tee(original_stdout, log_file)
        sys.stdout = tee

        try:
            print(f"Standings run started: {run_dt.strftime('%Y-%m-%d %H:%M:%S')}")

            args = parse_args()

            history = get_history()

            t0 = perf_counter()

            resolved_date = resolve_date(
                history=history,
                direction=args.direction,
                requested_date=args.date,
            )

            selected_dates = resolve_window_dates(
                history=history,
                date=resolved_date,
                direction=args.direction,
                num_basho=args.num_basho,
            )

            cache_rows, cache_status = load_or_create_totals_cache(history)

            t1 = perf_counter()

            standings_rows = compute_standings(
                cache_rows=cache_rows,
                selected_dates=selected_dates,
                wins=args.wins,
            )

            t2 = perf_counter()

            run_csv = standings_run_file(
                run_stamp=run_stamp,
                date=resolved_date.replace("/", "-"),
                direction=args.direction,
                num_basho=args.num_basho,
                wins=args.wins,
            )
            write_standings_csv(standings_rows, run_csv)
            latest_csv = copy_to_latest(run_csv)

            t3 = perf_counter()

            print(f"date: {resolved_date}{' (defaulted)' if args.date is None else ''}")
            print(f"direction: {args.direction}")
            print(f"num_basho: {args.num_basho}")
            print(f"wins: {args.wins}")
            print(f"selected basho: {', '.join(selected_dates)}")
            print(f"cache: {cache_status} files/output/standings/totals_cache.csv")
            print(f"cache rows: {len(cache_rows)}")
            print(f"rikishi ranked: {len(standings_rows)}")
            print(f"cache + selection time: {t1 - t0:.2f}s")
            print(f"standing calculation time: {t2 - t1:.2f}s")
            print(f"CSV write + latest copy time: {t3 - t2:.2f}s")
            print(f"total elapsed (excluding History connection): {t3 - t0:.2f}s")
            print(f"run output: {run_csv}")
            print(f"latest output: {latest_csv}")

        finally:
            sys.stdout = original_stdout

    copy_log_to_latest(run_log)


if __name__ == "__main__":
    main()
