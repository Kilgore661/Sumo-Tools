"""Declared configuration for the accepted Elo-89 prior."""

from __future__ import annotations

from pathlib import Path

from src.sumo_core.History import Date


DEFAULT_LAST_PRIOR_BASHO = Date.from_ints(2026, 9)
ACCEPTED_PRIOR_RUN = 1
PRIOR_OUTPUT_ROOT = Path("files/output/analysis/elo89/prior")
PRIOR_FILENAME = "prior.csv"
ACCEPTED_PRIOR_PATH = Path(
    "src/analysis/equelo_prior_aggregation/results/priors.csv"
)


def prior_boundary_directory(
    last_prior_basho: Date,
    *,
    output_root: Path = PRIOR_OUTPUT_ROOT,
) -> Path:
    """Return the output directory for one inclusive prior boundary."""

    return output_root / f"{int(last_prior_basho.year):04d}-{int(last_prior_basho.month):02d}"


def prior_run_directory(
    last_prior_basho: Date,
    run: int,
    *,
    output_root: Path = PRIOR_OUTPUT_ROOT,
) -> Path:
    """Return the immutable directory assigned to one numbered run."""

    if run < 1:
        raise ValueError("Prior run number must be positive")
    return prior_boundary_directory(last_prior_basho, output_root=output_root) / f"run-{run:03d}"


ACCEPTED_LITERAL_PRIOR_PATH = (
    prior_run_directory(DEFAULT_LAST_PRIOR_BASHO, ACCEPTED_PRIOR_RUN)
    / PRIOR_FILENAME
)
