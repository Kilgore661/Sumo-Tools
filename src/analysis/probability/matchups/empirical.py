from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
import math

from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.probability.classes import Z95
from src.analysis.probability.matchups.classes import (
    ChiiPairRow,
    EmpiricalBoutRow,
    EmpiricalMatchupResults,
    MatchupMetadata,
    ProbabilityDistributionRow,
    SelectedChiiMatchupRow,
    SidelessChiiPairRow,
)
from src.sumo_core.BasicEnums import Division, MSD, Outcome, Side
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii, Level
from src.sumo_core.History import History
from src.sumo_core.Summary import BoutResult


ORACLE_COLLAPSE_MODE = "annotation_only"
DEFAULT_DISTRIBUTION_BIN_WIDTH = 0.05


@dataclass
class _PairAccumulator:
    higher_or_equal_chii: Chii
    other_chii: Chii
    n_obs: int = 0
    n_higher_or_equal_wins: int = 0

    def record(self, higher_or_equal_won: int) -> None:
        self.n_obs += 1
        self.n_higher_or_equal_wins += int(higher_or_equal_won)


@dataclass
class _MetadataAccumulator:
    raw_candidate_bouts: int = 0
    oracle_retained_bouts: int = 0
    included_probability_bouts: int = 0
    excluded_fusen_blank: int = 0
    excluded_non_decisive: int = 0
    excluded_missing_chii: int = 0
    same_chii_bouts: int = 0


def compute_empirical_matchups(
    raw_history: History,
    *,
    start_year: int,
    end_year: int,
) -> EmpiricalMatchupResults:
    """Compute annotation-collapsed, side-preserving observed matchup data."""
    oracle = make_oracle(
        raw_history,
        bios={},
        collapse_mode=ORACLE_COLLAPSE_MODE,
    )
    history = oracle.history
    metadata = _MetadataAccumulator(
        raw_candidate_bouts=_count_bouts(raw_history),
        oracle_retained_bouts=_count_bouts(history),
    )

    bout_rows: list[EmpiricalBoutRow] = []
    pair_accumulators: dict[tuple[int, int], _PairAccumulator] = {}
    sideless_pair_accumulators: dict[tuple[int, int], _PairAccumulator] = {}

    for date in sorted(history.keys()):
        basho = history(date)
        banzuke = basho.banzuke

        for day in sorted(basho.summary.keys()):
            daily_results = basho.summary(day)

            for bout in daily_results.results_lookup.values():
                row = _build_bout_row(
                    date=date,
                    day=day,
                    bout=bout,
                    rikchii=banzuke.rikchii,
                    metadata=metadata,
                )
                if row is None:
                    continue

                bout_rows.append(row)
                _record_pair_row(row, pair_accumulators)
                _record_sideless_pair_row(row, sideless_pair_accumulators)

    chii_pair_rows = _build_pair_rows(pair_accumulators)
    selected_chii_rows = _build_selected_chii_rows(chii_pair_rows)
    sideless_chii_pair_rows = _build_sideless_pair_rows(sideless_pair_accumulators)
    sideless_distribution_rows = _build_probability_distribution_rows(
        sideless_chii_pair_rows,
        bin_width=DEFAULT_DISTRIBUTION_BIN_WIDTH,
    )

    return EmpiricalMatchupResults(
        bout_rows=tuple(bout_rows),
        chii_pair_rows=tuple(chii_pair_rows),
        selected_chii_rows=tuple(selected_chii_rows),
        sideless_chii_pair_rows=tuple(sideless_chii_pair_rows),
        sideless_distribution_rows=tuple(sideless_distribution_rows),
        metadata=MatchupMetadata(
            start_year=start_year,
            end_year=end_year,
            oracle_collapse_mode=ORACLE_COLLAPSE_MODE,
            raw_candidate_bouts=metadata.raw_candidate_bouts,
            oracle_retained_bouts=metadata.oracle_retained_bouts,
            included_probability_bouts=metadata.included_probability_bouts,
            excluded_fusen_blank=metadata.excluded_fusen_blank,
            excluded_non_decisive=metadata.excluded_non_decisive,
            excluded_missing_chii=metadata.excluded_missing_chii,
            same_chii_bouts=metadata.same_chii_bouts,
        ),
    )


