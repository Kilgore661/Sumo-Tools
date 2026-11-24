"""Matched categorical comparison of production Elo-89 and higher chii."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import random
from typing import Iterable

from scipy.stats import binomtest

from src.analysis.elo89.model import Elo89Run, Forecast
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import Date


DEFAULT_BOOTSTRAP_REPLICATES = 10_000
DEFAULT_BOOTSTRAP_SEED = 89
ROLLING_WINDOWS = (6, 12, 24)


@dataclass(frozen=True, slots=True)
class BoutComparison:
    date: Date
    day: int
    rikishi_a: int
    rikishi_b: int
    chii_a: str
    chii_b: str
    rating_a_before: float
    rating_b_before: float
    rated_bouts_a_before: int
    rated_bouts_b_before: int
    probability_a_wins: float
    a_won: bool
    elo_selection_a: bool | None
    chii_selection_a: bool | None
    elo_correct: bool | None
    chii_correct: bool | None
    paired_difference: int | None
    exclusion_reason: str
    population: str
    maturity_band: str
    elo_log_loss: float
    elo_brier_loss: float

    @property
    def primary(self) -> bool:
        return not self.exclusion_reason


@dataclass(frozen=True, slots=True)
class Interval:
    estimate: float
    lower_95: float
    upper_95: float
    one_sided_lower_95: float


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    evaluation_start: Date
    evaluation_end: Date
    rows: tuple[BoutComparison, ...]
    raw_result_count: int
    rated_bout_count: int
    excluded_fusen_count: int
    excluded_draw_count: int
    elo_tie_count: int
    missing_chii_count: int
    equal_chii_count: int
    primary_count: int
    both_correct: int
    elo_correct_chii_wrong: int
    elo_wrong_chii_correct: int
    both_wrong: int
    elo_accuracy: float
    chii_accuracy: float
    elo_minus_chii: Interval
    chii_minus_random: Interval
    elo_minus_random: Interval
    mcnemar_exact_p: float
    bootstrap_replicates: int
    bootstrap_seed: int
    conclusion: str
    mean_elo_log_loss: float
    mean_elo_brier_loss: float


def compare_forecasts(
    forecasts: Iterable[Forecast],
    *,
    evaluation_start: Date,
    evaluation_end: Date,
    raw_result_count: int | None = None,
    rated_bout_count: int | None = None,
    excluded_fusen_count: int = 0,
    excluded_draw_count: int = 0,
    bootstrap_replicates: int = DEFAULT_BOOTSTRAP_REPLICATES,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> ComparisonResult:
    """Score both rules on one filtered stream of production forecasts."""

    if evaluation_end < evaluation_start:
        raise ValueError("Evaluation end must not precede evaluation start")
    if bootstrap_replicates < 1:
        raise ValueError("bootstrap_replicates must be positive")
    selected = tuple(
        row for row in forecasts
        if evaluation_start <= row.date <= evaluation_end
    )
    if not selected:
        raise ValueError("No Elo-89 forecasts in the evaluation interval")
    rows = tuple(_compare_bout(row) for row in selected)
    primary = tuple(row for row in rows if row.primary)
    if not primary:
        raise ValueError("No bouts on which both rules select a winner")

    both_correct = sum(row.elo_correct is True and row.chii_correct is True for row in primary)
    elo_only = sum(row.elo_correct is True and row.chii_correct is False for row in primary)
    chii_only = sum(row.elo_correct is False and row.chii_correct is True for row in primary)
    both_wrong = sum(row.elo_correct is False and row.chii_correct is False for row in primary)
    elo_accuracy = sum(bool(row.elo_correct) for row in primary) / len(primary)
    chii_accuracy = sum(bool(row.chii_correct) for row in primary) / len(primary)
    distributions = _block_bootstrap(primary, bootstrap_replicates, bootstrap_seed)
    elo_minus_chii = _interval(elo_accuracy - chii_accuracy, distributions["elo_minus_chii"])
    chii_minus_random = _interval(chii_accuracy - 0.5, distributions["chii_minus_random"])
    elo_minus_random = _interval(elo_accuracy - 0.5, distributions["elo_minus_random"])

    if elo_accuracy - chii_accuracy <= 0 or chii_accuracy - 0.5 <= 0:
        conclusion = "contradicted"
    elif (
        elo_minus_chii.one_sided_lower_95 > 0
        and chii_minus_random.one_sided_lower_95 > 0
    ):
        conclusion = "confirmed"
    else:
        conclusion = "inconclusive"

    observed_rated = len(rows)
    rated = observed_rated if rated_bout_count is None else rated_bout_count
    raw = rated + excluded_fusen_count + excluded_draw_count if raw_result_count is None else raw_result_count
    if rated != observed_rated:
        raise ValueError(
            "Rated-bout count must equal the forecasts in the evaluation interval: "
            f"{rated} != {observed_rated}"
        )
    return ComparisonResult(
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        rows=rows,
        raw_result_count=raw,
        rated_bout_count=rated,
        excluded_fusen_count=excluded_fusen_count,
        excluded_draw_count=excluded_draw_count,
        elo_tie_count=sum(row.exclusion_reason == "elo_tie" for row in rows),
        missing_chii_count=sum(row.exclusion_reason == "missing_chii" for row in rows),
        equal_chii_count=sum(row.exclusion_reason == "equal_chii" for row in rows),
        primary_count=len(primary),
        both_correct=both_correct,
        elo_correct_chii_wrong=elo_only,
        elo_wrong_chii_correct=chii_only,
        both_wrong=both_wrong,
        elo_accuracy=elo_accuracy,
        chii_accuracy=chii_accuracy,
        elo_minus_chii=elo_minus_chii,
        chii_minus_random=chii_minus_random,
        elo_minus_random=elo_minus_random,
        mcnemar_exact_p=_exact_mcnemar_p(elo_only, chii_only),
        bootstrap_replicates=bootstrap_replicates,
        bootstrap_seed=bootstrap_seed,
        conclusion=conclusion,
        mean_elo_log_loss=sum(row.elo_log_loss for row in rows) / len(rows),
        mean_elo_brier_loss=sum(row.elo_brier_loss for row in rows) / len(rows),
    )


def compare_run(run: Elo89Run, **kwargs) -> ComparisonResult:
    """Convenience wrapper retaining the production replay as authority."""

    return compare_forecasts(run.forecasts, **kwargs)


def aggregate_rows(rows: Iterable[BoutComparison]) -> dict[str, float | int | None]:
    """Return categorical aggregates for any primary-domain subset."""

    materialised = tuple(row for row in rows if row.primary)
    count = len(materialised)
    if not count:
        return {"bouts": 0, "elo_correct": 0, "chii_correct": 0,
                "elo_accuracy": None, "chii_accuracy": None,
                "paired_difference": None, "agreement_fraction": None}
    elo_correct = sum(bool(row.elo_correct) for row in materialised)
    chii_correct = sum(bool(row.chii_correct) for row in materialised)
    agreement = sum(row.elo_selection_a == row.chii_selection_a for row in materialised)
    return {
        "bouts": count,
        "elo_correct": elo_correct,
        "chii_correct": chii_correct,
        "elo_accuracy": elo_correct / count,
        "chii_accuracy": chii_correct / count,
        "paired_difference": (elo_correct - chii_correct) / count,
        "agreement_fraction": agreement / count,
    }


def by_basho_rows(result: ComparisonResult) -> list[dict[str, object]]:
    grouped: dict[Date, list[BoutComparison]] = defaultdict(list)
    for row in result.rows:
        if row.primary:
            grouped[row.date].append(row)
    return [{"date": str(date), **aggregate_rows(grouped[date])} for date in sorted(grouped)]


def rolling_rows(result: ComparisonResult) -> list[dict[str, object]]:
    grouped: dict[Date, list[BoutComparison]] = defaultdict(list)
    for row in result.rows:
        if row.primary:
            grouped[row.date].append(row)
    dates = sorted(grouped)
    output: list[dict[str, object]] = []
    for window in ROLLING_WINDOWS:
        for index in range(window - 1, len(dates)):
            window_dates = dates[index - window + 1:index + 1]
            window_rows = [row for date in window_dates for row in grouped[date]]
            output.append({
                "window_basho": window,
                "start": str(window_dates[0]),
                "end": str(window_dates[-1]),
                **aggregate_rows(window_rows),
            })
    return output


def subgroup_rows(result: ComparisonResult) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [{"population": "ALL", **aggregate_rows(result.rows)}]
    populations = ("MAKUUCHI", "JURYO", "MAKUSHITA", "SANDANME", "JONIDAN", "JONOKUCHI", "CROSS_DIVISION")
    for population in populations:
        rows.append({"population": population, **aggregate_rows(
            row for row in result.rows if row.population == population
        )})
    for band in ("0", "1-9", "10-49", "50-99", "100+"):
        rows.append({"population": f"MATURITY_{band}", **aggregate_rows(
            row for row in result.rows if row.maturity_band == band
        )})
    return rows


def _compare_bout(row: Forecast) -> BoutComparison:
    probability = row.probability_a_wins
    elo_selection = True if probability > 0.5 else False if probability < 0.5 else None
    if row.chii_a is None or row.chii_b is None:
        chii_selection = None
        exclusion = "missing_chii"
        population = "UNKNOWN"
    else:
        ordinal_a = row.chii_a.ordinal()
        ordinal_b = row.chii_b.ordinal()
        chii_selection = True if ordinal_a < ordinal_b else False if ordinal_a > ordinal_b else None
        exclusion = "equal_chii" if chii_selection is None else ""
        population = _population(row)
    if elo_selection is None:
        exclusion = "elo_tie"
    elo_correct = None if elo_selection is None else elo_selection == row.a_won
    chii_correct = None if chii_selection is None else chii_selection == row.a_won
    primary = elo_selection is not None and chii_selection is not None
    outcome = 1.0 if row.a_won else 0.0
    clipped = min(max(probability, 1e-15), 1.0 - 1e-15)
    return BoutComparison(
        date=row.date, day=int(row.day), rikishi_a=int(row.rikishi_a), rikishi_b=int(row.rikishi_b),
        chii_a="" if row.chii_a is None else str(row.chii_a),
        chii_b="" if row.chii_b is None else str(row.chii_b),
        rating_a_before=row.rating_a_before, rating_b_before=row.rating_b_before,
        rated_bouts_a_before=row.rated_bouts_a_before, rated_bouts_b_before=row.rated_bouts_b_before,
        probability_a_wins=probability, a_won=row.a_won,
        elo_selection_a=elo_selection, chii_selection_a=chii_selection,
        elo_correct=elo_correct, chii_correct=chii_correct,
        paired_difference=(int(elo_correct) - int(chii_correct)) if primary else None,
        exclusion_reason="" if primary else exclusion, population=population,
        maturity_band=_maturity_band(min(row.rated_bouts_a_before, row.rated_bouts_b_before)),
        elo_log_loss=-(outcome * math.log(clipped) + (1.0 - outcome) * math.log(1.0 - clipped)),
        elo_brier_loss=(probability - outcome) ** 2,
    )


def _population(row: Forecast) -> str:
    assert row.chii_a is not None and row.chii_b is not None
    a = Division.MAKUUCHI if isinstance(row.chii_a.level, MSD) else row.chii_a.level
    b = Division.MAKUUCHI if isinstance(row.chii_b.level, MSD) else row.chii_b.level
    return a.name if a == b else "CROSS_DIVISION"


def _maturity_band(count: int) -> str:
    if count == 0:
        return "0"
    if count < 10:
        return "1-9"
    if count < 50:
        return "10-49"
    if count < 100:
        return "50-99"
    return "100+"


def _block_bootstrap(rows: tuple[BoutComparison, ...], replicates: int, seed: int) -> dict[str, list[float]]:
    grouped: dict[Date, list[BoutComparison]] = defaultdict(list)
    for row in rows:
        grouped[row.date].append(row)
    # Aggregate first: resampling these complete-basho sufficient statistics is
    # identical to materialising every sampled bout, and keeps the 10,000-run
    # analysis practical for the full post-1988 record.
    blocks = tuple(
        (
            len(values),
            sum(bool(row.elo_correct) for row in values),
            sum(bool(row.chii_correct) for row in values),
        )
        for _, values in sorted(grouped.items())
    )
    rng = random.Random(seed)
    output = {"elo_minus_chii": [], "chii_minus_random": [], "elo_minus_random": []}
    for _ in range(replicates):
        count = elo_correct = chii_correct = 0
        for _ in blocks:
            block_count, block_elo, block_chii = blocks[rng.randrange(len(blocks))]
            count += block_count
            elo_correct += block_elo
            chii_correct += block_chii
        elo = elo_correct / count
        chii = chii_correct / count
        output["elo_minus_chii"].append(elo - chii)
        output["chii_minus_random"].append(chii - 0.5)
        output["elo_minus_random"].append(elo - 0.5)
    return output


def _interval(estimate: float, values: list[float]) -> Interval:
    ordered = sorted(values)
    return Interval(estimate, _quantile(ordered, 0.025), _quantile(ordered, 0.975), _quantile(ordered, 0.05))


def _quantile(ordered: list[float], probability: float) -> float:
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _exact_mcnemar_p(elo_only: int, chii_only: int) -> float:
    discordant = elo_only + chii_only
    if discordant == 0:
        return 1.0
    return float(binomtest(elo_only, discordant, p=0.5, alternative="two-sided").pvalue)
