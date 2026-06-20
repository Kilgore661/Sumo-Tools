"""Build fixed-supported public landmark artifacts."""

from __future__ import annotations

from pathlib import Path

from src.analysis.equelo.fixed_v2.v5_landmarks import (
    V5LandmarkOutputs,
    write_typical_equelo_outputs,
)

from .api import master_chii_initial_rating_map_path
from .model import LANDMARKS_OUTPUT_DIR, OUTPUT_ROOT


def build_typical_equelo_values(
    *,
    output_dir: Path = LANDMARKS_OUTPUT_DIR,
    master_map_path: Path | None = None,
) -> V5LandmarkOutputs:
    """Build Typical Equelo Values from the fixed-supported master map."""

    source = (
        master_chii_initial_rating_map_path(OUTPUT_ROOT)
        if master_map_path is None
        else master_map_path
    )
    return write_typical_equelo_outputs(
        output_dir=output_dir,
        fp_source=source,
    )

