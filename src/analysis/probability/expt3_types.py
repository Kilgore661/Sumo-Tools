from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoutForecast:
    date: str
    day: int
    rikishi1: int
    rikishi2: int
    r1_before: float
    r2_before: float
    delta: float
    predicted: float
    outcome: int


@dataclass(frozen=True)
class DeltaCalibrationRow:
    delta_bin_lo: float
    delta_bin_hi: float
    n_obs: int
    n_wins_r1: int
    n_losses_r1: int
    mean_delta: float
    mean_predicted: float
    observed_win_rate: float
    signed_error: float
    abs_error: float
    sq_error: float


@dataclass(frozen=True)
class ProbabilityRegion:
    p_lo: float
    p_hi: float
    n_bins: int
    n_obs: int
    max_abs_error: float | None = None


@dataclass(frozen=True)
class Expt3BottomLine:
    support_regions_inadequate: list[ProbabilityRegion]
    support_regions_adequate: list[ProbabilityRegion]
    central_low_error_region: ProbabilityRegion | None
    central_low_error_delta_lo: float | None
    central_low_error_delta_hi: float | None
    warnings: list[str]
