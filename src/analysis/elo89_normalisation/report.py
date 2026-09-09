"""CSV, prose and offline interactive presentation of diagnostic accounting."""

import json
from pathlib import Path

import pandas as pd

from .accounting import WINDOWS, TOLERANCE
from .inputs import digest
from .summary import describe


def write_outputs(root, inputs, frame, exclusions, summaries, comparisons, exceptions,
                  source, site_checked, site_hashes):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    adjustments = pd.DataFrame(inputs.adjustments.values())
    adjustments["combined"] = adjustments.start_adjustment + adjustments.end_adjustment
    latest = frame[frame.end_date == inputs.dates[-1]]
    tables = {"basho_adjustments": adjustments, "window_changes": frame,
              "latest_changes": latest, "summaries": summaries, "comparisons": comparisons,
              "exceptions": exceptions, "exclusions": exclusions}
    adjustment_summary = pd.DataFrame([{"component": key, **describe(adjustments[key])}
                                      for key in ("start_adjustment", "end_adjustment", "combined")])
    tables["adjustment_summary"] = adjustment_summary
    extreme = pd.concat([adjustments.nlargest(5, "start_adjustment").assign(reason="largest_positive"),
                         adjustments.nsmallest(5, "start_adjustment").assign(reason="largest_negative")])
    tables["extreme_basho"] = extreme
    for name, data in tables.items():
        data.to_csv(root / f"{name}.csv", index=False, float_format="%.12g")

    # Local script shards work over file:// as well as HTTP; no remote dependencies.
    shard_dir = root / "chart_data"
    shard_dir.mkdir(exist_ok=True)
    columns = list(frame.columns)
    shards = []
    for date, rows in frame.groupby("end_date", sort=True):
        path = shard_dir / f"{date.replace('/', '-')}.js"
        encoded = rows.to_json(orient="values", double_precision=10, force_ascii=True)
        path.write_text(f"window.acceptData({json.dumps(date)}, {encoded});\n", encoding="utf-8")
        shards.append(str(path.relative_to(root)))
    config = {"columns": columns, "dates": sorted(frame.end_date.unique()), "windows": list(WINDOWS),
              "adjustments": json.loads(adjustments.to_json(orient="records")),
              "comparisons": json.loads(comparisons[comparisons.endpoint == "all"].to_json(orient="records"))}
    template = Path(__file__).with_name("charts.html").read_text(encoding="utf-8")
    (root / "charts.html").write_text(template.replace("/*CONFIG*/", "const config = " +
                                                     json.dumps(config).replace("<", "\\u003c") + ";"), encoding="utf-8")
    lines = ["# Elo-89 normalisation diagnostics", "",
        f"Saved run: {inputs.dates[0]}–{inputs.dates[-1]} ({len(inputs.dates)} basho).",
        f"History source: {source['kind']}. Model: elo-89.", "",
        f"Reconciled {len(frame):,} wrestler-window observations; maximum absolute residual "
        f"{frame.residual.abs().max():.3g} points (tolerance {TOLERANCE:g}).",
        f"Latest site rows checked: {site_checked if site_checked is not None else 'not available; no site CSV directory supplied'}.", "",
        "These are accounting contributions, holding observed bout updates fixed. They are not",
        "counterfactual ratings. A common shift changes no simultaneous pairwise gap.", "",
        "All rating quantities below are points. Ratios compare group-level absolute magnitudes;",
        "they are not individual percentages or pass/fail thresholds. No verdict on materiality is automated.", "",
        "## Common adjustments (one observation per basho)", "",
        "| Component | Mean | Mean absolute | Median | Min | Max |",
        "|---|---:|---:|---:|---:|---:|"]
    for _, row in adjustment_summary.iterrows():
        lines.append(f"| {row.component} | {row['mean']:.4f} | {row.mean_absolute:.4f} | {row.p50:.4f} | {row.p0:.4f} | {row.p100:.4f} |")
    lines += ["", "## Continuous rating windows over the full history", "",
        "Each wrestler-window has equal weight. Windows overlap and are not independent samples.",
        "Makuuchi means membership at the end endpoint; the throughout subgroup requires",
        "Makuuchi membership at every represented endpoint. Reset windows are reported separately.", "",
        "| Population | Basho window | Rows | Mean abs adjustment | Mean abs bouts | Ratio | Median abs adjustment | Median abs bouts | Sign reversals |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for _, row in comparisons[comparisons.endpoint == "all"].iterrows():
        ratio = "n/a" if pd.isna(row.mean_ratio) else f"{row.mean_ratio:.4f}"
        lines.append(f"| {row.population} | {row.window} | {row['count']:,} | {row.mean_abs_normalisation:.4f} | {row.mean_abs_bout:.4f} | {ratio} | {row.median_abs_normalisation:.4f} | {row.median_abs_bout:.4f} | {row.sign_reversals} |")
    lines += ["", "## Reading the outputs", "",
        "- [Interactive charts and enriched change table](charts.html) select endpoint, window and population.",
        "- `summaries.csv` contains signed and absolute percentiles, overall and per endpoint, split by episode status.",
        "- `comparisons.csv` preserves both ratio denominators, sign-reversal counts and exact-zero counts.",
        "- `exceptions.csv` contains the largest adjustment contributions (including ties), sign reversals, resets and largest residuals.",
        "- `extreme_basho.csv` records the five largest positive and negative pre-basho shifts.",
        "- `exclusions.csv` counts missing endpoints. Entrants without a start endpoint are not assigned a zero change.", "",
        f"Reset-containing windows: {int((frame.status == 'reset').sum()):,}. "
        f"Unclassified end divisions: {int((frame.end_division == 'unclassified').sum()):,}.", "",
        "Positive and negative normalisation may cancel over a window; both pre and post contributions remain available.",
        "A small sign reversal alone is not evidence of practical importance. The author should inspect",
        "the magnitudes, historical variation and exceptional cases before interpreting these results.", ""]
    (root / "report.md").write_text("\n".join(lines), encoding="utf-8")
    outputs = [f"{name}.csv" for name in tables] + ["report.md", "charts.html", *shards, "manifest.json"]
    manifest = {"package_id": "elo89_normalisation", "schema_version": 1,
        "code_sha256": {p.name: digest(p) for p in sorted(Path(__file__).parent.iterdir())
                        if p.suffix in (".py", ".html")},
        "model_manifest": inputs.manifest, "history_source": source,
        "input_files": {key: {"path": str(path), "sha256": inputs.hashes[key]} for key, path in inputs.paths.items()},
        "site_input_hashes": site_hashes, "site_rows_checked": site_checked,
        "start": inputs.dates[0], "end": inputs.dates[-1], "windows": WINDOWS,
        "row_count": len(frame), "maximum_absolute_residual": float(frame.residual.abs().max()),
        "tolerance": TOLERANCE, "percentile_method": "linear", "standard_deviation": "population",
        "outputs": outputs}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
