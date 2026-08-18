"""Test whether independently solved M/J and J/Ms priors agree in Juryo."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.analysis.boundary_positions import boundary_positions
from src.analysis.equelo.api import annotation_free_chii
from src.analysis.equelo.expt1.Oracle import make_oracle
from src.analysis.equelo.fixed_boundary.model import (
    PriorKey,
    build_jms_prior_world,
    build_prior_world,
)
from src.analysis.equelo.fixed_boundary.output import _write_plotly_html, _write_rows
from src.analysis.equelo.fixed_supported.build import oracle_collapse_mode
from src.analysis.equelo.fixed_supported.policy import collapse_chii
from src.infra.persistence.annotated_serialiser import load_history_with_annotations
from src.sumo_core.History import History


OUTPUT_ROOT = Path("files/output/Equelo/boundary_reconciliation")


@dataclass(frozen=True)
class ReconciliationOutputs:
    run_directory: Path
    summary_json: Path
    observations_csv: Path
    by_chii_csv: Path
    by_size_position_csv: Path
    comparison_chart_html: Path
    residual_chart_html: Path


def reconcile_boundary_maps(
    *,
    raw_history: History,
    mj_map_path: Path,
    jms_map_path: Path,
    output_root: Path = OUTPUT_ROOT,
    start_year: int = 1989,
    end_year: int | None = None,
) -> ReconciliationOutputs:
    scoped = _slice_history(raw_history, start_year=start_year, end_year=end_year)
    actual_end_year = max(date.year for date in scoped)
    history = make_oracle(scoped, collapse_mode=oracle_collapse_mode()).history
    mj_world = build_prior_world(history)
    jms_world = build_jms_prior_world(history)
    mj_ratings = _load_prior_ratings(mj_map_path)
    jms_ratings = _load_prior_ratings(jms_map_path)

    raw_rows = _juryo_observations(
        history=history,
        mj_world=mj_world,
        jms_world=jms_world,
        mj_ratings=mj_ratings,
        jms_ratings=jms_ratings,
    )
    shift = sum(row["mj_rating"] - row["jms_rating"] for row in raw_rows) / len(raw_rows)
    observations = []
    for row in raw_rows:
        aligned = row["jms_rating"] + shift
        observations.append({
            **row,
            "jms_aligned_rating": aligned,
            "residual_mj_minus_jms": row["mj_rating"] - aligned,
        })

    metrics = _alignment_metrics(observations, shift=shift)
    by_chii = _group_rows(observations, keys=("chii", "chii_ordinal"))
    by_chii.sort(key=lambda row: row["chii_ordinal"])
    by_size = _group_rows(
        observations,
        keys=("juryo_size", "from_top", "from_bottom"),
    )
    by_size.sort(key=lambda row: (row["juryo_size"], row["from_top"]))

    run_directory = _create_run_directory(output_root)
    observations_csv = _write_rows(
        run_directory / "juryo_alignment_observations.csv", observations
    )
    by_chii_csv = _write_rows(
        run_directory / "juryo_alignment_by_chii.csv", by_chii
    )
    by_size_csv = _write_rows(
        run_directory / "juryo_alignment_by_size_position.csv", by_size
    )
    comparison_chart = _write_comparison_chart(
        run_directory / "juryo_map_comparison.html", by_chii
    )
    residual_chart = _write_residual_chart(
        run_directory / "juryo_alignment_residuals.html", by_chii
    )
    summary_path = run_directory / "summary.json"
    summary_path.write_text(json.dumps({
        "kind": "boundary_map_reconciliation",
        "generated_at": datetime.now().astimezone().isoformat(),
        "history_scope": {"start_year": start_year, "end_year": actual_end_year},
        "alignment_contract": {
            "reference": "M/J contextual map",
            "aligned": "J/Ms contextual map",
            "permitted_transformation": "one observation-weighted additive shift",
            "rank_specific_adjustments": False,
        },
        "source_maps": {"mj": str(mj_map_path), "jms": str(jms_map_path)},
        "metrics": metrics,
        "outputs": {
            "observations_csv": str(observations_csv),
            "by_chii_csv": str(by_chii_csv),
            "by_size_position_csv": str(by_size_csv),
            "comparison_chart_html": str(comparison_chart),
            "residual_chart_html": str(residual_chart),
        },
    }, indent=2), encoding="utf-8")
    return ReconciliationOutputs(
        run_directory=run_directory,
        summary_json=summary_path,
        observations_csv=observations_csv,
        by_chii_csv=by_chii_csv,
        by_size_position_csv=by_size_csv,
        comparison_chart_html=comparison_chart,
        residual_chart_html=residual_chart,
    )


def _load_prior_ratings(path: Path) -> dict[PriorKey, float]:
    with path.open("r", newline="", encoding="utf-8") as stream:
        return {
            PriorKey(row["key_kind"], int(row["key_value"])): float(row["initial_rating"])
            for row in csv.DictReader(stream)
        }


def _juryo_observations(*, history, mj_world, jms_world, mj_ratings, jms_ratings):
    rows = []
    for date in sorted(history):
        banzuke = history[date].banzuke
        positions = boundary_positions(banzuke.rikchii)
        for rikid, chii in banzuke.rikchii.items():
            division, from_top, from_bottom = positions[rikid]
            if division != "J":
                continue
            clean = collapse_chii(annotation_free_chii(chii))
            mj_key = mj_world.key_by_date_rikishi[date][rikid]
            jms_key = jms_world.key_by_date_rikishi[date][rikid]
            size = from_top + from_bottom - 1
            rows.append({
                "date": str(date),
                "rikid": int(rikid),
                "chii": str(clean),
                "chii_ordinal": clean.ordinal(),
                "juryo_size": size,
                "from_top": from_top,
                "from_bottom": from_bottom,
                "relative_position": (from_top - 1) / (size - 1),
                "mj_key_value": mj_key.value,
                "jms_key_value": jms_key.value,
                "mj_rating": mj_ratings[mj_key],
                "jms_rating": jms_ratings[jms_key],
            })
    if not rows:
        raise ValueError("Scoped history contains no Juryo observations")
    return rows


def _alignment_metrics(rows, *, shift: float) -> dict[str, float | int]:
    residuals = [row["residual_mj_minus_jms"] for row in rows]
    positions = [row["relative_position"] for row in rows]
    mj = [row["mj_rating"] for row in rows]
    jms = [row["jms_aligned_rating"] for row in rows]
    slope = _slope(positions, residuals)
    return {
        "observation_count": len(rows),
        "additive_shift_to_jms": shift,
        "mean_residual": sum(residuals) / len(residuals),
        "mean_absolute_residual": sum(abs(value) for value in residuals) / len(residuals),
        "root_mean_square_residual": math.sqrt(sum(value * value for value in residuals) / len(residuals)),
        "maximum_absolute_residual": max(abs(value) for value in residuals),
        "rating_correlation": _correlation(mj, jms),
        "residual_relative_position_correlation": _correlation(positions, residuals),
        "residual_slope_top_to_bottom": slope,
        "top_half_mean_residual": _conditional_mean(rows, upper=False),
        "bottom_half_mean_residual": _conditional_mean(rows, upper=True),
    }


def _conditional_mean(rows, *, upper: bool) -> float:
    selected = [
        row["residual_mj_minus_jms"]
        for row in rows
        if (row["relative_position"] >= 0.5) == upper
    ]
    return sum(selected) / len(selected)


def _group_rows(rows, *, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    output = []
    for values, members in groups.items():
        residuals = [row["residual_mj_minus_jms"] for row in members]
        output.append({
            **dict(zip(keys, values)),
            "appearance_count": len(members),
            "mj_rating_mean": sum(row["mj_rating"] for row in members) / len(members),
            "jms_aligned_rating_mean": sum(row["jms_aligned_rating"] for row in members) / len(members),
            "residual_mean": sum(residuals) / len(residuals),
            "residual_min": min(residuals),
            "residual_max": max(residuals),
        })
    return output


def _correlation(xs, ys) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_ss = sum((x - x_mean) ** 2 for x in xs)
    y_ss = sum((y - y_mean) ** 2 for y in ys)
    return numerator / math.sqrt(x_ss * y_ss) if x_ss and y_ss else 0.0


def _slope(xs, ys) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    return (
        sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator
        if denominator
        else 0.0
    )


def _write_comparison_chart(path: Path, rows) -> Path:
    labels = [row["chii"] for row in rows]
    traces = [
        {
            "type": "scatter", "mode": "lines+markers", "name": "M/J map",
            "x": labels, "y": [row["mj_rating_mean"] for row in rows],
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<extra></extra>",
        },
        {
            "type": "scatter", "mode": "lines+markers", "name": "Aligned J/Ms map",
            "x": labels, "y": [row["jms_aligned_rating_mean"] for row in rows],
            "hovertemplate": "%{x}<br>rating=%{y:.2f}<extra></extra>",
        },
    ]
    layout = {
        "title": {"text": "Independent boundary maps over their Juryo overlap"},
        "xaxis": {"title": {"text": "Literal Juryo chii"}, "type": "category"},
        "yaxis": {"title": {"text": "Initial rating"}},
        "hovermode": "x unified",
        "legend": {"orientation": "h", "y": -0.20},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 110},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _write_residual_chart(path: Path, rows) -> Path:
    labels = [row["chii"] for row in rows]
    traces = [{
        "type": "scatter", "mode": "lines+markers", "name": "M/J minus aligned J/Ms",
        "x": labels, "y": [row["residual_mean"] for row in rows],
        "customdata": [row["appearance_count"] for row in rows],
        "hovertemplate": "%{x}<br>residual=%{y:.2f}<br>n=%{customdata}<extra></extra>",
    }]
    layout = {
        "title": {"text": "Residual disagreement after one common shift"},
        "xaxis": {"title": {"text": "Literal Juryo chii"}, "type": "category"},
        "yaxis": {"title": {"text": "Rating points"}, "zeroline": True},
        "margin": {"l": 70, "r": 25, "t": 70, "b": 90},
    }
    return _write_plotly_html(path, traces=traces, layout=layout)


def _slice_history(history: History, *, start_year: int, end_year: int | None) -> History:
    scoped = History()
    for date in sorted(history):
        if date.year >= start_year and (end_year is None or date.year <= end_year):
            scoped[date] = history[date]
    if not scoped:
        raise ValueError("Selected reconciliation history scope is empty")
    return scoped


def _create_run_directory(root: Path) -> Path:
    path = root / datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    path.mkdir(parents=True, exist_ok=False)
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-zip", type=Path, required=True)
    parser.add_argument("--mj-map", type=Path, required=True)
    parser.add_argument("--jms-map", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--start-year", type=int, default=1989)
    parser.add_argument("--end-year", type=int)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history = load_history_with_annotations(str(args.history_zip.with_suffix("")))
    outputs = reconcile_boundary_maps(
        raw_history=history,
        mj_map_path=args.mj_map,
        jms_map_path=args.jms_map,
        output_root=args.output_root,
        start_year=args.start_year,
        end_year=args.end_year,
    )
    print(f"Run directory: {outputs.run_directory}")
    print(f"Summary: {outputs.summary_json}")
    print(f"Comparison chart: {outputs.comparison_chart_html}")
    print(f"Residual chart: {outputs.residual_chart_html}")


if __name__ == "__main__":
    main()
