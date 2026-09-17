"""Publish the chii drift evidence, an offline explorer and reproducible provenance."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

import pandas as pd

from .chii_drift import SETTINGS, DriftTables
from .inputs import digest


def records(frame):
    """Convert pandas missing values to JSON nulls for the browser."""
    return json.loads(frame.to_json(orient="records", double_precision=10))


def markdown_table(frame, columns):
    """Render small evidence tables without a third-party Markdown dependency."""
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in frame[list(columns)].itertuples(index=False, name=None):
        values = ["—" if pd.isna(x) else f"{x:+.2f}" if isinstance(x, float) else str(x).replace("|", "\\|") for x in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def report_text(inputs, tables: DriftTables):
    """State data-derived findings and their interpretation limits explicitly."""
    trends = tables.trends
    main = trends[(trends.level == "numbered") & (trends.endpoint == "end") & (trends.selection == "full")]
    supported = main[main.eligible]
    examples = pd.concat([
        supported.nlargest(5, "slope_points_per_decade"),
        supported.nsmallest(5, "slope_points_per_decade"),
        supported.nlargest(5, "period_range"),
    ]).drop_duplicates("group")
    familiar = main[main.group.isin(["Y1", "O1", "S1", "K1", "M1", "J1", "Ms1", "Sd1", "Jd1", "Jk1"])]
    pop = tables.population[tables.population.division == "all"]
    pos = (supported.slope_points_per_decade > 0).sum()
    neg = (supported.slope_points_per_decade < 0).sum()
    columns = ["group", "basho_count", "slope_points_per_decade", "first_last_period_change", "period_range"]
    lines = [
        "# Per-chii rating drift in the saved Elo89 run", "",
        f"Coverage: **{inputs.dates[0]}–{inputs.dates[-1]}**, {len(inputs.dates)} represented basho. "
        f"The primary endpoint is after post-basho normalisation; ranks belong to that same basho.", "",
        "## Main findings", "",
        f"Of {len(main)} numbered-rank groups, {len(supported)} meet the presentation rule "
        f"(60 basho over ten years); {len(main)-len(supported)} have lower support. "
        f"Among eligible groups, {pos} have positive full-history slopes and {neg} negative slopes. "
        "These are descriptive signs, not significance decisions.", "",
    ]
    if len(supported):
        lines += [f"Full-history slopes range from {supported.slope_points_per_decade.min():+.2f} to "
                  f"{supported.slope_points_per_decade.max():+.2f} points per decade. "
                  f"The median is {supported.slope_points_per_decade.median():+.2f}. "
                  f"The largest separation between five-year period means is {supported.period_range.max():.2f} points. "
                  "The table below shows how net direction and within-history movement differ.", ""]
    for name in ("M1", "Y1", "Jk1"):
        sequence = tables.periods[(tables.periods.level == "numbered") & (tables.periods.group == name)
                                 & (tables.periods.endpoint == "end") & (tables.periods.basho_count > 0)]
        if len(sequence) >= 2:
            first, last = sequence.iloc[0], sequence.iloc[-1]
            peak = sequence.loc[sequence["mean"].idxmax()]
            lines += [f"**{name}:** mean {first['mean']:.1f} in {first.period_start}–{first.period_end}, "
                      f"maximum period mean {peak['mean']:.1f} in {peak.period_start}–{peak.period_end}, "
                      f"and {last['mean']:.1f} in {last.period_start}–{last.period_end}. "
                      "These period means make temporary rises or subsequent falls visible alongside the full-run slope.", ""]
    for label, selector in [
        ("basho-start endpoints", (trends.endpoint == "start") & (trends.selection == "full")),
        ("excluding the first 12 represented basho", (trends.endpoint == "end") & (trends.selection == "exclude_first_12")),
        ("January 2000 onward", (trends.endpoint == "end") & (trends.selection == "since_2000")),
    ]:
        comparison = supported.merge(trends[(trends.level == "numbered") & selector], on="group", suffixes=("_full", "_comparison"))
        comparison = comparison[comparison.eligible_comparison]
        opposing = comparison.slope_points_per_decade_full * comparison.slope_points_per_decade_comparison < 0
        difference = (comparison.slope_points_per_decade_full - comparison.slope_points_per_decade_comparison).abs()
        lines += [f"Compared with {label}, {int(opposing.sum())} of {len(comparison)} jointly eligible groups "
                  f"reverse slope sign; the median absolute slope difference is {difference.median():.2f} points per decade. "
                  "Signs close to zero should be read alongside magnitudes.", ""]
    lines += ["### Familiar ranks", "", markdown_table(familiar, columns), "",
              "### Largest movements", "",
              "Union of the five highest slopes, five lowest slopes and five largest period ranges among eligible numbered groups. "
              "Selection is for inspection, not a declaration of materiality. The explorer and CSVs retain every group.", "",
              markdown_table(examples, columns), "",
              "### Period and occupant context", ""]
    for group in examples.group:
        period = tables.periods[(tables.periods.level == "numbered") & (tables.periods.group == group) & (tables.periods.endpoint == "end")]
        sequence = "; ".join(f"{r.period_start}–{r.period_end}: {r.mean:.1f} ({r.basho_count} basho, {r.distinct_rikishi} rikishi)"
                             if r.basho_count else f"{r.period_start}–{r.period_end}: absent"
                             for r in period.itertuples())
        people = tables.occupants[(tables.occupants.level == "numbered") & (tables.occupants.group == group) & (tables.occupants.period == "full")].nlargest(3, "observations")
        names = "; ".join(f"{r.name} (ID {r.rikishi_id}): {r.share:.1%}" for r in people.itertuples())
        lines += [f"**{group}.** {sequence}. Most frequent occupants: {names}. "
                  "Shares count occupant observations, whereas period rating means weight basho equally.", ""]
    divisions = tables.population[(tables.population.endpoint == "end") & (tables.population.division != "all")]
    context = divisions.groupby("division").agg(min_count=("count", "min"), max_count=("count", "max"),
                                                 min_rank_depth=("rank_depth", "min"), max_rank_depth=("rank_depth", "max"))
    lines += ["### Population composition", "", markdown_table(context.reset_index(), list(context.reset_index().columns)), "",
              "Division membership and available rank depth change over the run. The occupant table provides per-period "
              "identities and shares for tracing turnover. These describe context; they do not identify causes.", "",
              "## Population verification", "",
              f"The saved target is {float(inputs.manifest['target_mean']):.10f}. Both endpoint means reconcile at every basho. "
              f"Mean residual range: {pop.mean_residual.min():.3g} to {pop.mean_residual.max():.3g} points; "
              f"largest absolute count-weighted division reconciliation residual: {pop.partition_residual.abs().max():.3g}. "
              f"Population size ranges from {pop['count'].min()} to {pop['count'].max()}.", "",
              f"The central 90% rating spread ranges from {pop.spread_90.min():.2f} to {pop.spread_90.max():.2f} points across both endpoints. "
              "Quantiles, division means and contemporaneous selected group gaps are included in the explorer and CSVs.", "",
              f"Observations: {len(tables.observations):,}; duplicate literal-position rows retained and flagged: "
              f"{tables.observations.duplicate_position.sum()}; unclassified rows retained in population checks: "
              f"{tables.observations.literal.eq('').sum()}.", "",
              "## What the account can say", "",
              "Elo89 holds the overall population mean fixed, while ratings associated with particular chii "
              "can move over historical time. The numerical tables quantify direction, period variation and "
              "sensitivity separately; a single full-history slope is not a sufficient description. "
              "A stable mean therefore does not establish stability at each rank.", "",
              "These observations do not establish algorithmic inflation, absolute ability comparisons across eras, "
              "or a need to change the accepted model. Occupants, rank availability, population composition, "
              "initialisation and competitive relationships can all matter. A trend reversal or a change in slope "
              "with the selected period must remain visible in the account.", "",
              "## Definitions and reproducibility", "",
              "The full analysis includes literal side/annotation-specific chii, east/west numbered groups, and "
              "separate Y/O/S/K title summaries. Numbered title ranks remain distinct. Empty periods have zero "
              "support counts and missing rating statistics. The final calendar period is partial. Period contrasts "
              "use the first and last *supported* periods of each selection, whose coverage is listed in the tables.", "",
              "Period medians, quartiles and ranges describe per-basho group means. Rolling means cover 12 represented "
              "basho with at least six observed values. Traces break at every missing represented basho or calendar "
              "gap exceeding four months. No missing rating is replaced by zero. Slopes use calendar dates and "
              "carry no independent-observation p-values or confidence intervals.", "",
              "The saved prior is validated and hashed as provenance but is not plotted: production grouping can "
              "differ from the study's numbered and literal groupings. No priors were fitted and no ratings replayed.", "",
              "Open `charts.html` beside `chart_data/data.js`; it works offline. `trend_summary.csv` contains "
              "both endpoints and all three selections, including ineligible groups. `chii_periods.csv` is the "
              "full coverage table. `occupant_context.csv`, `population_summary.csv` and `group_gaps.csv` support "
              "contextual inspection. `manifest.json` identifies all current outputs, input hashes and settings.", ""]
    return "\n".join(lines)


def write_outputs(output: Path, inputs, source, tables: DriftTables):
    """Write declared files without deleting unrelated diagnostics or source data."""
    output.mkdir(parents=True, exist_ok=True)
    frames = {
        "observations.csv": tables.observations, "chii_basho.csv": tables.basho,
        "chii_periods.csv": tables.periods, "trend_summary.csv": tables.trends,
        "population_summary.csv": tables.population, "occupant_context.csv": tables.occupants,
        "group_gaps.csv": tables.gaps,
    }
    for name, frame in frames.items():
        frame.to_csv(output / name, index=False)
    (output / "report.md").write_text(report_text(inputs, tables), encoding="utf-8")
    shutil.copyfile(Path(__file__).with_name("chii_drift_charts.html"), output / "charts.html")
    data_dir = output / "chart_data"
    data_dir.mkdir(exist_ok=True)
    data = {"dates": inputs.dates, "settings": SETTINGS,
            "trends": records(tables.trends), "periods": records(tables.periods),
            "population": records(tables.population), "gaps": records(tables.gaps), "series": {}}
    data["series_columns"] = ["basho_index", "rating", "rolling_mean", "rolling_count", "occupant_count"]
    for key, frame in tables.basho.groupby(["level", "group", "endpoint"], sort=False):
        data["series"]["|".join(key)] = json.loads(frame[data["series_columns"]].to_json(orient="values", double_precision=8))
    (data_dir / "data.js").write_text("window.DRIFT = " + json.dumps(data, ensure_ascii=True, separators=(",", ":")) + ";\n", encoding="utf-8")
    files = list(frames) + ["report.md", "charts.html", "chart_data/data.js"]
    scripts = [Path(__file__).with_name(name) for name in ("chii_drift.py", "chii_drift_report.py", "chii_drift_charts.html", "inputs.py")]
    manifest = {
        "schema_version": 1, "analysis": "elo89_per_chii_drift", "settings": SETTINGS,
        "history": source, "dates": inputs.dates, "model_manifest": inputs.manifest,
        "inputs": {key: {"path": str(path), "sha256": inputs.hashes[key]} for key, path in inputs.paths.items()},
        "implementation": {path.name: digest(path) for path in scripts},
        "files": files + ["manifest.json"],
        "output_sha256": {name: digest(output / name) for name in files},
        "verification": {"source_validation": "passed", "snapshot_and_partition_means": "passed", "tolerance_points": 1e-6},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
