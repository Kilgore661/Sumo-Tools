"""Persist the retrospective Chii-initialization experiment."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .charts import write_predictive_behaviour_chart
from .chii_initialisation import ChiiInitialisationResult
from .output import HistorySource, _dated_rows, _forecast_rows, _write_csv
from .scope_summary import RollingSignSummary, ScopeScoreSummary
from .sekitori import SekitoriEvaluationResult, SubSekitoriEvaluationResult


def write_chii_initialisation_outputs(
    result: ChiiInitialisationResult,
    sekitori: SekitoriEvaluationResult,
    sub_sekitori: SubSekitoriEvaluationResult,
    baseline_summaries: tuple[ScopeScoreSummary, ...],
    chii_summaries: tuple[ScopeScoreSummary, ...],
    baseline_signs: tuple[RollingSignSummary, ...],
    chii_signs: tuple[RollingSignSummary, ...],
    output_directory: Path,
    source: HistorySource,
) -> None:
    """Write prior audit evidence, comparisons, series, charts, and report."""

    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(output_directory / "chii_prior.csv", _prior_rows(result))
    _write_csv(
        output_directory / "chii_prior_observations.csv",
        _observation_rows(result),
    )
    _write_csv(
        output_directory / "forecast_ledger.csv",
        _forecast_rows(result),
    )
    _write_csv(
        output_directory / "comparison.csv",
        _comparison_rows(baseline_summaries, chii_summaries),
    )
    _write_csv(
        output_directory / "rolling_sign_comparison.csv",
        _rolling_sign_rows(baseline_signs, chii_signs),
    )
    for prefix, evaluation in (
        ("all_bouts", result),
        ("sekitori", sekitori),
        ("sub_sekitori", sub_sekitori),
    ):
        _write_csv(
            output_directory / f"{prefix}_basho_loss.csv",
            _dated_rows(evaluation.basho_losses),
        )
        _write_csv(
            output_directory / f"{prefix}_rolling_loss.csv",
            _dated_rows(evaluation.rolling_losses),
        )
        _write_csv(
            output_directory / f"{prefix}_cumulative_loss.csv",
            _dated_rows(evaluation.cumulative_losses),
        )
        _write_csv(
            output_directory / f"{prefix}_uncertainty.csv",
            _dated_rows(evaluation.uncertainty),
        )
        write_predictive_behaviour_chart(
            evaluation,
            output_directory / f"{prefix}_predictive_behaviour.html",
            title=f"Chii-initialized Basic Elo: {_display_scope(prefix)}",
        )
    (output_directory / "manifest.json").write_text(
        json.dumps(_manifest(result, source), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / "report.md").write_text(
        _report(
            result,
            sekitori,
            sub_sekitori,
            baseline_summaries,
            chii_summaries,
            baseline_signs,
            chii_signs,
            source,
        ),
        encoding="utf-8",
    )


def _prior_rows(result: ChiiInitialisationResult):
    for row in result.prior.rows:
        yield {
            "chii_ordinal": row.chii.ordinal(),
            "chii_display": str(row.chii),
            "initial_rating": row.initial_rating,
            "source": row.source,
            "observation_count": row.observation_count,
            "first_observation_date": (
                str(row.first_observation_date)
                if row.first_observation_date is not None else ""
            ),
            "last_observation_date": (
                str(row.last_observation_date)
                if row.last_observation_date is not None else ""
            ),
        }


def _observation_rows(result: ChiiInitialisationResult):
    for row in result.prior.observations:
        yield {
            "chii_ordinal": row.chii.ordinal(),
            "chii_display": str(row.chii),
            "date": str(row.date),
            "normalized_start_rating": row.normalized_rating,
        }


def _comparison_rows(
    baseline: tuple[ScopeScoreSummary, ...],
    chii: tuple[ScopeScoreSummary, ...],
):
    for model, summaries in (
        ("equal initial rating", baseline),
        ("trailing-10 Chii prior", chii),
    ):
        for row in summaries:
            yield {"initialization": model, **asdict(row)}


def _rolling_sign_rows(
    baseline: tuple[RollingSignSummary, ...],
    chii: tuple[RollingSignSummary, ...],
):
    for model, summaries in (
        ("equal initial rating", baseline),
        ("trailing-10 Chii prior", chii),
    ):
        for row in summaries:
            yield {
                "initialization": model,
                "scope": row.scope,
                "window_basho": row.window_basho,
                "first_defined_date": str(row.first_defined_date),
                "first_defined_difference": row.first_defined_difference,
                "first_favourable_date": _optional_date(row.first_favourable_date),
                "persistently_favourable_from": _optional_date(
                    row.persistently_favourable_from
                ),
                "zero_crossing_count": row.zero_crossing_count,
            }


def _manifest(
    result: ChiiInitialisationResult,
    source: HistorySource,
) -> dict[str, object]:
    prior = result.prior
    return {
        "experiment": "Retrospective trailing-10 Chii initialization",
        "history_source": asdict(source),
        "definition": {
            "start_date": str(result.definition.start_date),
            "end_date": str(result.definition.end_date),
            "q": result.definition.q,
            "k": result.definition.k,
            "trailing_observations_per_chii": prior.trailing_observations,
            "normalized_snapshot_mean": prior.common_mean,
            "monotonic_smoothing": False,
            "interpolation": "linear by ordered Chii position",
        },
        "prior": {
            "chii_count": len(prior.rows),
            "retained_observation_count": len(prior.observations),
            "unranked_initial_rikishi": [
                int(value) for value in prior.unranked_initial_rikishi
            ],
            "unranked_fallback_rating": prior.unranked_fallback_rating,
            "known_history_defect": (
                "RikId 13011 has seven 2026/07 W/L bouts but is absent from "
                "the 2026/07 banzuke"
            ),
        },
    }


def _report(
    result: ChiiInitialisationResult,
    sekitori: SekitoriEvaluationResult,
    sub_sekitori: SubSekitoriEvaluationResult,
    baseline_summaries: tuple[ScopeScoreSummary, ...],
    chii_summaries: tuple[ScopeScoreSummary, ...],
    baseline_signs: tuple[RollingSignSummary, ...],
    chii_signs: tuple[RollingSignSummary, ...],
    source: HistorySource,
) -> str:
    baseline = {row.scope: row for row in baseline_summaries}
    chii = {row.scope: row for row in chii_summaries}
    comparison_lines = []
    for scope in baseline:
        before = baseline[scope]
        after = chii[scope]
        comparison_lines.append(
            f"- {scope}: log loss {before.mean_log_loss:.6f} -> "
            f"{after.mean_log_loss:.6f} "
            f"({after.mean_log_loss - before.mean_log_loss:+.6f}); Brier "
            f"{before.mean_brier_score:.6f} -> {after.mean_brier_score:.6f} "
            f"({after.mean_brier_score - before.mean_brier_score:+.6f})."
        )
    prior_rows = result.prior.rows
    reversals = sum(
        weaker.initial_rating > stronger.initial_rating
        for stronger, weaker in zip(prior_rows, prior_rows[1:])
    )
    baseline_sign_lookup = {
        (row.scope, row.window_basho): row for row in baseline_signs
    }
    sign_lines = []
    for after in chii_signs:
        before = baseline_sign_lookup[(after.scope, after.window_basho)]
        sign_lines.append(
            f"- {after.scope}, {after.window_basho} basho: first favourable "
            f"{_optional_date(before.first_favourable_date)} -> "
            f"{_optional_date(after.first_favourable_date)}; persistently "
            f"favourable { _optional_date(before.persistently_favourable_from) } -> "
            f"{_optional_date(after.persistently_favourable_from)}; Chii-prior "
            f"curve zero crossings: {after.zero_crossing_count}."
        )
    return f"""# Retrospective Chii-based Initialization

