"""Canonical q=400, support-proportional fixed-point prior producer for BKP1."""

from .params import MODEL_BASE, MODEL_Q
from .solve import FixedPointResult, solve

__all__ = ["FixedPointResult", "MODEL_BASE", "MODEL_Q", "solve"]
