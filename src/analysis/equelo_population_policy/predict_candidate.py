"""Retrospective q=400 predictive gate for the support-alpha=1 prior."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Iterable

from src.analysis.elo_model_selection.evaluation import _population_indices
from src.analysis.elo_model_selection.model import (
    AdoptedPrior,
    ComparisonDefinition,
    ForecastRow,
    MODEL_SPECS,
    ModelSpec,
    _context,
    _run_model,
    load_adopted_prior,
    rank_pair,
    score,
)
from src.analysis.equelo.expt1.params import load_divisional_k_fn
from src.analysis.prediction.bouts import select_rated_bouts
from src.infra.persistence.new_sumo_serialiser import load_history_with_annotations
from src.sumo_core.BasicPrimitives import Month, Year
from src.sumo_core.Chii import Chii
from src.sumo_core.History import Date


DEFAULT_CANDIDATE_PRIOR = Path(
    "files/output/analysis/equelo_population_policy/recentering/prior_comparison.csv"
)
DEFAULT_OLD_PRIOR = Path(
    "files/output/Equelo/boundary_reconciliation/"
    "2026-08-19_lower_banzuke_merge/paired_literal_chii_merge_candidate.csv"
)
DEFAULT_K_CONFIG = Path("files/input/elo_fide.json")
DEFAULT_OUTPUT = Path(
    "files/output/analysis/equelo_population_policy/prediction_q400"
)
MODEL_ORDER = ("B", "B_k", "B_P", "B_kP", "B_kP1")


@dataclass(frozen=True, slots=True)
class PriorConversion:
    source_row_count: int
    pair_count: int
    singleton_pair_count: int
    fallback_rating: float


def load_alpha_prior(
    path: Path = DEFAULT_CANDIDATE_PRIOR,
    *,
    variant: str = "support_1",
) -> tuple[AdoptedPrior, PriorConversion]:
    """Pair a side-specific recentering result for the existing prior consumer."""

    resolved = path.resolve()
    grouped: dict[str, list[float]] = defaultdict(list)
    with resolved.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        has_variant = "variant" in (reader.fieldnames or ())
        for row in reader:
            if has_variant and row["variant"] != variant:
                continue
            grouped[rank_pair(Chii.from_str(row["chii"]))].append(float(row["rating"]))
    if not grouped:
        raise ValueError(f"No {variant!r} rows in candidate prior: {resolved}")
    ratings = {
        pair: sum(values) / len(values)
        for pair, values in grouped.items()
    }
    conversion = PriorConversion(
        source_row_count=sum(len(values) for values in grouped.values()),
        pair_count=len(ratings),
        singleton_pair_count=sum(len(values) == 1 for values in grouped.values()),
        fallback_rating=min(ratings.values()),
    )
    return (
        AdoptedPrior(
            source_path=str(resolved),
            sha256=_sha256(resolved),
            rating_by_pair=ratings,
            fallback_rating=conversion.fallback_rating,
        ),
        conversion,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    history_zip = args.history_zip.resolve()
    history = load_history_with_annotations(str(history_zip.with_suffix("")))
    definition = ComparisonDefinition(
        start_date=Date(Year(1989), Month(1)),
        end_date=_date(args.end),
        q=400.0,
        bootstrap_resamples=args.bootstrap_resamples,
        calibration_bin_width=args.calibration_bin_width,
        calibration_min_bin_participants=args.calibration_min_bin_participants,
    )
    old_prior = load_adopted_prior(args.old_prior)
    candidate_prior, conversion = load_alpha_prior(args.candidate_prior)

    selection = select_rated_bouts(
        history,
        start_date=definition.start_date,
        end_date=definition.end_date,
    )
    contexts = tuple(_context(history, bout) for bout in selection.bouts)
    divisional_k = load_divisional_k_fn(args.k_config.resolve())
    candidate_spec = ModelSpec(  # type: ignore[arg-type]
        "B_kP1", divisional_k=True, informed_prior=True
    )
    print("[B_kP1] running q=400 candidate forecasts", flush=True)
    candidate = _run_model(
        contexts, definition, candidate_spec, candidate_prior, divisional_k
    )
    populations = _population_indices(candidate.forecasts)
    candidate_losses = tuple(score(row) for row in candidate.forecasts)

    summaries = _summaries(
        "B_kP1", candidate.forecasts, candidate_losses, populations, definition
    )
    comparisons: list[dict[str, object]] = []
    for spec in MODEL_SPECS:
        print(f"[{spec.name}] running q=400 comparator forecasts", flush=True)
        comparator = _run_model(contexts, definition, spec, old_prior, divisional_k)
        comparator_losses = tuple(score(row) for row in comparator.forecasts)
        summaries.extend(
            _summaries(
                spec.name,
                comparator.forecasts,
                comparator_losses,
                populations,
                definition,
            )
        )
        comparisons.extend(
            _comparisons(
                candidate.forecasts,
                candidate_losses,
                comparator_losses,
                populations,
                definition,
                comparator=spec.name,
            )
        )

    summaries.sort(
        key=lambda row: (
            list(populations).index(str(row["population"])),
            MODEL_ORDER.index(str(row["model"])),
        )
    )
    comparisons.sort(
        key=lambda row: (
            list(populations).index(str(row["population"])),
            MODEL_ORDER.index(str(row["comparator"])),
        )
    )
    args.output.mkdir(parents=True, exist_ok=True)
    _write_csv(args.output / "summary.csv", summaries)
    _write_csv(args.output / "comparisons.csv", comparisons)
    manifest = _manifest(
        args,
        history_zip,
        definition,
        selection,
        old_prior,
        candidate_prior,
        conversion,
    )
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    candidate_source_manifest = args.candidate_prior.parent / "manifest.json"
    candidate_source_q = json.loads(
        candidate_source_manifest.read_text(encoding="utf-8")
    )["q"]
    findings = _findings(
        summaries,
        comparisons,
        definition,
        candidate_source_q=float(candidate_source_q),
    )
    (args.output / "findings.md").write_text(findings, encoding="utf-8")
    print(findings, flush=True)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", required=True, type=Path)
    parser.add_argument("--end", default="2026/07", metavar="YYYY/MM")
    parser.add_argument("--candidate-prior", type=Path, default=DEFAULT_CANDIDATE_PRIOR)
    parser.add_argument("--old-prior", type=Path, default=DEFAULT_OLD_PRIOR)
    parser.add_argument("--k-config", type=Path, default=DEFAULT_K_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--calibration-bin-width", type=float, default=0.05)
    parser.add_argument("--calibration-min-bin-participants", type=int, default=100)
    return parser


def _summaries(
    model: str,
    forecasts: tuple[ForecastRow, ...],
    losses: tuple[tuple[float, float], ...],
    populations: dict[str, tuple[int, ...]],
    definition: ComparisonDefinition,
) -> list[dict[str, object]]:
    result = []
    for population, indices in populations.items():
        count = len(indices)
        mean_log = sum(losses[index][0] for index in indices) / count
        mean_brier = sum(losses[index][1] for index in indices) / count
        result.append({
            "population": population,
            "model": model,
            "bout_count": count,
            "mean_log_loss": mean_log,
            "mean_brier_loss": mean_brier,
            "log_difference_from_50": mean_log - math.log(2.0),
            "brier_difference_from_50": mean_brier - 0.25,
            "expected_calibration_error": _ece(
                forecasts, indices, definition.calibration_bin_width
            ),
        })
    return result


def _comparisons(
    forecasts: tuple[ForecastRow, ...],
    candidate_losses: tuple[tuple[float, float], ...],
    comparator_losses: tuple[tuple[float, float], ...],
    populations: dict[str, tuple[int, ...]],
    definition: ComparisonDefinition,
    *,
    comparator: str,
) -> list[dict[str, object]]:
    result = []
    for population_index, (population, indices) in enumerate(populations.items()):
        log_blocks = _difference_blocks(
            forecasts, candidate_losses, comparator_losses, indices, metric=0
        )
        brier_blocks = _difference_blocks(
            forecasts, candidate_losses, comparator_losses, indices, metric=1
        )
        log_interval = _bootstrap_blocks(
            log_blocks,
            definition,
            seed_offset=1000 + population_index * 20 + MODEL_ORDER.index(comparator),
        )
        brier_interval = _bootstrap_blocks(
            brier_blocks,
            definition,
            seed_offset=11000 + population_index * 20 + MODEL_ORDER.index(comparator),
        )
        mean_log = sum(block[0] for block in log_blocks) / sum(block[1] for block in log_blocks)
        mean_brier = sum(block[0] for block in brier_blocks) / sum(block[1] for block in brier_blocks)
        result.append({
            "population": population,
            "model": "B_kP1",
            "comparator": comparator,
            "bout_count": len(indices),
            "mean_log_difference": mean_log,
            "log_lower": log_interval[0],
            "log_upper": log_interval[1],
            "log_one_sided_upper": log_interval[2],
            "mean_brier_difference": mean_brier,
            "brier_lower": brier_interval[0],
            "brier_upper": brier_interval[1],
            "brier_one_sided_upper": brier_interval[2],
        })
    return result


def _difference_blocks(
    forecasts: tuple[ForecastRow, ...],
    candidate: tuple[tuple[float, float], ...],
    comparator: tuple[tuple[float, float], ...],
    indices: tuple[int, ...],
    *,
    metric: int,
) -> tuple[tuple[float, int], ...]:
    grouped: dict[Date, list[float]] = defaultdict(list)
    for index in indices:
        grouped[forecasts[index].date].append(
            candidate[index][metric] - comparator[index][metric]
        )
    return tuple(
        (sum(grouped[date]), len(grouped[date]))
        for date in sorted(grouped)
    )


def _bootstrap_blocks(
    blocks: tuple[tuple[float, int], ...],
    definition: ComparisonDefinition,
    *,
    seed_offset: int,
) -> tuple[float, float, float]:
    rng = random.Random(definition.bootstrap_seed + seed_offset)
    samples = []
    for _ in range(definition.bootstrap_resamples):
        selected = tuple(rng.choice(blocks) for _ in blocks)
        samples.append(
            sum(block_sum for block_sum, _ in selected)
            / sum(block_count for _, block_count in selected)
        )
    samples.sort()
    count = len(samples)
    alpha = 1.0 - definition.confidence_level
    return (
        samples[int((alpha / 2.0) * (count - 1))],
        samples[int((1.0 - alpha / 2.0) * (count - 1))],
        samples[int(definition.confidence_level * (count - 1))],
    )


def _ece(
    forecasts: tuple[ForecastRow, ...],
    indices: tuple[int, ...],
    width: float,
) -> float:
    bin_count = round(1.0 / width)
    probability_sums = [0.0] * bin_count
    win_counts = [0] * bin_count
    counts = [0] * bin_count
    for index in indices:
        row = forecasts[index]
        for probability, outcome in (
            (row.probability_a_wins, int(row.a_won)),
            (1.0 - row.probability_a_wins, int(not row.a_won)),
        ):
            bin_index = min(int(probability / width), bin_count - 1)
            probability_sums[bin_index] += probability
            win_counts[bin_index] += outcome
            counts[bin_index] += 1
    total = sum(counts)
    return sum(
        count * abs(win_counts[index] / count - probability_sums[index] / count)
        for index, count in enumerate(counts)
        if count
    ) / total


def _manifest(
    args,
    history_zip: Path,
    definition: ComparisonDefinition,
    selection,
    old_prior: AdoptedPrior,
    candidate_prior: AdoptedPrior,
    conversion: PriorConversion,
) -> dict[str, object]:
    candidate_manifest = args.candidate_prior.parent / "manifest.json"
    with args.candidate_prior.open(newline="", encoding="utf-8") as stream:
        candidate_columns = next(csv.reader(stream))
    source_variant = "support_1" if "variant" in candidate_columns else "canonical_single_variant"
    return {
        "experiment": "Retrospective q=400 predictive gate for B_kP1",
        "status": "retrospective diagnostic; both prior artifacts are future-informed",
        "history_source": {"path": str(history_zip), "sha256": _sha256(history_zip)},
        "definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "q_model": definition.q,
            "constant_k": definition.constant_k,
            "bootstrap_resamples": definition.bootstrap_resamples,
            "confidence_level": definition.confidence_level,
            "noninferiority_fraction": definition.noninferiority_fraction,
        },
        "candidate_prior": {
            "path": candidate_prior.source_path,
            "sha256": candidate_prior.sha256,
            "source_manifest": str(candidate_manifest.resolve()),
            "source_manifest_sha256": _sha256(candidate_manifest),
            "source_variant": source_variant,
            "source_q": json.loads(candidate_manifest.read_text(encoding="utf-8"))["q"],
            "conversion": {
                **asdict(conversion),
                "rule": "unweighted mean of available east/west literal-chii ratings",
                "unranked_fallback": "minimum paired candidate rating",
            },
        },
        "old_prior": {
            "path": old_prior.source_path,
            "sha256": old_prior.sha256,
            "pair_count": len(old_prior.rating_by_pair),
            "fallback_rating": old_prior.fallback_rating,
        },
        "selection": {
            "raw_result_count": selection.raw_result_count,
            "rated_bout_count": selection.rated_bout_count,
            "excluded_fusen_count": selection.excluded_fusen_count,
            "excluded_draw_count": selection.excluded_draw_count,
        },
        "outputs": {"summary": "summary.csv", "comparisons": "comparisons.csv", "findings": "findings.md"},
    }


def _findings(
    summaries: list[dict[str, object]],
    comparisons: list[dict[str, object]],
    definition: ComparisonDefinition,
    *,
    candidate_source_q: float,
) -> str:
    all_rows = [row for row in summaries if row["population"] == "all"]
    comparison_rows = [row for row in comparisons if row["population"] == "all"]
    b = next(row for row in all_rows if row["model"] == "B")
    versus_b = next(row for row in comparison_rows if row["comparator"] == "B")
    margin = definition.noninferiority_fraction * max(
        0.0, math.log(2.0) - float(b["mean_log_loss"])
    )
    noninferior = float(versus_b["log_one_sided_upper"]) < margin
    lines = [
        "# BKP1 q=400 retrospective predictive gate",
        "",
        f"The candidate uses the alpha=1 prior produced by the q={candidate_source_q:g} fixed-point",
        "diagnostic, paired by an unweighted east/west mean, inside the exact",
        "q=400 forecast/update contract used by the established B-family comparison.",
        "Both informed priors are future-informed, so this is retrospective model",
        "selection evidence rather than prospective validation.",
        "",
        "## Aggregate result",
        "",
        "| Model | Mean log loss | Mean Brier loss | ECE |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(
        f"| {row['model']} | {float(row['mean_log_loss']):.6f} | "
        f"{float(row['mean_brier_loss']):.6f} | "
        f"{float(row['expected_calibration_error']):.6f} |"
        for row in all_rows
    )
    lines.extend([
        "",
        "Negative paired differences favour BKP1.",
        "",
        "| Comparator | Log difference | 95% interval | One-sided 95% upper | Brier difference |",
        "|---|---:|---:|---:|---:|",
    ])
    lines.extend(
        f"| {row['comparator']} | {float(row['mean_log_difference']):+.6f} | "
        f"[{float(row['log_lower']):+.6f}, {float(row['log_upper']):+.6f}] | "
        f"{float(row['log_one_sided_upper']):+.6f} | "
        f"{float(row['mean_brier_difference']):+.6f} |"
        for row in comparison_rows
    )
    lines.extend([
        "",
        f"The existing non-inferiority margin versus B is {margin:.6f}. BKP1 "
        f"{'passes' if noninferior else 'does not pass'} that retrospective gate "
        f"(one-sided upper {float(versus_b['log_one_sided_upper']):.6f}).",
        "",
        "## Rating-maturity result",
        "",
        "| Population | Bouts | BKP1 log loss | Difference from old B_kP |",
        "|---|---:|---:|---:|",
    ])
    for population in (
        "new_entrant",
        "career_experience_under_30",
        "career_experience_30_59",
        "career_experience_60_119",
        "career_experience_120_239",
        "career_experience_240_359",
        "career_experience_360_479",
        "career_experience_480_plus",
    ):
        row = next(item for item in summaries if item["population"] == population and item["model"] == "B_kP1")
        comparison = next(item for item in comparisons if item["population"] == population and item["comparator"] == "B_kP")
        lines.append(
            f"| {population} | {int(row['bout_count']):,} | "
            f"{float(row['mean_log_loss']):.6f} | "
            f"{float(comparison['mean_log_difference']):+.6f} |"
        )
    lines.append("")
    return "\n".join(lines)


def _write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    iterator = iter(rows)
    first = next(iterator)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(iterator)


def _date(value: str) -> Date:
    year, month = (int(part) for part in value.split("/"))
    return Date(Year(year), Month(month))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
