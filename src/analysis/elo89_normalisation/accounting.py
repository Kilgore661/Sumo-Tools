"""Endpoint accounting; no alternative rating model is calculated here."""

from __future__ import annotations

import pandas as pd

WINDOWS = (1, 2, 3, 4, 5, 6, 12)
TOLERANCE = 1e-6


def reconstruct(inputs, windows=WINDOWS):
    dates = inputs.dates
    last, previous, steps = {}, set(), {}
    for date in dates:
        adj = inputs.adjustments[date]
        active = set(inputs.starts[date])
        for rid in active:
            start, end = inputs.starts[date][rid], inputs.ends[date][rid]
            bout = inputs.bouts.get((date, rid), 0.0)
            residual = end - start - bout - adj["end_adjustment"]
            if abs(residual) > TOLERANCE:
                raise ValueError(f"Basho accounting mismatch {date}/{rid}: {residual}")
            reset = 0.0
            returning = rid not in previous and rid in last
            if returning:
                reset = start - adj["start_adjustment"] - last[rid]
            elif rid in previous and abs(start - adj["start_adjustment"] - last[rid]) > TOLERANCE:
                raise ValueError(f"Start accounting mismatch {date}/{rid}")
            steps[date, rid] = (bout, adj["start_adjustment"], adj["end_adjustment"], reset, int(returning))
            last[rid] = end
        previous = active
    records, exclusions = [], []
    for n in windows:
        if n < 1:
            raise ValueError("Window must be positive")
        for end_index in range(n, len(dates)):
            a, b = dates[end_index - n], dates[end_index]
            start_ids, end_ids = set(inputs.ends[a]), set(inputs.ends[b])
            exclusions.append({"window": n, "start_date": a, "end_date": b,
                               "missing_start": len(end_ids-start_ids), "missing_end": len(start_ids-end_ids)})
            for rid in sorted(start_ids & end_ids, key=int):
                period = dates[end_index-n+1:end_index+1]
                present = [t for t in period if (t, rid) in steps]
                values = [sum(steps[t, rid][k] for t in present) for k in range(5)]
                bout, pre, post, reset, resets = values
                change = inputs.ends[b][rid] - inputs.ends[a][rid]
                residual = change - bout - pre - post - reset
                if abs(residual) > TOLERANCE:
                    raise ValueError(f"Window accounting mismatch {a}/{b}/{rid}: {residual}")
                meta = inputs.metadata[b][rid]
                records.append({
                    "rikishi_id": int(rid), "name": meta["name"], "window": n,
                    "start_date": a, "end_date": b, "start_chii": inputs.metadata[a][rid]["chii"],
                    "end_chii": meta["chii"], "start_division": inputs.metadata[a][rid]["division"],
                    "end_division": meta["division"],
                    "makuuchi_throughout": all(rid in inputs.metadata[t] and
                        inputs.metadata[t][rid]["division"] == "makuuchi" for t in [a, *period]),
                    "status": "reset" if resets else "continuous", "reset_count": int(resets),
                    "represented_basho": len(present),
                    "start_rating": inputs.ends[a][rid], "end_rating": inputs.ends[b][rid],
                    "bout_count": sum(inputs.counts.get((t, rid), 0) for t in present),
                    "bout": bout, "pre": pre, "post": post, "normalisation": pre+post,
                    "reset": reset, "change": change, "residual": residual,
                })
    if not records:
        raise ValueError("No comparable windows in the supplied run")
    return pd.DataFrame.from_records(records), pd.DataFrame(exclusions)


def reconcile_site(frame, directory):
    """Compare latest rows to rounded site CSVs, including both endpoint ratings."""
    latest = frame[frame.end_date == frame.end_date.max()]
    checked = 0
    for window, rows in latest.groupby("window"):
        path = directory / f"{latest.end_date.max().replace('/', '-')} {window}-change.csv"
        published = pd.read_csv(path).set_index("rikishi_id")
        actual = rows.set_index("rikishi_id")
        if set(published.index) != set(actual.index):
            raise ValueError(f"Site membership differs: {path}")
        for column, site_column in (("change", "delta"), ("start_rating", "rating_at_start"),
                                    ("end_rating", "rating_at_end")):
            differences = actual[column] - published.loc[actual.index, site_column]
            if differences.abs().max() > 0.001:
                raise ValueError(f"Site {column} differs: {path}")
        checked += len(rows)
    return checked
