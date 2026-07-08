from __future__ import annotations

import argparse
import csv
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .audit import make_run_dir, write_manifest
from .bridge import build_bridge_metrics, unordered_pair
from .elo import expected_score, update_ratings
from .model import BaselineModel
from .progress import ProgressTimer, format_duration
from .split_division_sweep import first_event


DEFAULT_TOP_SIZE = 42
DEFAULT_BOTTOM_SIZE = 28
DEFAULT_DAYS_PER_EVENT = 15
DEFAULT_SUPPORT_THRESHOLD = 160
DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_evidence_bridge")
DEFAULT_BOUNDARY_PROFILE_GLOB = (
    "*_no_side_boundary_bridge_distribution.csv"
)
DEFAULT_LEGACY_PROFILE_GLOB = "*_no_side_bridge_distribution.csv"
DEFAULT_PROFILE_ROOT = Path("files/output/toy_elo_matchup")

METRIC_FIELDS = [
    "event",
    "top_rmse",
    "bottom_rmse",
    "whole_rmse",
    "cross_rmse",
    "division_offset_error",
    "sample_whole_rmse",
    "boundary_rating_gap",
    "boundary_skill_gap",
    "boundary_gap_error",
    "division_mean_rating_gap",
    "division_mean_skill_gap",
    "division_mean_gap_error",
    "top_slope",
    "bottom_slope",
    "whole_slope",
    "boundary_gap_error_slope",
    "division_mean_gap_error_slope",
    "top_stable_now",
    "bottom_stable_now",
    "internal_stable_now",
    "whole_stable_now",
    "bridge_stable_now",
    "top_stable_window_met",
    "bottom_stable_window_met",
    "internal_stable_window_met",
    "whole_stable_window_met",
    "bridge_stable_window_met",
]

ATTEMPT_FIELDS = [
    "tested_events",
    "runs",
    "days_per_event",
    "target",
    "converged",
    "top_first_stable_event",
    "bottom_first_stable_event",
    "internal_first_stable_event",
    "bridge_first_stable_event",
    "whole_first_stable_event",
    "top_final_rmse",
    "bottom_final_rmse",
    "whole_final_rmse",
    "cross_final_rmse",
    "division_offset_error",
    "boundary_gap_error",
    "division_mean_gap_error",
    "mean_bridge_bouts",
    "matches",
    "elapsed_seconds",
]


@dataclass(frozen=True)
class BridgeSlot:
    player: int
    source_group: str
    probability: float
    scheduled_bout_count: int
    interdivision_bout_count: int


@dataclass(frozen=True)
class EvidenceBridgeProfile:
    source_path: Path
    support_threshold: int
    upper_slots: tuple[BridgeSlot, ...]
    lower_slots: tuple[BridgeSlot, ...]


class EvidenceBridgeEnsemble:
    def __init__(
        self,
        *,
        model: BaselineModel,
        top_size: int,
        profile: EvidenceBridgeProfile,
        days_per_event: int,
        runs: int,
        seed: int,
    ) -> None:
        self.model = model
        self.top_size = top_size
        self.profile = profile
        self.days_per_event = days_per_event
        self.runs = runs
        self.skills = model.hidden_skills()
        self.ratings = [[model.baseline for _ in self.skills] for _ in range(runs)]
        self.rngs = [random.Random(seed + run) for run in range(runs)]
        self.current_event = 0
        self.means = [[model.baseline for _ in self.skills]]
        self.sample_rows = [self.ratings[0].copy()] if runs else []
        self.mean_bridge_bouts = [0.0]

    def extend_to(self, events: int, *, progress_every: int) -> None:
        if events < self.current_event:
            raise ValueError(
                f"cannot extend backwards from {self.current_event} to {events}"
            )

        progress = ProgressTimer(
            events - self.current_event,
            report_every=progress_every,
            label="events",
        )
        completed = 0
        while self.current_event < events:
            sums = [0.0 for _ in self.skills]
            bridge_total = 0
            for run, ratings in enumerate(self.ratings):
                event_pairs, bridge_count = build_event_pairs(
                    top_size=self.top_size,
                    player_count=self.model.player_count,
                    profile=self.profile,
                    days_per_event=self.days_per_event,
                    rng=self.rngs[run],
                )
                bridge_total += bridge_count
                for player_a, player_b in event_pairs:
                    p_a_wins = expected_score(
                        self.skills[player_a],
                        self.skills[player_b],
                        q=self.model.q,
                    )
                    winner = player_a if self.rngs[run].random() < p_a_wins else player_b
                    update_ratings(
                        ratings,
                        player_a,
                        player_b,
                        winner=winner,
                        k=self.model.k,
                        q=self.model.q,
                    )
                for player, rating in enumerate(ratings):
                    sums[player] += rating

            self.current_event += 1
            self.means.append([rating_sum / self.runs for rating_sum in sums])
            self.mean_bridge_bouts.append(bridge_total / self.runs if self.runs else 0.0)
            if self.ratings:
                self.sample_rows.append(self.ratings[0].copy())
            completed += 1
            progress.report(completed)


