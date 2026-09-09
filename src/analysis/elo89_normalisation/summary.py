"""Descriptive summaries, with explicit populations and no materiality verdict."""

import numpy as np
import pandas as pd

PERCENTILES = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)
COMPONENTS = ("bout", "pre", "post", "normalisation", "reset", "change", "residual")


def describe(values):
    values = np.asarray(values, dtype=float)
    if not len(values):
        return {"count": 0}
    absolute = np.abs(values)
    result = {"count": len(values), "mean": float(values.mean()),
              "mean_absolute": float(absolute.mean()), "sd": float(values.std()),
              "positive": int((values > 0).sum()), "negative": int((values < 0).sum()),
              "zero": int((values == 0).sum())}
    for prefix, data in (("p", values), ("abs_p", absolute)):
        result.update({f"{prefix}{p}": float(np.percentile(data, p)) for p in PERCENTILES})
    return result


def populations(frame):
    yield "all", frame
    yield "makuuchi", frame[frame.end_division == "makuuchi"]
    yield "makuuchi_throughout", frame[frame.makuuchi_throughout]


def build_summaries(frame):
    rows, comparisons, exceptions = [], [], []
    for population, subset in populations(frame):
        for window, group in subset.groupby("window", sort=True):
            continuous = group[group.status == "continuous"]
            for endpoint, sample in [("all", group), *list(group.groupby("end_date", sort=True))]:
                for status, selected in sample.groupby("status", sort=True):
                    tags = {"population": population, "window": int(window),
                            "endpoint": endpoint, "status": status}
                    for component in COMPONENTS:
                        rows.append({**tags, "component": component, **describe(selected[component])})
                    # Ratios only have the intended interpretation for continuous ratings.
                    if status == "continuous":
                        normal, bout = selected.normalisation.abs(), selected.bout.abs()
                        mean_den, median_den = float(bout.mean()), float(bout.median())
                        comparisons.append({**tags, "count": len(selected),
                            "mean_abs_normalisation": float(normal.mean()), "mean_abs_bout": mean_den,
                            "mean_ratio": float(normal.mean())/mean_den if mean_den else None,
                            "median_abs_normalisation": float(normal.median()), "median_abs_bout": median_den,
                            "median_ratio": float(normal.median())/median_den if median_den else None,
                            "sign_reversals": int(((selected.bout * selected.change) < 0).sum()),
                            "zero_bout": int((selected.bout == 0).sum()),
                            "zero_change": int((selected.change == 0).sum())})
            if len(continuous):
                threshold = continuous.normalisation.abs().nlargest(20).min()
                largest = continuous[continuous.normalisation.abs() >= threshold]
                exceptions.append(largest.assign(population=population, reason="largest_normalisation"))
                exceptions.append(continuous.loc[continuous.residual.abs().nlargest(20).index].assign(
                    population=population, reason="largest_residual"))
                exceptions.append(continuous[continuous.bout * continuous.change < 0].assign(
                    population=population, reason="sign_reversal"))
            exceptions.append(group[group.status == "reset"].assign(population=population, reason="reset"))
    return pd.DataFrame(rows), pd.DataFrame(comparisons), pd.concat(exceptions, ignore_index=True)
