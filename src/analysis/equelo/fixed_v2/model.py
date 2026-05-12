"""Configuration constants for the fixed_v2 Brierless Pivot experiment."""

from __future__ import annotations

from pathlib import Path

from src.analysis.equelo.fixed_v1.model import ALPHA, FIXED_POINT_SOURCE


MODEL_VERSION = "fixed_v2_experiment"
OUTPUT_ROOT = Path("files/output/Equelo/fixed_v2")
COMPARISON_CSV_FILE_NAME = "fp_brier_sanitised_comparison.csv"

# The first fixed_v2 experiment uses the same Expt2 fixed-point source as
# fixed_v1, but treats that source as the primary input rather than immediately
# applying the fixed_v1 Brier compression.
FP_SOURCE = FIXED_POINT_SOURCE
BRIER_ALPHA = ALPHA
