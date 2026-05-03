"""Build the fixed v1 Equelo rating artefacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from src.analysis.equelo.config_main import BIOS_PATH
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, SimulationResult, simulate
from src.analysis.probability.builder import load_ratings_csv
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .model import (
    ALPHA,
    COLLAPSE_MODE,
    FIXED_POINT_SOURCE,
    K_CONFIG,
    K_POLICY,
    OUTPUT_ROOT,
    Q,
)
from .output import write_outputs


EntrantInitialiser = Callable[[Chii], float]
ChiiRatings = dict[Chii, float]


def build_fixed_v1(output_root: Path = OUTPUT_ROOT) -> dict[str, Path]:
    """
    Generate and persist the fixed v1 Equelo rating series.

    Contract:
        A live History is available through the project live store.
        The fixed-point source CSV exists and covers chii used by the cleaned
        history entrant boundary.
    """

    raw_history = get_history()
    result, cleaned_history, entrant_initial_ratings = compute_fixed_v1(raw_history)
    return write_outputs(
        history=cleaned_history,
        day_end_ratings=result.day_end_ratings,
        entrant_initial_ratings=entrant_initial_ratings,
        output_root=output_root,
    )


def compute_fixed_v1(raw_history: History) -> tuple[SimulationResult, History, ChiiRatings]:
    """Compute fixed v1 ratings from a supplied raw History."""

    oracle = make_oracle(
        raw_history,
        load_bios(),
        collapse_mode=oracle_collapse_mode(),
    )
    params = build_elo_params(
        k_policy=K_POLICY,
        q=Q,
        config_path=K_CONFIG,
    )
    entrant_initial_ratings = scaled_fixed_point_ratings()
    result = simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=make_chii_initialiser(entrant_initial_ratings),
        mode=SimulationMode.CLOSED,
    )

    return result, oracle.history, entrant_initial_ratings


def load_bios() -> dict[RikId, dict]:
    """Load bios for Oracle construction."""

    with BIOS_PATH.open("r", encoding="utf-8") as f:
        raw_bios = json.load(f)

    return {RikId(int(key)): value for key, value in raw_bios.items()}


def scaled_fixed_point_ratings(
    *,
    source: Path = FIXED_POINT_SOURCE,
    alpha: float = ALPHA,
) -> ChiiRatings:
    """Return the fixed v1 scaled chii-to-entrant-rating map."""

    fixed_ratings = load_ratings_csv(source)
    mu = sum(fixed_ratings.values()) / len(fixed_ratings)
    return {
        chii: mu + alpha * (rating - mu)
        for chii, rating in fixed_ratings.items()
    }


def make_chii_initialiser(ratings: ChiiRatings) -> EntrantInitialiser:
    """Build a chii-based entrant initialiser from an explicit ratings map."""

    def initialise(chii: Chii) -> float:
        return float(ratings[chii])

    return initialise


def scaled_fixed_point_initialiser(
    *,
    source: Path = FIXED_POINT_SOURCE,
    alpha: float = ALPHA,
) -> EntrantInitialiser:
    """Build the fixed v1 chii-based entrant initialiser."""

    return make_chii_initialiser(
        scaled_fixed_point_ratings(source=source, alpha=alpha)
    )


def oracle_collapse_mode() -> str:
    """Return the Oracle collapse mode token for the fixed v1 spec value."""

    if COLLAPSE_MODE == "annotation-only":
        return "annotation_only"

    return COLLAPSE_MODE
