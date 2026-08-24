"""Chronological exposure and coupled-initialisation analysis."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable

from src.analysis.elo_model_selection.model import AdoptedPrior
from src.analysis.prediction.bouts import select_rated_bouts
from src.sumo_core.BasicEnums import Division, MSD, Outcome
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date, History

from .model import (
    BoutDisagreementRow,
    ChiiMaturityRow,
    Jd100SummaryRow,
    MaturityRow,
    ProbeDefinition,
    ProbeResult,
    PositionMaturityRow,
    ReversalSummaryRow,
    SensitivitySummaryRow,
    SupportSummaryRow,
    SupportSurvivalRow,
)


INHERITED_POSITION_CUTS = (0.0, 0.2, 0.4, 0.6, 0.8395, 1.0000000001)
SUPPORT_BAND_CUTS = (0, 15, 30, 60, 120, 180, 200, 240)


@dataclass(slots=True)
class _RatingState:
    ratings: dict[RikId, float] = field(default_factory=dict)
    rated_counts: dict[RikId, int] = field(default_factory=dict)


def run_probe(
    history: History,
    *,
    start_date: Date,
    end_date: Date,
    prior: AdoptedPrior,
    divisional_k: Callable[[int], float],
    definition: ProbeDefinition | None = None,
) -> ProbeResult:
    """Run the three-stage probe over one declared inclusive History range."""

    dates = tuple(date for date in sorted(history) if start_date <= date <= end_date)
    if not dates:
        raise ValueError("Rating maturity requires at least one represented basho")
    if dates[0] != start_date:
        raise ValueError(f"History begins at {dates[0]}, not declared boundary {start_date}")
    declared = definition or ProbeDefinition(str(start_date), str(end_date))
    if declared.start_basho != str(start_date) or declared.end_basho != str(end_date):
        raise ValueError("ProbeDefinition date strings do not match the replay dates")

    selection = select_rated_bouts(history, start_date=start_date, end_date=end_date)
    bouts_by_date: dict[Date, list[object]] = defaultdict(list)
    for bout in selection.bouts:
        bouts_by_date[bout.contest.id.date].append(bout)

    first_banzuke = history[dates[0]].banzuke
    boundary_ids = frozenset(first_banzuke.riks)
    first_observed: dict[RikId, Date] = {}
    date_index = {date: index for index, date in enumerate(dates)}
    fought_counts: dict[RikId, int] = defaultdict(int)
    bk = _RatingState()
    bkp = _RatingState()
    maturity_rows: list[MaturityRow] = []
    bout_rows: list[BoutDisagreementRow] = []

    for date in dates:
        state = history[date]
        banzuke = state.banzuke
        ordered = sorted(banzuke.riks, key=lambda rikishi: banzuke.rikchii[rikishi].ordinal())
        if len(ordered) < 2:
            raise ValueError(f"Banzuke {date} contains fewer than two ranked rikishi")
        for rikishi in ordered:
            first_observed.setdefault(rikishi, date)

        date_bouts = bouts_by_date.get(date, [])
        eligible_ids = {
            rikishi
            for bout in date_bouts
            for rikishi in (bout.contest.rikishi_a, bout.contest.rikishi_b)
        }
        for rikishi in sorted(eligible_ids, key=int):
            chii = banzuke.rikchii[rikishi] if rikishi in banzuke else None
            _ensure_rating(bk, rikishi, chii, informed=False, prior=prior, definition=declared)
            _ensure_rating(bkp, rikishi, chii, informed=True, prior=prior, definition=declared)

        available = [rikishi for rikishi in ordered if rikishi in bk.ratings]
        mean_bk = statistics.fmean(bk.ratings[rikishi] for rikishi in available) if available else 0.0
        mean_bkp = statistics.fmean(bkp.ratings[rikishi] for rikishi in available) if available else 0.0
        size = len(ordered)
        positions = {rikishi: index / (size - 1) for index, rikishi in enumerate(ordered)}
        cohorts = {
            rikishi: "boundary_incumbent" if rikishi in boundary_ids else "observed_entrant"
            for rikishi in ordered
        }

        for index, rikishi in enumerate(ordered):
            chii = banzuke.rikchii[rikishi]
            available_state = rikishi in bk.ratings
            centered_bk = bk.ratings[rikishi] - mean_bk if available_state else None
            centered_bkp = bkp.ratings[rikishi] - mean_bkp if available_state else None
            maturity_rows.append(MaturityRow(
                rikishi_id=int(rikishi),
                shikona=str(banzuke.rikshik[rikishi]),
                basho=str(date),
                cohort=cohorts[rikishi],
                first_observed_basho=str(first_observed[rikishi]),
                elapsed_represented_basho=date_index[date] - date_index[first_observed[rikishi]] + 1,
                chii=str(chii),
                chii_ordinal=chii.ordinal(),
                division=_division(chii),
                literal_jd100_group=_literal_jd100_group(chii),
                banzuke_size=size,
                position_from_top=index + 1,
                position_from_bottom=size - index,
                normalized_position=positions[rikishi],
                inherited_position_band=_float_band(positions[rikishi], INHERITED_POSITION_CUTS, 4),
                uniform_position_band=_uniform_position_band(
                    positions[rikishi], declared.normalized_bin_width
                ),
                prior_rated_bouts=bk.rated_counts.get(rikishi, 0),
                prior_fought_bouts=fought_counts[rikishi],
                model_state_available=available_state,
                model_state_exclusion="" if available_state else "no eligible rated bout yet",
                rating_bk=bk.ratings.get(rikishi),
                rating_bkp=bkp.ratings.get(rikishi),
                centered_rating_bk=centered_bk,
                centered_rating_bkp=centered_bkp,
                absolute_centered_rating_disagreement=(
                    abs(centered_bkp - centered_bk) if available_state else None
                ),
            ))

        for bout in date_bouts:
            a = bout.contest.rikishi_a
            b = bout.contest.rikishi_b
            chii_a = banzuke.rikchii[a] if a in banzuke else None
            chii_b = banzuke.rikchii[b] if b in banzuke else None
            probability_bk = _probability(bk.ratings[a], bk.ratings[b], declared.q)
            probability_bkp = _probability(bkp.ratings[a], bkp.ratings[b], declared.q)
            bout_rows.append(BoutDisagreementRow(
                basho=str(date),
                day=int(bout.contest.id.day),
                rikishi_a=int(a),
                rikishi_b=int(b),
                cohort_a="boundary_incumbent" if a in boundary_ids else "observed_entrant",
                cohort_b="boundary_incumbent" if b in boundary_ids else "observed_entrant",
                chii_a=str(chii_a) if chii_a is not None else "",
                chii_b=str(chii_b) if chii_b is not None else "",
                normalized_position_a=positions.get(a, -1.0),
                normalized_position_b=positions.get(b, -1.0),
                position_band_a=(
                    _float_band(positions[a], INHERITED_POSITION_CUTS, 4)
                    if a in positions else "unranked"
                ),
                position_band_b=(
                    _float_band(positions[b], INHERITED_POSITION_CUTS, 4)
                    if b in positions else "unranked"
                ),
                prior_rated_bouts_a=bk.rated_counts[a],
                prior_rated_bouts_b=bk.rated_counts[b],
                probability_a_bk=probability_bk,
                probability_a_bkp=probability_bkp,
                absolute_probability_disagreement=abs(probability_bkp - probability_bk),
                a_won=bout.a_won,
            ))
            _update_pair(
                bk, a, b, chii_a, chii_b, bout.a_won, probability_bk,
                divisional_k, declared.constant_k,
            )
            _update_pair(
                bkp, a, b, chii_a, chii_b, bout.a_won, probability_bkp,
                divisional_k, declared.constant_k,
            )

        _update_fought_counts(state.summary, fought_counts)

    maturity_tuple = tuple(maturity_rows)
    bout_tuple = tuple(bout_rows)
    support_summaries = _support_summaries(maturity_tuple, declared)
    support_survival = _support_survival(maturity_tuple)
    jd100_summaries = _jd100_summaries(maturity_tuple)
    sensitivity = _sensitivity_summaries(maturity_tuple, bout_tuple)
    chii_rows, position_rows, reversals = _maturity_shapes(maturity_tuple, declared)
    return ProbeResult(
        definition=declared,
        history_basho_count=len(dates),
        raw_result_count=selection.raw_result_count,
        rated_bout_count=selection.rated_bout_count,
        excluded_fusen_count=selection.excluded_fusen_count,
        excluded_draw_count=selection.excluded_draw_count,
        model_state_exclusion_count=sum(not row.model_state_available for row in maturity_tuple),
        maturity_rows=maturity_tuple,
        bout_rows=bout_tuple,
        support_summaries=support_summaries,
        support_survival=support_survival,
        jd100_summaries=jd100_summaries,
        sensitivity_summaries=sensitivity,
        chii_maturity_rows=chii_rows,
        position_maturity_rows=position_rows,
        reversal_summaries=reversals,
    )


def _ensure_rating(
    state: _RatingState,
    rikishi: RikId,
    chii: Chii | None,
    *,
    informed: bool,
    prior: AdoptedPrior,
    definition: ProbeDefinition,
) -> None:
    if rikishi in state.ratings:
        return
    state.ratings[rikishi] = (
        prior.rating_for(chii)[0] if informed else definition.constant_initial_rating
    )
    state.rated_counts[rikishi] = 0


def _probability(a: float, b: float, q: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((b - a) / q))


def _update_pair(
    state: _RatingState,
    a: RikId,
    b: RikId,
    chii_a: Chii | None,
    chii_b: Chii | None,
    a_won: bool,
    probability: float,
    divisional_k: Callable[[int], float],
    constant_k: float,
) -> None:
    residual = float(a_won) - probability
    k_a = divisional_k(chii_a.ordinal()) if chii_a is not None else constant_k
    k_b = divisional_k(chii_b.ordinal()) if chii_b is not None else constant_k
    state.ratings[a] += k_a * residual
    state.ratings[b] -= k_b * residual
    state.rated_counts[a] += 1
    state.rated_counts[b] += 1


def _update_fought_counts(summary: object, counts: dict[RikId, int]) -> None:
    for daily in summary.values():
        for result in daily.results_lookup.values():
            for rikishi, outcome in (
                (result.rikishi1, result.outcome1),
                (result.rikishi2, result.outcome2),
            ):
                if outcome in (Outcome.W, Outcome.L, Outcome.DRAW):
                    counts[rikishi] += 1


def _division(chii: Chii) -> str:
    return "Makuuchi" if isinstance(chii.level, MSD) else chii.level.name.capitalize()


def _literal_jd100_group(chii: Chii) -> str:
    if isinstance(chii.level, MSD):
        return "above_Jd100"
    if chii.level.value < Division.JONIDAN.value:
        return "above_Jd100"
    if chii.level == Division.JONIDAN and chii.number < 100:
        return "above_Jd100"
    if chii.level == Division.JONIDAN and chii.number == 100:
        return "Jd100"
    return "below_Jd100"


def _float_band(value: float, cuts: tuple[float, ...], decimals: int) -> str:
    for low, high in zip(cuts, cuts[1:]):
        if low <= value < high:
            shown_high = 1.0 if high > 1.0 else high
            final = shown_high == 1.0
            return f"{low:.{decimals}f}–{'1.0000' if final else f'<{shown_high:.{decimals}f}'}"
    raise ValueError(f"Value outside position domain: {value}")


def _uniform_position_band(value: float, width: float) -> str:
    index = min(int(value / width), math.ceil(1.0 / width) - 1)
    low = index * width
    high = min(1.0, low + width)
    return f"{low:.2f}–{'1.00' if high == 1.0 else f'<{high:.2f}'}"


def _support_band(value: int) -> str:
    for low, high in zip(SUPPORT_BAND_CUTS, SUPPORT_BAND_CUTS[1:]):
        if low <= value < high:
            return f"{low}–<{high}"
    return f"{SUPPORT_BAND_CUTS[-1]}+"


def _populations(rows: Iterable[MaturityRow]) -> tuple[tuple[str, list[MaturityRow]], ...]:
    values = list(rows)
    return (
        ("all", values),
        ("boundary_incumbent", [row for row in values if row.cohort == "boundary_incumbent"]),
        ("observed_entrant", [row for row in values if row.cohort == "observed_entrant"]),
    )


def _quantile(values: list[float] | list[int], probability: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    location = (len(ordered) - 1) * probability
    lower = math.floor(location)
    upper = math.ceil(location)
    if lower == upper:
        return float(ordered[lower])
    weight = location - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def _support_summaries(
    rows: tuple[MaturityRow, ...], definition: ProbeDefinition
) -> tuple[SupportSummaryRow, ...]:
    output: list[SupportSummaryRow] = []
    schemes = (("inherited", "inherited_position_band"), ("uniform", "uniform_position_band"))
    for population, selected in _populations(rows):
        for scheme, attribute in schemes:
            groups: dict[str, list[MaturityRow]] = defaultdict(list)
            for row in selected:
                groups[getattr(row, attribute)].append(row)
            for label, group in sorted(groups.items()):
                positions = [row.normalized_position for row in group]
                counts = [row.prior_rated_bouts for row in group]
                proportions = [sum(value < threshold for value in counts) / len(counts) for threshold in definition.support_thresholds]
                output.append(SupportSummaryRow(
                    population=population, band_scheme=scheme, position_band=label,
                    position_low=min(positions), position_high=max(positions),
                    observation_count=len(group),
                    distinct_rikishi_count=len({row.rikishi_id for row in group}),
                    prior_rated_min=min(counts), prior_rated_q25=_quantile(counts, .25),
                    prior_rated_median=_quantile(counts, .5), prior_rated_q75=_quantile(counts, .75),
                    prior_rated_q90=_quantile(counts, .9), prior_rated_q95=_quantile(counts, .95),
                    prior_rated_max=max(counts),
                    proportion_below_15=proportions[0], proportion_below_30=proportions[1],
                    proportion_below_60=proportions[2], proportion_below_120=proportions[3],
                    proportion_below_180=proportions[4], proportion_below_200=proportions[5],
                    proportion_below_240=proportions[6],
                ))
    return tuple(output)


def _support_survival(rows: tuple[MaturityRow, ...]) -> tuple[SupportSurvivalRow, ...]:
    output: list[SupportSurvivalRow] = []
    for population, selected in _populations(rows):
        groups: dict[str, list[int]] = defaultdict(list)
        for row in selected:
            groups[row.inherited_position_band].append(row.prior_rated_bouts)
        for label, counts in sorted(groups.items()):
            for threshold in range(max(counts) + 1):
                reaching = sum(value >= threshold for value in counts)
                output.append(SupportSurvivalRow(
                    population, label, threshold, len(counts), reaching, reaching / len(counts)
                ))
    return tuple(output)


def _jd100_summaries(rows: tuple[MaturityRow, ...]) -> tuple[Jd100SummaryRow, ...]:
    output: list[Jd100SummaryRow] = []
    for population, selected in _populations(rows):
        groups: dict[str, list[MaturityRow]] = defaultdict(list)
        for row in selected:
            groups[row.literal_jd100_group].append(row)
        for label, group in sorted(groups.items()):
            counts = [row.prior_rated_bouts for row in group]
            output.append(Jd100SummaryRow(
                population, label, len(group), len({row.rikishi_id for row in group}),
                _quantile(counts, .5),
                *(sum(value < threshold for value in counts) / len(counts) for threshold in (30, 60, 120, 180)),
            ))
    return tuple(output)


def _sensitivity_summaries(
    rows: tuple[MaturityRow, ...], bouts: tuple[BoutDisagreementRow, ...]
) -> tuple[SensitivitySummaryRow, ...]:
    rating_groups: dict[tuple[str, str, str], list[MaturityRow]] = defaultdict(list)
    forecast_groups: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        if row.model_state_available:
            for population in ("all", row.cohort):
                rating_groups[(population, row.inherited_position_band, _support_band(row.prior_rated_bouts))].append(row)
    for bout in bouts:
        for cohort, position_band, support in (
            (bout.cohort_a, bout.position_band_a, bout.prior_rated_bouts_a),
            (bout.cohort_b, bout.position_band_b, bout.prior_rated_bouts_b),
        ):
            if position_band == "unranked":
                continue
            for population in ("all", cohort):
                forecast_groups[(population, position_band, _support_band(support))].append(
                    bout.absolute_probability_disagreement
                )
    keys = sorted(set(rating_groups) | set(forecast_groups))
    output: list[SensitivitySummaryRow] = []
    for key in keys:
        rgroup = rating_groups.get(key, [])
        fvalues = forecast_groups.get(key, [])
        rvalues = [row.absolute_centered_rating_disagreement for row in rgroup]
        rvalues = [value for value in rvalues if value is not None]
        output.append(SensitivitySummaryRow(
            population=key[0], position_band=key[1], support_band=key[2],
            rating_observation_count=len(rvalues),
            distinct_rikishi_count=len({row.rikishi_id for row in rgroup}),
            rating_disagreement_q25=_quantile(rvalues, .25),
            rating_disagreement_median=_quantile(rvalues, .5),
            rating_disagreement_q75=_quantile(rvalues, .75),
            rating_disagreement_q90=_quantile(rvalues, .9),
            forecast_participant_count=len(fvalues),
            forecast_disagreement_mean=statistics.fmean(fvalues) if fvalues else math.nan,
            forecast_disagreement_q50=_quantile(fvalues, .5),
            forecast_disagreement_q90=_quantile(fvalues, .9),
            proportion_forecast_disagreement_above_0_005=(sum(v > .005 for v in fvalues) / len(fvalues) if fvalues else math.nan),
            proportion_forecast_disagreement_above_0_01=(sum(v > .01 for v in fvalues) / len(fvalues) if fvalues else math.nan),
            proportion_forecast_disagreement_above_0_02=(sum(v > .02 for v in fvalues) / len(fvalues) if fvalues else math.nan),
            proportion_forecast_disagreement_above_0_05=(sum(v > .05 for v in fvalues) / len(fvalues) if fvalues else math.nan),
        ))
    return tuple(output)


def _weighted_mean(rows: list[MaturityRow]) -> float:
    weighted = [
        (row.centered_rating_bkp, row.prior_rated_bouts / (row.prior_rated_bouts + 60.0))
        for row in rows
        if row.centered_rating_bkp is not None and row.prior_rated_bouts > 0
    ]
    total_weight = sum(weight for _, weight in weighted)
    return (
        sum(value * weight for value, weight in weighted) / total_weight
        if total_weight else math.nan
    )


def _maturity_shapes(
    rows: tuple[MaturityRow, ...], definition: ProbeDefinition
) -> tuple[
    tuple[ChiiMaturityRow, ...],
    tuple[PositionMaturityRow, ...],
    tuple[ReversalSummaryRow, ...],
]:
    output: list[ChiiMaturityRow] = []
    position_output: list[PositionMaturityRow] = []
    reversals: list[ReversalSummaryRow] = []
    available = [row for row in rows if row.model_state_available]
    for threshold in definition.maturity_thresholds:
        selected = [row for row in available if row.prior_rated_bouts >= threshold]
        groups: dict[int, list[MaturityRow]] = defaultdict(list)
        for row in selected:
            groups[row.chii_ordinal].append(row)
        threshold_rows: list[ChiiMaturityRow] = []
        for ordinal, group in sorted(groups.items()):
            first = group[0]
            item = ChiiMaturityRow(
                threshold, first.chii, ordinal, len(group),
                len({row.rikishi_id for row in group}),
                statistics.fmean(row.rating_bkp for row in group if row.rating_bkp is not None),
                statistics.fmean(row.centered_rating_bkp for row in group if row.centered_rating_bkp is not None),
                _weighted_mean(group),
                len(group) >= definition.minimum_chii_observations,
            )
            threshold_rows.append(item)
            output.append(item)
        plotted = [row for row in threshold_rows if row.plotted]
        increases = [
            later.mean_centered_rating_bkp - earlier.mean_centered_rating_bkp
            for earlier, later in zip(plotted, plotted[1:])
            if later.mean_centered_rating_bkp > earlier.mean_centered_rating_bkp
        ]
        jd100_ordinal = Chii.from_str("Jd100e").ordinal()
        lower_tail = [row for row in plotted if row.chii_ordinal >= jd100_ordinal]
        lower_increases = [
            later.mean_centered_rating_bkp - earlier.mean_centered_rating_bkp
            for earlier, later in zip(lower_tail, lower_tail[1:])
            if later.mean_centered_rating_bkp > earlier.mean_centered_rating_bkp
        ]
        reversals.append(ReversalSummaryRow(
            threshold, len(plotted), len(increases), max(increases, default=0.0),
            len(lower_tail), len(lower_increases), max(lower_increases, default=0.0),
            len(selected), len({row.rikishi_id for row in selected}),
        ))
        position_groups: dict[str, list[MaturityRow]] = defaultdict(list)
        for row in selected:
            position_groups[row.uniform_position_band].append(row)
        for label, group in sorted(position_groups.items()):
            position_output.append(PositionMaturityRow(
                threshold,
                label,
                len(group),
                len({row.rikishi_id for row in group}),
                statistics.fmean(
                    row.centered_rating_bkp for row in group
                    if row.centered_rating_bkp is not None
                ),
                _weighted_mean(group),
            ))
    return tuple(output), tuple(position_output), tuple(reversals)
