"""Exact B-family predictive comparison of BKP1 population operators."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Callable

from src.analysis.elo_model_selection.evaluation import _population_indices
from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    BoutContext,
    ComparisonDefinition,
    ForecastRow,
    ModelSpec,
    _context,
    _run_model,
    load_adopted_prior,
    score,
)
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.prediction.bouts import select_rated_bouts
from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, RikId, Year
from src.sumo_core.History import Date, History

from .predict_candidate import (
    DEFAULT_OLD_PRIOR,
    _bootstrap_blocks,
    _difference_blocks,
    _ece,
    load_alpha_prior,
)


DEFAULT_PRIOR = Path("files/output/analysis/equelo_bkp1/prior.csv")
DEFAULT_K_CONFIG = Path("files/input/elo_fide.json")
DEFAULT_OUTPUT = Path(
    "files/output/analysis/equelo_population_policy/prediction_bkp1_population_q400"
)
NONE = "BKP1_no_population_adjustment"
LEGACY = "BKP1_legacy_departure"
WHOLE = "BKP1_whole_population"
OLD = "old_B_kP"


@dataclass(slots=True)
class _PopulationState:
    ratings: dict[RikId, float] = field(default_factory=dict)
    counts: dict[RikId, int] = field(default_factory=dict)
    sources: dict[RikId, str] = field(default_factory=dict)


def run_whole_population_model(
    history: History,
    contexts: tuple[BoutContext, ...],
    definition: ComparisonDefinition,
    prior: AdoptedPrior,
    divisional_k: Callable[[int], float],
) -> tuple[ForecastRow, ...]:
    """Forecast canonical bouts while normalising the full active population."""

    by_date: dict[Date, list[BoutContext]] = defaultdict(list)
    for context in contexts:
        by_date[context.bout.contest.id.date].append(context)

    state = _PopulationState()
    previous_active: set[RikId] = set()
    target_mean: float | None = None
    rows: list[ForecastRow] = []
    dates = sorted(
        date for date in history
        if definition.start_date <= date <= definition.end_date
    )
    for date in dates:
        basho = history[date]
        day_contexts = by_date.get(date, ())
        active = set(basho.banzuke.riks)
        for context in day_contexts:
            active.add(context.bout.contest.rikishi_a)
            active.add(context.bout.contest.rikishi_b)

        for rikishi in previous_active - active:
            state.ratings.pop(rikishi, None)
            state.sources.pop(rikishi, None)
        for rikishi in sorted(active):
            if rikishi in state.ratings:
                continue
            chii = basho.banzuke.rikchii.get(rikishi)
            rating, source = prior.rating_for(chii)
            state.ratings[rikishi] = rating
            state.sources[rikishi] = source
            state.counts.setdefault(rikishi, 0)

        if not active:
            previous_active = active
            continue
        if target_mean is None:
            target_mean = _mean(state.ratings, active)
        _shift_to_target(state.ratings, active, target_mean)

        for context in day_contexts:
            rows.append(
                _forecast_and_update(state, context, definition, divisional_k)
            )

        _shift_to_target(state.ratings, active, target_mean)
        previous_active = active

    if target_mean is None:
        raise ValueError("Cannot evaluate an empty history")
    return tuple(rows)


def run_legacy_departure_model(
    history: History,
    contexts: tuple[BoutContext, ...],
    definition: ComparisonDefinition,
    prior: AdoptedPrior,
    divisional_k: Callable[[int], float],
) -> tuple[ForecastRow, ...]:
    """Forecast canonical bouts with Expt2 survivor redistribution."""

    by_date: dict[Date, list[BoutContext]] = defaultdict(list)
    for context in contexts:
        by_date[context.bout.contest.id.date].append(context)
    state = _PopulationState()
    previous_active: set[RikId] = set()
    rows: list[ForecastRow] = []
    dates = sorted(
        date for date in history
        if definition.start_date <= date <= definition.end_date
    )
    for date in dates:
        basho = history[date]
        day_contexts = by_date.get(date, ())
        active = set(basho.banzuke.riks)
        for context in day_contexts:
            active.add(context.bout.contest.rikishi_a)
            active.add(context.bout.contest.rikishi_b)
        _apply_legacy_departures(state.ratings, previous_active, active)
        for rikishi in sorted(active):
            if rikishi in state.ratings:
                continue
            rating, source = prior.rating_for(basho.banzuke.rikchii.get(rikishi))
            state.ratings[rikishi] = rating
            state.sources[rikishi] = source
            state.counts.setdefault(rikishi, 0)
        for context in day_contexts:
            row = _forecast_and_update(
                state, context, definition, divisional_k, model=LEGACY
            )
            rows.append(row)
        previous_active = active
    return tuple(rows)


def _apply_legacy_departures(
    ratings: dict[RikId, float],
    previous_active: set[RikId],
    current_active: set[RikId],
) -> None:
    for rikishi in sorted(previous_active - current_active):
        active_before = [candidate for candidate in previous_active if candidate in ratings]
        if rikishi not in active_before:
            continue
        mean_before = sum(ratings[candidate] for candidate in active_before) / len(active_before)
        survivors = [candidate for candidate in active_before if candidate != rikishi]
        if survivors:
            adjustment = (ratings[rikishi] - mean_before) / len(survivors)
            for survivor in survivors:
                ratings[survivor] += adjustment
        del ratings[rikishi]


def _forecast_and_update(
    state: _PopulationState,
    context: BoutContext,
    definition: ComparisonDefinition,
    divisional_k: Callable[[int], float],
    *,
    model: str = WHOLE,
) -> ForecastRow:
    bout = context.bout
    a = bout.contest.rikishi_a
    b = bout.contest.rikishi_b
    rating_a = state.ratings[a]
    rating_b = state.ratings[b]
    probability = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / definition.q))
    k_a = divisional_k(context.chii_a.ordinal()) if context.chii_a else definition.constant_k
    k_b = divisional_k(context.chii_b.ordinal()) if context.chii_b else definition.constant_k
    residual = float(bout.a_won) - probability
    delta_a = k_a * residual
    delta_b = -k_b * residual
    row = ForecastRow(
        model=model,  # type: ignore[arg-type]
        date=bout.contest.id.date,
        day=int(bout.contest.id.day),
        rikishi_a=int(a),
        rikishi_b=int(b),
        chii_a=context.chii_a,
        chii_b=context.chii_b,
        rating_a_before=rating_a,
        rating_b_before=rating_b,
        rated_bouts_a_before=state.counts[a],
        rated_bouts_b_before=state.counts[b],
        probability_a_wins=probability,
        a_won=bout.a_won,
        k_a=k_a,
        k_b=k_b,
        delta_a=delta_a,
        delta_b=delta_b,
        rating_a_after=rating_a + delta_a,
        rating_b_after=rating_b + delta_b,
        initialisation_a=state.sources[a],
        initialisation_b=state.sources[b],
    )
    state.ratings[a] += delta_a
    state.ratings[b] += delta_b
    state.counts[a] += 1
    state.counts[b] += 1
    return row


def _shift_to_target(
    ratings: dict[RikId, float], active: set[RikId], target: float
) -> float:
    adjustment = target - _mean(ratings, active)
    for rikishi in active:
        ratings[rikishi] += adjustment
    return adjustment


def _mean(ratings: dict[RikId, float], active: set[RikId]) -> float:
    return sum(ratings[rikishi] for rikishi in active) / len(active)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history_zip = args.history_zip.resolve()
    history = load_history_with_annotations(str(history_zip.with_suffix("")))
    definition = ComparisonDefinition(
        start_date=Date(Year(1989), Month(1)),
        end_date=_date(args.end),
        q=400.0,
        bootstrap_resamples=args.bootstrap_resamples,
    )
    prior, conversion = load_alpha_prior(args.prior)
    old_prior = load_adopted_prior(args.old_prior)
    selection = select_rated_bouts(
        history, start_date=definition.start_date, end_date=definition.end_date
    )
    contexts = tuple(_context(history, bout) for bout in selection.bouts)
    divisional_k = load_divisional_k_fn(args.k_config.resolve())
    spec = ModelSpec("B_kP", divisional_k=True, informed_prior=True)

    print(f"[{NONE}] running {len(contexts):,} canonical forecasts", flush=True)
    no_adjustment = _run_model(contexts, definition, spec, prior, divisional_k).forecasts
    print(f"[{LEGACY}] running Expt2 departure redistribution", flush=True)
    legacy = run_legacy_departure_model(history, contexts, definition, prior, divisional_k)
    print(f"[{WHOLE}] running full-population boundary corrections", flush=True)
    whole = run_whole_population_model(history, contexts, definition, prior, divisional_k)
    print(f"[{OLD}] running retained informed-prior benchmark", flush=True)
    old = _run_model(contexts, definition, spec, old_prior, divisional_k).forecasts
    _assert_same_domain(no_adjustment, legacy)
    _assert_same_domain(no_adjustment, whole)
    _assert_same_domain(no_adjustment, old)

    populations = _population_indices(no_adjustment)
    summaries = []
    comparisons = []
    losses = {
        NONE: tuple(score(row) for row in no_adjustment),
        LEGACY: tuple(score(row) for row in legacy),
        WHOLE: tuple(score(row) for row in whole),
        OLD: tuple(score(row) for row in old),
    }
    forecasts = {NONE: no_adjustment, LEGACY: legacy, WHOLE: whole, OLD: old}
    for population_index, (population, indices) in enumerate(populations.items()):
        for name in (NONE, LEGACY, WHOLE, OLD):
            rows = forecasts[name]
            values = losses[name]
            summaries.append({
                "population": population,
                "model": name,
                "bout_count": len(indices),
                "mean_log_loss": sum(values[i][0] for i in indices) / len(indices),
                "mean_brier_loss": sum(values[i][1] for i in indices) / len(indices),
                "expected_calibration_error": _ece(rows, indices, definition.calibration_bin_width),
            })
        for comparator_index, comparator in enumerate((NONE, LEGACY, OLD)):
            log_blocks = _difference_blocks(
                whole, losses[WHOLE], losses[comparator], indices, metric=0
            )
            brier_blocks = _difference_blocks(
                whole, losses[WHOLE], losses[comparator], indices, metric=1
            )
            offset = population_index * 10 + comparator_index
            log_interval = _bootstrap_blocks(
                log_blocks, definition, seed_offset=41000 + offset
            )
            brier_interval = _bootstrap_blocks(
                brier_blocks, definition, seed_offset=42000 + offset
            )
            comparisons.append({
                "population": population,
                "comparator": comparator,
                "bout_count": len(indices),
                "mean_log_difference": sum(x[0] for x in log_blocks) / sum(x[1] for x in log_blocks),
                "log_lower": log_interval[0],
                "log_upper": log_interval[1],
                "mean_brier_difference": sum(x[0] for x in brier_blocks) / sum(x[1] for x in brier_blocks),
                "brier_lower": brier_interval[0],
                "brier_upper": brier_interval[1],
            })

    args.output.mkdir(parents=True, exist_ok=True)
    _write_csv(args.output / "summary.csv", summaries)
    _write_csv(args.output / "comparisons.csv", comparisons)
    manifest = {
        "experiment": "Exact B-family BKP1 population-policy predictive comparison",
        "history": {"path": str(history_zip), "sha256": _sha256(history_zip)},
        "prior": {
            "path": str(args.prior.resolve()),
            "sha256": _sha256(args.prior.resolve()),
            "pair_count": conversion.pair_count,
            "fallback_rating": conversion.fallback_rating,
        },
        "old_prior": {
            "path": str(args.old_prior.resolve()),
            "sha256": _sha256(args.old_prior.resolve()),
        },
        "q": definition.q,
        "population": "full banzuke population at each basho boundary",
        "forecast_domain": "canonical B-family W/L bout selection",
        "rated_bout_count": selection.rated_bout_count,
        "policies": [NONE, LEGACY, WHOLE],
        "whole_population_rule": "uniform shift to initial active mean after population formation and after bouts",
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    findings = _findings(summaries, comparisons)
    (args.output / "findings.md").write_text(findings, encoding="utf-8")
    print(findings, flush=True)
    return 0


def _assert_same_domain(
    legacy: tuple[ForecastRow, ...], whole: tuple[ForecastRow, ...]
) -> None:
    keys = lambda rows: tuple((r.date, r.day, r.rikishi_a, r.rikishi_b) for r in rows)
    if keys(legacy) != keys(whole):
        raise AssertionError("Population-policy forecast domains differ")


def _findings(summaries, comparisons) -> str:
    all_rows = [row for row in summaries if row["population"] == "all"]
    all_differences = [row for row in comparisons if row["population"] == "all"]
    lines = [
        "# Exact B-family BKP1 population-policy predictive comparison",
        "",
        "All BKP1 variants use canonical P1, q=400, divisional k and the exact same",
        "canonical W/L forecast domain. Negative differences favour whole-population",
        "mean preservation.",
        "",
        "| Model | Bouts | Log loss | Brier loss | ECE |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in all_rows:
        lines.append(
            f"| {row['model']} | {row['bout_count']:,} | {row['mean_log_loss']:.6f} | "
            f"{row['mean_brier_loss']:.6f} | {row['expected_calibration_error']:.6f} |"
        )
    lines.extend([
        "",
        "| Comparator | Whole-population log difference | 95% interval | Brier difference |",
        "|---|---:|---:|---:|",
    ])
    for row in all_differences:
        lines.append(
            f"| {row['comparator']} | {row['mean_log_difference']:+.6f} | "
            f"[{row['log_lower']:+.6f}, {row['log_upper']:+.6f}] | "
            f"{row['mean_brier_difference']:+.6f} |"
        )
    lines.extend([
        "",
        "## Rating maturity",
        "",
        "| Population | Bouts | Whole minus none | Whole minus legacy | Whole minus old B_kP |",
        "|---|---:|---:|---:|---:|",
    ])
    wanted = (
        "new_entrant", "career_experience_under_30", "career_experience_30_59",
        "career_experience_60_119", "career_experience_120_239",
        "career_experience_240_359", "career_experience_360_479",
        "career_experience_480_plus",
    )
    for name in wanted:
        none_row = next(
            item for item in comparisons
            if item["population"] == name and item["comparator"] == NONE
        )
        legacy_row = next(
            item for item in comparisons
            if item["population"] == name and item["comparator"] == LEGACY
        )
        old_row = next(
            item for item in comparisons
            if item["population"] == name and item["comparator"] == OLD
        )
        lines.append(
            f"| {name} | {legacy_row['bout_count']:,} | "
            f"{none_row['mean_log_difference']:+.6f} | "
            f"{legacy_row['mean_log_difference']:+.6f} | "
            f"{old_row['mean_log_difference']:+.6f} |"
        )
    return "\n".join(lines) + "\n"


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _date(value: str) -> Date:
    year, month = value.split("/")
    return Date(Year(int(year)), Month(int(month)))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--end", default="2026/07", metavar="YYYY/MM")
    parser.add_argument("--prior", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--old-prior", type=Path, default=DEFAULT_OLD_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
