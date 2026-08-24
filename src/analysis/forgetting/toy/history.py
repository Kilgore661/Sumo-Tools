"""Generate, persist, and reload immutable synthetic bout histories."""

from __future__ import annotations

import csv
import hashlib
import random
from dataclasses import dataclass
from pathlib import Path

from .elo import expected_score
from .model import ToyWorld


@dataclass(frozen=True)
class ToyBout:
    event: int
    bout_in_event: int
    global_bout: int
    player_a: int
    player_b: int
    true_probability_a_wins: float
    random_draw: float
    a_won: bool


@dataclass(frozen=True)
class ToyHistory:
    master_seed: int
    schedule_seed: int
    outcome_seed: int
    events: int
    player_count: int
    bouts: tuple[ToyBout, ...]

    @property
    def expected_bout_count(self) -> int:
        return self.events * self.player_count * (self.player_count - 1) // 2

    def validate(self) -> None:
        if self.events < 1:
            raise ValueError("history must contain at least one event")
        if self.player_count < 2:
            raise ValueError("history must contain at least two players")
        if len(self.bouts) != self.expected_bout_count:
            raise ValueError(
                f"history has {len(self.bouts)} bouts; expected {self.expected_bout_count}"
            )

        expected_pairs = set(round_robin_pairs(self.player_count))
        next_global_bout = 1
        for event in range(1, self.events + 1):
            event_bouts = tuple(row for row in self.bouts if row.event == event)
            if len(event_bouts) != len(expected_pairs):
                raise ValueError(f"event {event} is not a complete round robin")
            if {(row.player_a, row.player_b) for row in event_bouts} != expected_pairs:
                raise ValueError(f"event {event} contains an invalid pair set")
            for bout_in_event, row in enumerate(event_bouts, start=1):
                if row.bout_in_event != bout_in_event:
                    raise ValueError(f"event {event} has a non-contiguous bout clock")
                if row.global_bout != next_global_bout:
                    raise ValueError("history has a non-contiguous global bout clock")
                if row.a_won != (row.random_draw < row.true_probability_a_wins):
                    raise ValueError(f"bout {row.global_bout} outcome does not match its draw")
                next_global_bout += 1


def round_robin_pairs(player_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (player_a, player_b)
        for player_a in range(player_count)
        for player_b in range(player_a + 1, player_count)
    )


def generate_history(*, world: ToyWorld, events: int, seed: int) -> ToyHistory:
    if events < 1:
        raise ValueError("events must be at least 1")

    seed_rng = random.Random(seed)
    schedule_seed = seed_rng.getrandbits(64)
    outcome_seed = seed_rng.getrandbits(64)
    schedule_rng = random.Random(schedule_seed)
    outcome_rng = random.Random(outcome_seed)
    skills = world.latent_skills
    base_pairs = round_robin_pairs(world.player_count)
    rows: list[ToyBout] = []
    global_bout = 0

    for event in range(1, events + 1):
        pairs = list(base_pairs)
        schedule_rng.shuffle(pairs)
        for bout_in_event, (player_a, player_b) in enumerate(pairs, start=1):
            global_bout += 1
            probability = expected_score(skills[player_a], skills[player_b], q=world.q)
            draw = outcome_rng.random()
            rows.append(
                ToyBout(
                    event=event,
                    bout_in_event=bout_in_event,
                    global_bout=global_bout,
                    player_a=player_a,
                    player_b=player_b,
                    true_probability_a_wins=probability,
                    random_draw=draw,
                    a_won=draw < probability,
                )
            )

    history = ToyHistory(
        master_seed=seed,
        schedule_seed=schedule_seed,
        outcome_seed=outcome_seed,
        events=events,
        player_count=world.player_count,
        bouts=tuple(rows),
    )
    history.validate()
    return history


HISTORY_FIELDS = (
    "event",
    "bout_in_event",
    "global_bout",
    "player_a",
    "player_b",
    "true_probability_a_wins",
    "random_draw",
    "a_won",
)


def write_history(path: Path, history: ToyHistory) -> None:
    history.validate()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=HISTORY_FIELDS)
        writer.writeheader()
        for row in history.bouts:
            writer.writerow(
                {
                    "event": row.event,
                    "bout_in_event": row.bout_in_event,
                    "global_bout": row.global_bout,
                    "player_a": row.player_a,
                    "player_b": row.player_b,
                    "true_probability_a_wins": repr(row.true_probability_a_wins),
                    "random_draw": repr(row.random_draw),
                    "a_won": int(row.a_won),
                }
            )


def read_history(
    path: Path,
    *,
    master_seed: int,
    schedule_seed: int,
    outcome_seed: int,
    events: int,
    player_count: int,
) -> ToyHistory:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = tuple(
            ToyBout(
                event=int(row["event"]),
                bout_in_event=int(row["bout_in_event"]),
                global_bout=int(row["global_bout"]),
                player_a=int(row["player_a"]),
                player_b=int(row["player_b"]),
                true_probability_a_wins=float(row["true_probability_a_wins"]),
                random_draw=float(row["random_draw"]),
                a_won=bool(int(row["a_won"])),
            )
            for row in csv.DictReader(stream)
        )
    history = ToyHistory(
        master_seed=master_seed,
        schedule_seed=schedule_seed,
        outcome_seed=outcome_seed,
        events=events,
        player_count=player_count,
        bouts=rows,
    )
    history.validate()
    return history


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

