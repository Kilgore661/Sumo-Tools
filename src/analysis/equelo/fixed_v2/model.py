"""Model constants for the fixed_v2 Equelo rating series."""

from __future__ import annotations

from pathlib import Path

from src.analysis.equelo.expt1.params import DEFAULT_K_CONFIG_PATH


MODEL_VERSION = "fixed_v2"
SOURCE_HISTORY_START = "1958/01"
HISTORY_CLEANING = "Expt1 Oracle"
SIMULATOR = "src.analysis.equelo.expt1.simulate.simulate"
MODE = "closed"
ENTRANT_POLICY = "raw_fixed_point"
FIXED_POINT_SOURCE = Path("files/output/Equelo/expt2_combined_final.csv")
FP_SOURCE = FIXED_POINT_SOURCE
Q = 900.0
K_POLICY = "divisional"
K_CONFIG = DEFAULT_K_CONFIG_PATH
COLLAPSE_MODE = "annotation-only"

OUTPUT_ROOT = Path("files/output/Equelo/fixed_v2")
METADATA_FILE_NAME = "metadata.json"
DAY_END_RATINGS_FILE_NAME = "day_end_ratings.json"
ENTRANT_INITIAL_RATINGS_FILE_NAME = "entrant_initial_ratings.json"
COMPARISON_CSV_FILE_NAME = "fp_brier_sanitised_comparison.csv"
SANITISATION_REPORT_FILE_NAME = "fp_sanitisation_report.txt"

# Retained only for the diagnostic comparison artefact that reconstructs the
# legacy fixed_v1 Brier-compressed entrant ratings beside the fixed_v2 FP source.
BRIER_ALPHA = 0.55


def model_metadata() -> dict[str, object]:
    """Return the fixed_v2 model metadata payload."""

    return {
        "source_history_start": SOURCE_HISTORY_START,
        "history_cleaning": HISTORY_CLEANING,
        "simulator": SIMULATOR,
        "mode": MODE,
        "entrant_policy": ENTRANT_POLICY,
        "fixed_point_source": str(FIXED_POINT_SOURCE),
        "q": Q,
        "k_policy": K_POLICY,
        "k_config": str(K_CONFIG),
        "collapse_mode": COLLAPSE_MODE,
    }
