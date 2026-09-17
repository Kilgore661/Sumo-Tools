"""Describe historical chii ratings in a saved Elo89 run; never replay the model."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .__main__ import DEFAULT_ELO_ROOT, load_history
from .inputs import digest, load_inputs, safe_output


DEFAULT_OUTPUT_ROOT = Path("files/output/analysis/elo89_normalisation/chii_drift")
KEYS = ["level", "group", "endpoint"]
SETTINGS = {
    "period_origin": 1989, "period_years": 5,
    "rolling_basho": 12, "rolling_min_observations": 6,
    "slope_min_basho": 60, "slope_min_years": 10,
    "sensitivities": ["full", "exclude_first_12", "since_2000"],
    "weighting": "occupants equally within basho, represented basho equally over time",
    "quantiles": "linear interpolation of per-basho group means",
    "gaps": "break traces at every missing represented basho and calendar gaps over four months",
    "examples": "union of top five positive slopes, negative slopes and period ranges among eligible numbered groups",
    "selected_gaps": [["Y", "O"], ["O", "M1"], ["M1", "J1"], ["J1", "Ms1"]],
    "tolerance_points": 1e-6,
}


@dataclass
class DriftTables:
    """Auditable observations and the derived descriptive tables."""

    observations: pd.DataFrame
    basho: pd.DataFrame
    periods: pd.DataFrame
    trends: pd.DataFrame
    population: pd.DataFrame
    occupants: pd.DataFrame
    gaps: pd.DataFrame


def calendar_year(date: str) -> float:
    """Calendar time measured in years, preserving irregular basho spacing."""
    year, month = map(int, date.split("/"))
    return year + (month - 1) / 12


def period_start(date: str) -> int:
    return 1989 + ((int(date[:4]) - 1989) // 5) * 5


def make_observations(inputs, history) -> pd.DataFrame:
    """Attach both saved endpoints to that basho's domain chii and membership."""
    from src.sumo_core.BasicEnums import MSD

    states = {str(date): history[date] for date in history}
    rows, previous, seen = [], set(), set()
    for index, date in enumerate(inputs.dates):
        active = set(inputs.starts[date])
        for rid in sorted(active, key=int):
            meta = inputs.metadata[date][rid]
            chii = states[date].banzuke.rikchii.get(int(rid))
            if ("" if chii is None else str(chii)) != meta["chii"]:
                raise ValueError(f"Chii mismatch: {date}/{rid}")
            numbered, title, ordinal, number = "", "", -1, 0
            if chii is not None:
                abbreviation = chii.level.as_abbreviation()
                numbered = f"{abbreviation}{chii.number}"
                title = abbreviation if chii.level in (MSD.YOKOZUNA, MSD.OZEKI, MSD.SEKIWAKE, MSD.KOMUSUBI) else ""
                ordinal, number = chii.ordinal(), chii.number
            rows.append({
                "date": date, "basho_index": index, "rikishi_id": int(rid),
                "name": meta["name"], "literal": meta["chii"], "numbered": numbered,
                "title": title, "ordinal": ordinal, "rank_number": number,
                "division": meta["division"], "start": inputs.starts[date][rid],
                "end": inputs.ends[date][rid], "first_observed": rid not in seen,
                "returning": rid in seen and rid not in previous,
            })
        seen.update(active)
        previous = active
    frame = pd.DataFrame(rows)
    frame["duplicate_position"] = frame.literal.ne("") & frame.duplicated(["date", "literal"], keep=False)
    if frame.duplicated(["date", "rikishi_id"]).any():
        raise ValueError("Duplicate rikishi/date observation")
    if not np.isfinite(frame[["start", "end"]].to_numpy()).all():
        raise ValueError("Non-finite rating")
    return frame


def grouped_observations(observations: pd.DataFrame) -> pd.DataFrame:
    """Expand three explicit groupings without inventing unclassified chii."""
    groups = []
    for level in ("literal", "numbered", "title"):
        frame = observations.loc[observations[level].ne("")].copy()
        frame["level"], frame["group"] = level, frame[level]
        groups.append(frame)
    return pd.concat(groups, ignore_index=True).melt(
        id_vars=["date", "basho_index", "rikishi_id", "name", "level", "group", "ordinal"],
        value_vars=["start", "end"], var_name="endpoint", value_name="rating",
    )


