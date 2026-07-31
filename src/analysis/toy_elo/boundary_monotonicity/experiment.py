"""Generate monotonic skills and test recovered Elo at the M-J boundary."""

from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Sequence

from ..elo import expected_score, update_ratings
from ..evidence_bridge import (
    EvidenceBridgeProfile,
    build_event_pairs,
    write_profile,
)
from ..model import BaselineModel
from ..progress import ProgressTimer


DEFAULT_OUTPUT_ROOT = Path(
    "files/output/analysis/toy_elo/boundary_monotonicity"
)
DEFAULT_TOP_SIZE = 42
DEFAULT_BOTTOM_SIZE = 28
DEFAULT_DAYS_PER_EVENT = 15
DEFAULT_EVENTS = 500
DEFAULT_RUNS = 100
DEFAULT_Q = 400.0
DEFAULT_GAP = 40.0
DEFAULT_LEARNING_FRACTION = 0.125
DEFAULT_TAIL_GROUPS = 7
DEFAULT_GROUP_SIZE = 2
DEFAULT_BOOTSTRAP_SAMPLES = 5_000
DEFAULT_SEED = 1

# From the 1989+ clean_elo paired boundary groups, top_bottom_7 through 1.
DEFAULT_HISTORICAL_ENDPOINT_DIFFERENCE = -9.309358591
DEFAULT_HISTORICAL_MAXIMUM_REVERSAL = (
    1928.545020795 - 1914.229849844
)
DEFAULT_HISTORICAL_Q = 900.0


@dataclass(frozen=True)
class ExperimentConfig:
    top_size: int = DEFAULT_TOP_SIZE
    bottom_size: int = DEFAULT_BOTTOM_SIZE
    days_per_event: int = DEFAULT_DAYS_PER_EVENT
    events: int = DEFAULT_EVENTS
    runs: int = DEFAULT_RUNS
    q: float = DEFAULT_Q
    gap: float = DEFAULT_GAP
    learning_fraction: float = DEFAULT_LEARNING_FRACTION
    tail_groups: int = DEFAULT_TAIL_GROUPS
    group_size: int = DEFAULT_GROUP_SIZE
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES
    historical_endpoint_difference: float = (
        DEFAULT_HISTORICAL_ENDPOINT_DIFFERENCE
    )
    historical_maximum_reversal: float = (
        DEFAULT_HISTORICAL_MAXIMUM_REVERSAL
    )
    historical_q: float = DEFAULT_HISTORICAL_Q
    seed: int = DEFAULT_SEED
    progress_every: int = 0

    @property
    def player_count(self) -> int:
        return self.top_size + self.bottom_size

    @property
    def scaled_endpoint_target(self) -> float:
        return (
            self.historical_endpoint_difference
            * self.q
            / self.historical_q
        )

    @property
    def scaled_maximum_target(self) -> float:
        return (
            self.historical_maximum_reversal
            * self.q
            / self.historical_q
        )

    def validate(self) -> None:
        positive_integers = {
            "top_size": self.top_size,
            "bottom_size": self.bottom_size,
            "days_per_event": self.days_per_event,
            "events": self.events,
            "runs": self.runs,
            "tail_groups": self.tail_groups,
            "group_size": self.group_size,
            "bootstrap_samples": self.bootstrap_samples,
        }
        for name, value in positive_integers.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.tail_groups * self.group_size > self.top_size:
            raise ValueError(
                "tail_groups * group_size cannot exceed top_size"
            )
        for name, value in {
            "q": self.q,
            "gap": self.gap,
            "learning_fraction": self.learning_fraction,
            "historical_q": self.historical_q,
        }.items():
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
        if not math.isfinite(self.historical_endpoint_difference):
            raise ValueError(
                "historical_endpoint_difference must be finite"
            )
        if self.historical_maximum_reversal < 0.0:
            raise ValueError(
                "historical_maximum_reversal cannot be negative"
            )


@dataclass(frozen=True)
class BoundaryGroup:
    position: int
    boundary_distance: int
    label: str
    players: tuple[int, ...]


@dataclass(frozen=True)
class GroupResult:
    position: int
    boundary_distance: int
    label: str
    players: tuple[int, ...]
    hidden_skill_mean: float
    rating_mean: float
    rating_standard_deviation: float
    rating_standard_error: float
    approximate_ci95_lower: float
    approximate_ci95_upper: float
    isotonic_fitted_mean: float
    isotonic_residual: float


