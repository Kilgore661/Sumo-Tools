"""Build fixed-supported process artifacts from an existing master map."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.equelo.fixed_v2.build import compute_fixed_v2
from src.analysis.equelo.fixed_v2.output import write_outputs
from src.infra.live_store.api import get_history
from src.sumo_core.History import History

from .api import master_chii_initial_rating_map_path
from .model import OUTPUT_ROOT, policy_metadata


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
    result, cleaned_history, entrant_initial_ratings = compute_fixed_v2(
        get_history() if raw_history is None else raw_history,
        entrant_initial_ratings_source=source,
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
