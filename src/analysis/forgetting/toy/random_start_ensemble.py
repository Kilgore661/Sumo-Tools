"""Orchestrate reproducible random initializations against T0."""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .constant_start_ensemble import (
    ConstantStartEnsembleResult,
    run_constant_start_ensemble,
)
from .metrics import centred_state_distance, forecast_distance
from .model import ToyWorld
from .outputs import make_run_directory
from .report_identity import refresh_run_reports
from .true_start_ensemble import _write_rows


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/forgetting/toy/random_start_ensemble"
)


@dataclass(frozen=True)
class RandomInitialisation:
    code: str
    map_seed: int
    raw_ratings: tuple[float, ...]
    centred_ratings: tuple[float, ...]
    raw_mean: float
    initial_state_rmse: float
    initial_probability_rmse: float
    adjacent_order_inversions: int
    all_pair_order_inversions: int


@dataclass(frozen=True)
class RandomModelSummary:
    code: str
    map_seed: int
    initial_state_rmse: float
    initial_probability_rmse: float
    adjacent_order_inversions: int
    all_pair_order_inversions: int
    final_state_rmse: float
    final_probability_rmse: float
    final_paired_state_rmse: float
    final_paired_probability_rmse: float
    median_event_probability_0_05: float | None
    median_event_probability_0_02: float | None
    median_event_probability_0_01: float | None
    median_event_probability_0_005: float | None
    elapsed_seconds: float
    output_directory: str


@dataclass(frozen=True)
class RandomBatchResult:
    run_directory: Path
    world: ToyWorld
    maps: int
    half_range: float
    map_seed: int
    history_seed: int
    runs: int
    events: int
    persistence_events: int
    initialisations: tuple[RandomInitialisation, ...]
    model_summaries: tuple[RandomModelSummary, ...]
    elapsed_seconds: float


def _inversion_counts(ratings: Sequence[float]) -> tuple[int, int]:
    adjacent = sum(
        ratings[player] < ratings[player + 1]
        for player in range(len(ratings) - 1)
    )
    all_pair = sum(
        ratings[player_a] < ratings[player_b]
        for player_a in range(len(ratings))
        for player_b in range(player_a + 1, len(ratings))
    )
    return adjacent, all_pair


def generate_random_initialisations(
    *,
    world: ToyWorld,
    count: int,
    half_range: float,
    seed: int,
) -> tuple[RandomInitialisation, ...]:
    if count < 1:
        raise ValueError("count must be at least 1")
    if not math.isfinite(half_range) or half_range <= 0:
        raise ValueError("half_range must be finite and positive")

    width = max(2, len(str(count)))
    seed_rng = random.Random(seed)
    map_seeds = tuple(seed_rng.getrandbits(64) for _ in range(count))
    rows: list[RandomInitialisation] = []
    for index, map_seed in enumerate(map_seeds, start=1):
        map_rng = random.Random(map_seed)
        raw = tuple(
            map_rng.uniform(-half_range, half_range)
            for _ in range(world.player_count)
        )
        raw_mean = sum(raw) / len(raw)
        centred = [value - raw_mean for value in raw]
        # Remove the final floating-point residue so zero-sum Elo and the
        # initialization map have exactly the same population mean.
        centred[-1] -= sum(centred)
        centred_tuple = tuple(centred)
        adjacent, all_pair = _inversion_counts(centred_tuple)
        rows.append(
            RandomInitialisation(
                code=f"TR{index:0{width}d}",
                map_seed=map_seed,
                raw_ratings=raw,
                centred_ratings=centred_tuple,
                raw_mean=raw_mean,
                initial_state_rmse=centred_state_distance(
                    centred_tuple, world.latent_skills
                ),
                initial_probability_rmse=forecast_distance(
                    centred_tuple, world.latent_skills, q=world.q
                ),
                adjacent_order_inversions=adjacent,
                all_pair_order_inversions=all_pair,
            )
        )
    return tuple(rows)


