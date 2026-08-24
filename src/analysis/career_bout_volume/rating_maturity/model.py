"""Immutable records for the rating-maturity investigation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProbeDefinition:
    start_basho: str
    end_basho: str
    q: float = 400.0
    constant_k: float = 35.0
    constant_initial_rating: float = 1500.0
    support_thresholds: tuple[int, ...] = (15, 30, 60, 120, 180, 200, 240)
    maturity_thresholds: tuple[int, ...] = (0, 30, 60, 120, 180)
    normalized_bin_width: float = 0.05
    minimum_chii_observations: int = 30
    practical_probability_tolerances: tuple[float, ...] = (0.005, 0.01, 0.02, 0.05)


@dataclass(frozen=True, slots=True)
class MaturityRow:
    rikishi_id: int
    shikona: str
    basho: str
    cohort: str
    first_observed_basho: str
    elapsed_represented_basho: int
    chii: str
    chii_ordinal: int
    division: str
    literal_jd100_group: str
    banzuke_size: int
    position_from_top: int
    position_from_bottom: int
    normalized_position: float
    inherited_position_band: str
    uniform_position_band: str
    prior_rated_bouts: int
    prior_fought_bouts: int
    model_state_available: bool
    model_state_exclusion: str
    rating_bk: float | None
    rating_bkp: float | None
    centered_rating_bk: float | None
    centered_rating_bkp: float | None
    absolute_centered_rating_disagreement: float | None


@dataclass(frozen=True, slots=True)
class BoutDisagreementRow:
    basho: str
    day: int
    rikishi_a: int
    rikishi_b: int
    cohort_a: str
    cohort_b: str
    chii_a: str
    chii_b: str
    normalized_position_a: float
    normalized_position_b: float
    position_band_a: str
    position_band_b: str
    prior_rated_bouts_a: int
    prior_rated_bouts_b: int
    probability_a_bk: float
    probability_a_bkp: float
    absolute_probability_disagreement: float
    a_won: bool


@dataclass(frozen=True, slots=True)
class SupportSummaryRow:
    population: str
    band_scheme: str
    position_band: str
    position_low: float
    position_high: float
    observation_count: int
    distinct_rikishi_count: int
    prior_rated_min: int
    prior_rated_q25: float
    prior_rated_median: float
    prior_rated_q75: float
    prior_rated_q90: float
    prior_rated_q95: float
    prior_rated_max: int
    proportion_below_15: float
    proportion_below_30: float
    proportion_below_60: float
    proportion_below_120: float
    proportion_below_180: float
    proportion_below_200: float
    proportion_below_240: float


@dataclass(frozen=True, slots=True)
class SupportSurvivalRow:
    population: str
    position_band: str
    threshold: int
    observation_count: int
    reaching_count: int
    empirical_probability: float


@dataclass(frozen=True, slots=True)
class Jd100SummaryRow:
    population: str
    literal_jd100_group: str
    observation_count: int
    distinct_rikishi_count: int
    prior_rated_median: float
    proportion_below_30: float
    proportion_below_60: float
    proportion_below_120: float
    proportion_below_180: float


@dataclass(frozen=True, slots=True)
class SensitivitySummaryRow:
    population: str
    position_band: str
    support_band: str
    rating_observation_count: int
    distinct_rikishi_count: int
    rating_disagreement_q25: float
    rating_disagreement_median: float
    rating_disagreement_q75: float
    rating_disagreement_q90: float
    forecast_participant_count: int
    forecast_disagreement_mean: float
    forecast_disagreement_q50: float
    forecast_disagreement_q90: float
    proportion_forecast_disagreement_above_0_005: float
    proportion_forecast_disagreement_above_0_01: float
    proportion_forecast_disagreement_above_0_02: float
    proportion_forecast_disagreement_above_0_05: float


@dataclass(frozen=True, slots=True)
class ChiiMaturityRow:
    minimum_prior_rated_bouts: int
    chii: str
    chii_ordinal: int
    observation_count: int
    distinct_rikishi_count: int
    mean_rating_bkp: float
    mean_centered_rating_bkp: float
    support_weighted_mean_centered_rating_bkp: float
    plotted: bool


@dataclass(frozen=True, slots=True)
class PositionMaturityRow:
    minimum_prior_rated_bouts: int
    position_band: str
    observation_count: int
    distinct_rikishi_count: int
    mean_centered_rating_bkp: float
    support_weighted_mean_centered_rating_bkp: float


@dataclass(frozen=True, slots=True)
class ReversalSummaryRow:
    minimum_prior_rated_bouts: int
    plotted_chii_count: int
    reversal_count: int
    maximum_reversal: float
    lower_tail_plotted_chii_count: int
    lower_tail_reversal_count: int
    lower_tail_maximum_reversal: float
    observations_retained: int
    distinct_rikishi_retained: int


@dataclass(frozen=True, slots=True)
class ProbeResult:
    definition: ProbeDefinition
    history_basho_count: int
    raw_result_count: int
    rated_bout_count: int
    excluded_fusen_count: int
    excluded_draw_count: int
    model_state_exclusion_count: int
    maturity_rows: tuple[MaturityRow, ...]
    bout_rows: tuple[BoutDisagreementRow, ...]
    support_summaries: tuple[SupportSummaryRow, ...]
    support_survival: tuple[SupportSurvivalRow, ...]
    jd100_summaries: tuple[Jd100SummaryRow, ...]
    sensitivity_summaries: tuple[SensitivitySummaryRow, ...]
    chii_maturity_rows: tuple[ChiiMaturityRow, ...]
    position_maturity_rows: tuple[PositionMaturityRow, ...]
    reversal_summaries: tuple[ReversalSummaryRow, ...]
