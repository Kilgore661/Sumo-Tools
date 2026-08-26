"""Fixed BKP1 model parameters, independent of legacy Equelo defaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable


MODEL_Q = 400.0
MODEL_BASE = 1517.0
DEFAULT_K_CONFIG = Path("files/input/elo_fide.json")
KFn = Callable[[int], float]


def expected_score(rating_a: float, rating_b: float) -> float:
    """Return the BKP1 expected score on its fixed q=400 scale."""

    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / MODEL_Q))


def load_divisional_k(path: Path = DEFAULT_K_CONFIG) -> KFn:
    """Load the declared divisional-k policy without importing legacy q defaults."""

    with path.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    maximum = float(config["max"])
    limits = {int(key): float(value) for key, value in config.get("lims", {}).items()}
    by_division: dict[int, float] = {}
    last_upper = -1
    for upper, value in sorted(limits.items()):
        for division in range(last_upper + 1, upper + 1):
            by_division[division] = value
        last_upper = upper
    for division in range(last_upper + 1, 10):
        by_division[division] = maximum

    def k(ordinal: int) -> float:
        return by_division[ordinal // 100000]

    return k
