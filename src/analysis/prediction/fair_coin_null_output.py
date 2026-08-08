"""Write Proposal 6's fair-coin null evidence."""

from __future__ import annotations

import csv
from dataclasses import asdict
import json
from pathlib import Path

from .fair_coin_null import FairCoinNullResult
from .output import HistorySource


def write_fair_coin_null_outputs(
    result: FairCoinNullResult,
    output_directory: Path,
    source: HistorySource,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_directory / "observed_betting.csv",
        (asdict(row) for row in result.observed_scores),
    )
    _write_csv(
        output_directory / "null_histories.csv",
        (
            {"replicate": replicate.replicate, **asdict(score)}
            for replicate in result.null_replicates
            for score in replicate.scores
        ),
    )
    _write_csv(
        output_directory / "null_summary.csv",
        (asdict(row) for row in result.summaries),
    )
    manifest = {
        "experiment": "Proposal 6: Fair-coin bookmaker null",
        "history_source": asdict(source),
        "epoch": {
            "start": str(result.elo_definition.start_date),
            "end": str(result.elo_definition.end_date),
        },
        "elo": {
            "q": result.elo_definition.q,
            "k": result.elo_definition.k,
            "initial_rating": result.elo_definition.initial_rating,
        },
        "null": asdict(result.null_definition),
        "statistic": (
            "mean profit per represented basho from one uniformly selected "
            "eligible bout per represented day, staking the Basic Elo "
            "favourite probability at evens"
        ),
    }
    (output_directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (output_directory / "report.md").write_text(
        _report(result), encoding="utf-8"
    )
    _write_chart(result, output_directory / "fair_coin_null.html")


def _report(result: FairCoinNullResult) -> str:
    lines = [
        "# Proposal 6: Fair-coin bookmaker null\n",
        "The bookmaker offers evens because every bout is hypothesized to be "
        "50–50. Before each bout, Basic Elo selects its favourite and stakes "
        "£p, where p is that favourite's forecast probability; it does not bet "
        "when p=0.5. A winning bet earns the stake and a losing bet loses it.\n",
        "For each represented day the result is averaged over all eligible "
        "bouts that could have been selected. Those daily values are summed and "
        "averaged over the represented basho. Each null history retains the real "
        "participants and chronology, replaces every result by an independent "
        "50–50 draw, and rebuilds Basic Elo from those simulated results.\n",
        "Each value below is a complete-epoch mean per represented basho, "
        "not the result of one individual basho.\n",
        "| Population | Mean stake | Mean profit | Return on stake | Null median profit | Null 95% range | Null ≥ observed | Monte Carlo p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    observed_by_scope = {row.scope: row for row in result.observed_scores}
    for row in result.summaries:
        observed = observed_by_scope[row.scope]
        lines.append(
            f"| {row.scope} | {_money(observed.mean_stake_per_basho)} | "
            f"{_money(row.observed_profit)} | "
            f"{observed.return_on_stake:.2%} | "
            f"{_money(row.null_median_profit)} | "
            f"{_money(row.null_lower_profit)} to "
            f"{_money(row.null_upper_profit)} | "
            f"{row.null_at_least_observed}/{row.replicate_count} | "
            f"{row.monte_carlo_p:.6g} |"
        )
    lines.extend([
        "",
        "The p value is the fixed one-sided Monte Carlo comparison "
        "`(1 + null histories at least as profitable as observed) / "
        "(1 + number of histories)`. The ordered 95% range is descriptive of "
        "the fair-coin histories. No null history reaches the historical result "
        "in any population, giving the finite simulation value 1/2,001. This "
        "is the experiment's resolution, not a claim that the underlying "
        "probability is exactly 1/2,001.\n",
        "Under this declared test, the historical directional return is "
        "incompatible with independent 50–50 outcomes. The result establishes "
        "predictive information, not calibration of Elo's numerical "
        "probabilities or an available gambling strategy.",
        "",
    ])
    return "\n".join(lines)


def _money(value: float) -> str:
    sign = "-" if value < 0.0 else ""
    return f"{sign}£{abs(value):.6f}"


def _write_chart(result: FairCoinNullResult, filename: Path) -> None:
    traces = []
    for scope in (row.scope for row in result.observed_scores):
        values = [
            next(score for score in replicate.scores if score.scope == scope)
            .mean_profit_per_basho
            for replicate in result.null_replicates
        ]
        observed = next(
            row.observed_profit for row in result.summaries if row.scope == scope
        )
        traces.append({
            "type": "histogram",
            "x": values,
            "name": "Fair-coin histories",
            "visible": scope == result.observed_scores[0].scope,
            "marker": {"color": "#4c78a8"},
            "xaxis": "x",
            "yaxis": "y",
        })
        traces.append({
            "type": "scatter",
            "x": [observed, observed],
            "y": [0, 1],
            "name": "Actual complete-epoch mean",
            "visible": scope == result.observed_scores[0].scope,
            "mode": "lines",
            "line": {"color": "#e45756", "width": 3},
            "yaxis": "y2",
        })
    buttons = []
    for index, score in enumerate(result.observed_scores):
        visible = [False] * len(traces)
        visible[index * 2:index * 2 + 2] = [True, True]
        buttons.append({
            "label": score.scope,
            "method": "update",
            "args": [
                {"visible": visible},
                {"title": _chart_title(result, score.scope)},
            ],
        })
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Proposal 6 fair-coin null</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script></head>
<body><div id="chart" style="width:100%;height:720px"></div><script>
const traces = {json.dumps(traces)};
const layout = {{title: {json.dumps(_chart_title(result, result.observed_scores[0].scope))},
  margin: {{t: 150, r: 50, b: 80, l: 70}},
  xaxis: {{title: {json.dumps(_axis_title(result))}}},
  yaxis: {{title: "Number of fair-coin histories"}}, yaxis2: {{overlaying:"y", range:[0,1], visible:false}},
  updatemenus: [{{type:"dropdown", x:0, y:1.22, xanchor:"left", buttons:{json.dumps(buttons)}}}],
  legend: {{orientation:"h", y:1.10, x:1, xanchor:"right"}}}};
Plotly.newPlot("chart", traces, layout, {{responsive:true}});
</script></body></html>"""
    filename.write_text(html, encoding="utf-8")


def _chart_title(result: FairCoinNullResult, scope: str) -> str:
    count = result.null_definition.replicate_count
    return (
        f"Distribution of complete-epoch mean profit across {count:,} "
        f"fair-coin histories<br><sup>{scope}</sup>"
    )


def _axis_title(result: FairCoinNullResult) -> str:
    return (
        "Mean profit per basho over the complete "
        f"{result.elo_definition.start_date}–{result.elo_definition.end_date} "
        "epoch (£)"
    )


def _write_csv(filename: Path, rows) -> None:
    rows = tuple(rows)
    with filename.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
