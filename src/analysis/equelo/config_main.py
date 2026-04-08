INITIAL_ELO = 1500.0
INITIAL_Q = 400.0
CONSTANT_K = 35.0

from pathlib import Path

"""File-system paths used by Expt1 orchestration and diagnostics."""

BIOS_PATH = Path("files/input/bios.json")
OUTPUT_ROOT = Path("files/output/Equelo")
EQUELO_RATINGS = OUTPUT_ROOT / "equelo.csv"