def _count_bouts(history: History) -> int:
    total = 0
    for date in sorted(history.keys()):
        for day in sorted(history(date).summary.keys()):
            total += len(history(date).summary(day).results_lookup)
    return total


def _build_bout_row(date, day, bout: BoutResult, rikchii, metadata: _MetadataAccumulator):
    if bout.decision in ("fusen", "blank"):
        metadata.excluded_fusen_blank += 1
        return None

    if {bout.outcome1, bout.outcome2} != {Outcome.W, Outcome.L}:
        metadata.excluded_non_decisive += 1
        return None

    r1 = bout.rikishi1
    r2 = bout.rikishi2

    if r1 not in rikchii or r2 not in rikchii:
        metadata.excluded_missing_chii += 1
        return None

    c1 = rikchii[r1]
    c2 = rikchii[r2]
    o1 = c1.ordinal()
    o2 = c2.ordinal()
    r1_won = int(bout.outcome1 == Outcome.W)
    winner = r1 if r1_won else r2

    if o1 <= o2:
        higher_or_equal_rikishi = r1
        other_rikishi = r2
        higher_or_equal_chii = c1
        other_chii = c2
        higher_or_equal_ordinal = o1
        other_ordinal = o2
        higher_or_equal_won = r1_won
    else:
        higher_or_equal_rikishi = r2
        other_rikishi = r1
        higher_or_equal_chii = c2
        other_chii = c1
        higher_or_equal_ordinal = o2
        other_ordinal = o1
        higher_or_equal_won = 1 - r1_won

    same_chii = int(o1 == o2)
    metadata.included_probability_bouts += 1
    metadata.same_chii_bouts += same_chii

    return EmpiricalBoutRow(
        date=str(date),
        day=int(day),
        rikishi1=int(r1),
        rikishi2=int(r2),
        chii1=str(c1),
        chii2=str(c2),
        ordinal1=o1,
        ordinal2=o2,
        division1=_division_label(c1),
        division2=_division_label(c2),
        winner=int(winner),
        rikishi1_won=r1_won,
        higher_or_equal_rikishi=int(higher_or_equal_rikishi),
        other_rikishi=int(other_rikishi),
        higher_or_equal_chii=str(higher_or_equal_chii),
        other_chii=str(other_chii),
        higher_or_equal_ordinal=higher_or_equal_ordinal,
        other_ordinal=other_ordinal,
        same_chii=same_chii,
        higher_or_equal_won=int(higher_or_equal_won),
    )


def _record_pair_row(
    row: EmpiricalBoutRow,
    pair_accumulators: dict[tuple[int, int], _PairAccumulator],
) -> None:
    key = (row.higher_or_equal_ordinal, row.other_ordinal)
    if key not in pair_accumulators:
        pair_accumulators[key] = _PairAccumulator(
            higher_or_equal_chii=Chii.from_ordinal(row.higher_or_equal_ordinal),
            other_chii=Chii.from_ordinal(row.other_ordinal),
        )

    pair_accumulators[key].record(row.higher_or_equal_won)


def _record_sideless_pair_row(
    row: EmpiricalBoutRow,
    pair_accumulators: dict[tuple[int, int], _PairAccumulator],
) -> None:
    c1 = _remove_side(Chii.from_ordinal(row.ordinal1))
    c2 = _remove_side(Chii.from_ordinal(row.ordinal2))
    r1_won = row.rikishi1_won

    if c1.ordinal() <= c2.ordinal():
        higher_or_equal_chii = c1
        other_chii = c2
        higher_or_equal_won = r1_won
    else:
        higher_or_equal_chii = c2
        other_chii = c1
        higher_or_equal_won = 1 - r1_won

    key = (higher_or_equal_chii.ordinal(), other_chii.ordinal())
    if key not in pair_accumulators:
        pair_accumulators[key] = _PairAccumulator(
            higher_or_equal_chii=higher_or_equal_chii,
            other_chii=other_chii,
        )

    pair_accumulators[key].record(higher_or_equal_won)