def resolve_profile_path(path: Path | None) -> Path:
    if path is not None:
        return path
    boundary_candidates = sorted(
        DEFAULT_PROFILE_ROOT.glob(DEFAULT_BOUNDARY_PROFILE_GLOB),
        key=lambda candidate: candidate.stat().st_mtime,
    )
    if boundary_candidates:
        return boundary_candidates[-1]
    candidates = sorted(
        DEFAULT_PROFILE_ROOT.glob(DEFAULT_LEGACY_PROFILE_GLOB),
        key=lambda candidate: candidate.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(
            "No no_side bridge distribution file found under files/output/toy_elo_matchup. "
            "Run python -m src.analysis.toy_elo.matchup first, or pass --profile."
        )
    return candidates[-1]


def load_makuuchi_juryo_profile(
    *,
    path: Path,
    support_threshold: int,
    top_size: int,
) -> EvidenceBridgeProfile:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        rows = list(reader)

    if "boundary_distance" in fieldnames:
        return load_boundary_makuuchi_juryo_profile(
            path=path,
            rows=rows,
            support_threshold=support_threshold,
            top_size=top_size,
        )

    return load_legacy_makuuchi_juryo_profile(
        path=path,
        rows=rows,
        support_threshold=support_threshold,
        top_size=top_size,
    )


def load_boundary_makuuchi_juryo_profile(
    *,
    path: Path,
    rows: list[dict[str, str]],
    support_threshold: int,
    top_size: int,
) -> EvidenceBridgeProfile:
    upper_rows: list[dict[str, str]] = []
    lower_rows: list[dict[str, str]] = []
    for row in rows:
        if row["upper_division"] != "M" or row["lower_division"] != "J":
            continue
        if int(row["interdivision_bout_count"]) < support_threshold:
            continue
        if (
            row["focal_division"] == "M"
            and row["opponent_division"] == "J"
            and row["boundary_anchor"] == "bottom"
        ):
            upper_rows.append(row)
        elif (
            row["focal_division"] == "J"
            and row["opponent_division"] == "M"
            and row["boundary_anchor"] == "top"
        ):
            lower_rows.append(row)

    if not upper_rows:
        raise ValueError(f"No M-side bridge rows met support threshold {support_threshold}")
    if not lower_rows:
        raise ValueError(f"No J-side bridge rows met support threshold {support_threshold}")

    upper_rows.sort(key=lambda row: int(row["boundary_distance"]), reverse=True)
    lower_rows.sort(key=lambda row: int(row["boundary_distance"]))
    upper_slots = tuple(
        BridgeSlot(
            player=top_size - int(row["boundary_distance"]),
            source_group=(
                f"{row['focal_division']} {row['boundary_anchor']} "
                f"{row['boundary_distance']}"
            ),
            probability=float(row["probability"]),
            scheduled_bout_count=int(row["scheduled_bout_count"]),
            interdivision_bout_count=int(row["interdivision_bout_count"]),
        )
        for row in upper_rows
    )
    lower_slots = tuple(
        BridgeSlot(
            player=top_size + int(row["boundary_distance"]) - 1,
            source_group=(
                f"{row['focal_division']} {row['boundary_anchor']} "
                f"{row['boundary_distance']}"
            ),
            probability=float(row["probability"]),
            scheduled_bout_count=int(row["scheduled_bout_count"]),
            interdivision_bout_count=int(row["interdivision_bout_count"]),
        )
        for row in lower_rows
    )
    return EvidenceBridgeProfile(
        source_path=path,
        support_threshold=support_threshold,
        upper_slots=upper_slots,
        lower_slots=lower_slots,
    )


def load_legacy_makuuchi_juryo_profile(
    *,
    path: Path,
    rows: list[dict[str, str]],
    support_threshold: int,
    top_size: int,
) -> EvidenceBridgeProfile:
    upper_rows: list[dict[str, str]] = []
    lower_rows: list[dict[str, str]] = []
    for row in rows:
        if row["upper_division"] != "M" or row["lower_division"] != "J":
            continue
        if int(row["interdivision_bout_count"]) < support_threshold:
            continue
        if row["focal_division"] == "M" and row["opponent_division"] == "J":
            upper_rows.append(row)
        elif row["focal_division"] == "J" and row["opponent_division"] == "M":
            lower_rows.append(row)

    if not upper_rows:
        raise ValueError(f"No M-side bridge rows met support threshold {support_threshold}")
    if not lower_rows:
        raise ValueError(f"No J-side bridge rows met support threshold {support_threshold}")

    upper_rows.sort(key=lambda row: int(row["focal_rank_number"]))
    lower_rows.sort(key=lambda row: int(row["focal_rank_number"]))
    upper_start = top_size - len(upper_rows)

    upper_slots = tuple(
        BridgeSlot(
            player=upper_start + index,
            source_group=row["focal_group"],
            probability=float(row["probability"]),
            scheduled_bout_count=int(row["scheduled_bout_count"]),
            interdivision_bout_count=int(row["interdivision_bout_count"]),
        )
        for index, row in enumerate(upper_rows)
    )
    lower_slots = tuple(
        BridgeSlot(
            player=top_size + index,
            source_group=row["focal_group"],
            probability=float(row["probability"]),
            scheduled_bout_count=int(row["scheduled_bout_count"]),
            interdivision_bout_count=int(row["interdivision_bout_count"]),
        )
        for index, row in enumerate(lower_rows)
    )
    return EvidenceBridgeProfile(
        source_path=path,
        support_threshold=support_threshold,
        upper_slots=upper_slots,
        lower_slots=lower_slots,
    )


def weighted_choice(slots: list[BridgeSlot], rng: random.Random) -> BridgeSlot:
    total = sum(slot.probability for slot in slots)
    if total <= 0:
        return rng.choice(slots)
    threshold = rng.random() * total
    cumulative = 0.0
    for slot in slots:
        cumulative += slot.probability
        if cumulative >= threshold:
            return slot
    return slots[-1]


def choose_lower_slot(
    *,
    lower_slots: list[BridgeSlot],
    upper_player: int,
    seen_pairs: set[tuple[int, int]],
    rng: random.Random,
) -> BridgeSlot:
    unseen = [
        slot
        for slot in lower_slots
        if unordered_pair(upper_player, slot.player) not in seen_pairs
    ]
    return weighted_choice(unseen or lower_slots, rng)


def build_bridge_pairs_for_day(
    *,
    profile: EvidenceBridgeProfile,
    seen_pairs: set[tuple[int, int]],
    rng: random.Random,
) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    available_lower = list(profile.lower_slots)
    upper_slots = list(profile.upper_slots)
    rng.shuffle(upper_slots)
    for upper in upper_slots:
        if not available_lower:
            break
        if rng.random() >= upper.probability:
            continue
        lower = choose_lower_slot(
            lower_slots=available_lower,
            upper_player=upper.player,
            seen_pairs=seen_pairs,
            rng=rng,
        )
        pair = unordered_pair(upper.player, lower.player)
        pairs.append(pair)
        seen_pairs.add(pair)
        available_lower.remove(lower)
    rng.shuffle(pairs)
    return pairs


def closest_candidate(
    *,
    player: int,
    candidates: list[int],
    seen_pairs: set[tuple[int, int]],
    rng: random.Random,
) -> int:
    unseen = [
        candidate
        for candidate in candidates
        if unordered_pair(player, candidate) not in seen_pairs
    ]
    pool = unseen or candidates
    best_distance = min(abs(player - candidate) for candidate in pool)
    best = [candidate for candidate in pool if abs(player - candidate) == best_distance]
    return rng.choice(best)


def build_division_pairs_for_day(
    *,
    players: list[int],
    unavailable: set[int],
    seen_pairs: set[tuple[int, int]],
    rng: random.Random,
) -> list[tuple[int, int]]:
    remaining = [player for player in players if player not in unavailable]
    rng.shuffle(remaining)
    pairs: list[tuple[int, int]] = []
    while len(remaining) >= 2:
        player = remaining.pop()
        opponent = closest_candidate(
            player=player,
            candidates=remaining,
            seen_pairs=seen_pairs,
            rng=rng,
        )
        remaining.remove(opponent)
        pair = unordered_pair(player, opponent)
        pairs.append(pair)
        seen_pairs.add(pair)
    rng.shuffle(pairs)
    return pairs


def build_event_pairs(
    *,
    top_size: int,
    player_count: int,
    profile: EvidenceBridgeProfile,
    days_per_event: int,
    rng: random.Random,
) -> tuple[list[tuple[int, int]], int]:
    top_players = list(range(top_size))
    bottom_players = list(range(top_size, player_count))
    seen_pairs: set[tuple[int, int]] = set()
    event_pairs: list[tuple[int, int]] = []
    bridge_count = 0

    for _day in range(days_per_event):
        day_pairs = build_bridge_pairs_for_day(
            profile=profile,
            seen_pairs=seen_pairs,
            rng=rng,
        )
        bridge_count += len(day_pairs)
        unavailable = {player for pair in day_pairs for player in pair}
        day_pairs.extend(
            build_division_pairs_for_day(
                players=top_players,
                unavailable=unavailable,
                seen_pairs=seen_pairs,
                rng=rng,
            )
        )
        day_pairs.extend(
            build_division_pairs_for_day(
                players=bottom_players,
                unavailable=unavailable,
                seen_pairs=seen_pairs,
                rng=rng,
            )
        )
        rng.shuffle(day_pairs)
        event_pairs.extend(day_pairs)

    return event_pairs, bridge_count


def evidence_match_count(
    *,
    player_count: int,
    days_per_event: int,
    events: int,
    runs: int,
) -> int:
    return runs * events * days_per_event * player_count // 2


def write_profile(path: Path, profile: EvidenceBridgeProfile) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "side",
                "player",
                "source_group",
                "probability",
                "scheduled_bout_count",
                "interdivision_bout_count",
            ]
        )
        for side, slots in [
            ("upper", profile.upper_slots),
            ("lower", profile.lower_slots),
        ]:
            for slot in slots:
                writer.writerow(
                    [
                        side,
                        slot.player,
                        slot.source_group,
                        f"{slot.probability:.8f}",
                        slot.scheduled_bout_count,
                        slot.interdivision_bout_count,
                    ]
                )


