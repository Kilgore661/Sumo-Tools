"""Evaluate P1-WL as an initialiser and inside exact Elo-89."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
from time import perf_counter

from src.analysis.elo89.output import write_elo89_outputs
from src.analysis.elo89.replay import Q, replay_elo89
from src.analysis.elo_model_selection.evaluation import _calibration, _population_indices
from src.analysis.elo_model_selection.model import (
    ComparisonDefinition,
    ModelSpec,
    _context,
    _run_model,
    load_adopted_prior,
    score,
)
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.equelo_population_policy.predict_candidate import (
    _bootstrap_blocks,
    _difference_blocks,
    _ece,
    load_alpha_prior,
)
from src.analysis.prediction.bouts import select_rated_bouts
from src.sumo_core.BasicEnums import Division, MSD
from src.sumo_core.History import Date, History

from .audit import load_history
from .p1_wl import history_fingerprint


DEFAULT_OUTPUT_PARENT = Path(
    "src/validation/elo89-expert-account/Matters Arising/Kimarite/"
    "P1-WL Evaluation/output"
)
DEFAULT_PUBLISHED_P1 = Path("files/output/analysis/equelo_bkp1/prior.csv")
DEFAULT_OLD_PRIOR = Path(
    "files/output/Equelo/boundary_reconciliation/"
    "2026-08-19_lower_banzuke_merge/paired_literal_chii_merge_candidate.csv"
)
DEFAULT_K = Path("files/input/elo_fide.json")
ELO89_START = Date.from_ints(1989, 1)


def run_evaluation(
    history: History,
    *,
    output_root: Path,
    published_p1_path: Path,
    p1_path: Path,
    p1_wl_path: Path,
    old_prior_path: Path,
    k_config_path: Path,
    bootstrap_resamples: int = 2000,
    history_source: dict[str, object] | None = None,
) -> Path:
    """Run the declared initialisation and exact-Elo-89 comparisons."""

    started = perf_counter()
    if output_root.exists():
        raise FileExistsError(f"Refusing to overwrite evaluation: {output_root}")
    if bootstrap_resamples < 1:
        raise ValueError("bootstrap_resamples must be positive")
    dates = sorted(history)
    if not dates or dates[0] != ELO89_START:
        raise ValueError("P1-WL evaluation History must begin at 1989/01")

    published, published_conversion = load_alpha_prior(published_p1_path)
    p1, p1_conversion = load_alpha_prior(p1_path)
    p1_wl, p1_wl_conversion = load_alpha_prior(p1_wl_path)
    old = load_adopted_prior(old_prior_path)
    if set(p1.rating_by_pair) != set(p1_wl.rating_by_pair):
        raise ValueError("Same-History P1 and P1-WL paired domains differ")
    if set(published.rating_by_pair) != set(p1.rating_by_pair):
        raise ValueError("Published and same-History P1 paired domains differ")

    output_root.mkdir(parents=True)
    initial_root = output_root / "initialisation"
    elo_root = output_root / "elo89"
    initial_root.mkdir()
    elo_root.mkdir()

    definition = ComparisonDefinition(
        start_date=dates[0],
        end_date=dates[-1],
        q=Q,
        bootstrap_resamples=bootstrap_resamples,
    )
    selection = select_rated_bouts(
        history, start_date=definition.start_date, end_date=definition.end_date
    )
    contexts = tuple(_context(history, bout) for bout in selection.bouts)
    divisional_k = load_divisional_k_fn(k_config_path.resolve())

    initial_models = _run_initialisation_models(
        contexts, definition, divisional_k, old, published, p1, p1_wl
    )
    _assert_forecast_domains(initial_models)
    populations = _population_indices(initial_models["B"])
    initial_summaries, initial_comparisons, calibration = _evaluate_models(
        initial_models, populations, definition, candidate="B_kP1-WL"
    )
    _write_csv(initial_root / "summary.csv", initial_summaries)
    _write_csv(initial_root / "paired_comparisons.csv", initial_comparisons)
    _write_csv(initial_root / "calibration.csv", calibration)
    (initial_root / "findings.md").write_text(
        _initial_findings(initial_summaries, initial_comparisons), encoding="utf-8"
    )

    elo_runs = {}
    for label, prior in (
        ("published-p1", published),
        ("p1", p1),
        ("p1-wl", p1_wl),
    ):
        print(f"[elo89/{label}] replaying {len(contexts):,} bouts", flush=True)
        run = replay_elo89(
            history=history,
            start_date=dates[0],
            end_date=dates[-1],
            prior=prior,
            divisional_k=divisional_k,
            q=Q,
        )
        elo_runs[label] = run
        write_elo89_outputs(
            run=run,
            prior=prior,
            output_root=elo_root / label,
            history_source="P1-WL frozen validation History",
            start_date=dates[0],
            end_date=dates[-1],
            k_config_path=k_config_path.resolve(),
            q=Q,
        )
    _assert_elo_domains(elo_runs)

    (
        elo_summaries,
        elo_comparisons,
        probability_rows,
        probability_summaries,
    ) = _evaluate_elo_runs(
        elo_runs, definition
    )
    _write_csv(elo_root / "forecast_summary.csv", elo_summaries)
    _write_csv(elo_root / "forecast_comparison.csv", elo_comparisons)
    _write_csv(
        elo_root / "probability_difference_summary.csv", probability_summaries
    )
    _write_csv(
        elo_root / "largest_probability_differences.csv",
        sorted(
            probability_rows,
            key=lambda row: float(row["absolute_probability_difference"]),
            reverse=True,
        )[:100],
    )

    rating_summaries, largest_ratings = _rating_comparisons(elo_runs, history)
    _write_csv(elo_root / "rating_difference_summary.csv", rating_summaries)
    _write_csv(elo_root / "largest_rating_differences.csv", largest_ratings)
    _write_csv(
        elo_root / "rating_difference_by_basho.csv",
        _rating_by_basho(elo_runs["p1"], elo_runs["p1-wl"]),
    )
    _write_csv(
        elo_root / "rating_difference_by_division.csv",
        _rating_by_division(elo_runs["p1"], elo_runs["p1-wl"], history),
    )
    _write_csv(
        elo_root / "rating_difference_by_maturity.csv",
        _rating_by_maturity(elo_runs["p1"], elo_runs["p1-wl"]),
    )
    _write_csv(
        elo_root / "rating_difference_by_entry_status.csv",
        _rating_by_entry_status(elo_runs["p1"], elo_runs["p1-wl"]),
    )
    _write_csv(
        elo_root / "publication_comparison.csv",
        _publication_rows(elo_runs, dates[-1]),
    )
    (elo_root / "findings.md").write_text(
        _elo_findings(elo_summaries, elo_comparisons, rating_summaries),
        encoding="utf-8",
    )

    elapsed = perf_counter() - started
    source = dict(history_source or {"kind": "provided History"})
    source["selected_history_sha256"] = history_fingerprint(history)
    manifest = {
        "schema_version": 1,
        "experiment": "P1-WL initialisation and exact Elo-89 evaluation",
        "history": {
            **source,
            "start": str(dates[0]),
            "end": str(dates[-1]),
            "basho_count": len(dates),
        },
        "selection": {
            "raw_result_count": selection.raw_result_count,
            "rated_bout_count": selection.rated_bout_count,
            "excluded_fusen_count": selection.excluded_fusen_count,
            "excluded_draw_count": selection.excluded_draw_count,
        },
        "model": {
            "q": Q,
            "k_config": _file_identity(k_config_path),
            "bootstrap_unit": "basho",
            "bootstrap_resamples": bootstrap_resamples,
            "bootstrap_seed": definition.bootstrap_seed,
            "calibration_bin_width": definition.calibration_bin_width,
            "calibration_min_bin_participants": definition.calibration_min_bin_participants,
        },
        "priors": {
            "published_p1": _prior_identity(published_p1_path, published_conversion),
            "same_history_p1": _prior_identity(p1_path, p1_conversion),
            "p1_wl": _prior_identity(p1_wl_path, p1_wl_conversion),
            "old_informed": _file_identity(old_prior_path),
            "pairing_rule": "unweighted mean of available east/west literal-chii ratings",
            "fallback_rule": "minimum paired rating",
        },
        "controlled_contrasts": {
            "kimarite_effect": "p1-wl minus same-History p1",
            "source_refit_drift": "same-History p1 minus published p1",
            "publication_change": "p1-wl minus published p1",
        },
        "runtime": {"total_seconds": elapsed},
        "outputs": {
            "initialisation": "initialisation",
            "elo89": "elo89",
        },
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Total run time: {elapsed:.3f} seconds", flush=True)
    return output_root


def _run_initialisation_models(contexts, definition, divisional_k, old, published, p1, p1_wl):
    definitions = (
        ("B", False, False, old),
        ("B_k", True, False, old),
        ("old_B_kP", True, True, old),
        ("published_B_kP1", True, True, published),
        ("B_kP1", True, True, p1),
        ("B_kP1-WL", True, True, p1_wl),
    )
    result = {}
    for label, uses_divisional_k, informed, prior in definitions:
        print(f"[initialisation/{label}] running forecasts", flush=True)
        spec = ModelSpec(label, divisional_k=uses_divisional_k, informed_prior=informed)  # type: ignore[arg-type]
        result[label] = _run_model(contexts, definition, spec, prior, divisional_k).forecasts
    return result


def _evaluate_models(models, populations, definition, *, candidate):
    losses = {name: tuple(score(row) for row in rows) for name, rows in models.items()}
    summaries = []
    calibration = []
    for population, indices in populations.items():
        for name, rows in models.items():
            selected = tuple(rows[index] for index in indices)
            values = losses[name]
            summaries.append(_summary_row(population, name, values, indices, rows, definition))
            bins, _ = _calibration(
                population,
                name,  # type: ignore[arg-type]
                selected,
                definition.calibration_bin_width,
                definition.calibration_min_bin_participants,
            )
            calibration.extend(asdict(row) for row in bins)
    comparisons = []
    candidate_rows = models[candidate]
    for population_index, (population, indices) in enumerate(populations.items()):
        for comparator_index, comparator in enumerate(models):
            if comparator == candidate:
                continue
            comparisons.append(
                _paired_row(
                    population,
                    candidate,
                    comparator,
                    candidate_rows,
                    losses[candidate],
                    losses[comparator],
                    indices,
                    definition,
                    seed_offset=1000 + population_index * 20 + comparator_index,
                )
            )
    return summaries, comparisons, calibration


def _evaluate_elo_runs(runs, definition):
    models = {name: run.forecasts for name, run in runs.items()}
    populations = _population_indices(models["p1"])  # type: ignore[arg-type]
    summaries, comparisons, _ = _evaluate_models(
        models, populations, definition, candidate="p1-wl"
    )
    p1 = models["p1"]
    candidate = models["p1-wl"]
    probability_rows = []
    for left, right in zip(p1, candidate, strict=True):
        difference = right.probability_a_wins - left.probability_a_wins
        probability_rows.append(
            {
                "date": str(left.date),
                "day": int(left.day),
                "rikishi_a": int(left.rikishi_a),
                "rikishi_b": int(left.rikishi_b),
                "chii_a": "" if left.chii_a is None else str(left.chii_a),
                "chii_b": "" if left.chii_b is None else str(left.chii_b),
                "p1_probability": left.probability_a_wins,
                "p1_wl_probability": right.probability_a_wins,
                "probability_difference": difference,
                "absolute_probability_difference": abs(difference),
                "rated_bouts_a_before": left.rated_bouts_a_before,
                "rated_bouts_b_before": left.rated_bouts_b_before,
            }
        )
    probability_summaries = []
    for population, indices in populations.items():
        differences = [
            probability_rows[index]["probability_difference"] for index in indices
        ]
        probability_summaries.append(
            {"population": population, **_difference_stats(differences)}
        )
    return summaries, comparisons, probability_rows, probability_summaries


def _summary_row(population, model, losses, indices, rows, definition):
    return {
        "population": population,
        "model": model,
        "bout_count": len(indices),
        "mean_log_loss": sum(losses[i][0] for i in indices) / len(indices),
        "mean_brier_loss": sum(losses[i][1] for i in indices) / len(indices),
        "expected_calibration_error": _ece(rows, indices, definition.calibration_bin_width),
    }


def _paired_row(population, model, comparator, rows, candidate_losses, comparator_losses, indices, definition, *, seed_offset):
    log_blocks = _difference_blocks(rows, candidate_losses, comparator_losses, indices, metric=0)
    brier_blocks = _difference_blocks(rows, candidate_losses, comparator_losses, indices, metric=1)
    log_interval = _bootstrap_blocks(log_blocks, definition, seed_offset=seed_offset)
    brier_interval = _bootstrap_blocks(
        brier_blocks, definition, seed_offset=10000 + seed_offset
    )
    return {
        "population": population,
        "model": model,
        "comparator": comparator,
        "bout_count": len(indices),
        "mean_log_difference": sum(value for value, _ in log_blocks) / sum(count for _, count in log_blocks),
        "log_lower": log_interval[0],
        "log_upper": log_interval[1],
        "log_one_sided_upper": log_interval[2],
        "mean_brier_difference": sum(value for value, _ in brier_blocks) / sum(count for _, count in brier_blocks),
        "brier_lower": brier_interval[0],
        "brier_upper": brier_interval[1],
        "brier_one_sided_upper": brier_interval[2],
    }


def _assert_forecast_domains(models) -> None:
    reference_name, reference = next(iter(models.items()))
    expected = tuple(_forecast_key(row) for row in reference)
    for name, rows in models.items():
        if tuple(_forecast_key(row) for row in rows) != expected:
            raise AssertionError(f"Forecast domain differs: {reference_name} versus {name}")


def _assert_elo_domains(runs) -> None:
    _assert_forecast_domains({name: run.forecasts for name, run in runs.items()})


def _forecast_key(row):
    return str(row.date), int(row.day), int(row.rikishi_a), int(row.rikishi_b), bool(row.a_won)


def _rating_comparisons(runs, history):
    contrasts = (
        ("kimarite_effect", "p1", "p1-wl"),
        ("source_refit_drift", "published-p1", "p1"),
        ("publication_change", "published-p1", "p1-wl"),
    )
    summaries = []
    largest = []
    for contrast, left_name, right_name in contrasts:
        left = runs[left_name]
        right = runs[right_name]
        anchor_difference = right.target_mean - left.target_mean
        for stage, left_values, right_values in _stages(left, right):
            differences = []
            stage_rows = []
            for date, day, rikishi, left_rating, right_rating in _paired_states(left_values, right_values):
                difference = right_rating - left_rating
                differences.append(difference)
                chii = history[date].banzuke.rikchii.get(rikishi)
                stage_rows.append(
                    {
                        "contrast": contrast,
                        "stage": stage,
                        "date": str(date),
                        "day": "" if day is None else int(day),
                        "rikishi": int(rikishi),
                        "chii": "" if chii is None else str(chii),
                        "left_rating": left_rating,
                        "right_rating": right_rating,
                        "difference": difference,
                        "aligned_difference": difference - anchor_difference,
                        "absolute_difference": abs(difference),
                    }
                )
            stats = _difference_stats(differences)
            aligned_stats = _prefixed_stats(
                _difference_stats(
                    [difference - anchor_difference for difference in differences]
                ),
                "aligned_",
                omit=("count",),
            )
            summaries.append(
                {
                    "contrast": contrast,
                    "stage": stage,
                    "target_mean_difference": anchor_difference,
                    **stats,
                    **aligned_stats,
                }
            )
            largest.extend(sorted(stage_rows, key=lambda row: row["absolute_difference"], reverse=True)[:100])
    largest.sort(key=lambda row: row["absolute_difference"], reverse=True)
    return summaries, largest[:300]


def _stages(left, right):
    return (
        ("basho_start", left.basho_start_ratings, right.basho_start_ratings),
        ("day_end", left.day_end_ratings, right.day_end_ratings),
        ("basho_end", left.basho_end_ratings, right.basho_end_ratings),
    )


def _paired_states(left, right):
    for date in sorted(left):
        if date not in right:
            raise AssertionError(f"Missing rating date in comparison: {date}")
        left_value = left[date]
        right_value = right[date]
        if left_value and isinstance(next(iter(left_value.values())), dict):
            for day in sorted(left_value):
                yield from _paired_rating_map(date, day, left_value[day], right_value[day])
        else:
            yield from _paired_rating_map(date, None, left_value, right_value)


def _paired_rating_map(date, day, left, right):
    if set(left) != set(right):
        raise AssertionError(f"Rating-state domain differs at {date} day {day}")
    for rikishi in sorted(left):
        yield date, day, rikishi, float(left[rikishi]), float(right[rikishi])


def _difference_stats(values):
    if not values:
        raise ValueError("Cannot summarize empty differences")
    ordered = sorted(abs(value) for value in values)
    return {
        "count": len(values),
        "mean_difference": sum(values) / len(values),
        "mean_absolute_difference": sum(ordered) / len(ordered),
        "rms_difference": math.sqrt(sum(value * value for value in values) / len(values)),
        "p50_absolute_difference": _percentile(ordered, 0.50),
        "p90_absolute_difference": _percentile(ordered, 0.90),
        "p99_absolute_difference": _percentile(ordered, 0.99),
        "maximum_absolute_difference": ordered[-1],
    }


def _prefixed_stats(stats, prefix, *, omit=()):
    return {
        f"{prefix}{name}": value
        for name, value in stats.items()
        if name not in omit
    }


def _percentile(ordered, fraction):
    return ordered[round(fraction * (len(ordered) - 1))]


def _rating_by_basho(p1, p1_wl):
    rows = []
    for date in sorted(p1.basho_end_ratings):
        differences = [
            p1_wl.basho_end_ratings[date][rikishi] - rating
            for rikishi, rating in p1.basho_end_ratings[date].items()
        ]
        rows.append({"date": str(date), **_difference_stats(differences)})
    return rows


def _rating_by_division(p1, p1_wl, history):
    grouped = {}
    for date, ratings in p1.basho_end_ratings.items():
        for rikishi, rating in ratings.items():
            chii = history[date].banzuke.rikchii.get(rikishi)
            division = _division(chii)
            grouped.setdefault(division, []).append(p1_wl.basho_end_ratings[date][rikishi] - rating)
    return [{"division": division, **_difference_stats(values)} for division, values in sorted(grouped.items())]


def _rating_by_maturity(p1, p1_wl):
    counts = {}
    forecasts_by_date = {}
    for forecast in p1.forecasts:
        forecasts_by_date.setdefault(forecast.date, []).append(forecast)
    grouped = {}
    anchor_difference = p1_wl.target_mean - p1.target_mean
    for date in sorted(p1.basho_end_ratings):
        for forecast in forecasts_by_date.get(date, ()):
            counts[forecast.rikishi_a] = forecast.rated_bouts_a_before + 1
            counts[forecast.rikishi_b] = forecast.rated_bouts_b_before + 1
        for rikishi, rating in p1.basho_end_ratings[date].items():
            population = _maturity_label(counts.get(rikishi, 0))
            difference = p1_wl.basho_end_ratings[date][rikishi] - rating
            grouped.setdefault(population, []).append(difference)
    return _grouped_rating_rows(grouped, anchor_difference, "population")


def _rating_by_entry_status(p1, p1_wl):
    grouped = {}
    previous = set()
    anchor_difference = p1_wl.target_mean - p1.target_mean
    for date in sorted(p1.basho_end_ratings):
        active = set(p1.basho_end_ratings[date])
        for rikishi, rating in p1.basho_end_ratings[date].items():
            status = "continuing" if rikishi in previous else "initialised_this_basho"
            difference = p1_wl.basho_end_ratings[date][rikishi] - rating
            grouped.setdefault(status, []).append(difference)
        previous = active
    return _grouped_rating_rows(grouped, anchor_difference, "entry_status")


def _grouped_rating_rows(grouped, anchor_difference, label):
    rows = []
    for name, values in grouped.items():
        aligned = [value - anchor_difference for value in values]
        rows.append(
            {
                label: name,
                **_difference_stats(values),
                **_prefixed_stats(
                    _difference_stats(aligned), "aligned_", omit=("count",)
                ),
            }
        )
    return rows


def _maturity_label(count):
    if count == 0:
        return "no_prior_rated_bouts"
    if count < 30:
        return "under_30"
    if count < 60:
        return "30_59"
    if count < 120:
        return "60_119"
    if count < 240:
        return "120_239"
    if count < 360:
        return "240_359"
    if count < 480:
        return "360_479"
    return "480_plus"


def _division(chii):
    if chii is None:
        return "off_banzuke"
    return "Makuuchi" if isinstance(chii.level, MSD) else chii.level.name.capitalize()


def _publication_rows(runs, final_date):
    current = {name: run.basho_end_ratings[final_date] for name, run in runs.items()}
    peaks = {name: _peaks(run.day_end_ratings) for name, run in runs.items()}
    rows = []
    common_current = set.intersection(*(set(values) for values in current.values()))
    current_ranks = {name: _ranks(values) for name, values in current.items()}
    for rikishi in sorted(common_current):
        rows.append(_publication_row("current", rikishi, current, current_ranks))
    common_peaks = set.intersection(*(set(values) for values in peaks.values()))
    peak_values = {name: {rid: value[0] for rid, value in values.items()} for name, values in peaks.items()}
    peak_ranks = {name: _ranks(values) for name, values in peak_values.items()}
    for rikishi in sorted(common_peaks):
        row = _publication_row("peak", rikishi, peak_values, peak_ranks)
        for name in runs:
            row[f"{name}_peak_date"] = peaks[name][rikishi][1]
            row[f"{name}_peak_day"] = peaks[name][rikishi][2]
        rows.append(row)
    return rows


def _publication_row(kind, rikishi, values, ranks):
    row = {"kind": kind, "rikishi": int(rikishi)}
    for name in values:
        row[f"{name}_rating"] = values[name][rikishi]
        row[f"{name}_rank"] = ranks[name][rikishi]
        row[f"{name}_peak_date"] = ""
        row[f"{name}_peak_day"] = ""
    row["kimarite_rating_difference"] = values["p1-wl"][rikishi] - values["p1"][rikishi]
    row["publication_rating_difference"] = values["p1-wl"][rikishi] - values["published-p1"][rikishi]
    row["kimarite_rank_change"] = ranks["p1-wl"][rikishi] - ranks["p1"][rikishi]
    row["publication_rank_change"] = ranks["p1-wl"][rikishi] - ranks["published-p1"][rikishi]
    return row


def _peaks(day_end):
    result = {}
    for date in sorted(day_end):
        for day in sorted(day_end[date]):
            for rikishi, rating in day_end[date][day].items():
                if rikishi not in result or rating > result[rikishi][0]:
                    result[rikishi] = (rating, str(date), int(day))
    return result


def _ranks(values):
    return {rikishi: index for index, rikishi in enumerate(sorted(values, key=lambda rid: (-values[rid], int(rid))), start=1)}


def _initial_findings(summaries, comparisons):
    all_rows = {row["model"]: row for row in summaries if row["population"] == "all"}
    versus = {row["comparator"]: row for row in comparisons if row["population"] == "all"}
    lines = [
        "# P1-WL initialisation comparison", "",
        "Negative paired differences favour P1-WL.", "",
        "| Model | Log loss | Brier loss | ECE |", "|---|---:|---:|---:|",
    ]
    lines.extend(f"| {name} | {row['mean_log_loss']:.6f} | {row['mean_brier_loss']:.6f} | {row['expected_calibration_error']:.6f} |" for name, row in all_rows.items())
    lines.extend(["", "| Comparator | P1-WL log difference | 95% interval |", "|---|---:|---:|"])
    lines.extend(f"| {name} | {row['mean_log_difference']:+.6f} | [{row['log_lower']:+.6f}, {row['log_upper']:+.6f}] |" for name, row in versus.items())
    return "\n".join(lines) + "\n"


def _elo_findings(summaries, comparisons, rating_summaries):
    all_rows = {row["model"]: row for row in summaries if row["population"] == "all"}
    versus = {row["comparator"]: row for row in comparisons if row["population"] == "all"}
    causal = next(row for row in rating_summaries if row["contrast"] == "kimarite_effect" and row["stage"] == "basho_end")
    return "\n".join([
        "# Exact Elo-89 P1-WL comparison", "",
        "Negative paired differences favour P1-WL.", "",
        "| Prior | Log loss | Brier loss | ECE |", "|---|---:|---:|---:|",
        *(f"| {name} | {row['mean_log_loss']:.6f} | {row['mean_brier_loss']:.6f} | {row['expected_calibration_error']:.6f} |" for name, row in all_rows.items()),
        "", "| Comparator | P1-WL log difference | 95% interval |", "|---|---:|---:|",
        *(f"| {name} | {row['mean_log_difference']:+.6f} | [{row['log_lower']:+.6f}, {row['log_upper']:+.6f}] |" for name, row in versus.items()),
        "", f"Across basho-end states, the causal P1-WL-minus-P1 mean absolute rating difference is {causal['mean_absolute_difference']:.3f} and the maximum is {causal['maximum_absolute_difference']:.3f}.", "",
    ])


def _prior_identity(path, conversion):
    result = {**_file_identity(path), "pair_count": conversion.pair_count, "fallback_rating": conversion.fallback_rating}
    manifest = path.parent / "manifest.json"
    if manifest.is_file():
        result["source_manifest"] = _file_identity(manifest)
    root_manifest = path.parent.parent / "manifest.json"
    if root_manifest.is_file():
        result["comparison_manifest"] = _file_identity(root_manifest)
    return result


def _file_identity(path):
    resolved = path.resolve()
    return {"path": str(resolved), "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}


def _write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _selected_history(history, start, end):
    selected = History({date: history[date] for date in sorted(history) if date >= start and (end is None or date <= end)})
    if not selected:
        raise ValueError("Selected evaluation interval is empty")
    return selected


def _parse_date(value):
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if match is None:
        raise argparse.ArgumentTypeError("expected YYYY-MM")
    return Date.from_ints(int(match.group(1)), int(match.group(2)))


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--start", type=_parse_date, default=ELO89_START)
    parser.add_argument("--end", type=_parse_date)
    parser.add_argument("--published-p1", type=Path, default=DEFAULT_PUBLISHED_P1)
    parser.add_argument("--p1", required=True, type=Path)
    parser.add_argument("--p1-wl", required=True, type=Path)
    parser.add_argument("--old-prior", type=Path, default=DEFAULT_OLD_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    full = load_history(args.history_zip)
    history = _selected_history(full, args.start, args.end)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output = args.output or DEFAULT_OUTPUT_PARENT / f"p1-wl-evaluation_{stamp}"
    source_path = args.history_zip.resolve()
    source = {"kind": "annotated History zip", **_file_identity(source_path)}
    root = run_evaluation(
        history,
        output_root=output,
        published_p1_path=args.published_p1,
        p1_path=args.p1,
        p1_wl_path=args.p1_wl,
        old_prior_path=args.old_prior,
        k_config_path=args.k_config,
        bootstrap_resamples=args.bootstrap_resamples,
        history_source=source,
    )
    print(f"Output: {root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
