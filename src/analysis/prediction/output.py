"""Persist the evidence and human-facing account of Proposal 1."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

from .charts import write_predictive_behaviour_chart
from .run import Proposal1Result


@dataclass(frozen=True)
class HistorySource:
    path: str
    sha256: str


def write_proposal_1_outputs(
    result: Proposal1Result,
    output_directory: Path,
    source: HistorySource,
) -> None:
    """Write every declared Proposal 1 artifact."""

    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(output_directory / "forecast_ledger.csv", _forecast_rows(result))
    _write_csv(output_directory / "basho_loss.csv", _dated_rows(result.basho_losses))
    _write_csv(output_directory / "rolling_loss.csv", _dated_rows(result.rolling_losses))
    _write_csv(output_directory / "cumulative_loss.csv", _dated_rows(result.cumulative_losses))
    _write_csv(output_directory / "uncertainty.csv", _dated_rows(result.uncertainty))
    (output_directory / "manifest.json").write_text(
        json.dumps(_manifest(result, source), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / "report.md").write_text(
        _report(result, source),
        encoding="utf-8",
    )
    write_predictive_behaviour_chart(
        result,
        output_directory / "predictive_behaviour.html",
    )


def _forecast_rows(result: Proposal1Result) -> Iterable[dict[str, object]]:
    scored_by_bout = {
        row.forecast.bout_id: row for row in result.scored_forecasts
    }
    for forecast in result.forecasts:
        scored = scored_by_bout[forecast.bout_id]
        yield {
            "date": str(forecast.bout_id.date),
            "day": int(forecast.bout_id.day),
            "rikishi_a": forecast.rikishi_a,
            "rikishi_b": forecast.rikishi_b,
            "rating_a_before": forecast.rating_a_before,
            "rating_b_before": forecast.rating_b_before,
            "rated_bouts_a_before": forecast.rated_bouts_a_before,
            "rated_bouts_b_before": forecast.rated_bouts_b_before,
            "probability_a_wins": forecast.probability_a_wins,
            "a_won": forecast.a_won,
            "delta_a": forecast.delta_a,
            "rating_a_after": forecast.rating_a_after,
            "rating_b_after": forecast.rating_b_after,
            "log_loss": scored.log_loss,
            "reference_log_loss": scored.reference_log_loss,
            "log_loss_difference": scored.log_loss_difference,
            "brier_score": scored.brier_score,
            "reference_brier_score": scored.reference_brier_score,
            "brier_difference": scored.brier_difference,
        }


def _dated_rows(rows: Iterable[object]) -> Iterable[dict[str, object]]:
    for row in rows:
        values = asdict(row)
        for key in ("date", "start_date", "end_date"):
            if key in values:
                values[key] = str(getattr(row, key))
        yield values


def _write_csv(filename: Path, rows: Iterable[dict[str, object]]) -> None:
    row_iterator = iter(rows)
    first_row = next(row_iterator)
    with filename.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(first_row))
        writer.writeheader()
        writer.writerow(first_row)
        writer.writerows(row_iterator)


def _manifest(result: Proposal1Result, source: HistorySource) -> dict[str, object]:
    definition = result.definition
    return {
        "experiment": "Proposal 1: Basic Elo Predictive Behaviour",
        "history_source": asdict(source),
        "definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "q": definition.q,
            "k": definition.k,
            "initial_rating": definition.initial_rating,
            "reference_probability": definition.reference_probability,
            "rolling_windows_basho": definition.rolling_windows,
            "bootstrap_seed": definition.bootstrap_seed,
            "bootstrap_resamples": definition.bootstrap_resamples,
            "confidence_level": definition.confidence_level,
        },
        "selection": {
            "raw_result_count": result.selection.raw_result_count,
            "rated_bout_count": result.selection.rated_bout_count,
            "excluded_fusen_count": result.selection.excluded_fusen_count,
            "excluded_draw_count": result.selection.excluded_draw_count,
            "bouts": "forecast_ledger.csv",
        },
        "actual_range": {
            "first_basho": str(result.basho_losses[0].date),
            "last_basho": str(result.basho_losses[-1].date),
            "basho_count": len(result.basho_losses),
        },
    }


def _report(result: Proposal1Result, source: HistorySource) -> str:
    final = result.cumulative_losses[-1]
    selection = result.selection
    log_loss_reduction = (
        -final.mean_log_loss_difference / final.mean_reference_log_loss * 100
    )
    brier_reduction = (
        -final.mean_brier_difference / final.mean_reference_brier_score * 100
    )
    observations: list[str] = []
    uncertainty = {
        (row.window_basho, row.end_date): row for row in result.uncertainty
    }
    for window in result.definition.rolling_windows:
        rows = tuple(row for row in result.rolling_losses if row.window_basho == window)
        first_better = next((row for row in rows if row.mean_log_loss_difference < 0), None)
        first_interval = next(
            (
                row for row in rows
                if uncertainty[(window, row.end_date)].log_loss_difference_upper < 0
            ),
            None,
        )
        observations.append(
            f"- {window}-basho log-loss curve first falls below the 50% reference at "
            f"{_date_or_never(first_better)}; its pointwise 95% interval first lies wholly "
            f"below zero at {_date_or_never(first_interval)}."
        )
    return f"""# Proposal 1: Basic Elo Predictive Behaviour

