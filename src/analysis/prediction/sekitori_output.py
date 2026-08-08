"""Persist the sekitori-only evaluation and its baseline comparison."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .charts import write_predictive_behaviour_chart
from .output import HistorySource, _dated_rows, _forecast_rows, _write_csv
from .run import Proposal1Result
from .sekitori import SekitoriEvaluationResult


def write_sekitori_outputs(
    result: SekitoriEvaluationResult,
    baseline: Proposal1Result,
    output_directory: Path,
    source: HistorySource,
) -> None:
    """Write the evidence owned by the sekitori-only experiment."""

    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_directory / "sekitori_forecast_ledger.csv",
        _forecast_rows(result),
    )
    _write_csv(
        output_directory / "basho_loss.csv",
        _dated_rows(result.basho_losses),
    )
    _write_csv(
        output_directory / "rolling_loss.csv",
        _dated_rows(result.rolling_losses),
    )
    _write_csv(
        output_directory / "cumulative_loss.csv",
        _dated_rows(result.cumulative_losses),
    )
    _write_csv(
        output_directory / "uncertainty.csv",
        _dated_rows(result.uncertainty),
    )
    _write_csv(
        output_directory / "comparison.csv",
        _comparison_rows(result, baseline),
    )
    (output_directory / "manifest.json").write_text(
        json.dumps(_manifest(result, baseline, source), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / "report.md").write_text(
        _report(result, baseline, source),
        encoding="utf-8",
    )
    write_predictive_behaviour_chart(
        result,
        output_directory / "predictive_behaviour.html",
        title="Basic Elo predictive behaviour: sekitori bouts only",
    )


def _comparison_rows(
    result: SekitoriEvaluationResult,
    baseline: Proposal1Result,
) -> tuple[dict[str, object], ...]:
    return (
        _comparison_row(
            "all eligible bouts",
            baseline.cumulative_losses[-1],
        ),
        _comparison_row(
            "both participants sekitori",
            result.cumulative_losses[-1],
        ),
    )


def _comparison_row(scope: str, row: object) -> dict[str, object]:
    return {
        "evaluation_scope": scope,
        "start_date": str(row.start_date),
        "end_date": str(row.end_date),
        "basho_count": row.basho_count,
        "bout_count": row.bout_count,
        "mean_log_loss": row.mean_log_loss,
        "mean_reference_log_loss": row.mean_reference_log_loss,
        "mean_log_loss_difference": row.mean_log_loss_difference,
        "mean_brier_score": row.mean_brier_score,
        "mean_reference_brier_score": row.mean_reference_brier_score,
        "mean_brier_difference": row.mean_brier_difference,
    }


def _manifest(
    result: SekitoriEvaluationResult,
    baseline: Proposal1Result,
    source: HistorySource,
) -> dict[str, object]:
    definition = result.definition
    return {
        "experiment": "Sekitori-only Evaluation of Proposal 1 Basic Elo",
        "history_source": asdict(source),
        "definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "q": definition.q,
            "k": definition.k,
            "initial_rating": definition.initial_rating,
            "rating_domain": "all eligible represented W/L bouts",
            "evaluation_domain": "both participants sekitori on the basho banzuke",
            "reference_probability": definition.reference_probability,
            "rolling_windows_basho": definition.rolling_windows,
            "bootstrap_seed": definition.bootstrap_seed,
            "bootstrap_resamples": definition.bootstrap_resamples,
            "confidence_level": definition.confidence_level,
        },
        "rating_pass": {
            "rated_bout_count": baseline.selection.rated_bout_count,
            "excluded_fusen_count": baseline.selection.excluded_fusen_count,
            "excluded_draw_count": baseline.selection.excluded_draw_count,
        },
        "evaluation_selection": asdict(result.selection),
        "actual_range": {
            "first_basho": str(result.basho_losses[0].date),
            "last_basho": str(result.basho_losses[-1].date),
            "basho_count": len(result.basho_losses),
        },
    }


def _report(
    result: SekitoriEvaluationResult,
    baseline: Proposal1Result,
    source: HistorySource,
) -> str:
    final = result.cumulative_losses[-1]
    baseline_final = baseline.cumulative_losses[-1]
    log_reduction = (
        -final.mean_log_loss_difference / final.mean_reference_log_loss * 100
    )
    brier_reduction = (
        -final.mean_brier_difference / final.mean_reference_brier_score * 100
    )
    log_scope_difference = final.mean_log_loss - baseline_final.mean_log_loss
    brier_scope_difference = final.mean_brier_score - baseline_final.mean_brier_score
    uncertainty = {
        (row.window_basho, row.end_date): row for row in result.uncertainty
    }
    observations: list[str] = []
    for window in result.definition.rolling_windows:
        rows = tuple(
            row for row in result.rolling_losses
            if row.window_basho == window
        )
        first_better = next(
            (row for row in rows if row.mean_log_loss_difference < 0),
            None,
        )
        first_interval = next(
            (
                row for row in rows
                if uncertainty[(window, row.end_date)].log_loss_difference_upper < 0
            ),
            None,
        )
        point_estimate_description = (
            "its first defined estimate is below the 50% reference at "
            if first_better == rows[0]
            else "it first falls below the 50% reference at "
        )
        observations.append(
            f"- For the {window}-basho log-loss curve, "
            f"{point_estimate_description}{_date_or_never(first_better)}; its pointwise "
            f"95% interval first lies wholly below zero at "
            f"{_date_or_never(first_interval)}."
        )
    selection = result.selection
    return f"""# Sekitori-only Evaluation of Basic Elo

