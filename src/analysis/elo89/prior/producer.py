"""Produce a bounded, immutable P1-WL prior run."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from time import perf_counter
from typing import Callable

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo_bkp1.model import FixedPointResult, IterationRow
from src.analysis.equelo_bkp1.params import (
    DEFAULT_K_CONFIG,
    MODEL_BASE,
    MODEL_Q,
    load_divisional_k,
)
from src.analysis.equelo_bkp1.simulate import BoutEligibility, count_eligibility
from src.analysis.equelo_bkp1.solve import solve
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from ..config import (
    DEFAULT_LAST_PRIOR_BASHO,
    PRIOR_FILENAME,
    PRIOR_OUTPUT_ROOT,
    prior_boundary_directory,
)


ELO89_START = Date.from_ints(1989, 1)
EPSILON = 10.0
MAX_ITERATIONS = 200


@dataclass(frozen=True, slots=True)
class PriorRun:
    root: Path
    prior: Path
    iterations: Path
    manifest: Path
    result: FixedPointResult
    runtime_seconds: float


def produce_prior(
    history: History,
    *,
    last_prior_basho: Date = DEFAULT_LAST_PRIOR_BASHO,
    output_root: Path = PRIOR_OUTPUT_ROOT,
    history_source: str = "provided History",
    progress: Callable[[IterationRow], None] | None = None,
) -> PriorRun:
    """Fit P1-WL through and including ``last_prior_basho``.

    Output is written to the next unused ``run-NNN`` directory beneath the
    boundary directory. Existing runs are never overwritten.
    """

    started = perf_counter()
    selected = select_prior_history(history, last_prior_basho=last_prior_basho)
    counts = count_eligibility(selected, BoutEligibility.P1_WL)
    result = solve(
        selected,
        load_divisional_k(DEFAULT_K_CONFIG),
        epsilon=EPSILON,
        max_iterations=MAX_ITERATIONS,
        progress=progress,
        eligibility=BoutEligibility.P1_WL,
    )
    runtime_seconds = perf_counter() - started
    root = _allocate_run_directory(last_prior_basho, output_root=output_root)
    prior_path = root / PRIOR_FILENAME
    iterations_path = root / "iterations.csv"
    manifest_path = root / "manifest.json"

    _write_csv(
        prior_path,
        (
            {
                "chii": str(chii),
                "ordinal": chii.ordinal(),
                "support": result.support[chii],
                "rating": result.priors[chii],
            }
            for chii in sorted(result.priors, key=Chii.ordinal)
        ),
    )
    _write_csv(iterations_path, (asdict(row) for row in result.iteration_rows))
    dates = sorted(selected)
    manifest = {
        "schema_version": 1,
        "artifact": "Elo-89 P1-WL prior",
        "history": {
            "source": history_source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "last_prior_basho_inclusive": str(last_prior_basho),
            "basho_count": len(dates),
        },
        "bout_eligibility": {
            "policy": BoutEligibility.P1_WL.value,
            **asdict(counts),
        },
        "model": {
            "q": MODEL_Q,
            "base": MODEL_BASE,
            "epsilon": EPSILON,
            "max_iterations": MAX_ITERATIONS,
            "k_config": str(DEFAULT_K_CONFIG),
            "history_preprocessing": "oracle annotation_only",
            "fit_rating_lifecycle": "legacy departure handling",
        },
        "convergence": {
            "converged": result.converged,
            "iterations_taken": result.iterations,
            "final_maximum_change": result.final_delta,
        },
        "runtime_seconds": runtime_seconds,
        "files": {
            "prior": PRIOR_FILENAME,
            "iterations": "iterations.csv",
            "manifest": "manifest.json",
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return PriorRun(
        root=root,
        prior=prior_path,
        iterations=iterations_path,
        manifest=manifest_path,
        result=result,
        runtime_seconds=runtime_seconds,
    )


def select_prior_history(
    history: History,
    *,
    last_prior_basho: Date,
) -> History:
    """Return canonical Elo-89 history through the inclusive boundary."""

    if ELO89_START not in history:
        raise ValueError("Prior History must contain the 1989/01 basho")
    if last_prior_basho not in history:
        raise ValueError(
            "--last-prior-basho names a basho absent from History: "
            f"{last_prior_basho}"
        )
    if last_prior_basho < ELO89_START:
        raise ValueError("--last-prior-basho cannot precede 1989/01")
    bounded = History(
        {
            date: history[date]
            for date in sorted(history)
            if ELO89_START <= date <= last_prior_basho
        }
    )
    return make_oracle(bounded, collapse_mode="annotation_only").history


def _allocate_run_directory(last_prior_basho: Date, *, output_root: Path) -> Path:
    boundary = prior_boundary_directory(last_prior_basho, output_root=output_root)
    boundary.mkdir(parents=True, exist_ok=True)
    run = 1
    while True:
        candidate = boundary / f"run-{run:03d}"
        try:
            candidate.mkdir()
        except FileExistsError:
            run += 1
            continue
        return candidate


def _write_csv(path: Path, rows) -> None:
    iterator = iter(rows)
    try:
        first = next(iterator)
    except StopIteration as error:
        raise ValueError(f"Refusing to write empty CSV: {path}") from error
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)
