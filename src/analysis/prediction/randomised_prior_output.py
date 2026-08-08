"""Persist Proposal 4 audit evidence, summaries, chart, and report."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .output import HistorySource, _write_csv
from .randomised_prior import (
    CumulativeScore,
    GLOBAL_PLACEBO,
    PLACEBOS,
    RandomisedPriorResult,
    SCOPES,
    WITHIN_DIVISION_PLACEBO,
    summarize_ordered,
)


def write_randomised_prior_outputs(
    result: RandomisedPriorResult,
    output_directory: Path,
    history_source: HistorySource,
    prior_source: HistorySource,
) -> None:
    """Write every Proposal 4 artifact declared by the proposal."""

    output_directory.mkdir(parents=True, exist_ok=True)
    horizon_rows = tuple(_horizon_rows(result))
    cumulative_rows = tuple(_cumulative_envelope_rows(result))
    _write_csv(
        output_directory / "permutation_assignments.csv",
        _assignment_rows(result),
    )
    _write_csv(output_directory / "horizon_results.csv", horizon_rows)
    _write_csv(
        output_directory / "cumulative_envelope.csv",
        cumulative_rows,
    )
    (output_directory / "manifest.json").write_text(
        json.dumps(
            _manifest(result, history_source, prior_source),
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (output_directory / "report.md").write_text(
        _report(result, horizon_rows, history_source, prior_source),
        encoding="utf-8",
    )
    _write_chart(
        cumulative_rows,
        output_directory / "randomised_prior_placebo.html",
    )


def _assignment_rows(result: RandomisedPriorResult):
    for mapping in result.mappings:
        for prior, assigned in zip(result.prior_values, mapping.ratings):
            yield {
                "placebo": mapping.placebo,
                "replicate": mapping.replicate,
                "chii_ordinal": prior.chii.ordinal(),
                "chii_display": str(prior.chii),
                "assigned_rating": assigned,
                "genuine_rating": prior.rating,
            }


def _horizon_rows(result: RandomisedPriorResult):
    equal = _score_lookup(result.equal_scores)
    genuine = _score_lookup(result.genuine_scores)
    randomized = tuple(
        (mapping, _score_lookup(rows))
        for mapping, rows in zip(result.mappings, result.randomised_scores)
    )
    final_basho = max(row.basho_count for row in result.equal_scores)
    horizons = result.randomisation.horizons_basho + (final_basho,)
    for scope in SCOPES:
        for horizon in horizons:
            equal_row = equal[(scope, horizon)]
            genuine_row = genuine[(scope, horizon)]
            yield _horizon_row(
                "equal",
                "",
                equal_row,
                equal_row,
                horizon == final_basho,
            )
            yield _horizon_row(
                "genuine Chii",
                "",
                genuine_row,
                equal_row,
                horizon == final_basho,
            )
            for mapping, lookup in randomized:
                yield _horizon_row(
                    f"{mapping.placebo} randomized Chii",
                    mapping.replicate,
                    lookup[(scope, horizon)],
                    equal_row,
                    horizon == final_basho,
                    mapping.placebo,
                )


def _horizon_row(
    model: str,
    replicate: int | str,
    score: CumulativeScore,
    equal: CumulativeScore,
    complete_epoch: bool,
    placebo: str = "",
) -> dict[str, object]:
    return {
        "model": model,
        "placebo": placebo,
        "replicate": replicate,
        "scope": score.scope,
        "horizon": "complete represented epoch" if complete_epoch else score.basho_count,
        "horizon_basho": score.basho_count,
        "horizon_date": str(score.end_date),
        "bout_count": score.bout_count,
        "mean_log_loss": score.mean_log_loss,
        "log_loss_difference_from_equal": (
            score.mean_log_loss - equal.mean_log_loss
        ),
        "mean_brier_score": score.mean_brier_score,
        "brier_difference_from_equal": (
            score.mean_brier_score - equal.mean_brier_score
        ),
    }


def _cumulative_envelope_rows(result: RandomisedPriorResult):
    genuine = {
        (row.scope, row.end_date): row for row in result.genuine_scores
    }
    randomized = {
        placebo: tuple(
            {(row.scope, row.end_date): row for row in scores}
            for mapping, scores in zip(result.mappings, result.randomised_scores)
            if mapping.placebo == placebo
        )
        for placebo in PLACEBOS
    }
    for equal in result.equal_scores:
        key = (equal.scope, equal.end_date)
        real = genuine[key]
        values: dict[str, object] = {
            "scope": equal.scope,
            "date": str(equal.end_date),
            "basho_count": equal.basho_count,
            "bout_count": equal.bout_count,
            "equal_log_loss": equal.mean_log_loss,
            "genuine_log_loss": real.mean_log_loss,
            "genuine_log_difference_from_equal": (
                real.mean_log_loss - equal.mean_log_loss
            ),
            "equal_brier_score": equal.mean_brier_score,
            "genuine_brier_score": real.mean_brier_score,
            "genuine_brier_difference_from_equal": (
                real.mean_brier_score - equal.mean_brier_score
            ),
        }
        for placebo in PLACEBOS:
            prefix = _placebo_prefix(placebo)
            random_log = tuple(
                rows[key].mean_log_loss for rows in randomized[placebo]
            )
            random_brier = tuple(
                rows[key].mean_brier_score for rows in randomized[placebo]
            )
            log_summary = summarize_ordered(random_log)
            brier_summary = summarize_ordered(random_brier)
            values.update({
                f"{prefix}_log_median": log_summary.median,
                f"{prefix}_log_p05": log_summary.percentile_5,
                f"{prefix}_log_p95": log_summary.percentile_95,
                f"{prefix}_log_median_difference_from_equal": (
                    log_summary.median - equal.mean_log_loss
                ),
                f"{prefix}_log_p05_difference_from_equal": (
                    log_summary.percentile_5 - equal.mean_log_loss
                ),
                f"{prefix}_log_p95_difference_from_equal": (
                    log_summary.percentile_95 - equal.mean_log_loss
                ),
                f"{prefix}_better_log_than_genuine": sum(
                    value < real.mean_log_loss for value in random_log
                ),
                f"{prefix}_better_log_than_equal": sum(
                    value < equal.mean_log_loss for value in random_log
                ),
                f"{prefix}_brier_median": brier_summary.median,
                f"{prefix}_brier_p05": brier_summary.percentile_5,
                f"{prefix}_brier_p95": brier_summary.percentile_95,
                f"{prefix}_brier_median_difference_from_equal": (
                    brier_summary.median - equal.mean_brier_score
                ),
                f"{prefix}_brier_p05_difference_from_equal": (
                    brier_summary.percentile_5 - equal.mean_brier_score
                ),
                f"{prefix}_brier_p95_difference_from_equal": (
                    brier_summary.percentile_95 - equal.mean_brier_score
                ),
                f"{prefix}_better_brier_than_genuine": sum(
                    value < real.mean_brier_score for value in random_brier
                ),
                f"{prefix}_better_brier_than_equal": sum(
                    value < equal.mean_brier_score for value in random_brier
                ),
            })
        yield values


def _score_lookup(
    rows: tuple[CumulativeScore, ...],
) -> dict[tuple[str, int], CumulativeScore]:
    return {(row.scope, row.basho_count): row for row in rows}


def _manifest(
    result: RandomisedPriorResult,
    history_source: HistorySource,
    prior_source: HistorySource,
) -> dict[str, object]:
    definition = result.elo_definition
    randomisation = result.randomisation
    return {
        "experiment": "Proposal 4: Randomized Chii-prior Placebo",
        "history_source": asdict(history_source),
        "prior_source": asdict(prior_source),
        "elo_definition": {
            "start_date": str(definition.start_date),
            "end_date": str(definition.end_date),
            "q": definition.q,
            "k": definition.k,
            "equal_initial_rating": definition.initial_rating,
            "eligible_result": "W/L irrespective of kimarite",
        },
        "randomisation": {
            "replicate_count_per_placebo": randomisation.replicate_count,
            "placebos": PLACEBOS,
            "seed": randomisation.seed,
            "algorithms": {
                "global": (
                    "one random.Random stream; copy genuine ratings in "
                    "ascending Chii ordinal order and shuffle once per replicate"
                ),
                "within division": (
                    "a separate random.Random stream; copy genuine ratings, "
                    "visit actual divisions in first-Chii order, and shuffle "
                    "the values at each division's positions once per replicate"
                ),
            },
            "horizons_basho": randomisation.horizons_basho,
            "order_statistics": {
                "median": "mean of ordered values 50 and 51",
                "percentile_5": "ordered value 5",
                "percentile_95": "ordered value 95",
            },
        },
        "data": {
            "chii_count": len(result.prior_values),
            "rated_bout_count": result.prepared.selection.rated_bout_count,
            "represented_basho_count": max(
                row.basho_count for row in result.equal_scores
            ),
            "unranked_initial_rikishi": [
                int(value)
                for value in result.prepared.unranked_initial_rikishi
            ],
        },
        "interpretation_boundary": (
            "The randomized envelopes describe the 5th-to-95th ordered "
            "results from 100 mappings of each placebo; every prior retains "
            "Proposal 3's retrospective use of future outcomes."
        ),
    }


def _report(
    result: RandomisedPriorResult,
    horizon_rows: tuple[dict[str, object], ...],
    history_source: HistorySource,
    prior_source: HistorySource,
) -> str:
    lines: list[str] = []
    for scope in SCOPES:
        lines.extend((f"### {scope.capitalize()}", "", _table_header()))
        scope_rows = tuple(row for row in horizon_rows if row["scope"] == scope)
        horizons = tuple(dict.fromkeys(row["horizon_basho"] for row in scope_rows))
        for horizon in horizons:
            rows = tuple(
                row for row in scope_rows if row["horizon_basho"] == horizon
            )
            equal = next(row for row in rows if row["model"] == "equal")
            genuine = next(row for row in rows if row["model"] == "genuine Chii")
            placebo_losses = {
                placebo: tuple(
                    float(row["mean_log_loss"])
                    for row in rows if row["placebo"] == placebo
                )
                for placebo in PLACEBOS
            }
            summaries = {
                placebo: summarize_ordered(values)
                for placebo, values in placebo_losses.items()
            }
            global_summary = summaries[GLOBAL_PLACEBO]
            within_summary = summaries[WITHIN_DIVISION_PLACEBO]
            label = str(equal["horizon"])
            lines.append(
                f"| {label} | {float(equal['mean_log_loss']):.6f} | "
                f"{float(genuine['mean_log_loss']):.6f} "
                f"({float(genuine['log_loss_difference_from_equal']):+.6f}) | "
                f"{global_summary.percentile_5:.6f} / {global_summary.median:.6f} / "
                f"{global_summary.percentile_95:.6f} | "
                f"{within_summary.percentile_5:.6f} / {within_summary.median:.6f} / "
                f"{within_summary.percentile_95:.6f} | "
                f"{sum(value < float(genuine['mean_log_loss']) for value in placebo_losses[GLOBAL_PLACEBO])} | "
                f"{sum(value < float(equal['mean_log_loss']) for value in placebo_losses[GLOBAL_PLACEBO])} | "
                f"{sum(value < float(genuine['mean_log_loss']) for value in placebo_losses[WITHIN_DIVISION_PLACEBO])} | "
                f"{sum(value < float(equal['mean_log_loss']) for value in placebo_losses[WITHIN_DIVISION_PLACEBO])} |"
            )
        lines.append("")

    final_basho = max(row.basho_count for row in result.equal_scores)
    final_rows = tuple(
        row for row in horizon_rows if row["horizon_basho"] == final_basho
    )
    brier_lines = []
    for scope in SCOPES:
        rows = tuple(row for row in final_rows if row["scope"] == scope)
        equal = next(row for row in rows if row["model"] == "equal")
        genuine = next(row for row in rows if row["model"] == "genuine Chii")
        placebo_values = {
            placebo: tuple(
                float(row["mean_brier_score"])
                for row in rows if row["placebo"] == placebo
            )
            for placebo in PLACEBOS
        }
        brier_lines.append(
            f"- {scope}: equal {float(equal['mean_brier_score']):.6f}; genuine "
            f"{float(genuine['mean_brier_score']):.6f} "
            f"({float(genuine['brier_difference_from_equal']):+.6f}); "
            f"global lower than genuine/equal "
            f"{sum(value < float(genuine['mean_brier_score']) for value in placebo_values[GLOBAL_PLACEBO])}/"
            f"{sum(value < float(equal['mean_brier_score']) for value in placebo_values[GLOBAL_PLACEBO])}; "
            f"within-division lower than genuine/equal "
            f"{sum(value < float(genuine['mean_brier_score']) for value in placebo_values[WITHIN_DIVISION_PLACEBO])}/"
            f"{sum(value < float(equal['mean_brier_score']) for value in placebo_values[WITHIN_DIVISION_PLACEBO])}."
        )

    return f"""# Proposal 4: Randomized Chii-prior Placebo