def _build_pair_rows(
    pair_accumulators: dict[tuple[int, int], _PairAccumulator],
) -> list[ChiiPairRow]:
    rows: list[ChiiPairRow] = []
    for key in sorted(pair_accumulators):
        acc = pair_accumulators[key]
        p = acc.n_higher_or_equal_wins / acc.n_obs
        ci_lo, ci_hi = _wilson95(acc.n_higher_or_equal_wins, acc.n_obs)
        rows.append(
            ChiiPairRow(
                higher_or_equal_chii=str(acc.higher_or_equal_chii),
                other_chii=str(acc.other_chii),
                higher_or_equal_ordinal=acc.higher_or_equal_chii.ordinal(),
                other_ordinal=acc.other_chii.ordinal(),
                same_chii=int(acc.higher_or_equal_chii == acc.other_chii),
                n_obs=acc.n_obs,
                n_higher_or_equal_wins=acc.n_higher_or_equal_wins,
                n_other_wins=acc.n_obs - acc.n_higher_or_equal_wins,
                p_higher_or_equal_wins=p,
                ci95_lower=ci_lo,
                ci95_upper=ci_hi,
            )
        )
    return rows


def _build_sideless_pair_rows(
    pair_accumulators: dict[tuple[int, int], _PairAccumulator],
) -> list[SidelessChiiPairRow]:
    rows: list[SidelessChiiPairRow] = []
    for key in sorted(pair_accumulators):
        acc = pair_accumulators[key]
        p = acc.n_higher_or_equal_wins / acc.n_obs
        ci_lo, ci_hi = _wilson95(acc.n_higher_or_equal_wins, acc.n_obs)
        rows.append(
            SidelessChiiPairRow(
                higher_or_equal_chii=str(acc.higher_or_equal_chii),
                other_chii=str(acc.other_chii),
                higher_or_equal_ordinal=acc.higher_or_equal_chii.ordinal(),
                other_ordinal=acc.other_chii.ordinal(),
                same_chii=int(acc.higher_or_equal_chii == acc.other_chii),
                n_obs=acc.n_obs,
                n_higher_or_equal_wins=acc.n_higher_or_equal_wins,
                n_other_wins=acc.n_obs - acc.n_higher_or_equal_wins,
                p_higher_or_equal_wins=p,
                ci95_lower=ci_lo,
                ci95_upper=ci_hi,
            )
        )
    return rows


def _build_selected_chii_rows(pair_rows: list[ChiiPairRow]) -> list[SelectedChiiMatchupRow]:
    rows: list[SelectedChiiMatchupRow] = []
    for row in pair_rows:
        rows.append(
            SelectedChiiMatchupRow(
                selected_chii=row.higher_or_equal_chii,
                opponent_chii=row.other_chii,
                selected_ordinal=row.higher_or_equal_ordinal,
                opponent_ordinal=row.other_ordinal,
                selected_is_higher_or_equal=1,
                same_chii=row.same_chii,
                n_obs=row.n_obs,
                n_selected_wins=row.n_higher_or_equal_wins,
                n_opponent_wins=row.n_other_wins,
                p_selected_wins=row.p_higher_or_equal_wins,
                ci95_lower=row.ci95_lower,
                ci95_upper=row.ci95_upper,
            )
        )

        if row.same_chii:
            continue

        ci_lo, ci_hi = _wilson95(row.n_other_wins, row.n_obs)
        rows.append(
            SelectedChiiMatchupRow(
                selected_chii=row.other_chii,
                opponent_chii=row.higher_or_equal_chii,
                selected_ordinal=row.other_ordinal,
                opponent_ordinal=row.higher_or_equal_ordinal,
                selected_is_higher_or_equal=0,
                same_chii=0,
                n_obs=row.n_obs,
                n_selected_wins=row.n_other_wins,
                n_opponent_wins=row.n_higher_or_equal_wins,
                p_selected_wins=row.n_other_wins / row.n_obs,
                ci95_lower=ci_lo,
                ci95_upper=ci_hi,
            )
        )

    return sorted(
        rows,
        key=lambda r: (r.selected_ordinal, r.opponent_ordinal),
    )