def write_metrics(path: Path, rows: list[dict[str, float | int | bool]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METRIC_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in METRIC_FIELDS})


def write_bridge_counts(path: Path, counts: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["event", "mean_bridge_bouts"])
        for event, count in enumerate(counts):
            writer.writerow([event, f"{count:.6f}"])


def write_attempt_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(ATTEMPT_FIELDS)


def append_attempt(path: Path, row: dict[str, float | int | bool | str | None]) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["" if row[field] is None else row[field] for field in ATTEMPT_FIELDS])


def write_final_ratings(
    *,
    path: Path,
    top_size: int,
    ratings: list[float],
    skills: list[float],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["player", "division", "rating", "hidden_skill"])
        for player, rating in enumerate(ratings):
            writer.writerow(
                [
                    player,
                    "top" if player < top_size else "bottom",
                    f"{rating:.6f}",
                    f"{skills[player]:.6f}",
                ]
            )


def metric_firsts(rows: list[dict[str, float | int | bool]]) -> dict[str, int | None]:
    return {
        "top": first_event(rows, "top_stable_window_met"),
        "bottom": first_event(rows, "bottom_stable_window_met"),
        "internal": first_event(rows, "internal_stable_window_met"),
        "bridge": first_event(rows, "bridge_stable_window_met"),
        "whole": first_event(rows, "whole_stable_window_met"),
    }


