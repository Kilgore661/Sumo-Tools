"""Persist Proposal 5 audit evidence, comparisons, chart, and report."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .division_initialisation import DivisionInitialisationResult
from .output import HistorySource, _write_csv
from .randomised_prior import SCOPES


def write_division_initialisation_outputs(
    result: DivisionInitialisationResult,
    placebo_envelope: tuple[dict[str, str], ...],
    output_directory: Path,
    history_source: HistorySource,
    prior_source: HistorySource,
    placebo_source: HistorySource,
) -> None:
    """Write all Proposal 5 artifacts except CLI wall-clock timing."""

    output_directory.mkdir(parents=True, exist_ok=True)
    cumulative = tuple(_comparison_rows(result, placebo_envelope))
    horizons = tuple(_horizon_rows(cumulative, (6, 12, 30, 60)))
    _write_csv(output_directory / "division_prior.csv", _prior_rows(result))
    _write_csv(output_directory / "cumulative_comparison.csv", cumulative)
    _write_csv(output_directory / "horizon_comparison.csv", horizons)
    (output_directory / "manifest.json").write_text(
        json.dumps(
            _manifest(
                result,
                history_source,
                prior_source,
                placebo_source,
            ),
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (output_directory / "report.md").write_text(
        _report(result, horizons, history_source, prior_source, placebo_source),
        encoding="utf-8",
    )
    _write_chart(
        cumulative,
        output_directory / "division_initialisation.html",
    )


def _prior_rows(result: DivisionInitialisationResult):
    for row in result.division_prior:
        yield {
            "division": row.division.name,
            "initial_rating": row.initial_rating,
            "chii_count": row.chii_count,
            "minimum_chii_rating": row.minimum_chii_rating,
            "maximum_chii_rating": row.maximum_chii_rating,
        }


def _comparison_rows(
    result: DivisionInitialisationResult,
    placebo_envelope: tuple[dict[str, str], ...],
):
    genuine = {
        (row.scope, str(row.end_date)): row for row in result.genuine_scores
    }
    division = {
        (row.scope, str(row.end_date)): row for row in result.division_scores
    }
    placebo = {
        (row["scope"], row["date"]): row for row in placebo_envelope
    }
    for equal in result.equal_scores:
        key = (equal.scope, str(equal.end_date))
        real = genuine[key]
        division_only = division[key]
        random = placebo[key]
        yield {
            "scope": equal.scope,
            "date": str(equal.end_date),
            "basho_count": equal.basho_count,
            "bout_count": equal.bout_count,
            "equal_log_loss": equal.mean_log_loss,
            "genuine_log_loss": real.mean_log_loss,
            "genuine_log_difference_from_equal": (
                real.mean_log_loss - equal.mean_log_loss
            ),
            "division_log_loss": division_only.mean_log_loss,
            "division_log_difference_from_equal": (
                division_only.mean_log_loss - equal.mean_log_loss
            ),
            "within_random_log_p05": random["within_division_random_log_p05"],
            "within_random_log_median": random["within_division_random_log_median"],
            "within_random_log_p95": random["within_division_random_log_p95"],
            "equal_brier_score": equal.mean_brier_score,
            "genuine_brier_score": real.mean_brier_score,
            "genuine_brier_difference_from_equal": (
                real.mean_brier_score - equal.mean_brier_score
            ),
            "division_brier_score": division_only.mean_brier_score,
            "division_brier_difference_from_equal": (
                division_only.mean_brier_score - equal.mean_brier_score
            ),
            "within_random_brier_p05": random["within_division_random_brier_p05"],
            "within_random_brier_median": random["within_division_random_brier_median"],
            "within_random_brier_p95": random["within_division_random_brier_p95"],
        }


def _horizon_rows(
    cumulative: tuple[dict[str, object], ...],
    horizons: tuple[int, ...],
):
    final_basho = max(int(row["basho_count"]) for row in cumulative)
    selected = horizons + (final_basho,)
    for scope in SCOPES:
        for horizon in selected:
            row = next(
                row for row in cumulative
                if row["scope"] == scope and row["basho_count"] == horizon
            )
            yield {
                **row,
                "horizon": (
                    "complete represented epoch"
                    if horizon == final_basho else horizon
                ),
            }


def _manifest(
    result: DivisionInitialisationResult,
    history_source: HistorySource,
    prior_source: HistorySource,
    placebo_source: HistorySource,
) -> dict[str, object]:
    return {
        "experiment": "Proposal 5: Deterministic Division-only Initialization",
        "history_source": asdict(history_source),
        "prior_source": asdict(prior_source),
        "placebo_envelope_source": asdict(placebo_source),
        "definition": {
            "start_date": str(result.definition.start_date),
            "end_date": str(result.definition.end_date),
            "q": result.definition.q,
            "k": result.definition.k,
            "division_value": (
                "unweighted arithmetic mean of completed Proposal 3 Chii "
                "ratings in the actual division"
            ),
            "makuuchi_membership": "Yokozuna, Ozeki, Sekiwake, Komusubi, Maegashira",
            "unranked_fallback": "Jonokuchi division mean",
        },
        "division_prior": [
            {"division": row.division.name, **{
                key: value
                for key, value in asdict(row).items()
                if key != "division"
            }}
            for row in result.division_prior
        ],
        "unranked_initial_rikishi": [
            int(value) for value in result.prepared.unranked_initial_rikishi
        ],
        "interpretation_boundary": (
            "The division means inherit Proposal 3's retrospective use of "
            "future outcomes; comparisons are descriptive and have no "
            "sampling interval or practical-importance threshold."
        ),
    }


def _report(
    result: DivisionInitialisationResult,
    horizons: tuple[dict[str, object], ...],
    history_source: HistorySource,
    prior_source: HistorySource,
    placebo_source: HistorySource,
) -> str:
    sections: list[str] = []
    for scope in SCOPES:
        sections.extend((f"### {scope.capitalize()}", "", _table_header()))
        for row in (value for value in horizons if value["scope"] == scope):
            sections.append(
                f"| {row['horizon']} | {float(row['equal_log_loss']):.6f} | "
                f"{float(row['genuine_log_loss']):.6f} | "
                f"{float(row['division_log_loss']):.6f} "
                f"({float(row['division_log_difference_from_equal']):+.6f}) | "
                f"{float(row['within_random_log_p05']):.6f} / "
                f"{float(row['within_random_log_median']):.6f} / "
                f"{float(row['within_random_log_p95']):.6f} |"
            )
        sections.append("")

    final_basho = max(int(row["basho_count"]) for row in horizons)
    final_rows = tuple(
        row for row in horizons if row["basho_count"] == final_basho
    )
    brier = "\n".join(
        f"- {row['scope']}: equal {float(row['equal_brier_score']):.6f}; "
        f"genuine {float(row['genuine_brier_score']):.6f}; division-only "
        f"{float(row['division_brier_score']):.6f} "
        f"({float(row['division_brier_difference_from_equal']):+.6f}); "
        f"within-division median {float(row['within_random_brier_median']):.6f}."
        for row in final_rows
    )
    prior_lines = "\n".join(
        f"- {row.division.name}: {row.initial_rating:.6f} from "
        f"{row.chii_count} Chii values (range "
        f"{row.minimum_chii_rating:.6f} to {row.maximum_chii_rating:.6f})."
        for row in result.division_prior
    )
    return f"""# Proposal 5: Deterministic Division-only Initialization

