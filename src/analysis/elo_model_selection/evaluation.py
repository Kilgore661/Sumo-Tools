"""Paired summaries and basho-block uncertainty for model selection."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import random

from src.analysis.prediction.sekitori import is_sekitori

from .model import ComparisonRun, ForecastRow, ModelName, score


@dataclass(frozen=True, slots=True)
class SummaryRow:
    population: str
    model: ModelName
    bout_count: int
    mean_log_loss: float
    mean_brier_loss: float
    mean_log_difference_from_50: float
    mean_brier_difference_from_50: float


@dataclass(frozen=True, slots=True)
class ComparisonRow:
    population: str
    model: ModelName
    comparator: str
    bout_count: int
    mean_log_difference: float
    log_lower: float
    log_upper: float
    log_one_sided_upper: float
    mean_brier_difference: float
    brier_lower: float
    brier_upper: float
    brier_one_sided_upper: float
    predictive_information_criterion_met: bool | None
    superior_to_b: bool | None
    noninferiority_margin_log: float | None
    noninferior_to_b: bool | None


@dataclass(frozen=True, slots=True)
class Evaluation:
    summaries: tuple[SummaryRow, ...]
    comparisons: tuple[ComparisonRow, ...]
    factorial_contrasts: tuple["FactorialRow", ...]
    calibration_bins: tuple["CalibrationBinRow", ...]
    calibration_summaries: tuple["CalibrationSummaryRow", ...]
    support_pair_calibration: tuple["SupportPairCalibrationRow", ...]
    coarse_support_pair_calibration: tuple["SupportPairCalibrationRow", ...]


@dataclass(frozen=True, slots=True)
class FactorialRow:
    population: str
    contrast: str
    bout_count: int
    mean_log_difference: float
    log_lower: float
    log_upper: float
    mean_brier_difference: float
    brier_lower: float
    brier_upper: float


@dataclass(frozen=True, slots=True)
class CalibrationBinRow:
    population: str
    model: ModelName
    bin_lower: float
    bin_upper: float
    upper_inclusive: bool
    bout_count: int
    participant_count: int
    win_count: int
    mean_predicted_probability: float
    observed_win_rate: float
    calibration_gap: float
    absolute_calibration_gap: float


@dataclass(frozen=True, slots=True)
class CalibrationSummaryRow:
    population: str
    model: ModelName
    bout_count: int
    participant_count: int
    populated_bin_count: int
    supported_bin_count: int
    minimum_bin_participants: int
    expected_calibration_error: float
    maximum_calibration_error: float
    supported_maximum_calibration_error: float | None


@dataclass(frozen=True, slots=True)
class SupportPairCalibrationRow:
    model: ModelName
    lower_support_band: str
    higher_support_band: str
    bout_count: int
    participant_count: int
    populated_bin_count: int
    expected_calibration_error: float


def evaluate(run: ComparisonRun) -> Evaluation:
    """Evaluate every model on identical population-specific bout sets."""

    by_model = {model.spec.name: model.forecasts for model in run.models}
    populations = _population_indices(by_model["B"])
    summaries: list[SummaryRow] = []
    comparisons: list[ComparisonRow] = []
    factorial: list[FactorialRow] = []
    calibration_bins: list[CalibrationBinRow] = []
    calibration_summaries: list[CalibrationSummaryRow] = []
    for population_index, (population, indices) in enumerate(populations.items()):
        model_losses: dict[ModelName, tuple[tuple[float, float], ...]] = {}
        for model_index, model in enumerate(run.models):
            rows = tuple(model.forecasts[index] for index in indices)
            losses = tuple(score(row) for row in rows)
            model_losses[model.spec.name] = losses
            summary = _summary(population, model.spec.name, losses)
            summaries.append(summary)
            bins, calibration_summary = _calibration(
                population,
                model.spec.name,
                rows,
                run.definition.calibration_bin_width,
                run.definition.calibration_min_bin_participants,
            )
            calibration_bins.extend(bins)
            calibration_summaries.append(calibration_summary)
            comparisons.append(_comparison(
                population,
                model.spec.name,
                "50%",
                rows,
                tuple((log - math.log(2.0), brier - 0.25) for log, brier in losses),
                run,
                seed_offset=population_index * 20 + model_index,
            ))
        b_losses = model_losses["B"]
        b_summary = next(row for row in summaries if row.population == population and row.model == "B")
        margin = run.definition.noninferiority_fraction * max(
            0.0, math.log(2.0) - b_summary.mean_log_loss
        )
        for model_index, model in enumerate(run.models[1:], start=1):
            losses = model_losses[model.spec.name]
            differences = tuple(
                (left[0] - right[0], left[1] - right[1])
                for left, right in zip(losses, b_losses)
            )
            rows = tuple(model.forecasts[index] for index in indices)
            comparisons.append(_comparison(
                population,
                model.spec.name,
                "B",
                rows,
                differences,
                run,
                seed_offset=1000 + population_index * 20 + model_index,
                noninferiority_margin=margin,
            ))
        factorial.extend(_factorial_rows(
            population,
            tuple(by_model["B"][index] for index in indices),
            model_losses,
            run,
            population_index,
        ))
    support_pair_calibration = _evaluate_support_pairs(
        run, by_model["B"], _PAIR_SUPPORT_BANDS
    )
    coarse_support_pair_calibration = _evaluate_support_pairs(
        run, by_model["B"], _COARSE_PAIR_SUPPORT_BANDS
    )
    return Evaluation(
        tuple(summaries),
        tuple(comparisons),
        tuple(factorial),
        tuple(calibration_bins),
        tuple(calibration_summaries),
        support_pair_calibration,
        coarse_support_pair_calibration,
    )


def _calibration(
    population: str,
    model: ModelName,
    rows: tuple[ForecastRow, ...],
    bin_width: float,
    minimum_bin_participants: int,
) -> tuple[tuple[CalibrationBinRow, ...], CalibrationSummaryRow]:
    """Build participant-level calibration bins from complementary forecasts."""

    bin_count = round(1.0 / bin_width)
    probability_sums = [0.0] * bin_count
    win_counts = [0] * bin_count
    participant_counts = [0] * bin_count
    bout_counts = [0] * bin_count
    for row in rows:
        p_a = row.probability_a_wins
        observations = ((p_a, int(row.a_won)), (1.0 - p_a, int(not row.a_won)))
        touched: set[int] = set()
        for probability, outcome in observations:
            index = min(int(probability / bin_width), bin_count - 1)
            probability_sums[index] += probability
            win_counts[index] += outcome
            participant_counts[index] += 1
            touched.add(index)
        for index in touched:
            bout_counts[index] += 1

    result: list[CalibrationBinRow] = []
    weighted_absolute_gap = 0.0
    maximum_gap = 0.0
    supported_maximum_gap: float | None = None
    for index, participant_count in enumerate(participant_counts):
        if participant_count == 0:
            continue
        mean_probability = probability_sums[index] / participant_count
        win_rate = win_counts[index] / participant_count
        gap = win_rate - mean_probability
        absolute_gap = abs(gap)
        weighted_absolute_gap += participant_count * absolute_gap
        maximum_gap = max(maximum_gap, absolute_gap)
        if participant_count >= minimum_bin_participants:
            supported_maximum_gap = max(supported_maximum_gap or 0.0, absolute_gap)
        result.append(CalibrationBinRow(
            population=population,
            model=model,
            bin_lower=round(index * bin_width, 12),
            bin_upper=round((index + 1) * bin_width, 12),
            upper_inclusive=index == bin_count - 1,
            bout_count=bout_counts[index],
            participant_count=participant_count,
            win_count=win_counts[index],
            mean_predicted_probability=mean_probability,
            observed_win_rate=win_rate,
            calibration_gap=gap,
            absolute_calibration_gap=absolute_gap,
        ))
    total_participants = 2 * len(rows)
    summary = CalibrationSummaryRow(
        population=population,
        model=model,
        bout_count=len(rows),
        participant_count=total_participants,
        populated_bin_count=len(result),
        supported_bin_count=sum(
            count >= minimum_bin_participants for count in participant_counts
        ),
        minimum_bin_participants=minimum_bin_participants,
        expected_calibration_error=weighted_absolute_gap / total_participants,
        maximum_calibration_error=maximum_gap,
        supported_maximum_calibration_error=supported_maximum_gap,
    )
    return tuple(result), summary


def _summary(
    population: str,
    model: ModelName,
    losses: tuple[tuple[float, float], ...],
) -> SummaryRow:
    count = len(losses)
    mean_log = sum(row[0] for row in losses) / count
    mean_brier = sum(row[1] for row in losses) / count
    return SummaryRow(
        population, model, count, mean_log, mean_brier,
        mean_log - math.log(2.0), mean_brier - 0.25,
    )


def _comparison(
    population: str,
    model: ModelName,
    comparator: str,
    rows: tuple[ForecastRow, ...],
    differences: tuple[tuple[float, float], ...],
    run: ComparisonRun,
    *,
    seed_offset: int,
    noninferiority_margin: float | None = None,
) -> ComparisonRow:
    log_values = tuple(value[0] for value in differences)
    brier_values = tuple(value[1] for value in differences)
    log_interval = _bootstrap(rows, log_values, run, seed_offset)
    brier_interval = _bootstrap(rows, brier_values, run, seed_offset + 10000)
    log_mean = sum(log_values) / len(log_values)
    brier_mean = sum(brier_values) / len(brier_values)
    versus_b = comparator == "B"
    return ComparisonRow(
        population=population,
        model=model,
        comparator=comparator,
        bout_count=len(rows),
        mean_log_difference=log_mean,
        log_lower=log_interval[0],
        log_upper=log_interval[1],
        log_one_sided_upper=log_interval[2],
        mean_brier_difference=brier_mean,
        brier_lower=brier_interval[0],
        brier_upper=brier_interval[1],
        brier_one_sided_upper=brier_interval[2],
        predictive_information_criterion_met=(log_interval[2] < 0.0)
        if not versus_b else None,
        superior_to_b=(log_interval[2] < 0.0) if versus_b else None,
        noninferiority_margin_log=noninferiority_margin,
        noninferior_to_b=(log_interval[2] < noninferiority_margin)
        if versus_b and noninferiority_margin is not None else None,
    )


def _factorial_rows(
    population: str,
    rows: tuple[ForecastRow, ...],
    losses: dict[ModelName, tuple[tuple[float, float], ...]],
    run: ComparisonRun,
    population_index: int,
) -> tuple[FactorialRow, ...]:
    formulas = (
        ("k under constant initialisation", lambda b, bk, bp, bkp: bk - b),
        ("P under constant k", lambda b, bk, bp, bkp: bp - b),
        ("P under divisional k", lambda b, bk, bp, bkp: bkp - bk),
        ("k under informed initialisation", lambda b, bk, bp, bkp: bkp - bp),
        (
            "k-by-P interaction",
            lambda b, bk, bp, bkp: (bkp - bp) - (bk - b),
        ),
    )
    result: list[FactorialRow] = []
    for formula_index, (label, formula) in enumerate(formulas):
        paired = tuple(
            tuple(
                formula(
                    losses["B"][index][metric],
                    losses["B_k"][index][metric],
                    losses["B_P"][index][metric],
                    losses["B_kP"][index][metric],
                )
                for metric in (0, 1)
            )
            for index in range(len(rows))
        )
        log_values = tuple(value[0] for value in paired)
        brier_values = tuple(value[1] for value in paired)
        log_interval = _bootstrap(
            rows, log_values, run, 20000 + population_index * 20 + formula_index
        )
        brier_interval = _bootstrap(
            rows, brier_values, run, 30000 + population_index * 20 + formula_index
        )
        result.append(FactorialRow(
            population=population,
            contrast=label,
            bout_count=len(rows),
            mean_log_difference=sum(log_values) / len(log_values),
            log_lower=log_interval[0],
            log_upper=log_interval[1],
            mean_brier_difference=sum(brier_values) / len(brier_values),
            brier_lower=brier_interval[0],
            brier_upper=brier_interval[1],
        ))
    return tuple(result)


def _bootstrap(
    rows: tuple[ForecastRow, ...],
    values: tuple[float, ...],
    run: ComparisonRun,
    seed_offset: int,
) -> tuple[float, float, float]:
    grouped: dict[object, list[float]] = defaultdict(list)
    for row, value in zip(rows, values):
        grouped[row.date].append(value)
    blocks = tuple(
        (sum(grouped[date]), len(grouped[date]))
        for date in sorted(grouped)
    )
    rng = random.Random(run.definition.bootstrap_seed + seed_offset)
    samples: list[float] = []
    for _ in range(run.definition.bootstrap_resamples):
        selected = tuple(rng.choice(blocks) for _ in blocks)
        samples.append(
            sum(block_sum for block_sum, _ in selected)
            / sum(block_count for _, block_count in selected)
        )
    samples.sort()
    count = len(samples)
    alpha = 1.0 - run.definition.confidence_level
    return (
        samples[int((alpha / 2.0) * (count - 1))],
        samples[int((1.0 - alpha / 2.0) * (count - 1))],
        samples[int(run.definition.confidence_level * (count - 1))],
    )


def _population_indices(rows: tuple[ForecastRow, ...]) -> dict[str, tuple[int, ...]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups["all"].append(index)
        chii_a = row.chii_a
        chii_b = row.chii_b
        a_sekitori = chii_a is not None and is_sekitori(chii_a)
        b_sekitori = chii_b is not None and is_sekitori(chii_b)
        if a_sekitori and b_sekitori:
            groups["sekitori"].append(index)
        elif chii_a is not None and chii_b is not None and not a_sekitori and not b_sekitori:
            groups["sub_sekitori"].append(index)
        elif a_sekitori != b_sekitori:
            groups["cross_boundary"].append(index)
        if row.rated_bouts_a_before == 0 or row.rated_bouts_b_before == 0:
            groups["new_entrant"].append(index)
        experience = min(row.rated_bouts_a_before, row.rated_bouts_b_before)
        label = (
            "experience_under_15" if experience < 15 else
            "experience_15_19" if experience < 20 else
            "experience_20_24" if experience < 25 else
            "experience_25_29" if experience < 30 else
            "experience_30_34" if experience < 35 else
            "experience_35_39" if experience < 40 else
            "experience_40_44" if experience < 45 else
            "experience_45_49" if experience < 50 else
            "experience_50_plus"
        )
        groups[label].append(index)
        career_label = _CAREER_SUPPORT_BANDS[_career_support_index(experience)][1]
        groups[career_label].append(index)
    return {name: tuple(indices) for name, indices in groups.items() if indices}


_CAREER_SUPPORT_BANDS = (
    (30, "career_experience_under_30", "<30"),
    (60, "career_experience_30_59", "30-59"),
    (120, "career_experience_60_119", "60-119"),
    (240, "career_experience_120_239", "120-239"),
    (360, "career_experience_240_359", "240-359"),
    (480, "career_experience_360_479", "360-479"),
    (None, "career_experience_480_plus", "480+"),
)


def _career_support_index(experience: int) -> int:
    for index, (upper_bound, _, _) in enumerate(_CAREER_SUPPORT_BANDS):
        if upper_bound is None or experience < upper_bound:
            return index
    raise AssertionError("Final career-support band must be open-ended")


def _support_pair_indices(
    rows: tuple[ForecastRow, ...],
    bands: tuple[tuple[int | None, str], ...],
) -> dict[tuple[int, int], tuple[int, ...]]:
    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        a_band = _support_index(row.rated_bouts_a_before, bands)
        b_band = _support_index(row.rated_bouts_b_before, bands)
        groups[min(a_band, b_band), max(a_band, b_band)].append(index)
    return {
        support_pair: tuple(indices)
        for support_pair, indices in groups.items()
        if indices
    }


_PAIR_SUPPORT_BANDS = tuple(
    (
        30 * (index + 1),
        "<30" if index == 0 else f"{30 * index}-{30 * (index + 1) - 1}",
    )
    for index in range(20)
) + ((None, "600+"),)


_COARSE_PAIR_SUPPORT_BANDS = (
    (30, "<30"),
    (60, "30-59"),
    (120, "60-119"),
    (240, "120-239"),
    (360, "240-359"),
    (480, "360-479"),
    (None, "480+"),
)


def _support_index(
    experience: int,
    bands: tuple[tuple[int | None, str], ...],
) -> int:
    for index, (upper_bound, _) in enumerate(bands):
        if upper_bound is None or experience < upper_bound:
            return index
    raise AssertionError("Final support-pair band must be open-ended")


def _evaluate_support_pairs(
    run: ComparisonRun,
    reference_rows: tuple[ForecastRow, ...],
    bands: tuple[tuple[int | None, str], ...],
) -> tuple[SupportPairCalibrationRow, ...]:
    result: list[SupportPairCalibrationRow] = []
    support_pairs = _support_pair_indices(reference_rows, bands)
    for model in run.models:
        for (lower_index, higher_index), indices in support_pairs.items():
            rows = tuple(model.forecasts[index] for index in indices)
            _, summary = _calibration(
                "support_pair",
                model.spec.name,
                rows,
                run.definition.calibration_bin_width,
                run.definition.calibration_min_bin_participants,
            )
            result.append(SupportPairCalibrationRow(
                model=model.spec.name,
                lower_support_band=bands[lower_index][1],
                higher_support_band=bands[higher_index][1],
                bout_count=summary.bout_count,
                participant_count=summary.participant_count,
                populated_bin_count=summary.populated_bin_count,
                expected_calibration_error=summary.expected_calibration_error,
            ))
    return tuple(result)