## Definition

One chronological predict-then-update pass was made from {result.definition.start_date} through {result.definition.end_date}. Basic Elo was fixed in advance at q=400, k=35 and initial rating b=1500. Ratings persist for each RikId. Every W/L bout was included regardless of whether kimarite was recorded; FS/FP and draws were excluded.

At the epoch, all represented rikishi begin with equal ratings. This equality is an externally imposed initial condition: it is not inferred from the data and does not assert that the rikishi had equal abilities. The common numerical value 1500 is arbitrary because translating every rating by the same constant does not change any prediction.

History source: `{source.path}`  
SHA-256: `{source.sha256}`

## Dataset

- {len(result.basho_losses):,} basho represented, from {result.basho_losses[0].date} to {result.basho_losses[-1].date}.
- {selection.raw_result_count:,} represented results inspected.
- {selection.rated_bout_count:,} W/L bouts rated and scored.
- {selection.excluded_fusen_count:,} FS/FP results excluded.
- {selection.excluded_draw_count:,} other non-binary results excluded.

## Whole-epoch result

Through {final.end_date}, Basic Elo's mean log loss was {final.mean_log_loss:.6f}, compared with {final.mean_reference_log_loss:.6f} for the neutral forecast: a paired difference of {final.mean_log_loss_difference:+.6f}, or a {log_loss_reduction:.1f}% reduction. Its mean Brier loss was {final.mean_brier_score:.6f}, a paired difference of {final.mean_brier_difference:+.6f}, or a {brier_reduction:.1f}% reduction. Negative differences favour Basic Elo.

## Descriptive curve landmarks

{chr(10).join(observations)}

## Interpretation

Under the externally imposed equal-rating initial condition at the January 1989 epoch, the results are consistent with Basic Elo requiring roughly a decade before its point estimates outperform a neutral 50% predictor. The pointwise intervals provide stronger evidence of superiority after roughly 12 to 13 years. Over the full epoch, Basic Elo is the better predictor, but its average advantage is modest; later rolling performance is stronger than the whole-epoch result because the aggregate retains the early underperformance.

The crossings are descriptions of overlapping rolling curves, not estimates of an intrinsic warm-up date. Pointwise intervals do not provide simultaneous coverage, repeated inspection of crossings is not a formal threshold test, and crossings may reverse later. The conclusions concern Basic Elo under this experiment's initial condition; they do not establish how long continuously maintained Elo ratings generally take to become useful. The HTML chart and CSV tables retain the full trajectories.
"""


def _date_or_never(row: object | None) -> str:
    return str(row.end_date) if row is not None else "no represented basho"