## Definition

The Proposal 1 Basic Elo producer was run unchanged from {result.definition.start_date} through {result.definition.end_date}. Every eligible represented W/L bout updated the persistent ratings. A forecast was evaluated only when both participants were sekitori on that basho's banzuke. Bouts with one or no sekitori participants were ignored by the evaluator, not by the rating producer.

History source: `{source.path}`  
SHA-256: `{source.sha256}`

## Evaluation population

- {baseline.selection.rated_bout_count:,} W/L bouts updated the ratings.
- {selection.evaluated_bout_count:,} bouts had two sekitori participants and were evaluated.
- {selection.excluded_one_sekitori_count:,} bouts had exactly one sekitori participant and were not evaluated.
- {selection.excluded_no_sekitori_count:,} bouts had no sekitori participants and were not evaluated.

## Whole-epoch result

For sekitori bouts, mean log loss was {final.mean_log_loss:.6f}, compared with {final.mean_reference_log_loss:.6f} for the neutral forecast: a paired difference of {final.mean_log_loss_difference:+.6f}, or a {log_reduction:.1f}% reduction. Mean Brier loss was {final.mean_brier_score:.6f}, a paired difference of {final.mean_brier_difference:+.6f}, or a {brier_reduction:.1f}% reduction.

The all-bout Proposal 1 mean log loss was {baseline_final.mean_log_loss:.6f}; sekitori-only evaluation changes it by {log_scope_difference:+.6f}. The all-bout Brier loss was {baseline_final.mean_brier_score:.6f}; sekitori-only evaluation changes it by {brier_scope_difference:+.6f}. These scope differences are descriptive: the evaluated contests differ, while the rating producer is identical.

## Descriptive curve landmarks

{chr(10).join(observations)}

The crossings describe overlapping rolling curves and are not estimates of an intrinsic warm-up date. Pointwise intervals do not provide simultaneous coverage, and repeated inspection of crossings is not a formal threshold test.

Unlike the all-bout aggregate, the sekitori-only curves do not show a decade of observed early underperformance: every rolling window's first defined point estimate already favours Basic Elo. The later interval landmarks describe when the pointwise evidence becomes stronger, not when the point estimate first becomes favourable. The decade-long pattern in Proposal 1 is therefore population-sensitive and is associated with including the much larger lower-division evaluation population.
"""


def _date_or_never(row: object | None) -> str:
    return str(row.end_date) if row is not None else "no represented basho"
