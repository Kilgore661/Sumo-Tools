# The first two numbers should be written to manifest.json (resolved k=policy too). 
INITIAL_ELO = 2000.0 # Was 1500 but after scaling yoks had a rating of 2000
INITIAL_Q = 900 # Was 850.0 # ~1430.333 +/- 0.333 was optimal
CONSTANT_K = 35.0

from pathlib import Path

"""File-system paths used by Expt1 orchestration and diagnostics."""

BIOS_PATH = Path("files/input/bios.json")
OUTPUT_ROOT = Path("files/output/Equelo")
EQUELO_RATINGS = OUTPUT_ROOT / "equelo.csv"