def _build_probability_distribution_rows(
    pair_rows: tuple[SidelessChiiPairRow, ...] | list[SidelessChiiPairRow],
    *,
    bin_width: float,
) -> list[ProbabilityDistributionRow]:
    if not pair_rows:
        return []
    if not (0.0 < bin_width <= 1.0):
        raise ValueError(f"bin_width must lie in (0, 1], got {bin_width}")

    n_bins = math.ceil(1.0 / bin_width)
    buckets: dict[int, dict[str, float | int]] = {}
    total_bouts = sum(row.n_obs for row in pair_rows)

    for row in pair_rows:
        index = _probability_bin_index(row.p_higher_or_equal_wins, bin_width, n_bins)
        if index not in buckets:
            buckets[index] = {
                "n_pairs": 0,
                "n_bouts": 0,
                "n_higher_or_equal_wins": 0,
                "sum_pair_p": 0.0,
            }

        bucket = buckets[index]
        bucket["n_pairs"] += 1
        bucket["n_bouts"] += row.n_obs
        bucket["n_higher_or_equal_wins"] += row.n_higher_or_equal_wins
        bucket["sum_pair_p"] += row.p_higher_or_equal_wins

    rows: list[ProbabilityDistributionRow] = []
    for index in range(n_bins):
        lo = index * bin_width
        hi = min(1.0, lo + bin_width)
        bucket = buckets.get(
            index,
            {
                "n_pairs": 0,
                "n_bouts": 0,
                "n_higher_or_equal_wins": 0,
                "sum_pair_p": 0.0,
            },
        )
        n_pairs = int(bucket["n_pairs"])
        n_bouts = int(bucket["n_bouts"])
        n_wins = int(bucket["n_higher_or_equal_wins"])

        rows.append(
            ProbabilityDistributionRow(
                p_bin_lo=lo,
                p_bin_hi=hi,
                n_pairs=n_pairs,
                n_bouts=n_bouts,
                n_higher_or_equal_wins=n_wins,
                share=0.0 if total_bouts == 0 else n_bouts / total_bouts,
                mean_pair_p=0.0 if n_pairs == 0 else float(bucket["sum_pair_p"]) / n_pairs,
                bout_weighted_p=0.0 if n_bouts == 0 else n_wins / n_bouts,
            )
        )

    return rows


def _probability_bin_index(p: float, bin_width: float, n_bins: int) -> int:
    p = max(0.0, min(1.0, float(p)))
    if p == 1.0:
        return n_bins - 1
    return min(int(p / bin_width), n_bins - 1)


def _wilson95(n_wins: int, n_obs: int) -> tuple[float, float]:
    phat = n_wins / n_obs
    z2 = Z95 * Z95
    denom = 1.0 + z2 / n_obs
    centre = (phat + z2 / (2.0 * n_obs)) / denom
    halfwidth = (
        Z95
        * sqrt((phat * (1.0 - phat) / n_obs) + (z2 / (4.0 * n_obs * n_obs)))
        / denom
    )
    return centre - halfwidth, centre + halfwidth


def _division_label(chii: Chii) -> str:
    division = _division_from_level(chii.level)
    return division.name.lower()


def _division_from_level(level: Level) -> Division:
    if isinstance(level, MSD):
        return Division.MAKUUCHI
    return level


def _remove_side(chii: Chii) -> Chii:
    return Chii(
        level=chii.level,
        number=chii.number,
        side=Side.NONE,
        ann=chii.ann,
    )
