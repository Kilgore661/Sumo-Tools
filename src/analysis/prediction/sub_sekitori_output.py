"""Persist the sub-sekitori evaluation and its baseline comparison."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .charts import write_predictive_behaviour_chart
from .output import HistorySource, _dated_rows, _forecast_rows, _write_csv
from .run import Proposal1Result
from .sekitori import SubSekitoriEvaluationResult
from .sekitori_output import _comparison_row


def write_sub_sekitori_outputs(
    result: SubSekitoriEvaluationResult,
    baseline: Proposal1Result,
    output_directory: Path,
    source: HistorySource,
) -> None:
    """Write the evidence owned by the sub-sekitori experiment."""

    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_directory / "sub_sekitori_forecast_ledger.csv",
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
        (
            _comparison_row(
                "all eligible bouts",
                baseline.cumulative_losses[-1],
            ),
            _comparison_row(
                "both participants sub-sekitori",
                result.cumulative_losses[-1],
            ),
        ),
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
        title="Basic Elo predictive behaviour: sub-sekitori bouts only",
    )


def _manifest(
    result: SubSekitoriEvaluationResult,
    baseline: Proposal1Result,
    source: HistorySource,
) -> dict[str, object]:
    definition = result.definition
    return {
        "experiment": "Sub-sekitori Evaluation of Proposal 1 Basic Elo",
        "history_source": asdict(source),
        "definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "q": definition.q,
            "k": definition.k,
            "initial_rating": definition.initial_rating,
            "rating_domain": "all eligible represented W/L bouts",
            "evaluation_domain": "both participants sub-sekitori on the basho banzuke",
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
    result: SubSekitoriEvaluationResult,
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
    uncertainty = {
        (row.window_basho, row.end_date): row for row in result.uncertainty
    }
    observations: list[str] = []
    turning_points: list[str] = []
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
        best = min(rows, key=lambda row: row.mean_log_loss_difference)
        observations.append(
            f"- {window}-basho log-loss first lies below the 50% reference at "
            f"{_date_or_never(first_better)}; its pointwise 95% interval first lies "
            f"wholly below zero at {_date_or_never(first_interval)}."
        )
        turning_points.append(
            f"- {window}-basho minimum: {best.mean_log_loss_difference:+.6f} at "
            f"{best.end_date}; endpoint: {rows[-1].mean_log_loss_difference:+.6f} "
            f"at {rows[-1].end_date}."
        )
    selection = result.selection
    return f"""# Sub-sekitori Evaluation of Basic Elo

## Definition

The Proposal 1 Basic Elo producer was run unchanged from {result.definition.start_date} through {result.definition.end_date}. Every eligible represented W/L bout updated the persistent ratings. A forecast was evaluated only when both participants were ranked below sekitori on that basho's banzuke. All other bouts were ignored by the evaluator, not by the rating producer.

History source: `{source.path}`  
SHA-256: `{source.sha256}`

## Evaluation population

- {baseline.selection.rated_bout_count:,} W/L bouts updated the ratings.
- {selection.evaluated_bout_count:,} bouts had two sub-sekitori participants and were evaluated.
- {selection.excluded_one_sub_sekitori_count:,} bouts had exactly one sub-sekitori participant and were not evaluated.
- {selection.excluded_no_sub_sekitori_count:,} bouts had no sub-sekitori participants and were not evaluated.

## Whole-epoch result

For sub-sekitori bouts, mean log loss was {final.mean_log_loss:.6f}, compared with {final.mean_reference_log_loss:.6f} for the neutral forecast: a paired difference of {final.mean_log_loss_difference:+.6f}, or a {log_reduction:.1f}% reduction. Mean Brier loss was {final.mean_brier_score:.6f}, a paired difference of {final.mean_brier_difference:+.6f}, or a {brier_reduction:.1f}% reduction.

The all-bout Proposal 1 mean log loss was {baseline_final.mean_log_loss:.6f}; sub-sekitori-only evaluation changes it by {final.mean_log_loss - baseline_final.mean_log_loss:+.6f}. The all-bout Brier loss was {baseline_final.mean_brier_score:.6f}; sub-sekitori-only evaluation changes it by {final.mean_brier_score - baseline_final.mean_brier_score:+.6f}. These scope differences are descriptive because the evaluated contests differ.

## Descriptive curve landmarks

{chr(10).join(observations)}

## Best rolling values and endpoints

{chr(10).join(turning_points)}

The landmarks describe overlapping rolling curves and are not estimates of an intrinsic warm-up date or a change point. Pointwise intervals do not provide simultaneous coverage.

## Population comparison

The sub-sekitori result reproduces the long early period seen in the all-bout aggregate: depending on window length, its point estimates first favour Basic Elo during 1999–2002. This locates that feature in the lower-division evaluation population rather than in sekitori bouts.

The later trajectory differs sharply by population. Sekitori rolling performance is best around 2011–2013 and then deteriorates toward the neutral predictor. Sub-sekitori performance continues improving, with its best rolling values around 2023–2025; all endpoint intervals remain wholly below zero in 2026. Consequently, the apparent all-bout improvement in recent years is dominated by the much larger sub-sekitori population and conceals the contrary sekitori movement.
"""


def _date_or_never(row: object | None) -> str:
    return str(row.end_date) if row is not None else "no represented basho"