@dataclass(frozen=True)
class RunReversal:
    run: int
    endpoint_reversal: float
    maximum_reversal: float
    monotonic: bool
    endpoint_reaches_target: bool
    maximum_reaches_target: bool


@dataclass(frozen=True)
class ScenarioSummary:
    scenario: str
    total_bouts: int
    mean_bouts_per_run_event: float
    mean_bridge_bouts_per_run_event: float
    ensemble_endpoint_reversal: float
    endpoint_ci95_lower: float
    endpoint_ci95_upper: float
    ensemble_maximum_reversal: float
    maximum_ci95_lower: float
    maximum_ci95_upper: float
    ensemble_rating_is_monotonic: bool
    individual_monotonic_rate: float
    endpoint_reversal_rate: float
    maximum_reversal_rate: float
    endpoint_target_rate: float
    maximum_target_rate: float
    scaled_endpoint_target: float
    scaled_maximum_target: float


@dataclass(frozen=True)
class ScenarioResult:
    summary: ScenarioSummary
    groups: tuple[GroupResult, ...]
    run_reversals: tuple[RunReversal, ...]


@dataclass(frozen=True)
class ExperimentResult:
    config: ExperimentConfig
    hidden_skills: tuple[float, ...]
    scenarios: tuple[ScenarioResult, ...]


@dataclass(frozen=True)
class OutputPaths:
    run_directory: Path
    scenario_summary_csv: Path
    boundary_groups_csv: Path
    run_reversals_csv: Path
    profile_csv: Path
    manifest_json: Path


@dataclass(frozen=True)
class _SimulationResult:
    final_ratings: tuple[tuple[float, ...], ...]
    total_bouts: int
    total_bridge_bouts: int


def build_boundary_groups(config: ExperimentConfig) -> tuple[BoundaryGroup, ...]:
    """Return BP4-like paired groups ordered from better to worse."""
    config.validate()
    first_player = (
        config.top_size - config.tail_groups * config.group_size
    )
    groups = []
    for position in range(config.tail_groups):
        start = first_player + position * config.group_size
        boundary_distance = config.tail_groups - position
        groups.append(
            BoundaryGroup(
                position=position,
                boundary_distance=boundary_distance,
                label=f"top_bottom_{boundary_distance}",
                players=tuple(
                    range(start, start + config.group_size)
                ),
            )
        )
    return tuple(groups)


def run_experiment(
    *,
    profile: EvidenceBridgeProfile,
    config: ExperimentConfig = ExperimentConfig(),
) -> ExperimentResult:
    """Run evidence-bridge and no-bridge control scenarios."""
    config.validate()
    model = BaselineModel(
        player_count=config.player_count,
        max_rating=config.gap * (config.player_count - 1),
        q=config.q,
        learning_fraction=config.learning_fraction,
    )
    skills = tuple(model.hidden_skills())
    groups = build_boundary_groups(config)
    local_profile = EvidenceBridgeProfile(
        source_path=profile.source_path,
        support_threshold=profile.support_threshold,
        upper_slots=(),
        lower_slots=(),
    )
    scenario_profiles = (
        ("evidence_bridge", profile),
        ("rank_local_control", local_profile),
    )
    scenarios = []
    for scenario_position, (name, scenario_profile) in enumerate(
        scenario_profiles
    ):
        simulation = _simulate(
            model=model,
            skills=skills,
            profile=scenario_profile,
            config=config,
            seed=config.seed + scenario_position * 1_000_000,
            progress_label=name,
        )
        scenarios.append(
            _summarize_scenario(
                name=name,
                simulation=simulation,
                skills=skills,
                groups=groups,
                config=config,
                bootstrap_seed=(
                    config.seed + scenario_position * 1_000_000 + 500_000
                ),
            )
        )
    return ExperimentResult(
        config=config,
        hidden_skills=skills,
        scenarios=tuple(scenarios),
    )


