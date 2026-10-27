"""Shared filesystem locations for validation work."""

from pathlib import Path


# Complete generated runs are workspace artifacts, not repository artifacts.
VALIDATION_OUTPUT_ROOT = Path("files/output/validation")
ELO89_OUTPUT_ROOT = VALIDATION_OUTPUT_ROOT / "elo89-expert-account"
ELO89_MATTERS_OUTPUT_ROOT = ELO89_OUTPUT_ROOT / "Matters Arising"
KIMARITE_OUTPUT_ROOT = ELO89_MATTERS_OUTPUT_ROOT / "Kimarite"
