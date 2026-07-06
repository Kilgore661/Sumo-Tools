from __future__ import annotations

import argparse
import math


DEFAULT_SECONDS_PER_MATCH = 4.70e-7


def match_count(*, players: int, runs: int, events: int) -> int:
    return runs * events * players * (players - 1) // 2


def estimate_seconds(
    *,
    players: int,
    runs: int,
    events: int,
    seconds_per_match: float = DEFAULT_SECONDS_PER_MATCH,
) -> float:
    return match_count(players=players, runs=runs, events=events) * seconds_per_match


def solve_runs(
    *,
    players: int,
    events: int,
    seconds: float,
    seconds_per_match: float = DEFAULT_SECONDS_PER_MATCH,
) -> int:
    matches_per_run = events * players * (players - 1) / 2
    return max(1, int(seconds / (matches_per_run * seconds_per_match)))


def solve_events(
    *,
    players: int,
    runs: int,
    seconds: float,
    seconds_per_match: float = DEFAULT_SECONDS_PER_MATCH,
) -> int:
    matches_per_event_set = runs * players * (players - 1) / 2
    return max(1, int(seconds / (matches_per_event_set * seconds_per_match)))


def solve_players(
    *,
    runs: int,
    events: int,
    seconds: float,
    seconds_per_match: float = DEFAULT_SECONDS_PER_MATCH,
) -> int:
    target_pair_count = 2 * seconds / (runs * events * seconds_per_match)
    # Solve n^2 - n - target_pair_count = 0.
    players = (1 + math.sqrt(1 + 4 * target_pair_count)) / 2
    return max(2, int(players))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Estimate toy Elo runtime from any three of players, runs, events, and seconds."
    )
    parser.add_argument("--players", type=int)
    parser.add_argument("--runs", type=int)
    parser.add_argument("--events", type=int)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--seconds-per-match", type=float, default=DEFAULT_SECONDS_PER_MATCH)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    values = [args.players, args.runs, args.events, args.seconds]
    if sum(value is None for value in values) != 1:
        raise SystemExit("Provide exactly three of --players, --runs, --events, and --seconds.")

    if args.seconds is None:
        seconds = estimate_seconds(
            players=args.players,
            runs=args.runs,
            events=args.events,
            seconds_per_match=args.seconds_per_match,
        )
        matches = match_count(players=args.players, runs=args.runs, events=args.events)
        print(f"matches: {matches}")
        print(f"seconds: {seconds:.3f}")
        return

    if args.runs is None:
        runs = solve_runs(
            players=args.players,
            events=args.events,
            seconds=args.seconds,
            seconds_per_match=args.seconds_per_match,
        )
        print(f"runs: {runs}")
        print(
            f"estimated seconds: "
            f"{estimate_seconds(players=args.players, runs=runs, events=args.events, seconds_per_match=args.seconds_per_match):.3f}"
        )
        return

    if args.events is None:
        events = solve_events(
            players=args.players,
            runs=args.runs,
            seconds=args.seconds,
            seconds_per_match=args.seconds_per_match,
        )
        print(f"events: {events}")
        print(
            f"estimated seconds: "
            f"{estimate_seconds(players=args.players, runs=args.runs, events=events, seconds_per_match=args.seconds_per_match):.3f}"
        )
        return

    players = solve_players(
        runs=args.runs,
        events=args.events,
        seconds=args.seconds,
        seconds_per_match=args.seconds_per_match,
    )
    print(f"players: {players}")
    print(
        f"estimated seconds: "
        f"{estimate_seconds(players=players, runs=args.runs, events=args.events, seconds_per_match=args.seconds_per_match):.3f}"
    )


if __name__ == "__main__":
    main()
