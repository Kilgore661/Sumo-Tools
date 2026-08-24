"""Extract one eight-number descriptive results row per toy Elo model."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence


DEFAULT_INPUT_ROOT = Path("files/output/analysis/forgetting/toy")
DEFAULT_OUTPUT = DEFAULT_INPUT_ROOT / "results_table" / "results_seed1.csv"
DEFAULT_PROTOCOLS = ((800, 500), (3200, 2000))


@dataclass(frozen=True)
class ExtractionContract:
    event_tail: int = 100
    event_persistence: int = 25
    event_relative_tolerance: float = 0.05


@dataclass(frozen=True)
class ModelResultsRow:
    model: str
    replicates: int
    events: int
    trmse_level: float
    trmse_settling_event: int | None
    trmse_spread_q05_q95: float
    prmse_level: float
    prmse_settling_event: int | None
    prmse_spread_q05_q95: float
    cancel_level: float
    cancel_replicates: int | None


@dataclass(frozen=True)
class ModelRun:
    model: str
    directory: Path
    manifest: Mapping[str, object]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _validate_contract(contract: ExtractionContract) -> None:
    integer_values = (
        contract.event_tail,
        contract.event_persistence,
    )
    if any(value < 1 for value in integer_values):
        raise ValueError("tail and persistence lengths must be positive")
    tolerance_values = (contract.event_relative_tolerance,)
    if any(not math.isfinite(value) or value < 0 for value in tolerance_values):
        raise ValueError("relative tolerances must be finite and non-negative")


def _model_from_manifest(manifest: Mapping[str, object]) -> str | None:
    experiment = str(manifest.get("experiment", "")).lower()
    if "true-start ensemble" in experiment:
        return "T0"

    initializations = manifest.get("initializations")
    if not isinstance(initializations, Mapping):
        return None
    keys = {str(key) for key in initializations}
    if "T_prime" in keys:
        return "TC"
    comparison_keys = sorted(keys - {"T", "T0", "true"})
    if len(comparison_keys) == 1:
        return comparison_keys[0]
    return None


def discover_model_runs(
    *,
    input_root: Path,
    runs: int,
    events: int,
    seed: int,
) -> tuple[ModelRun, ...]:
    """Find the latest matching run for each named model."""
    candidates: dict[str, list[ModelRun]] = {}
    for manifest_path in input_root.rglob("manifest.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ensemble = manifest.get("ensemble")
        if not isinstance(ensemble, Mapping):
            continue
        if (
            ensemble.get("replicate_count") != runs
            or ensemble.get("events_per_replicate") != events
            or ensemble.get("master_seed") != seed
        ):
            continue
        model = _model_from_manifest(manifest)
        if model is None:
            continue
        run = ModelRun(model=model, directory=manifest_path.parent, manifest=manifest)
        candidates.setdefault(model, []).append(run)

    selected = []
    for model, model_candidates in candidates.items():
        selected.append(
            max(
                model_candidates,
                key=lambda run: (
                    str(run.manifest.get("finished_at", "")),
                    str(run.directory),
                ),
            )
        )
    return tuple(sorted(selected, key=lambda run: _model_sort_key(run.model)))


def _model_sort_key(model: str) -> tuple[int, int | str]:
    fixed = {"T0": 0, "TC": 1, "TI": 2}
    if model in fixed:
        return (0, fixed[model])
    if model.startswith("TR") and model[2:].isdigit():
        return (1, int(model[2:]))
    return (2, model)


def _first_persistent_coordinate(
    *,
    rows: Sequence[Mapping[str, str]],
    coordinate_name: str,
    value_names: Sequence[str],
    targets: Sequence[float],
    relative_tolerance: float,
    persistence: int,
) -> int | None:
    if len(rows) < persistence:
        return None
    for start in range(len(rows) - persistence + 1):
        window = rows[start : start + persistence]
        if all(
            all(
                abs(float(row[name]) - target)
                <= relative_tolerance * abs(target)
                for name, target in zip(value_names, targets)
            )
            for row in window
        ):
            return int(rows[start][coordinate_name])
    return None


def _event_triplet(
    *,
    rows: Sequence[Mapping[str, str]],
    mean_name: str,
    q05_name: str,
    q95_name: str,
    contract: ExtractionContract,
) -> tuple[float, int | None, float]:
    if len(rows) < contract.event_tail:
        raise ValueError(
            f"event series has {len(rows)} rows but tail requires "
            f"{contract.event_tail}"
        )
    tail = rows[-contract.event_tail :]
    level = statistics.median(float(row[mean_name]) for row in tail)
    widths = [float(row[q95_name]) - float(row[q05_name]) for row in rows]
    spread = statistics.median(widths[-contract.event_tail :])
    augmented = [dict(row, __band_width=str(width)) for row, width in zip(rows, widths)]
    settling_event = _first_persistent_coordinate(
        rows=augmented,
        coordinate_name="event",
        value_names=(mean_name, "__band_width"),
        targets=(level, spread),
        relative_tolerance=contract.event_relative_tolerance,
        persistence=contract.event_persistence,
    )
    return level, settling_event, spread


def _cancellation_pair(
    *,
    rows: Sequence[Mapping[str, str]],
) -> tuple[float, int | None]:
    if not rows:
        raise ValueError("cancellation series is empty")
    final = rows[-1]
    return (
        float(final["mean_rating_error_rmse"]),
        int(final["replicate_count"]),
    )


def extract_model_results(
    run: ModelRun,
    *,
    contract: ExtractionContract,
) -> ModelResultsRow:
    _validate_contract(contract)
    event_rows = _read_csv(run.directory / "event_summary.csv")
    if not event_rows:
        raise ValueError(f"empty event summary in {run.directory}")

    if "state_mean" in event_rows[0]:
        state_names = ("state_mean", "state_q05", "state_q95")
        probability_names = (
            "probability_mean",
            "probability_q05",
            "probability_q95",
        )
    else:
        state_names = (
            "t_prime_state_mean",
            "t_prime_state_q05",
            "t_prime_state_q95",
        )
        probability_names = (
            "t_prime_probability_mean",
            "t_prime_probability_q05",
            "t_prime_probability_q95",
        )

    trmse = _event_triplet(
        rows=event_rows,
        mean_name=state_names[0],
        q05_name=state_names[1],
        q95_name=state_names[2],
        contract=contract,
    )
    prmse = _event_triplet(
        rows=event_rows,
        mean_name=probability_names[0],
        q05_name=probability_names[1],
        q95_name=probability_names[2],
        contract=contract,
    )

    outputs = run.manifest.get("outputs")
    if not isinstance(outputs, Mapping):
        raise ValueError(f"manifest has no outputs mapping in {run.directory}")
    progress_files = [
        str(value)
        for key, value in outputs.items()
        if str(key).endswith("final_mean_error_progress")
    ]
    if len(progress_files) != 1:
        raise ValueError(
            f"expected one final mean-error progress file in {run.directory}"
        )
    cancel = _cancellation_pair(
        rows=_read_csv(run.directory / progress_files[0]),
    )
    ensemble = run.manifest.get("ensemble")
    if not isinstance(ensemble, Mapping):
        raise ValueError(f"manifest has no ensemble mapping in {run.directory}")
    return ModelResultsRow(
        model=run.model,
        replicates=int(ensemble["replicate_count"]),
        events=int(ensemble["events_per_replicate"]),
        trmse_level=trmse[0],
        trmse_settling_event=trmse[1],
        trmse_spread_q05_q95=trmse[2],
        prmse_level=prmse[0],
        prmse_settling_event=prmse[1],
        prmse_spread_q05_q95=prmse[2],
        cancel_level=cancel[0],
        cancel_replicates=cancel[1],
    )


def write_results_table(path: Path, rows: Sequence[ModelResultsRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ModelResultsRow.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def build_results_table(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    output: Path = DEFAULT_OUTPUT,
    protocols: Sequence[tuple[int, int]] = DEFAULT_PROTOCOLS,
    seed: int = 1,
    contract: ExtractionContract = ExtractionContract(),
) -> tuple[ModelResultsRow, ...]:
    model_runs_by_directory: dict[Path, ModelRun] = {}
    for runs, events in protocols:
        for run in discover_model_runs(
            input_root=input_root,
            runs=runs,
            events=events,
            seed=seed,
        ):
            model_runs_by_directory[run.directory] = run
    model_runs = tuple(
        sorted(
            model_runs_by_directory.values(),
            key=lambda run: (
                _model_sort_key(run.model),
                int(run.manifest["ensemble"]["replicate_count"]),
                int(run.manifest["ensemble"]["events_per_replicate"]),
            ),
        )
    )
    if not model_runs:
        raise FileNotFoundError(
            f"no requested seed-{seed} model runs found beneath {input_root}"
        )
    rows = tuple(
        extract_model_results(run, contract=contract) for run in model_runs
    )
    write_results_table(output, rows)
    for run, row in zip(model_runs, rows):
        print(f"{run.model} [{row.replicates}x{row.events}]: {run.directory}")
    print(f"Wrote {len(rows)} model rows to {output.resolve()}")
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the toy Elo model-results comparison CSV."
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--protocol",
        action="append",
        metavar="REPLICATESxEVENTS",
        help="protocol to include; repeat as needed (default: 800x500 and 3200x2000)",
    )
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--event-tail", type=int, default=100)
    parser.add_argument("--event-persistence", type=int, default=25)
    parser.add_argument("--event-relative-tolerance", type=float, default=0.05)
    return parser


def _parse_protocol(value: str) -> tuple[int, int]:
    try:
        runs_text, events_text = value.lower().split("x", maxsplit=1)
        runs, events = int(runs_text), int(events_text)
    except ValueError as error:
        raise ValueError(
            f"invalid protocol {value!r}; expected REPLICATESxEVENTS"
        ) from error
    if runs < 1 or events < 1:
        raise ValueError("protocol values must be positive")
    return runs, events


def main() -> None:
    args = build_parser().parse_args()
    protocols = (
        tuple(_parse_protocol(value) for value in args.protocol)
        if args.protocol
        else DEFAULT_PROTOCOLS
    )
    build_results_table(
        input_root=args.input_root,
        output=args.output,
        protocols=protocols,
        seed=args.seed,
        contract=ExtractionContract(
            event_tail=args.event_tail,
            event_persistence=args.event_persistence,
            event_relative_tolerance=args.event_relative_tolerance,
        ),
    )


if __name__ == "__main__":
    main()
