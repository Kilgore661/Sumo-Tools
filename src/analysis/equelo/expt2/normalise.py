from __future__ import annotations

from .types import ChiiRatings, NormalisationResult


def normalise(mu: ChiiRatings, base: float) -> NormalisationResult:
    """Apply a uniform additive shift so that the unweighted mean equals ``base``."""
    if not mu:
        return NormalisationResult(mu={}, shift=0.0)

    current_mean = sum(mu.values()) / len(mu)
    shift = float(base) - current_mean
    shifted = {chii: rating + shift for chii, rating in mu.items()}
    return NormalisationResult(mu=shifted, shift=shift)