def write_outputs(
    *,
    result: ExperimentResult,
    profile: EvidenceBridgeProfile,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> OutputPaths:
    generated_at, run_directory = _create_run_directory(output_root)
    summary_path = run_directory / "scenario_summary.csv"
    groups_path = run_directory / "boundary_groups.csv"
    reversals_path = run_directory / "run_reversals.csv"
    profile_path = run_directory / "profile.csv"
    manifest_path = run_directory / "manifest.json"

    _write_scenario_summary(summary_path, result.scenarios)
    _write_boundary_groups(groups_path, result.scenarios)
    _write_run_reversals(reversals_path, result.scenarios)
    write_profile(profile_path, profile)

    config_values = asdict(result.config)
    config_values["scaled_endpoint_target"] = (
        result.config.scaled_endpoint_target
    )
    config_values["scaled_maximum_target"] = (
        result.config.scaled_maximum_target
    )
    manifest = {
        "generated_at_utc": generated_at.isoformat(),
        "experiment": "toy_elo_boundary_monotonicity",
        "question": (
            "Can an evidence-shaped Makuuchi-Juryo comparison graph produce "
            "a lower-boundary Elo reversal when latent skill is strictly "
            "monotonic?"
        ),
        "profile_source": str(profile.source_path),
        "parameters": config_values,
        "scenarios": [
            asdict(scenario.summary) for scenario in result.scenarios
        ],
        "interpretation": {
            "primary_comparison": (
                "evidence_bridge versus rank_local_control"
            ),
            "historical_target": (
                "1989+ clean_elo paired boundary-group endpoint difference "
                "and maximum local reversal, each scaled by toy q / "
                "historical q"
            ),
            "ensemble_mean": (
                "Mean final rating over independently seeded simulated runs"
            ),
            "individual_rates": (
                "Fraction of independently seeded runs with the stated "
                "boundary reversal"
            ),
        },
        "limitations": [
            "Players retain fixed skills and fixed division positions.",
            "The scheduler uses boundary propensities but not day, record, "
            "promotion, demotion, absence, or torikumi judgement.",
            "The no-bridge control is disconnected across divisions and is "
            "used only to diagnose top-division boundary shape.",
            "Odd daily bridge counts can leave one unmatched player in each "
            "division, while the even-sized no-bridge divisions pair fully; "
            "the scenario bout counts are therefore reported explicitly.",
            "The historical boundary statistics are compared after q "
            "scaling; this is not a proof that the historical and toy scales "
            "are identical.",
        ],
        "outputs": {
            "scenario_summary_csv": str(summary_path),
            "boundary_groups_csv": str(groups_path),
            "run_reversals_csv": str(reversals_path),
            "profile_csv": str(profile_path),
            "manifest_json": str(manifest_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return OutputPaths(
        run_directory=run_directory,
        scenario_summary_csv=summary_path,
        boundary_groups_csv=groups_path,
        run_reversals_csv=reversals_path,
        profile_csv=profile_path,
        manifest_json=manifest_path,
    )


def _simulate(
    *,
    model: BaselineModel,
    skills: Sequence[float],
    profile: EvidenceBridgeProfile,
    config: ExperimentConfig,
    seed: int,
    progress_label: str,
) -> _SimulationResult:
    final_ratings = []
    total_bouts = 0
    total_bridge_bouts = 0
    progress = ProgressTimer(
        config.runs,
        report_every=config.progress_every,
        label=f"{progress_label} runs",
    )
    for run in range(config.runs):
        rng = random.Random(seed + run)
        ratings = [model.baseline for _ in skills]
        for _event in range(config.events):
            pairs, bridge_bouts = build_event_pairs(
                top_size=config.top_size,
                player_count=config.player_count,
                profile=profile,
                days_per_event=config.days_per_event,
                rng=rng,
            )
            total_bouts += len(pairs)
            total_bridge_bouts += bridge_bouts
            for player_a, player_b in pairs:
                probability_a = expected_score(
                    skills[player_a],
                    skills[player_b],
                    q=config.q,
                )
                winner = (
                    player_a
                    if rng.random() < probability_a
                    else player_b
                )
                update_ratings(
                    ratings,
                    player_a,
                    player_b,
                    winner=winner,
                    k=model.k,
                    q=config.q,
                )
        final_ratings.append(tuple(ratings))
        progress.report(run + 1)
    return _SimulationResult(
        final_ratings=tuple(final_ratings),
        total_bouts=total_bouts,
        total_bridge_bouts=total_bridge_bouts,
    )


def _summarize_scenario(
    *,
    name: str,
    simulation: _SimulationResult,
    skills: Sequence[float],
    groups: Sequence[BoundaryGroup],
    config: ExperimentConfig,
    bootstrap_seed: int,
) -> ScenarioResult:
    run_group_ratings = [
        [
            mean(ratings[player] for player in group.players)
            for group in groups
        ]
        for ratings in simulation.final_ratings
    ]
    group_means = [
        mean(run_values[position] for run_values in run_group_ratings)
        for position in range(len(groups))
    ]
    group_standard_deviations = [
        (
            stdev(
                run_values[position]
                for run_values in run_group_ratings
            )
            if config.runs >= 2
            else 0.0
        )
        for position in range(len(groups))
    ]
    group_standard_errors = [
        value / math.sqrt(config.runs)
        for value in group_standard_deviations
    ]
    isotonic_weights = [
        1.0 / (value * value) if value > 0.0 else 1.0
        for value in group_standard_errors
    ]
    isotonic_fit = fit_non_increasing(group_means, isotonic_weights)
    group_results = []
    for position, group in enumerate(groups):
        standard_error = group_standard_errors[position]
        margin = 1.96 * standard_error
        group_results.append(
            GroupResult(
                position=group.position,
                boundary_distance=group.boundary_distance,
                label=group.label,
                players=group.players,
                hidden_skill_mean=mean(
                    skills[player] for player in group.players
                ),
                rating_mean=group_means[position],
                rating_standard_deviation=(
                    group_standard_deviations[position]
                ),
                rating_standard_error=standard_error,
                approximate_ci95_lower=(
                    group_means[position] - margin
                ),
                approximate_ci95_upper=(
                    group_means[position] + margin
                ),
                isotonic_fitted_mean=isotonic_fit[position],
                isotonic_residual=(
                    group_means[position] - isotonic_fit[position]
                ),
            )
        )

    endpoint_target = config.scaled_endpoint_target
    maximum_target = config.scaled_maximum_target
    reversals = []
    for run, values in enumerate(run_group_ratings):
        endpoint = values[-1] - values[0]
        maximum = maximum_reversal(values)
        monotonic = is_non_increasing(values)
        reversals.append(
            RunReversal(
                run=run,
                endpoint_reversal=endpoint,
                maximum_reversal=maximum,
                monotonic=monotonic,
                endpoint_reaches_target=endpoint >= endpoint_target,
                maximum_reaches_target=maximum >= maximum_target,
            )
        )

    endpoint_reversal = group_means[-1] - group_means[0]
    maximum = maximum_reversal(group_means)
    endpoint_interval, maximum_interval = _bootstrap_intervals(
        run_group_ratings=run_group_ratings,
        samples=config.bootstrap_samples,
        seed=bootstrap_seed,
    )
    denominator = config.runs * config.events
    summary = ScenarioSummary(
        scenario=name,
        total_bouts=simulation.total_bouts,
        mean_bouts_per_run_event=simulation.total_bouts / denominator,
        mean_bridge_bouts_per_run_event=(
            simulation.total_bridge_bouts / denominator
        ),
        ensemble_endpoint_reversal=endpoint_reversal,
        endpoint_ci95_lower=endpoint_interval[0],
        endpoint_ci95_upper=endpoint_interval[1],
        ensemble_maximum_reversal=maximum,
        maximum_ci95_lower=maximum_interval[0],
        maximum_ci95_upper=maximum_interval[1],
        ensemble_rating_is_monotonic=is_non_increasing(group_means),
        individual_monotonic_rate=mean(
            1.0 if item.monotonic else 0.0 for item in reversals
        ),
        endpoint_reversal_rate=mean(
            1.0 if item.endpoint_reversal > 0.0 else 0.0
            for item in reversals
        ),
        maximum_reversal_rate=mean(
            1.0 if item.maximum_reversal > 0.0 else 0.0
            for item in reversals
        ),
        endpoint_target_rate=mean(
            1.0 if item.endpoint_reaches_target else 0.0
            for item in reversals
        ),
        maximum_target_rate=mean(
            1.0 if item.maximum_reaches_target else 0.0
            for item in reversals
        ),
        scaled_endpoint_target=endpoint_target,
        scaled_maximum_target=maximum_target,
    )
    return ScenarioResult(
        summary=summary,
        groups=tuple(group_results),
        run_reversals=tuple(reversals),
    )


def fit_non_increasing(
    values: Sequence[float],
    weights: Sequence[float],
) -> tuple[float, ...]:
    """Return a weighted least-squares non-increasing isotonic fit."""
    if len(values) != len(weights):
        raise ValueError("values and weights must have equal lengths")
    blocks: list[list[float | int]] = []
    for position, (value, weight) in enumerate(zip(values, weights)):
        if weight <= 0.0:
            raise ValueError("weights must be positive")
        blocks.append([position, position, weight, weight * value])
        while len(blocks) >= 2:
            previous = blocks[-2]
            current = blocks[-1]
            previous_mean = float(previous[3]) / float(previous[2])
            current_mean = float(current[3]) / float(current[2])
            if previous_mean >= current_mean:
                break
            blocks[-2:] = [
                [
                    int(previous[0]),
                    int(current[1]),
                    float(previous[2]) + float(current[2]),
                    float(previous[3]) + float(current[3]),
                ]
            ]
    fitted = [0.0 for _ in values]
    for start, end, weight, weighted_sum in blocks:
        value = float(weighted_sum) / float(weight)
        for position in range(int(start), int(end) + 1):
            fitted[position] = value
    return tuple(fitted)


def is_non_increasing(values: Sequence[float]) -> bool:
    return all(
        earlier >= later
        for earlier, later in zip(values, values[1:])
    )


def maximum_reversal(values: Sequence[float]) -> float:
    """Return the largest later-minus-earlier increase, or zero."""
    if len(values) < 2:
        return 0.0
    lowest_earlier = values[0]
    result = 0.0
    for value in values[1:]:
        result = max(result, value - lowest_earlier)
        lowest_earlier = min(lowest_earlier, value)
    return result


def _bootstrap_intervals(
    *,
    run_group_ratings: Sequence[Sequence[float]],
    samples: int,
    seed: int,
) -> tuple[tuple[float, float], tuple[float, float]]:
    generator = random.Random(seed)
    run_count = len(run_group_ratings)
    group_count = len(run_group_ratings[0])
    endpoint_values = []
    maximum_values = []
    for _ in range(samples):
        selected = [
            run_group_ratings[generator.randrange(run_count)]
            for _run in range(run_count)
        ]
        group_means = [
            mean(row[position] for row in selected)
            for position in range(group_count)
        ]
        endpoint_values.append(group_means[-1] - group_means[0])
        maximum_values.append(maximum_reversal(group_means))
    return (
        (
            _percentile(endpoint_values, 0.025),
            _percentile(endpoint_values, 0.975),
        ),
        (
            _percentile(maximum_values, 0.025),
            _percentile(maximum_values, 0.975),
        ),
    )


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return (
        ordered[lower] * (1.0 - fraction)
        + ordered[upper] * fraction
    )


def _write_scenario_summary(
    path: Path,
    scenarios: Sequence[ScenarioResult],
) -> None:
    fields = list(asdict(scenarios[0].summary))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for scenario in scenarios:
            writer.writerow(asdict(scenario.summary))


def _write_boundary_groups(
    path: Path,
    scenarios: Sequence[ScenarioResult],
) -> None:
    fields = [
        "scenario",
        "position",
        "boundary_distance",
        "label",
        "players",
        "hidden_skill_mean",
        "rating_mean",
        "rating_standard_deviation",
        "rating_standard_error",
        "approximate_ci95_lower",
        "approximate_ci95_upper",
        "isotonic_fitted_mean",
        "isotonic_residual",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for scenario in scenarios:
            for group in scenario.groups:
                row = asdict(group)
                row["scenario"] = scenario.summary.scenario
                row["players"] = " ".join(
                    str(player) for player in group.players
                )
                writer.writerow(row)


def _write_run_reversals(
    path: Path,
    scenarios: Sequence[ScenarioResult],
) -> None:
    fields = [
        "scenario",
        "run",
        "endpoint_reversal",
        "maximum_reversal",
        "monotonic",
        "endpoint_reaches_target",
        "maximum_reaches_target",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for scenario in scenarios:
            for reversal in scenario.run_reversals:
                writer.writerow(
                    {
                        "scenario": scenario.summary.scenario,
                        **asdict(reversal),
                    }
                )


def _create_run_directory(root: Path) -> tuple[datetime, Path]:
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    while True:
        run_directory = root / timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        try:
            run_directory.mkdir()
        except FileExistsError:
            timestamp += timedelta(seconds=1)
            continue
        return timestamp, run_directory