## Definition

The Proposal 3 rating values were assigned to their genuine Chii ordinals, to
100 fixed-seed global permutations, and to 100 fixed-seed permutations that
preserved each actual division's rating multiset. Each mapping initialized one
complete q=400, k=35 chronological Elo pass. Equal-1500 initialization supplied
the deterministic control. Every eligible bout updated every producer; Chii
selected initial values and evaluation populations only.

History source: `{history_source.path}`  
History SHA-256: `{history_source.sha256}`  
Prior source: `{prior_source.path}`  
Prior SHA-256: `{prior_source.sha256}`

## Cumulative log loss at declared horizons

Each placebo column is 5th percentile / median / 95th percentile. The final
four columns count strict losses among the corresponding 100 mappings. Lower
loss is better.

{chr(10).join(lines)}
## Complete-epoch Brier check

{chr(10).join(brier_lines)}

## Interpretation boundary

The global range compares the observed Chii-to-rating association with
arbitrary assignments of exactly the same values. The within-division range
preserves broad division structure and tests the additional association with
exact Chii inside each division. The genuine mapping and all placebos retain
the same retrospective use of future outcomes, so none is an out-of-sample
prior. With 100 permutations per placebo, ranks and order-statistic bands are
exploratory.
"""


def _table_header() -> str:
    return (
        "| Horizon | Equal | Genuine (difference) | Global p05 / median / p95 | "
        "Within-division p05 / median / p95 | Global < genuine | Global < equal | "
        "Within < genuine | Within < equal |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    )


def _write_chart(rows: tuple[dict[str, object], ...], filename: Path) -> None:
    traces: list[dict[str, object]] = []
    traces_per_scope = 10
    for scope_index, scope in enumerate(SCOPES):
        scope_rows = tuple(row for row in rows if row["scope"] == scope)
        dates = [_plot_date_from_text(str(row["date"])) for row in scope_rows]
        visible = scope_index == 0
        for axis, stem in (
            ("y", "log"),
            ("y2", "brier"),
        ):
            for prefix, label, colour, fillcolour in (
                ("global_random", "Global random", "#666", "rgba(120,120,120,0.18)"),
                ("within_division_random", "Within-division random", "#dd7500", "rgba(238,140,30,0.16)"),
            ):
                lower = [
                    row[f"{prefix}_{stem}_p05_difference_from_equal"]
                    for row in scope_rows
                ]
                upper = [
                    row[f"{prefix}_{stem}_p95_difference_from_equal"]
                    for row in scope_rows
                ]
                traces.append({
                    "type": "scatter",
                    "x": dates + dates[::-1],
                    "y": upper + lower[::-1],
                    "xaxis": "x" if axis == "y" else "x2",
                    "yaxis": axis,
                    "fill": "toself",
                    "fillcolor": fillcolour,
                    "line": {"color": "rgba(0,0,0,0)"},
                    "hoverinfo": "skip",
                    "name": f"{label} 5th-95th",
                    "legendgroup": f"{prefix} band",
                    "showlegend": axis == "y",
                    "visible": visible,
                })
                traces.append({
                    "type": "scatter",
                    "x": dates,
                    "y": [
                        row[f"{prefix}_{stem}_median_difference_from_equal"]
                        for row in scope_rows
                    ],
                    "xaxis": "x" if axis == "y" else "x2",
                    "yaxis": axis,
                    "mode": "lines",
                    "line": {"color": colour, "width": 2, "dash": "dot"},
                    "name": f"{label} median",
                    "legendgroup": f"{prefix} median",
                    "showlegend": axis == "y",
                    "visible": visible,
                    "hovertemplate": "%{x|%Y/%m}<br>difference=%{y:.6f}<extra></extra>",
                })
            traces.append({
                "type": "scatter",
                "x": dates,
                "y": [row[f"genuine_{stem}_difference_from_equal"] for row in scope_rows],
                "xaxis": "x" if axis == "y" else "x2",
                "yaxis": axis,
                "mode": "lines",
                "line": {"color": "#3366cc", "width": 2},
                "name": "Genuine Chii",
                "legendgroup": "genuine",
                "showlegend": axis == "y",
                "visible": visible,
                "hovertemplate": "%{x|%Y/%m}<br>difference=%{y:.6f}<extra></extra>",
            })

    buttons = []
    for index, scope in enumerate(SCOPES):
        visible = [False] * len(traces)
        start = index * traces_per_scope
        visible[start:start + traces_per_scope] = [True] * traces_per_scope
        buttons.append({
            "label": scope.capitalize(),
            "method": "update",
            "args": [{"visible": visible}],
        })
    layout = {
        "title": {
            "text": (
                "Proposal 4: randomized Chii-prior placebo"
                "<br><sup>Negative differences favour the alternative to equal initialization; "
                "each shaded band spans ordered results 5 to 95 from its 100 randomized Chii mappings.</sup>"
            ),
            "x": 0.5,
            "xanchor": "center",
            "y": 0.98,
            "yanchor": "top",
        },
        "template": "plotly_white",
        "height": 850,
        "hovermode": "x unified",
        "legend": {
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": 1.15,
            "yanchor": "middle",
        },
        "updatemenus": [{
            "type": "dropdown",
            "buttons": buttons,
            "x": 0,
            "xanchor": "left",
            "y": 1.08,
            "yanchor": "middle",
        }],
        "margin": {"l": 80, "r": 30, "t": 180, "b": 60},
        "xaxis": {
            "domain": [0, 1], "anchor": "y", "type": "date",
            "tickformat": "%Y/%m", "showticklabels": False,
        },
        "yaxis": {
            "domain": [0.56, 1], "title": "Log-loss difference",
            "zeroline": True, "zerolinecolor": "#222",
        },
        "xaxis2": {
            "domain": [0, 1], "anchor": "y2", "type": "date",
            "tickformat": "%Y/%m", "title": "Basho",
        },
        "yaxis2": {
            "domain": [0, 0.44], "title": "Brier-loss difference",
            "zeroline": True, "zerolinecolor": "#222",
        },
        "annotations": [
            {"text": "Cumulative mean log-loss difference from equal", "x": 0.5, "y": 1.04, "xref": "paper", "yref": "paper", "showarrow": False},
            {"text": "Cumulative mean Brier-loss difference from equal", "x": 0.5, "y": 0.48, "xref": "paper", "yref": "paper", "showarrow": False},
        ],
    }
    document = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Proposal 4 randomized Chii-prior placebo</title>
  <script src="https://cdn.plot.ly/plotly-3.0.1.min.js" charset="utf-8"></script>
</head>
<body style="margin:0">
  <div id="chart" style="width:100%;min-height:850px"></div>
  <script>
    const traces = __TRACES__;
    const layout = __LAYOUT__;
    Plotly.newPlot("chart", traces, layout, {responsive: true, displaylogo: false});
  </script>
</body>
</html>
"""
    filename.write_text(
        document.replace("__TRACES__", json.dumps(traces)).replace(
            "__LAYOUT__", json.dumps(layout)
        ),
        encoding="utf-8",
    )


def _plot_date_from_text(date: str) -> str:
    return f"{date[:4]}-{date[5:7]}-01"


def _placebo_prefix(placebo: str) -> str:
    return placebo.replace(" ", "_") + "_random"
