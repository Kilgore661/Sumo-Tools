from __future__ import annotations

from pathlib import Path


DEFAULT_OUTPUT_ROOT = Path("files/output/toy_elo_matchup")
DEFAULT_START = "1989/01"

ADJACENT_BOUNDARIES = (
    ("M", "J"),
    ("J", "Ms"),
    ("Ms", "Sd"),
    ("Sd", "Jd"),
    ("Jd", "Jk"),
)