def describe_periods(long: pd.DataFrame, basho: pd.DataFrame, dates: list[str]) -> pd.DataFrame:
    """Summarise distributions of basho means, including unsupported periods."""
    values = basho.assign(period_start=basho.date.map(period_start))
    grouped = values.groupby(KEYS + ["period_start"], sort=False)
    table = grouped.rating.agg(
        basho_count="count", mean="mean", median="median", minimum="min", maximum="max",
        q25=lambda x: x.quantile(.25), q75=lambda x: x.quantile(.75),
    )
    table["occupant_observations"] = grouped.occupant_count.sum()
    table["first_date"] = grouped.date.min()
    table["last_date"] = grouped.date.max()
    people = long.assign(period_start=long.date.map(period_start)).groupby(KEYS + ["period_start"])
    table["distinct_rikishi"] = people.rikishi_id.nunique()
    periods = list(range(period_start(dates[0]), period_start(dates[-1]) + 1, 5))
    all_keys = [(a, b, c, p) for a, b, c in basho[KEYS].drop_duplicates().itertuples(index=False, name=None) for p in periods]
    table = table.reindex(pd.MultiIndex.from_tuples(all_keys, names=KEYS + ["period_start"])).reset_index()
    for column in ("basho_count", "occupant_observations", "distinct_rikishi"):
        table[column] = table[column].fillna(0).astype(int)
    available = pd.Series([period_start(date) for date in dates]).value_counts()
    table["represented_basho_available"] = table.period_start.map(available).fillna(0).astype(int)
    table["period_end"] = table.period_start.map(lambda p: min(p + 4, int(dates[-1][:4])))
    table["partial_calendar_period"] = table.period_start.map(
        lambda p: dates[0] > f"{p}/01" or dates[-1] < f"{p+4}/11")
    return table


def trend_rows(basho: pd.DataFrame, dates: list[str]) -> pd.DataFrame:
    """Descriptive calendar slopes and period contrasts for each sensitivity."""
    rows = []
    for key, all_values in basho.groupby(KEYS, sort=False):
        for selection in SETTINGS["sensitivities"]:
            values = all_values
            if selection == "exclude_first_12":
                values = values[values.basho_index >= 12]
            elif selection == "since_2000":
                values = values[values.date >= "2000/01"]
            n = len(values)
            years = values.date.map(calendar_year).to_numpy()
            span = years[-1] - years[0] if n else 0.
            slope = float(np.polyfit(years - years[0], values.rating, 1)[0] * 10) if n >= 2 and span > 0 else np.nan
            means = values.groupby(values.date.map(period_start)).rating.mean()
            rows.append(dict(zip(KEYS, key)) | {
                "ordinal": int(all_values.ordinal.min()),
                "selection": selection, "basho_count": n, "span_years": span,
                "first_date": values.date.min() if n else "", "last_date": values.date.max() if n else "",
                "support_periods": ";".join(map(str, means.index)),
                "slope_points_per_decade": slope,
                "first_last_period_change": float(means.iloc[-1] - means.iloc[0]) if len(means) >= 2 else np.nan,
                "period_range": float(means.max() - means.min()) if len(means) >= 2 else np.nan,
                "eligible": n >= 60 and span >= 10,
            })
    return pd.DataFrame(rows)


def population_rows(observations: pd.DataFrame, target: float) -> pd.DataFrame:
    """Reconcile exhaustive division partitions to the fixed global mean."""
    rows = []
    for date, frame in observations.groupby("date", sort=True):
        for endpoint in ("start", "end"):
            mean = frame[endpoint].mean()
            partition = frame.groupby("division")[endpoint].agg(["count", "mean"])
            reconciled = (partition["count"] * partition["mean"]).sum() / len(frame)
            if abs(mean - target) > 1e-6 or abs(reconciled - mean) > 1e-6:
                raise ValueError(f"Population reconciliation failed: {date}/{endpoint}")
            for division, group in [("all", frame), *frame.groupby("division")]:
                values = group[endpoint]
                rows.append({"date": date, "endpoint": endpoint, "division": division,
                             "count": len(group), "mean": values.mean(),
                             "q05": values.quantile(.05), "q25": values.quantile(.25),
                             "median": values.median(), "q75": values.quantile(.75),
                             "q95": values.quantile(.95), "minimum": values.min(), "maximum": values.max(),
                             "spread_90": values.quantile(.95) - values.quantile(.05),
                             "rank_depth": group.rank_number.max(),
                             "mean_residual": mean - target if division == "all" else np.nan,
                             "partition_residual": reconciled - mean if division == "all" else np.nan})
    return pd.DataFrame(rows)


