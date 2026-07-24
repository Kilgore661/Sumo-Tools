"""Default model and output configuration for clean Elo."""

from pathlib import Path

from src.analysis.equelo.config_main import INITIAL_ELO, INITIAL_Q


DEFAULT_ELO = float(INITIAL_ELO)
DEFAULT_Q = float(INITIAL_Q)
DEFAULT_FIDE_K_CONFIG_PATH = Path("files/input/elo_fide.json")
DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/clean_elo")
