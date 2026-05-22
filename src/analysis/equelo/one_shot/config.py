from pathlib import Path

from ....sumo_core.Chii import Chii

MODERN_START_YEAR = 1989

OUTPUT_ROOT = Path("files/output/Equelo/one_shot")
RUNS_ROOT = OUTPUT_ROOT / "runs"

ALL_HIGH_VALUE = 5000.0

RANDOM_MIN = 1000.0
RANDOM_MAX = 3000.0
RANDOM_RUN_COUNT = 2
DEFAULT_SEED_BASE = 1729

PROBE_CHII_STRS = [
    "Y1e",
    "S1e",
    "M1e",
    "M4e",
    "M8e",
    "M12e",
    "M16e",
]

PROBE_CHII = [Chii.from_str(s) for s in PROBE_CHII_STRS]