def build_tables(observations: pd.DataFrame, dates: list[str], target: float) -> DriftTables:
    """Derive equal-basho summaries, support-aware smoothing and contextual tables."""
    long = grouped_observations(observations)
    basho = long.groupby(KEYS + ["date", "basho_index"], sort=True).agg(
        rating=("rating", "mean"), occupant_count=("rikishi_id", "size"),
        distinct_rikishi=("rikishi_id", "nunique"), ordinal=("ordinal", "min"),
    ).reset_index()
    smoothed = []
    for _, group in basho.groupby(KEYS, sort=False):
        group = group.copy()
        grid = group.set_index("basho_index").rating.reindex(range(len(dates)))
        rolling = grid.rolling(12, min_periods=6)
        group["rolling_mean"] = rolling.mean().reindex(group.basho_index).to_numpy()
        group["rolling_count"] = grid.rolling(12, min_periods=1).count().reindex(group.basho_index).to_numpy().astype(int)
        smoothed.append(group)
    basho = pd.concat(smoothed, ignore_index=True)
    periods = describe_periods(long, basho, dates)
    trends = trend_rows(basho, dates)
    people = long[long.endpoint == "end"].copy()
    people["period"] = people.date.map(period_start).astype(str)
    full = people.assign(period="full")
    people = pd.concat([people, full], ignore_index=True)
    occupants = people.groupby(["level", "group", "period", "rikishi_id"]).agg(
        observations=("date", "size"), name=("name", "last"), first_date=("date", "min"), last_date=("date", "max")
    ).reset_index()
    occupants["share"] = occupants.observations / occupants.groupby(["level", "group", "period"]).observations.transform("sum")
    gaps = []
    for a, b in SETTINGS["selected_gaps"]:
        left = basho[(basho.level == ("title" if a in "YOSK" else "numbered")) & (basho.group == a)]
        right = basho[(basho.level == "numbered") & (basho.group == b)] if b not in "YOSK" else basho[(basho.level == "title") & (basho.group == b)]
        pair = left.merge(right, on=["date", "endpoint"], suffixes=("_a", "_b"))
        for row in pair.itertuples():
            gaps.append({"date": row.date, "endpoint": row.endpoint, "group_a": a, "group_b": b,
                         "gap": row.rating_a - row.rating_b, "count_a": row.occupant_count_a, "count_b": row.occupant_count_b})
    return DriftTables(observations, basho, periods, trends, population_rows(observations, target),
                       occupants, pd.DataFrame(gaps, columns=["date", "endpoint", "group_a", "group_b", "gap", "count_a", "count_b"]))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elo-root", type=Path, default=DEFAULT_ELO_ROOT)
    parser.add_argument("--history-zip", type=Path, help="Annotated ZIP; otherwise use the published live store.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv=None):
    """Validate saved inputs, publish the independent study, and verify provenance."""
    from .chii_drift_report import write_outputs

    args = build_parser().parse_args(argv)
    sources = [args.elo_root]
    if args.history_zip is not None:
        sources.append(args.history_zip.with_suffix(".zip"))
    safe_output(args.output_root, sources)
    print("Loading History and validating saved Elo89 artifacts...", flush=True)
    history, source = load_history(args)
    inputs = load_inputs(args.elo_root, history)
    prior_path = (args.elo_root / inputs.manifest["files"]["prior"]).resolve()
    if args.elo_root.resolve() not in prior_path.parents:
        raise ValueError("Prior path outside Elo89 run")
    inputs.paths["prior"] = prior_path
    inputs.hashes["prior"] = digest(prior_path)
    prior = pd.read_csv(prior_path)
    if prior.rank_pair.duplicated().any() or not np.isfinite(prior.rating).all():
        raise ValueError("Invalid saved prior")
    source["represented_history_sha256"] = inputs.history_digest
    print(f"Summarising {len(inputs.dates)} represented basho...", flush=True)
    observations = make_observations(inputs, history)
    tables = build_tables(observations, inputs.dates, float(inputs.manifest["target_mean"]))
    inputs.verify_unchanged()
    write_outputs(args.output_root, inputs, source, tables)
    inputs.verify_unchanged()
    if source["kind"] == "history_zip" and digest(Path(source["path"])) != source["sha256"]:
        raise ValueError("History ZIP changed during analysis")
    print(f"Outputs: {args.output_root.resolve()}", flush=True)


if __name__ == "__main__":
    main()
