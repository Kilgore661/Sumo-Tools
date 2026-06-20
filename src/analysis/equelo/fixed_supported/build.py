"""Build fixed-supported process artifacts from an existing master map."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from src.analysis.equelo.config_main import BIOS_PATH
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.expt1.params import build_elo_params
from src.analysis.equelo.expt1.simulate import SimulationMode, simulate
from src.infra.live_store.api import get_history
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History

from .api import master_chii_initial_rating_map_path
from .master_map import load_master_chii_initial_rating_map, ratings_by_chii
from .model import COLLAPSE_MODE, K_CONFIG, K_POLICY, OUTPUT_ROOT, Q, policy_metadata
from .output import write_outputs


EntrantInitialiser = Callable[[Chii], float]
ChiiRatings = dict[Chii, float]


def build_process_ratings(
    *,
    output_root: Path = OUTPUT_ROOT,
    master_map_path: Path | None = None,
    raw_history: History | None = None,
) -> dict[str, Path]:
    """Build process/day-end ratings from an existing master chii map."""

    source = (
        master_chii_initial_rating_map_path(output_root)
        if master_map_path is None
        else master_map_path
    )
    result, cleaned_history, entrant_initial_ratings = compute_process_ratings(
        get_history() if raw_history is None else raw_history,
        master_map_path=source,
    )
    outputs = write_outputs(
        history=cleaned_history,
        day_end_ratings=result.day_end_ratings,
        entrant_initial_ratings=entrant_initial_ratings,
        output_root=output_root,
        model_metadata_overrides={
            "entrant_policy": "fixed_supported_master_chii_initial_rating_map",
            "master_chii_initial_rating_map": str(source),
        },
    )
    _annotate_metadata(outputs["metadata"], master_map_path=source)
    return outputs


def _annotate_metadata(path: Path, *, master_map_path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["model_version"] = "fixed_supported"
    payload["model"] = {
        **payload.get("model", {}),
        **policy_metadata(),
        "master_chii_initial_rating_map": str(master_map_path),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def compute_process_ratings(
    raw_history: History,
    *,
    master_map_path: Path,
):
    """Compute fixed-supported process ratings from supplied raw History."""

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
    entrant_initial_ratings = ratings_by_chii(load_master_chii_initial_rating_map(master_map_path))
    result = simulate(
        history=oracle.history,
        params=params,
        entrant_initialiser=make_chii_initialiser(entrant_initial_ratings),
        mode=SimulationMode.CLOSED,
    )
    return result, oracle.history, entrant_initial_ratings


def load_bios() -> dict[RikId, dict]:
    """Load bios for Oracle construction."""

    return {
        RikId(int(key)): value
        for key, value in json.loads(BIOS_PATH.read_text(encoding="utf-8")).items()
    }


def make_chii_initialiser(ratings: ChiiRatings) -> EntrantInitialiser:
    """Build a chii-based entrant initialiser from an explicit ratings map."""

    def initialise(chii: Chii) -> float:
        return float(ratings[chii])

    return initialise


def oracle_collapse_mode() -> str:
    """Return the Oracle collapse mode token for the fixed-supported spec."""

    if COLLAPSE_MODE == "annotation-only":
        return "annotation_only"
    return COLLAPSE_MODE