## Definition

Each actual division receives the unweighted arithmetic mean of its completed
Proposal 3 Chii ratings. That value initializes every newly encountered RikId
whose first pre-bout Chii belongs to the division. Equal and genuine exact-Chii
passes are recomputed over the same represented bouts. Proposal 4's
within-division randomized range is read as comparison evidence.

History source: `{history_source.path}`  
History SHA-256: `{history_source.sha256}`  
Prior source: `{prior_source.path}`  
Prior SHA-256: `{prior_source.sha256}`  
Placebo source: `{placebo_source.path}`  
Placebo SHA-256: `{placebo_source.sha256}`

## Division prior

{prior_lines}

## Cumulative log loss at declared horizons

The within-division column is Proposal 4's ordered value 5 / median / ordered
value 95. Lower loss is better.

{chr(10).join(sections)}
## Complete-epoch Brier check

{brier}

## Interpretation boundary

These are observed proper-score differences on the represented bouts. Small
differences remain small: this experiment supplies neither a sampling interval
nor a threshold for practical importance. The randomized range describes
mapping sensitivity. All non-equal priors inherit Proposal 3's future outcomes
and remain oracle diagnostics rather than prospective models.
"""


def _table_header() -> str:
    return (
        "| Horizon | Equal | Genuine Chii | Division-only (difference) | "
        "Within-division p05 / median / p95 |\n"
        "|---|---:|---:|---:|---:|"
    )


def _write_chart(rows: tuple[dict[str, object], ...], filename: Path) -> None:
    traces: list[dict[str, object]] = []
    traces_per_scope = 4
    for scope_index, scope in enumerate(SCOPES):
        scope_rows = tuple(row for row in rows if row["scope"] == scope)
        dates = [_plot_date(str(row["date"])) for row in scope_rows]
        visible = scope_index == 0
        for axis, stem in (("y", "log"), ("y2", "brier")):
            equal_key = "equal_log_loss" if stem == "log" else "equal_brier_score"
            genuine_key = "genuine_log_loss" if stem == "log" else "genuine_brier_score"
            division_key = "division_log_loss" if stem == "log" else "division_brier_score"
            lower_key = f"within_random_{stem}_p05"
            upper_key = f"within_random_{stem}_p95"
            median_key = f"within_random_{stem}_median"
            traces.append({
                "type": "scatter",
                "x": dates + dates[::-1],
                "y": [float(row[upper_key]) - float(row[equal_key]) for row in scope_rows]
                + [float(row[lower_key]) - float(row[equal_key]) for row in reversed(scope_rows)],
                "xaxis": "x" if axis == "y" else "x2",
                "yaxis": axis,
                "fill": "toself",
                "fillcolor": "rgba(238,140,30,0.16)",
                "line": {"color": "rgba(0,0,0,0)"},
                "hoverinfo": "skip",
                "name": "Within-division random 5th-95th",
                "legendgroup": "random band",
                "showlegend": axis == "y",
                "visible": visible,
            })
            traces.append({
                "type": "scatter",
                "x": dates,
                "y": [float(row[median_key]) - float(row[equal_key]) for row in scope_rows],
                "xaxis": "x" if axis == "y" else "x2",
                "yaxis": axis,
                "mode": "lines",
                "line": {"color": "#dd7500", "width": 2, "dash": "dot"},
                "name": "Within-division random median",
                "legendgroup": "random median",
                "showlegend": axis == "y",
                "visible": visible,
            })
            traces.append(_line_trace(
                dates,
                [float(row[genuine_key]) - float(row[equal_key]) for row in scope_rows],
                axis,
                "Genuine Chii",
                "#3366cc",
                visible,
            ))
            traces.append(_line_trace(
                dates,
                [float(row[division_key]) - float(row[equal_key]) for row in scope_rows],
                axis,
                "Division only",
                "#109618",
                visible,
            ))

    buttons = []
    for index, scope in enumerate(SCOPES):
        visibility = [False] * len(traces)
        start = index * traces_per_scope * 2
        visibility[start:start + traces_per_scope * 2] = [True] * (traces_per_scope * 2)
        buttons.append({
            "label": scope.capitalize(),
            "method": "update",
            "args": [{"visible": visibility}],
        })
    layout = {
        "title": {
            "text": (
                "Proposal 5: deterministic division-only initialization"
                "<br><sup>Negative differences favour the alternative to equal initialization; "
                "the shaded band contains ordered within-division results 5 to 95.</sup>"
            ),
            "x": 0.5, "xanchor": "center", "y": 0.98, "yanchor": "top",
        },
        "template": "plotly_white",
        "height": 850,
        "hovermode": "x unified",
        "legend": {
            "orientation": "h", "x": 0.5, "xanchor": "center",
            "y": 1.15, "yanchor": "middle",
        },
        "updatemenus": [{
            "type": "dropdown", "buttons": buttons, "x": 0,
            "xanchor": "left", "y": 1.08, "yanchor": "middle",
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
  <title>Proposal 5 division-only initialization</title>
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


def _line_trace(
    dates: list[str],
    values: list[float],
    axis: str,
    name: str,
    colour: str,
    visible: bool,
) -> dict[str, object]:
    return {
        "type": "scatter",
        "x": dates,
        "y": values,
        "xaxis": "x" if axis == "y" else "x2",
        "yaxis": axis,
        "mode": "lines",
        "line": {"color": colour, "width": 2},
        "name": name,
        "legendgroup": name,
        "showlegend": axis == "y",
        "visible": visible,
        "hovertemplate": "%{x|%Y/%m}<br>difference=%{y:.6f}<extra></extra>",
    }


def _plot_date(date: str) -> str:
    return f"{date[:4]}-{date[5:7]}-01"
