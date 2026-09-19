"""Orchestrate the Ozeki promotion-prospects analysis."""

from .dataset import build_dataset
from .output import write_artifacts
from .statistics import (
    describe_groups,
    forward_validation,
    period_scores,
    score_rules,
)


def run_analysis(history, output_dir, *, source, bootstrap_samples=2000,
                 seed=20260919, progress=print):
    if bootstrap_samples < 0:
        raise ValueError("bootstrap_samples must be non-negative")

    progress("[1/8] Auditing promotions and building candidate opportunities...")
    dataset = build_dataset(history)
    progress(
        f"      {len(dataset['promotions'])} promotions; "
        f"{len(dataset['opportunities'])} candidate windows."
    )

    opportunities = dataset["opportunities"]
    progress("[2/8] Summarising total wins (complete 45-bout windows)...")
    total_values = list(range(0, 46))
    total_wins = describe_groups(opportunities, "total_wins", total_values)

    progress("[3/8] Summarising rank and component-result patterns...")
    rank_patterns = describe_groups(opportunities, "rank_pattern")
    minimum_wins = describe_groups(opportunities, "minimum_wins", list(range(16)))
    weak_position = describe_groups(opportunities, "weak_result_position")

    progress(
        f"[4/8] Scoring predeclared rules with {bootstrap_samples} "
        "rikishi-cluster resamples..."
    )
    rules = score_rules(
        opportunities, dataset["promotions"], bootstrap_samples, seed
    )

    progress("[5/8] Computing fixed-period diagnostics...")
    periods = period_scores(opportunities, dataset["promotions"])

    progress("[6/8] Running expanding-window chronological validation...")
    validation = forward_validation(opportunities, dataset["promotions"])

    tables = {
        "total_wins": total_wins,
        "rank_patterns": rank_patterns,
        "minimum_wins": minimum_wins,
        "weak_result_position": weak_position,
        "rules": rules,
        "period_rules": periods,
        "forward_validation": validation,
    }

    progress("[7/8] Writing versioned research artifacts...")
    report = write_artifacts(
        output_dir, dataset, tables, source=source,
        bootstrap_samples=bootstrap_samples, seed=seed,
    )
    progress("[8/8] Complete.")
    progress(f"      Report: {report.resolve()}")
    return report

