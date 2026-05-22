from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmpiricalBoutRow:
    date: str
    day: int
    rikishi1: int
    rikishi2: int
    chii1: str
    chii2: str
    ordinal1: int
    ordinal2: int
    division1: str
    division2: str
    winner: int
    rikishi1_won: int
    higher_or_equal_rikishi: int
    other_rikishi: int
    higher_or_equal_chii: str
    other_chii: str
    higher_or_equal_ordinal: int
    other_ordinal: int
    same_chii: int
    higher_or_equal_won: int


@dataclass(frozen=True)
class ChiiPairRow:
    higher_or_equal_chii: str
    other_chii: str
    higher_or_equal_ordinal: int
    other_ordinal: int
    same_chii: int
    n_obs: int
    n_higher_or_equal_wins: int
    n_other_wins: int
    p_higher_or_equal_wins: float
    ci95_lower: float
    ci95_upper: float


@dataclass(frozen=True)
class SelectedChiiMatchupRow:
    selected_chii: str
    opponent_chii: str
    selected_ordinal: int
    opponent_ordinal: int
    selected_is_higher_or_equal: int
    same_chii: int
    n_obs: int
    n_selected_wins: int
    n_opponent_wins: int
    p_selected_wins: float
    ci95_lower: float
    ci95_upper: float


@dataclass(frozen=True)
class SidelessChiiPairRow:
    higher_or_equal_chii: str
    other_chii: str
    higher_or_equal_ordinal: int
    other_ordinal: int
    same_chii: int
    n_obs: int
    n_higher_or_equal_wins: int
    n_other_wins: int
    p_higher_or_equal_wins: float
    ci95_lower: float
    ci95_upper: float


@dataclass(frozen=True)
class ProbabilityDistributionRow:
    p_bin_lo: float
    p_bin_hi: float
    n_pairs: int
    n_bouts: int
    n_higher_or_equal_wins: int
    share: float
    mean_pair_p: float
    bout_weighted_p: float


@dataclass(frozen=True)
class MatchupMetadata:
    start_year: int
    end_year: int
    oracle_collapse_mode: str
    raw_candidate_bouts: int
    oracle_retained_bouts: int
    included_probability_bouts: int
    excluded_fusen_blank: int
    excluded_non_decisive: int
    excluded_missing_chii: int
    same_chii_bouts: int


@dataclass(frozen=True)
class EmpiricalMatchupResults:
    bout_rows: tuple[EmpiricalBoutRow, ...]
    chii_pair_rows: tuple[ChiiPairRow, ...]
    selected_chii_rows: tuple[SelectedChiiMatchupRow, ...]
    sideless_chii_pair_rows: tuple[SidelessChiiPairRow, ...]
    sideless_distribution_rows: tuple[ProbabilityDistributionRow, ...]
    metadata: MatchupMetadata