def target_first(firsts: dict[str, int | None], target: str) -> int | None:
    if target == "global":
        return firsts["whole"]
    return firsts[target]


def summarize_attempt(
    *,
    metrics: list[dict[str, float | int | bool]],
    firsts: dict[str, int | None],
    target: str,
    runs: int,
    days_per_event: int,
    mean_bridge_bouts: float,
    matches: int,
    elapsed_seconds: float,
) -> dict[str, float | int | bool | str | None]:
    final = metrics[-1]
    return {
        "tested_events": int(final["event"]),
        "runs": runs,
        "days_per_event": days_per_event,
        "target": target,
        "converged": int(target_first(firsts, target) is not None),
        "top_first_stable_event": firsts["top"],
        "bottom_first_stable_event": firsts["bottom"],
        "internal_first_stable_event": firsts["internal"],
        "bridge_first_stable_event": firsts["bridge"],
        "whole_first_stable_event": firsts["whole"],
        "top_final_rmse": final["top_rmse"],
        "bottom_final_rmse": final["bottom_rmse"],
        "whole_final_rmse": final["whole_rmse"],
        "cross_final_rmse": final["cross_rmse"],
        "division_offset_error": final["division_offset_error"],
        "boundary_gap_error": final["boundary_gap_error"],
        "division_mean_gap_error": final["division_mean_gap_error"],
        "mean_bridge_bouts": mean_bridge_bouts,
        "matches": matches,
        "elapsed_seconds": elapsed_seconds,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a 42+28 toy Elo simulation with an evidence-aligned M-J bridge."
    )
    parser.add_argument("--profile", type=Path, default=None)
    parser.add_argument("--support-threshold", type=int, default=DEFAULT_SUPPORT_THRESHOLD)
    parser.add_argument("--top-size", type=int, default=DEFAULT_TOP_SIZE)
    parser.add_argument("--bottom-size", type=int, default=DEFAULT_BOTTOM_SIZE)
    parser.add_argument("--days-per-event", type=int, default=DEFAULT_DAYS_PER_EVENT)
    parser.add_argument("--events", type=int, default=None)
    parser.add_argument("--event-start", type=int, default=500)
    parser.add_argument("--event-step", type=int, default=500)
    parser.add_argument("--event-stop", type=int, default=None)
    parser.add_argument(
        "--convergence-target",
        choices=["internal", "bridge", "whole", "global"],
        default="bridge",
    )
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--learning-fraction", type=float, default=0.125)
    parser.add_argument("--gap", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--stable-epsilon", type=float, default=4.0)
    parser.add_argument("--slope-epsilon", type=float, default=0.05)
    parser.add_argument("--stable-window", type=int, default=25)
    parser.add_argument("--bridge-offset-epsilon", type=float, default=10.0)
    parser.add_argument("--bridge-boundary-epsilon", type=float, default=10.0)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def serializable_args(args: argparse.Namespace, profile_path: Path) -> dict[str, object]:
    values = vars(args).copy()
    values["profile"] = str(profile_path)
    values["output_root"] = str(args.output_root)
    return values


def main() -> None:
    args = build_parser().parse_args()
    if args.top_size <= 0 or args.bottom_size <= 0:
        raise ValueError("top-size and bottom-size must be positive")
    if args.days_per_event <= 0:
        raise ValueError("days-per-event must be positive")
    if args.runs <= 0:
        raise ValueError("runs must be positive")
    if args.events is not None and args.events <= 0:
        raise ValueError("events must be positive")
    if args.event_start <= 0:
        raise ValueError("event-start must be positive")
    if args.event_step <= 0:
        raise ValueError("event-step must be positive")
    if args.event_stop is not None and args.event_stop < args.event_start:
        raise ValueError("event-stop must be greater than or equal to event-start")

    profile_path = resolve_profile_path(args.profile)
    profile = load_makuuchi_juryo_profile(
        path=profile_path,
        support_threshold=args.support_threshold,
        top_size=args.top_size,
    )
    players = args.top_size + args.bottom_size
    model = BaselineModel(
        player_count=players,
        max_rating=args.gap * (players - 1),
        q=args.q,
        learning_fraction=args.learning_fraction,
    )
    started_at = datetime.now().astimezone()
    run_dir = make_run_dir(args.output_root, seed=args.seed, timestamp=started_at)
    manifest_path = run_dir / "manifest.json"
    attempts_path = run_dir / "attempts.csv"
    metrics_path = run_dir / "metrics.csv"
    counts_path = run_dir / "bridge_counts.csv"
    profile_output_path = run_dir / "profile.csv"
    ratings_path = run_dir / "final_ratings.csv"

    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "parameters": serializable_args(args, profile_path),
            "outputs": {
                "run_dir": str(run_dir),
                "manifest": str(manifest_path),
                "attempts": str(attempts_path),
                "metrics": str(metrics_path),
                "bridge_counts": str(counts_path),
                "profile": str(profile_output_path),
                "final_ratings": str(ratings_path),
            },
            "status": "running",
        },
    )
    write_attempt_header(attempts_path)

    fixed_events = args.events if args.events is not None else 500
    search_mode = args.event_stop is not None
    event_description = (
        f"search={args.event_start}:{args.event_step}:{args.event_stop}; "
        f"target={args.convergence_target}"
        if search_mode
        else f"events={fixed_events}"
    )
    print(f"Evidence bridge output: {run_dir}", flush=True)
    print(
        f"Profile: {profile_path}; support_threshold={args.support_threshold}; "
        f"divisions={args.top_size}+{args.bottom_size}; {event_description}; "
        f"runs={args.runs}; days_per_event={args.days_per_event}",
        flush=True,
    )
    print(
        "Upper slots: "
        + ", ".join(
            f"{slot.source_group}->p{slot.player} ({slot.probability:.4f})"
            for slot in profile.upper_slots
        ),
        flush=True,
    )
    print(
        "Lower slots: "
        + ", ".join(
            f"{slot.source_group}->p{slot.player} ({slot.probability:.4f})"
            for slot in profile.lower_slots
        ),
        flush=True,
    )

    start = time.perf_counter()
    ensemble = EvidenceBridgeEnsemble(
        model=model,
        top_size=args.top_size,
        profile=profile,
        days_per_event=args.days_per_event,
        runs=args.runs,
        seed=args.seed,
    )
    top_players = list(range(args.top_size))
    bottom_players = list(range(args.top_size, players))

    attempt_events = (
        range(args.event_start, args.event_stop + 1, args.event_step)
        if search_mode
        else [fixed_events]
    )
    metrics: list[dict[str, float | int | bool]] = []
    firsts: dict[str, int | None] = {
        "top": None,
        "bottom": None,
        "internal": None,
        "bridge": None,
        "whole": None,
    }
    for events in attempt_events:
        attempt_start = time.perf_counter()
        print(f"Trying events={events}; runs={args.runs}", flush=True)
        ensemble.extend_to(events, progress_every=args.progress_every)
        metrics = build_bridge_metrics(
            skills=ensemble.skills,
            means=ensemble.means,
            sample_rows=ensemble.sample_rows,
            top_players=top_players,
            bottom_players=bottom_players,
            stable_epsilon=args.stable_epsilon,
            slope_epsilon=args.slope_epsilon,
            stable_window=args.stable_window,
            bridge_offset_epsilon=args.bridge_offset_epsilon,
            bridge_boundary_epsilon=args.bridge_boundary_epsilon,
        )
        firsts = metric_firsts(metrics)
        attempt_elapsed = time.perf_counter() - attempt_start
        matches = evidence_match_count(
            player_count=players,
            days_per_event=args.days_per_event,
            events=events,
            runs=args.runs,
        )
        row = summarize_attempt(
            metrics=metrics,
            firsts=firsts,
            target=args.convergence_target,
            runs=args.runs,
            days_per_event=args.days_per_event,
            mean_bridge_bouts=ensemble.mean_bridge_bouts[-1],
            matches=matches,
            elapsed_seconds=attempt_elapsed,
        )
        append_attempt(attempts_path, row)
        print(
            f"  converged={bool(row['converged'])} "
            f"top={firsts['top']} bottom={firsts['bottom']} "
            f"internal={firsts['internal']} bridge={firsts['bridge']} whole={firsts['whole']} "
            f"whole_rmse={float(row['whole_final_rmse']):.3f} "
            f"cross_rmse={float(row['cross_final_rmse']):.3f} "
            f"offset_error={float(row['division_offset_error']):.3f} "
            f"elapsed={format_duration(attempt_elapsed)}",
            flush=True,
        )
        if search_mode and row["converged"]:
            break

    elapsed = time.perf_counter() - start

    write_profile(profile_output_path, profile)
    write_metrics(metrics_path, metrics)
    write_bridge_counts(counts_path, ensemble.mean_bridge_bouts)
    write_final_ratings(
        path=ratings_path,
        top_size=args.top_size,
        ratings=ensemble.means[-1],
        skills=ensemble.skills,
    )

    final = metrics[-1]
    total_matches = evidence_match_count(
        player_count=players,
        days_per_event=args.days_per_event,
        events=ensemble.current_event,
        runs=args.runs,
    )

    write_manifest(
        manifest_path,
        {
            "started_at": started_at.isoformat(),
            "finished_at": datetime.now().astimezone().isoformat(),
            "parameters": serializable_args(args, profile_path),
            "outputs": {
                "run_dir": str(run_dir),
                "manifest": str(manifest_path),
                "attempts": str(attempts_path),
                "metrics": str(metrics_path),
                "bridge_counts": str(counts_path),
                "profile": str(profile_output_path),
                "final_ratings": str(ratings_path),
            },
            "summary": {
                "top_first_stable_event": firsts["top"],
                "bottom_first_stable_event": firsts["bottom"],
                "internal_first_stable_event": firsts["internal"],
                "bridge_first_stable_event": firsts["bridge"],
                "whole_first_stable_event": firsts["whole"],
                "final_whole_rmse": final["whole_rmse"],
                "final_cross_rmse": final["cross_rmse"],
                "final_division_offset_error": final["division_offset_error"],
                "mean_bridge_bouts_final_event": ensemble.mean_bridge_bouts[-1],
                "matches": total_matches,
                "elapsed_seconds": elapsed,
            },
            "status": "complete",
        },
    )
    print(
        f"Stable events: top={firsts['top']}, bottom={firsts['bottom']}, "
        f"internal={firsts['internal']}, bridge={firsts['bridge']}, whole={firsts['whole']}",
        flush=True,
    )
    print(
        f"Final whole_rmse={float(final['whole_rmse']):.3f}; "
        f"cross_rmse={float(final['cross_rmse']):.3f}; "
        f"offset_error={float(final['division_offset_error']):.3f}; "
        f"mean_bridge_bouts={ensemble.mean_bridge_bouts[-1]:.3f}",
        flush=True,
    )
    print(f"Wrote metrics to {metrics_path}", flush=True)
    print(f"Total elapsed: {format_duration(elapsed)}", flush=True)


if __name__ == "__main__":
    main()