def _initialisation_rows(
    initialisations: Sequence[RandomInitialisation],
    world: ToyWorld,
) -> list[dict[str, object]]:
    return [
        {
            "code": initialisation.code,
            "map_seed": initialisation.map_seed,
            "player": player + 1,
            "latent_skill": world.latent_skills[player],
            "raw_rating": initialisation.raw_ratings[player],
            "centred_rating": initialisation.centred_ratings[player],
            "raw_map_mean": initialisation.raw_mean,
        }
        for initialisation in initialisations
        for player in range(world.player_count)
    ]


def _absolute_median(
    result: ConstantStartEnsembleResult, tolerance: float
) -> float | None:
    return next(
        (
            row.first_event_median
            for row in result.forgetting_summary
            if row.kind == "absolute_tolerance" and row.target == tolerance
        ),
        None,
    )


def _model_summary(
    initialisation: RandomInitialisation,
    result: ConstantStartEnsembleResult,
    batch_directory: Path,
) -> RandomModelSummary:
    final = result.event_summary[-1]
    return RandomModelSummary(
        code=initialisation.code,
        map_seed=initialisation.map_seed,
        initial_state_rmse=initialisation.initial_state_rmse,
        initial_probability_rmse=initialisation.initial_probability_rmse,
        adjacent_order_inversions=initialisation.adjacent_order_inversions,
        all_pair_order_inversions=initialisation.all_pair_order_inversions,
        final_state_rmse=final.t_prime_state_mean,
        final_probability_rmse=final.t_prime_probability_mean,
        final_paired_state_rmse=final.paired_state_mean,
        final_paired_probability_rmse=final.paired_probability_mean,
        median_event_probability_0_05=_absolute_median(result, 0.05),
        median_event_probability_0_02=_absolute_median(result, 0.02),
        median_event_probability_0_01=_absolute_median(result, 0.01),
        median_event_probability_0_005=_absolute_median(result, 0.005),
        elapsed_seconds=result.elapsed_seconds,
        output_directory=str(result.run_directory.relative_to(batch_directory)),
    )


def _summary_markdown(result: RandomBatchResult) -> str:
    rows = "\n".join(
        f"| {row.code} | {row.initial_state_rmse:.2f} | "
        f"{row.initial_probability_rmse:.4f} | {row.all_pair_order_inversions} | "
        f"{row.median_event_probability_0_05} | "
        f"{row.median_event_probability_0_02} | "
        f"{row.median_event_probability_0_01} | "
        f"{row.median_event_probability_0_005} |"
        for row in result.model_summaries
    )
    return f"""# Random-Start Ensemble Batch

## Run

- Random models: {result.maps}
- Raw drawing range: {-result.half_range:g} to {result.half_range:g}
- Map master seed: {result.map_seed}
- History master seed: {result.history_seed}
- Histories per model: {result.runs}
- Events per history: {result.events}
- Persistence requirement: {result.persistence_events} consecutive events
- Total run time: {result.elapsed_seconds:.3f} seconds

Every map is fixed across the same reproducible T0 history ensemble. Raw maps
are independently drawn from the declared uniform range and then centred to
population mean zero. Fixed absolute probability tolerances are used for
cross-map comparison.

| Model | Initial state RMSE | Initial probability RMSE | Pair inversions | Median ≤0.05 | Median ≤0.02 | Median ≤0.01 | Median ≤0.005 |
|---|---:|---:|---:|---:|---:|---:|---:|
{rows}
"""


