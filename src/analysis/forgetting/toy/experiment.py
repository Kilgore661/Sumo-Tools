"""Orchestrate the first true-start versus flat-start development experiment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .elo import ReplayResult, replay_history
from .history import (
    ToyHistory,
    file_sha256,
    generate_history,
    read_history,
    write_history,
)
from .metrics import (
    EventMetric,
    ForgettingLandmark,
    build_event_metrics,
    build_forgetting_landmarks,
    integrated_forecast_disagreement,
)
from .model import ToyWorld
from .outputs import make_run_directory, write_development_outputs


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/forgetting/toy")


@dataclass(frozen=True)
class DevelopmentResult:
    run_directory: Path
    world: ToyWorld
    history: ToyHistory
    history_sha256: str
    true_run: ReplayResult
    flat_run: ReplayResult
    metrics: tuple[EventMetric, ...]
    landmarks: tuple[ForgettingLandmark, ...]
    integrated_disagreement: float


def run_development_experiment(
    *,
    world: ToyWorld = ToyWorld(),
    events: int = 500,
    seed: int = 1,
    persistence_events: int = 25,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    started_at: datetime | None = None,
) -> DevelopmentResult:
    """Generate, persist, reload, and replay one paired development history."""

    if persistence_events < 1:
        raise ValueError("persistence_events must be at least 1")
    started_at = started_at or datetime.now().astimezone()
    run_directory = make_run_directory(
        output_root,
        role="development",
        seed=seed,
        timestamp=started_at,
    )
    history_path = run_directory / "history.csv"
    generated_history = generate_history(world=world, events=events, seed=seed)
    write_history(history_path, generated_history)
    history_digest = file_sha256(history_path)

    # Re-read the persisted artifact so both processes demonstrably consume the
    # exact Stage 1 history rather than merely regenerating from the same seed.
    history = read_history(
        history_path,
        master_seed=generated_history.master_seed,
        schedule_seed=generated_history.schedule_seed,
        outcome_seed=generated_history.outcome_seed,
        events=generated_history.events,
        player_count=generated_history.player_count,
    )
    true_run = replay_history(
        history,
        label="true",
        initial_ratings=world.latent_skills,
        q=world.q,
        k=world.k,
    )
    flat_run = replay_history(
        history,
        label="flat",
        initial_ratings=world.flat_initial_ratings,
        q=world.q,
        k=world.k,
    )
    metrics = build_event_metrics(
        true_run=true_run,
        flat_run=flat_run,
        latent_skills=world.latent_skills,
        q=world.q,
    )
    landmarks = build_forgetting_landmarks(
        metrics,
        persistence_events=persistence_events,
    )
    result = DevelopmentResult(
        run_directory=run_directory,
        world=world,
        history=history,
        history_sha256=history_digest,
        true_run=true_run,
        flat_run=flat_run,
        metrics=metrics,
        landmarks=landmarks,
        integrated_disagreement=integrated_forecast_disagreement(metrics),
    )
    write_development_outputs(
        result,
        persistence_events=persistence_events,
        started_at=started_at,
        finished_at=datetime.now().astimezone(),
    )
    return result
