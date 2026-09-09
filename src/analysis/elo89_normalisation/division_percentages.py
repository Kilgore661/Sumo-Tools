"""Reproduce the full-history division table of signed normalisation percentages."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .inputs import digest

DIVISIONS = ("makuuchi", "juryo", "makushita", "sandanme", "jonidan", "jonokuchi")
RECENT_START = "2016/01"


def division_table(frame):
    """One observation per continuous 12-basho window; division at end endpoint."""
    selected = frame[(frame.window == 12) & (frame.status == "continuous")].copy()
    if selected.empty:
        raise ValueError("No continuous 12-basho windows")
    if (not np.isfinite(selected.end_rating).all() or (selected.end_rating <= 0).any()
            or not np.isfinite(selected.normalisation).all()):
        raise ValueError("Percentages require finite contributions and positive finite end ratings")
    selected["percentage"] = 100 * selected.normalisation / selected.end_rating
    rows = []
    extra = sorted(set(selected.end_division.fillna("unclassified")) - set(DIVISIONS))
    selected["end_division"] = selected.end_division.fillna("unclassified")
    for division in (*DIVISIONS, *extra, "all"):
        group = selected if division == "all" else selected[selected.end_division == division]
        p = group.percentage
        row = {"division": division, "observations": len(group),
               "mean_signed_percentage": p.mean(), "median_signed_percentage": p.median(),
               "lowest_percentage": p.min(), "highest_percentage": p.max()}
        for threshold in (1, 5):
            within = int(p.between(-threshold, threshold, inclusive="both").sum())
            row[f"within_{threshold}_count"] = within
            row[f"within_{threshold}_percentage"] = 100 * within / len(p) if len(p) else None
            row[f"below_minus_{threshold}_count"] = int((p < -threshold).sum())
            row[f"above_plus_{threshold}_count"] = int((p > threshold).sum())
        rows.append(row)
    return pd.DataFrame(rows), selected


def recent_sekitori_table(frame):
    """Fixed recent comparison; select by window start, not window end."""
    recent = frame[(frame.start_date >= RECENT_START)
                   & frame.end_division.isin(("makuuchi", "juryo"))]
    table, selected = division_table(recent)
    table = table[table.division.isin(("makuuchi", "juryo"))].copy()
    table["outside_1_count"] = table.below_minus_1_count + table.above_plus_1_count
    return table, selected


def write_table(root: Path):
    source = root / "window_changes.csv"
    source_hash = digest(source)
    frame = pd.read_csv(source)
    table, selected = division_table(frame)
    if digest(source) != source_hash:
        raise ValueError("Source changed while reading")
    table.to_csv(root / "division_percentages.csv", index=False, float_format="%.12g")
    outside = selected[~selected.percentage.between(-5, 5)]
    outside.sort_values("percentage", ascending=False).to_csv(
        root / "division_percentage_exceptions.csv", index=False, float_format="%.12g")
    def number(value, digits=2, signed=False):
        if pd.isna(value):
            return "n/a"
        return format(value, f"{'+' if signed else ''}.{digits}f") + "%"
    lines = ["# Normalisation contribution as a percentage of end rating", "",
        f"Window coverage: {selected.start_date.min()} to {selected.end_date.max()}.", "",
        "Each observation is a continuous 12-basho wrestler-window, classified by division at its end.",
        "Percentage = 100 × net signed normalisation contribution / end rating.",
        "Positive and negative adjustments within each window cancel before division.",
        "Within ±1% and ±5% includes the boundaries. These are the author's descriptive",
        "benchmarks on the published Elo-89 scale, not origin-independent probability measures.", "",
        "| Division | Observations | Mean signed percentage | Within ±1% | Within ±5% | Highest |",
        "|---|---:|---:|---:|---:|---:|"]
    for _, row in table.iterrows():
        lines.append(f"| {row.division.title()} | {row.observations:,} | "
            f"{number(row.mean_signed_percentage, signed=True)} | "
            f"{number(row.within_1_percentage, 1)} | {number(row.within_5_percentage, 1)} | "
            f"{number(row.highest_percentage, signed=True)} |")
    lines += ["", f"Observations outside ±5%: {len(outside):,} of {len(selected):,}.", "",
        "Windows overlap; these are not distinct wrestlers or whole-career contributions.",
        "Reinitialisation windows are excluded. CSV outputs retain minima, medians, exact counts",
        "on either side of each threshold, and the individual observations outside ±5%.", ""]
    (root / "division_percentages.md").write_text("\n".join(lines), encoding="utf-8")
    manifest = {"source": str(source.resolve()), "source_sha256": source_hash,
        "script_sha256": digest(Path(__file__)), "window": 12, "status": "continuous",
        "classification": "division at end", "denominator": "end rating",
        "thresholds_percentage": [1, 5], "boundaries_inclusive": True,
        "start": selected.start_date.min(), "end": selected.end_date.max(),
        "outputs": ["division_percentages.csv", "division_percentages.md",
                    "division_percentage_exceptions.csv"]}
    (root / "division_percentages_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # A run ending before the fixed recent period can still produce its full-history table.
    eligible = frame[(frame.start_date >= RECENT_START) & (frame.window == 12)
                     & (frame.status == "continuous")
                     & frame.end_division.isin(("makuuchi", "juryo"))]
    if eligible.empty:
        recent_table = pd.DataFrame(columns=["division", "observations", "lowest_percentage",
            "highest_percentage", "within_1_count", "outside_1_count"])
        recent_rows = eligible.assign(percentage=pd.Series(dtype=float))
    else:
        recent_table, recent_rows = recent_sekitori_table(frame)
    recent_table.to_csv(root / "recent_sekitori_percentages.csv", index=False, float_format="%.12g")
    recent_rows.to_csv(root / "recent_sekitori_windows.csv", index=False, float_format="%.12g")
    recent_lines = ["# Recent Makuuchi and Juryo normalisation contributions", "",
        f"Window start: {RECENT_START} or later. Latest end in source: {selected.end_date.max()}.", "",
        "Continuous 12-basho windows only. Division is determined at the end endpoint;",
        "the wrestler need not have remained in that division throughout the window.",
        "Percentage = 100 × net signed normalisation contribution / end rating.",
        "Adjustments cancel within each window. Reinitialisation windows are excluded.",
        "The ±1% boundaries are inclusive. Counts use unrounded values.", "",
        "| Division | Observations | Lowest | Highest | Within ±1% | Outside ±1% |",
        "|---|---:|---:|---:|---:|---:|"]
    for _, row in recent_table.iterrows():
        recent_lines.append(f"| {row.division.title()} | {row.observations:,} | "
            f"{number(row.lowest_percentage, signed=True)} | "
            f"{number(row.highest_percentage, signed=True)} | "
            f"{row.within_1_count:,} | {row.outside_1_count:,} |")
    if recent_rows.empty:
        recent_lines += ["", "No eligible recent windows in this source run."]
    recent_lines += ["", "These are overlapping wrestler-windows, not distinct wrestlers or career totals.",
        "The January 2016 cutoff is an explicit exploratory choice. The accompanying full-history",
        "division table is retained. This report does not automatically judge practical significance.", ""]
    (root / "recent_sekitori_percentages.md").write_text("\n".join(recent_lines), encoding="utf-8")
    recent_manifest = {**manifest, "window_start_cutoff": RECENT_START,
        "divisions": ["makuuchi", "juryo"], "start": None if recent_rows.empty else recent_rows.start_date.min(),
        "end": None if recent_rows.empty else recent_rows.end_date.max(),
        "outputs": ["recent_sekitori_percentages.csv", "recent_sekitori_windows.csv",
                    "recent_sekitori_percentages.md"]}
    (root / "recent_sekitori_percentages_manifest.json").write_text(
        json.dumps(recent_manifest, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path,
                        default=Path("files/output/analysis/elo89_normalisation"))
    args = parser.parse_args()
    write_table(args.output_root)
    print(f"Division table: {(args.output_root / 'division_percentages.md').resolve()}")


if __name__ == "__main__":
    main()