def _summary_html(markdown: str, result: RandomBatchResult) -> str:
    table_rows = "".join(
        "<tr>"
        f"<td><a href='{html.escape(row.output_directory)}/{row.code.lower()}_report.html'>{row.code}</a></td>"
        f"<td>{row.initial_state_rmse:.2f}</td>"
        f"<td>{row.initial_probability_rmse:.4f}</td>"
        f"<td>{row.all_pair_order_inversions}</td>"
        f"<td>{row.median_event_probability_0_05}</td>"
        f"<td>{row.median_event_probability_0_02}</td>"
        f"<td>{row.median_event_probability_0_01}</td>"
        f"<td>{row.median_event_probability_0_005}</td>"
        f"<td><a href='{html.escape(row.output_directory)}/paired_report.html'>T0 comparison</a></td>"
        "</tr>"
        for row in result.model_summaries
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Random-Start Ensemble Batch</title>
  <style>
    body {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; font-family: system-ui, sans-serif; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: .45rem; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    pre {{ white-space: pre-wrap; background: #f4f4f4; padding: 1rem; }}
  </style>
</head>
<body>
  <h1>Random-Start Ensemble Batch</h1>
  <table>
    <thead><tr><th>Model</th><th>Initial state RMSE</th><th>Initial probability RMSE</th><th>Pair inversions</th><th>Median ≤0.05</th><th>Median ≤0.02</th><th>Median ≤0.01</th><th>Median ≤0.005</th><th>Paired report</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
  <h2>Audit summary</h2>
  <pre>{html.escape(markdown)}</pre>
</body>
</html>
"""


def _write_batch_manifest(
    *,
    path: Path,
    world: ToyWorld,
    initialisations: Sequence[RandomInitialisation],
    half_range: float,
    map_seed: int,
    history_seed: int,
    runs: int,
    events: int,
    persistence_events: int,
    started_at: datetime,
    elapsed_seconds: float,
    completed_models: int,
    status: str,
) -> None:
    manifest = {
        "experiment": "forgetting toy reproducible random-start batch",
        "experimental_contract_version": 1,
        "status": status,
        "started_at": started_at.isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "world": {
            "player_count": world.player_count,
            "latent_gap": world.latent_gap,
            "latent_skills": list(world.latent_skills),
            "q": world.q,
            "k": world.k,
        },
        "batch": {
            "requested_models": len(initialisations),
            "completed_models": completed_models,
            "half_range": half_range,
            "map_master_seed": map_seed,
            "history_master_seed": history_seed,
            "histories_per_model": runs,
            "events_per_history": events,
            "persistence_events": persistence_events,
            "maps_are_centred": True,
            "common_histories_across_models": True,
        },
        "models": [
            {
                "code": row.code,
                "map_seed": row.map_seed,
                "raw_ratings": list(row.raw_ratings),
                "centred_ratings": list(row.centred_ratings),
            }
            for row in initialisations
        ],
        "outputs": {
            "random_initialisations": "random_initialisations.csv",
            "model_summary": "model_summary.csv",
            "summary_markdown": "summary_report.md",
            "summary_html": "summary_report.html",
        },
    }
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def run_random_start_batch(
    *,
    world: ToyWorld = ToyWorld(),
    maps: int = 10,
    half_range: float = 360.0,
    map_seed: int = 1,
    history_seed: int = 1,
    runs: int = 800,
    events: int = 500,
    persistence_events: int = 25,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    progress_every: int = 50,
) -> RandomBatchResult:
    if runs < 1 or events < 1 or persistence_events < 1:
        raise ValueError("runs, events, and persistence_events must be positive")
    if progress_every < 0:
        raise ValueError("progress_every must not be negative")

    started_at = datetime.now().astimezone()
    timer_started = time.perf_counter()
    run_directory = make_run_directory(
        output_root,
        role="batch",
        seed=map_seed,
        timestamp=started_at,
    )
    initialisations = generate_random_initialisations(
        world=world,
        count=maps,
        half_range=half_range,
        seed=map_seed,
    )
    _write_rows(
        run_directory / "random_initialisations.csv",
        _initialisation_rows(initialisations, world),
    )
    _write_batch_manifest(
        path=run_directory / "manifest.json",
        world=world,
        initialisations=initialisations,
        half_range=half_range,
        map_seed=map_seed,
        history_seed=history_seed,
        runs=runs,
        events=events,
        persistence_events=persistence_events,
        started_at=started_at,
        elapsed_seconds=0.0,
        completed_models=0,
        status="running",
    )

    print(
        f"Random batch contains {maps} models; completed 0/{maps}.",
        flush=True,
    )
    summaries: list[RandomModelSummary] = []
    for index, initialisation in enumerate(initialisations, start=1):
        print(
            f"Starting {initialisation.code} ({index}/{maps}); "
            f"completed {index - 1}/{maps} random models.",
            flush=True,
        )
        model_root = run_directory / initialisation.code
        result = run_constant_start_ensemble(
            world=world,
            events=events,
            runs=runs,
            seed=history_seed,
            persistence_events=persistence_events,
            output_root=model_root,
            progress_every=progress_every,
            initialization="custom",
            custom_code=initialisation.code,
            custom_name=(
                f"Random Centred Uniform [-{half_range:g}, {half_range:g}]"
            ),
            custom_initial_ratings=initialisation.centred_ratings,
        )
        summaries.append(_model_summary(initialisation, result, run_directory))
        _write_rows(run_directory / "model_summary.csv", map(asdict, summaries))
        elapsed = time.perf_counter() - timer_started
        _write_batch_manifest(
            path=run_directory / "manifest.json",
            world=world,
            initialisations=initialisations,
            half_range=half_range,
            map_seed=map_seed,
            history_seed=history_seed,
            runs=runs,
            events=events,
            persistence_events=persistence_events,
            started_at=started_at,
            elapsed_seconds=elapsed,
            completed_models=index,
            status="running" if index < maps else "complete",
        )
        print(
            f"Completed {initialisation.code} ({index}/{maps}); "
            f"completed {index}/{maps} random models.",
            flush=True,
        )

    elapsed = time.perf_counter() - timer_started
    batch_result = RandomBatchResult(
        run_directory=run_directory,
        world=world,
        maps=maps,
        half_range=half_range,
        map_seed=map_seed,
        history_seed=history_seed,
        runs=runs,
        events=events,
        persistence_events=persistence_events,
        initialisations=initialisations,
        model_summaries=tuple(summaries),
        elapsed_seconds=elapsed,
    )
    report = _summary_markdown(batch_result)
    (run_directory / "summary_report.md").write_text(report, encoding="utf-8")
    (run_directory / "summary_report.html").write_text(
        _summary_html(report, batch_result), encoding="utf-8"
    )
    _write_batch_manifest(
        path=run_directory / "manifest.json",
        world=world,
        initialisations=initialisations,
        half_range=half_range,
        map_seed=map_seed,
        history_seed=history_seed,
        runs=runs,
        events=events,
        persistence_events=persistence_events,
        started_at=started_at,
        elapsed_seconds=elapsed,
        completed_models=maps,
        status="complete",
    )
    refresh_run_reports(run_directory)
    return batch_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run reproducible centred random initializations against T0."
    )
    parser.add_argument("--maps", type=int, default=10)
    parser.add_argument("--half-range", type=float, default=360.0)
    parser.add_argument("--map-seed", type=int, default=1)
    parser.add_argument("--history-seed", type=int, default=1)
    parser.add_argument("--players", type=int, default=10)
    parser.add_argument("--latent-gap", type=float, default=40.0)
    parser.add_argument("--q", type=float, default=400.0)
    parser.add_argument("--k", type=float, default=5.0)
    parser.add_argument("--runs", type=int, default=800)
    parser.add_argument("--events", type=int, default=500)
    parser.add_argument("--persistence-events", type=int, default=25)
    parser.add_argument("--progress-every", type=int, default=50)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_random_start_batch(
        world=ToyWorld(
            player_count=args.players,
            latent_gap=args.latent_gap,
            q=args.q,
            k=args.k,
        ),
        maps=args.maps,
        half_range=args.half_range,
        map_seed=args.map_seed,
        history_seed=args.history_seed,
        runs=args.runs,
        events=args.events,
        persistence_events=args.persistence_events,
        output_root=args.output_root,
        progress_every=args.progress_every,
    )
    print(f"Wrote random batch to {result.run_directory.resolve()}")
    print(
        f"Completed {len(result.model_summaries)}/{result.maps} random models."
    )
    print(f"Total run time: {result.elapsed_seconds:.3f} seconds")


if __name__ == "__main__":
    main()
