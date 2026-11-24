"""Retained artifacts for the matched Elo-89 versus chii comparison."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .comparison import (
    ComparisonResult,
    by_basho_rows,
    rolling_rows,
    subgroup_rows,
)


@dataclass(frozen=True, slots=True)
class ComparisonOutputPaths:
    root: Path
    manifest: Path
    bout_comparison: Path
    summary: Path
    discordance: Path
    by_basho: Path
    rolling: Path
    report: Path


def write_comparison_outputs(
    *,
    result: ComparisonResult,
    output_root: Path,
    history_source: Path,
    history_sha256: str,
    represented_start: str,
    represented_end: str,
    prior_source: str,
    prior_sha256: str,
    k_config_path: Path,
    k_config_sha256: str,
    q: float,
) -> ComparisonOutputPaths:
    """Write the complete audit trail and human-readable conclusion."""

    label = f"elo89_vs_chii_{str(result.evaluation_start).replace('/', '_')}_to_{str(result.evaluation_end).replace('/', '_')}"
    root = output_root / label
    root.mkdir(parents=True, exist_ok=True)
    paths = ComparisonOutputPaths(
        root=root,
        manifest=root / "manifest.json",
        bout_comparison=root / "bout_comparison.csv",
        summary=root / "summary.csv",
        discordance=root / "discordance.csv",
        by_basho=root / "by_basho.csv",
        rolling=root / "rolling.csv",
        report=root / "report.md",
    )
    _write_csv(paths.bout_comparison, (_bout_row(row) for row in result.rows))
    _write_csv(paths.summary, _summary_rows(result))
    _write_csv(paths.discordance, (
        {"outcome": "both_correct", "count": result.both_correct},
        {"outcome": "elo_correct_chii_wrong", "count": result.elo_correct_chii_wrong},
        {"outcome": "elo_wrong_chii_correct", "count": result.elo_wrong_chii_correct},
        {"outcome": "both_wrong", "count": result.both_wrong},
    ))
    _write_csv(paths.by_basho, by_basho_rows(result))
    _write_csv(paths.rolling, rolling_rows(result))
    paths.report.write_text(_report(result), encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "analysis_id": "elo89-vs-higher-chii-matched",
        "history": {
            "source": str(history_source), "sha256": history_sha256,
            "represented_start": represented_start, "represented_end": represented_end,
        },
        "evaluation": {"start": str(result.evaluation_start), "end": str(result.evaluation_end)},
        "elo89": {
            "prior_source": prior_source, "prior_sha256": prior_sha256,
            "k_config": str(k_config_path), "k_config_sha256": k_config_sha256,
            "q": q, "replay_origin": "1989/01",
            "rating_lifecycle": "frozen across absence",
            "population_policy": "whole-population mean preservation",
        },
        "bootstrap": {
            "unit": "complete basho", "replicates": result.bootstrap_replicates,
            "seed": result.bootstrap_seed, "interval": "percentile",
        },
        "selection": {
            "raw_result_count": result.raw_result_count,
            "rated_bout_count": result.rated_bout_count,
            "excluded_fusen_count": result.excluded_fusen_count,
            "excluded_draw_count": result.excluded_draw_count,
            "elo_tie_count": result.elo_tie_count,
            "missing_chii_count": result.missing_chii_count,
            "equal_chii_count": result.equal_chii_count,
            "primary_count": result.primary_count,
        },
        "conclusion": result.conclusion,
        "files": {field: getattr(paths, field).name for field in (
            "bout_comparison", "summary", "discordance", "by_basho", "rolling", "report"
        )},
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def _bout_row(row) -> dict[str, object]:
    value = asdict(row)
    value["date"] = str(row.date)
    value["primary"] = row.primary
    return value


def _summary_rows(result: ComparisonResult) -> list[dict[str, object]]:
    rows = subgroup_rows(result)
    rows.extend([
        {"population": "PRIMARY_INFERENCE", "bouts": result.primary_count,
         "elo_accuracy": result.elo_accuracy, "chii_accuracy": result.chii_accuracy,
         "paired_difference": result.elo_minus_chii.estimate,
         "lower_95": result.elo_minus_chii.lower_95,
         "upper_95": result.elo_minus_chii.upper_95,
         "one_sided_lower_95": result.elo_minus_chii.one_sided_lower_95},
        {"population": "CHII_MINUS_RANDOM", "bouts": result.primary_count,
         "paired_difference": result.chii_minus_random.estimate,
         "lower_95": result.chii_minus_random.lower_95,
         "upper_95": result.chii_minus_random.upper_95,
         "one_sided_lower_95": result.chii_minus_random.one_sided_lower_95},
        {"population": "ELO_MINUS_RANDOM", "bouts": result.primary_count,
         "paired_difference": result.elo_minus_random.estimate,
         "lower_95": result.elo_minus_random.lower_95,
         "upper_95": result.elo_minus_random.upper_95,
         "one_sided_lower_95": result.elo_minus_random.one_sided_lower_95},
    ])
    return rows


def _report(result: ComparisonResult) -> str:
    pct = lambda value: f"{100 * value:.3f}%"
    pp = lambda value: f"{100 * value:+.3f} pp"
    conclusion = {
        "confirmed": "The complete ordering production Elo89 > higher chii > random choice is confirmed by both predeclared one-sided criteria.",
        "contradicted": "The complete proposed ordering is contradicted on this record because at least one observed difference is non-positive.",
        "inconclusive": "Both observed differences have the proposed sign, but at least one predeclared lower bound is not above zero; the complete ordering is inconclusive.",
    }[result.conclusion]
    return "\n".join([
        "# Matched Elo89 versus higher-chii accuracy", "",
        f"Evaluation: {result.evaluation_start} through {result.evaluation_end}, inclusive.", "",
        "## Primary result", "",
        f"- Common-domain bouts: {result.primary_count:,}",
        f"- Elo89 accuracy: {pct(result.elo_accuracy)}",
        f"- Higher-chii accuracy: {pct(result.chii_accuracy)}",
        f"- Elo89 minus higher chii: {pp(result.elo_minus_chii.estimate)} "
        f"(two-sided 95% bootstrap interval {pp(result.elo_minus_chii.lower_95)} to {pp(result.elo_minus_chii.upper_95)}; "
        f"one-sided 95% lower bound {pp(result.elo_minus_chii.one_sided_lower_95)})",
        f"- Higher chii minus 50%: {pp(result.chii_minus_random.estimate)} "
        f"(one-sided 95% lower bound {pp(result.chii_minus_random.one_sided_lower_95)})",
        f"- Exact McNemar/binomial two-sided p-value: {result.mcnemar_exact_p:.6g}", "",
        f"**Decision: {result.conclusion}.** {conclusion}", "",
        "## Population flow", "",
        "| Stage | Count |", "|---|---:|",
        f"| Raw represented results | {result.raw_result_count:,} |",
        f"| Production Elo89 eligible W/L forecasts | {result.rated_bout_count:,} |",
        f"| Elo89 exact-rating ties | {result.elo_tie_count:,} |",
        f"| Missing chii | {result.missing_chii_count:,} |",
        f"| Equal chii | {result.equal_chii_count:,} |",
        f"| Primary common-domain bouts | {result.primary_count:,} |", "",
        "## Paired outcomes", "",
        "| Outcome | Count |", "|---|---:|",
        f"| Both correct | {result.both_correct:,} |",
        f"| Elo89 correct, chii wrong | {result.elo_correct_chii_wrong:,} |",
        f"| Elo89 wrong, chii correct | {result.elo_wrong_chii_correct:,} |",
        f"| Both wrong | {result.both_wrong:,} |", "",
        "## Probability-score context", "",
        f"Elo89 mean log loss is {result.mean_elo_log_loss:.6f} (50-50 reference: {math_log_two():.6f}); "
        f"mean Brier loss is {result.mean_elo_brier_loss:.6f} (50-50 reference: 0.250000).",
        "Higher chii is a categorical rule, not a fitted probability model, so no proper score is assigned to it.", "",
        "This is a retrospective historical comparison. The accepted entrant prior was fitted using information from the broad period being scored, so this is not prospective or out-of-sample validation.", "",
    ])


def math_log_two() -> float:
    import math
    return math.log(2.0)


def _write_csv(path: Path, rows) -> None:
    materialised = list(rows)
    if not materialised:
        path.write_text("", encoding="utf-8")
        return
    columns: list[str] = []
    for row in materialised:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(materialised)
