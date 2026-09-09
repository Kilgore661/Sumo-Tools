"""Summarise existing diagnostic outputs using signed contributions only."""

import argparse
import json
from pathlib import Path

import pandas as pd

from .inputs import digest


def summarise(root: Path):
    paths = {name: root / f"{name}.csv" for name in ("basho_adjustments", "window_changes")}
    hashes = {name: digest(path) for name, path in paths.items()}
    adjustments = pd.read_csv(paths["basho_adjustments"])
    windows = pd.read_csv(paths["window_changes"])
    summaries, years, seasons, cumulative = [], [], [], []
    for period, cutoff in (("full_history", "0000/00"), ("since_2016", "2016/01")):
        a = adjustments[adjustments.date >= cutoff].copy()
        if a.empty:
            continue
        a["period"] = period
        for key in ("start_adjustment", "end_adjustment", "combined"):
            a[f"cumulative_{key}"] = a[key].cumsum()
            s = a[key]
            summaries.append({"period": period, "population": "common_adjustment",
                "window": 1, "component": key, "count": len(s), "mean": s.mean(),
                "median": s.median(), "p5": s.quantile(.05), "p95": s.quantile(.95),
                "min": s.min(), "max": s.max(), "signed_sum": s.sum()})
        cumulative.append(a)
        for year, group in a.groupby(a.date.str[:4]):
            years.append({"period": period, "year": year, "basho_count": len(group),
                "pre": group.start_adjustment.sum(), "post": group.end_adjustment.sum(),
                "combined": group.combined.sum()})
        for month, group in a.groupby(a.date.str[5:]):
            seasons.append({"period": period, "month": month, "basho_count": len(group),
                            "mean": group.combined.mean(), "median": group.combined.median()})
        selected = windows[(windows.start_date >= cutoff) & (windows.status == "continuous")]
        for population, group in (("all", selected),
                                  ("makuuchi", selected[selected.end_division == "makuuchi"]),
                                  ("makuuchi_throughout", selected[selected.makuuchi_throughout])):
            for n, rows in group.groupby("window"):
                for key in ("bout", "pre", "post", "normalisation", "change"):
                    s = rows[key]
                    summaries.append({"period": period, "population": population,
                        "window": int(n), "component": key, "count": len(s),
                        "mean": s.mean(), "median": s.median(), "p5": s.quantile(.05),
                        "p95": s.quantile(.95), "min": s.min(), "max": s.max(),
                        # Overlapping windows must not be added as a cumulative history.
                        "signed_sum": None})
    outputs = {"signed_summaries": pd.DataFrame(summaries), "signed_years": pd.DataFrame(years),
               "signed_seasons": pd.DataFrame(seasons), "signed_cumulative": pd.concat(cumulative)}
    for name, frame in outputs.items():
        frame.to_csv(root / f"{name}.csv", index=False, float_format="%.12g")
    for name, path in paths.items():
        if digest(path) != hashes[name]:
            raise ValueError(f"Input changed: {path}")
    manifest = {"source_hashes": hashes, "script_sha256": digest(Path(__file__)),
                "recent_cutoff": "2016/01", "recent_window_rule": "start_date >= cutoff",
                "common_weighting": "one observation per basho",
                "window_weighting": "one observation per continuous wrestler-window",
                "outputs": [f"{name}.csv" for name in outputs]}
    (root / "signed_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path,
                        default=Path("files/output/analysis/elo89_normalisation"))
    args = parser.parse_args()
    summarise(args.output_root)
    print(f"Signed summaries: {args.output_root.resolve()}")


if __name__ == "__main__":
    main()