## Definition

The equal-initialization Basic Elo run supplied the last ten normalized start-of-basho ratings observed at each exact Chii. Their unsmoothed mean formed a retrospective initialization surface; absent Chii were interpolated by ordered Chii position. A second q=400, k=35 pass used that surface whenever a RikId first received a rating.

History source: `{source.path}`  
SHA-256: `{source.sha256}`

This is an oracle diagnostic. Outcomes later evaluated by the second pass contributed to its initialization surface, so the resulting losses are not out-of-sample estimates.

## Prior audit

- {len(prior_rows):,} Chii values appear in the mapping.
- {len(result.prior.observations):,} normalized start-rating observations are retained.
- {sum(row.source == "observed trailing mean" for row in prior_rows):,} Chii use observed trailing means.
- {sum(row.source != "observed trailing mean" for row in prior_rows):,} Chii use interpolation or an observed edge.
- {reversals:,} adjacent ordered Chii pairs reverse the nominal stronger-to-weaker rating direction; none were smoothed away.
- RikId 13011 uses the weakest-edge fallback because of the recorded 2026/07 History-building defect.

The authoritative mapping is `chii_prior.csv`, keyed by chii ordinal. `chii_prior_observations.csv` contains every retained value behind the means.

## Equal versus Chii-based initialization

{chr(10).join(comparison_lines)}

Negative changes favour Chii-based initialization.

## Rolling sign behaviour

{chr(10).join(sign_lines)}

The Chii prior makes several short-window estimates favourable much earlier, but persistent superiority changes much less. In particular, the long sub-sekitori pattern is shortened rather than removed. These landmarks describe overlapping rolling curves and are not formal warm-up estimates. The comparison tests whether supplying a retrospective chii-shaped prior can remove the observed initial behaviour; it does not validate this future-informed mapping as a prospective model.
"""


def _display_scope(prefix: str) -> str:
    return prefix.replace("_", " ")


def _date_or_never(row: object | None) -> str:
    return str(row.end_date) if row is not None else "no represented basho"


def _optional_date(date: object | None) -> str:
    return str(date) if date is not None else "never"
