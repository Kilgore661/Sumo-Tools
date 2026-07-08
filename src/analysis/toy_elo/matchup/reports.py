from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .collect import BoundaryKey, MatchupTallies
from .config import ADJACENT_BOUNDARIES
from .grouping import GroupKey, GroupingName, division_number


@dataclass(frozen=True)
class BridgeReachRow:
    upper_division: str
    lower_division: str
    highest_ranked_upper_group: str
    highest_ranked_upper_count: int
    lowest_ranked_lower_group: str
    lowest_ranked_lower_count: int


@dataclass(frozen=True)
class BridgeDistributionRow:
    upper_division: str
    lower_division: str
    focal_division: str
    opponent_division: str
    focal_group: str
    focal_rank_number: int
    scheduled_bout_count: int
    interdivision_bout_count: int
    probability: float
    ci95_low: float
    ci95_high: float
    ci95_width: float
    ci95_half_width: float
    ci95_width_over_probability: float
    ci95_half_width_over_probability: float


@dataclass(frozen=True)
class BoundaryBridgeDistributionRow:
    upper_division: str
    lower_division: str
    focal_division: str
    opponent_division: str
    boundary_anchor: str
    boundary_distance: int
    scheduled_bout_count: int
    interdivision_bout_count: int
    probability: float
    ci95_low: float
    ci95_high: float
    ci95_width: float
    ci95_half_width: float
    ci95_width_over_probability: float
    ci95_half_width_over_probability: float
    sample_groups: str


def write_day_matrices(
    *,
    output_root: Path,
    period: str,
    grouping: GroupingName,
    tallies: MatchupTallies,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    groups = sorted(tallies.groups, key=lambda group: group.sort_key)
    group_ids = {group: index for index, group in enumerate(groups)}
    prefix = f"{period}_{grouping.value}"
    counts_dir = output_root / "counts"
    probabilities_dir = output_root / "probabilities"

    for day in range(1, 16):
        write_counts_matrix(
            counts_dir / f"{prefix}_Day_{day:02d}_counts.csv",
            day=day,
            groups=groups,
            group_ids=group_ids,
            tallies=tallies,
        )
        write_probability_matrix(
            probabilities_dir / f"{prefix}_Day_{day:02d}_probabilities.csv",
            day=day,
            groups=groups,
            group_ids=group_ids,
            tallies=tallies,
        )


def compute_bridge_reach(tallies: MatchupTallies) -> list[BridgeReachRow]:
    rows = []

    for upper, lower in ADJACENT_BOUNDARIES:
        upper_counts: dict[GroupKey, int] = defaultdict(int)
        lower_counts: dict[GroupKey, int] = defaultdict(int)

        for (_day, focal, opponent), count in tallies.counts.items():
            if focal.level == upper and opponent.level == lower:
                upper_counts[focal] += count
            elif focal.level == lower and opponent.level == upper:
                lower_counts[focal] += count

        highest_upper = min(
            upper_counts,
            key=lambda group: division_number(group, upper),
            default=None,
        )
        lowest_lower = max(
            lower_counts,
            key=lambda group: division_number(group, lower),
            default=None,
        )

        rows.append(
            BridgeReachRow(
                upper_division=upper,
                lower_division=lower,
                highest_ranked_upper_group=(
                    highest_upper.label if highest_upper is not None else ""
                ),
                highest_ranked_upper_count=(
                    upper_counts[highest_upper] if highest_upper is not None else 0
                ),
                lowest_ranked_lower_group=(
                    lowest_lower.label if lowest_lower is not None else ""
                ),
                lowest_ranked_lower_count=(
                    lower_counts[lowest_lower] if lowest_lower is not None else 0
                ),
            )
        )

    return rows


def write_bridge_reach(
    *,
    output_root: Path,
    period: str,
    grouping: GroupingName,
    tallies: MatchupTallies,
) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / f"{period}_{grouping.value}_bridge_reach.csv"
    rows = compute_bridge_reach(tallies)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "upper_division",
                "lower_division",
                "highest_ranked_upper_group",
                "highest_ranked_upper_count",
                "lowest_ranked_lower_group",
                "lowest_ranked_lower_count",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "upper_division": row.upper_division,
                    "lower_division": row.lower_division,
                    "highest_ranked_upper_group": row.highest_ranked_upper_group,
                    "highest_ranked_upper_count": row.highest_ranked_upper_count,
                    "lowest_ranked_lower_group": row.lowest_ranked_lower_group,
                    "lowest_ranked_lower_count": row.lowest_ranked_lower_count,
                }
            )

    return path


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if trials == 0:
        return 0.0, 0.0

    phat = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    centre = phat + z2 / (2 * trials)
    margin = z * ((phat * (1 - phat) + z2 / (4 * trials)) / trials) ** 0.5
    return (centre - margin) / denominator, (centre + margin) / denominator


def compute_bridge_distribution(tallies: MatchupTallies) -> list[BridgeDistributionRow]:
    rows = []
    groups = sorted(tallies.groups, key=lambda group: group.sort_key)

    for upper, lower in ADJACENT_BOUNDARIES:
        for focal_division, opponent_division in ((upper, lower), (lower, upper)):
            focal_groups = [
                group
                for group in groups
                if group.level == focal_division and group.number is not None
            ]
            for focal in focal_groups:
                scheduled_count = sum(
                    total
                    for (day, group), total in tallies.row_totals.items()
                    if group == focal
                )
                interdivision_count = sum(
                    count
                    for (_day, group, opponent), count in tallies.counts.items()
                    if group == focal and opponent.level == opponent_division
                )
                if scheduled_count == 0 or interdivision_count == 0:
                    continue

                probability = interdivision_count / scheduled_count
                ci_low, ci_high = wilson_interval(
                    interdivision_count,
                    scheduled_count,
                )
                ci_width = ci_high - ci_low
                ci_half_width = ci_width / 2
                ci_width_over_probability = (
                    ci_width / probability if probability else 0.0
                )
                ci_half_width_over_probability = (
                    ci_half_width / probability if probability else 0.0
                )
                rows.append(
                    BridgeDistributionRow(
                        upper_division=upper,
                        lower_division=lower,
                        focal_division=focal_division,
                        opponent_division=opponent_division,
                        focal_group=focal.label,
                        focal_rank_number=focal.number,
                        scheduled_bout_count=scheduled_count,
                        interdivision_bout_count=interdivision_count,
                        probability=probability,
                        ci95_low=ci_low,
                        ci95_high=ci_high,
                        ci95_width=ci_width,
                        ci95_half_width=ci_half_width,
                        ci95_width_over_probability=ci_width_over_probability,
                        ci95_half_width_over_probability=(
                            ci_half_width_over_probability
                        ),
                    )
                )

    return rows


def write_bridge_distribution(
    *,
    output_root: Path,
    period: str,
    grouping: GroupingName,
    tallies: MatchupTallies,
) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / f"{period}_{grouping.value}_bridge_distribution.csv"
    rows = compute_bridge_distribution(tallies)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "upper_division",
                "lower_division",
                "focal_division",
                "opponent_division",
                "focal_group",
                "focal_rank_number",
                "scheduled_bout_count",
                "interdivision_bout_count",
                "probability",
                "ci95_low",
                "ci95_high",
                "ci95_width",
                "ci95_half_width",
                "ci95_width_over_probability",
                "ci95_half_width_over_probability",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "upper_division": row.upper_division,
                    "lower_division": row.lower_division,
                    "focal_division": row.focal_division,
                    "opponent_division": row.opponent_division,
                    "focal_group": row.focal_group,
                    "focal_rank_number": row.focal_rank_number,
                    "scheduled_bout_count": row.scheduled_bout_count,
                    "interdivision_bout_count": row.interdivision_bout_count,
                    "probability": f"{row.probability:.8f}",
                    "ci95_low": f"{row.ci95_low:.8f}",
                    "ci95_high": f"{row.ci95_high:.8f}",
                    "ci95_width": f"{row.ci95_width:.8f}",
                    "ci95_half_width": f"{row.ci95_half_width:.8f}",
                    "ci95_width_over_probability": (
                        f"{row.ci95_width_over_probability:.8f}"
                    ),
                    "ci95_half_width_over_probability": (
                        f"{row.ci95_half_width_over_probability:.8f}"
                    ),
                }
            )

    return path


def compute_boundary_bridge_distribution(
    tallies: MatchupTallies,
) -> list[BoundaryBridgeDistributionRow]:
    rows = []
    for key in sorted(
        tallies.boundary_row_totals,
        key=lambda item: (
            item.upper_division,
            item.lower_division,
            item.focal_division != item.upper_division,
            item.boundary_distance,
        ),
    ):
        scheduled_count = tallies.boundary_row_totals[key]
        interdivision_count = tallies.boundary_counts.get(key, 0)
        if scheduled_count == 0 or interdivision_count == 0:
            continue

        probability = interdivision_count / scheduled_count
        ci_low, ci_high = wilson_interval(interdivision_count, scheduled_count)
        ci_width = ci_high - ci_low
        ci_half_width = ci_width / 2
        ci_width_over_probability = ci_width / probability if probability else 0.0
        ci_half_width_over_probability = (
            ci_half_width / probability if probability else 0.0
        )
        rows.append(
            BoundaryBridgeDistributionRow(
                upper_division=key.upper_division,
                lower_division=key.lower_division,
                focal_division=key.focal_division,
                opponent_division=key.opponent_division,
                boundary_anchor=key.boundary_anchor,
                boundary_distance=key.boundary_distance,
                scheduled_bout_count=scheduled_count,
                interdivision_bout_count=interdivision_count,
                probability=probability,
                ci95_low=ci_low,
                ci95_high=ci_high,
                ci95_width=ci_width,
                ci95_half_width=ci_half_width,
                ci95_width_over_probability=ci_width_over_probability,
                ci95_half_width_over_probability=ci_half_width_over_probability,
                sample_groups=sample_groups(tallies.boundary_group_counts.get(key, {})),
            )
        )

    return rows


def sample_groups(group_counts: dict[str, int], *, limit: int = 12) -> str:
    ordered = sorted(group_counts.items(), key=lambda item: (-item[1], item[0]))
    labels = [label for label, _count in ordered[:limit]]
    if len(ordered) > limit:
        labels.append("...")
    return "|".join(labels)


def write_boundary_bridge_distribution(
    *,
    output_root: Path,
    period: str,
    grouping: GroupingName,
    tallies: MatchupTallies,
) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / f"{period}_{grouping.value}_boundary_bridge_distribution.csv"
    rows = compute_boundary_bridge_distribution(tallies)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "upper_division",
                "lower_division",
                "focal_division",
                "opponent_division",
                "boundary_anchor",
                "boundary_distance",
                "scheduled_bout_count",
                "interdivision_bout_count",
                "probability",
                "ci95_low",
                "ci95_high",
                "ci95_width",
                "ci95_half_width",
                "ci95_width_over_probability",
                "ci95_half_width_over_probability",
                "sample_groups",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "upper_division": row.upper_division,
                    "lower_division": row.lower_division,
                    "focal_division": row.focal_division,
                    "opponent_division": row.opponent_division,
                    "boundary_anchor": row.boundary_anchor,
                    "boundary_distance": row.boundary_distance,
                    "scheduled_bout_count": row.scheduled_bout_count,
                    "interdivision_bout_count": row.interdivision_bout_count,
                    "probability": f"{row.probability:.8f}",
                    "ci95_low": f"{row.ci95_low:.8f}",
                    "ci95_high": f"{row.ci95_high:.8f}",
                    "ci95_width": f"{row.ci95_width:.8f}",
                    "ci95_half_width": f"{row.ci95_half_width:.8f}",
                    "ci95_width_over_probability": (
                        f"{row.ci95_width_over_probability:.8f}"
                    ),
                    "ci95_half_width_over_probability": (
                        f"{row.ci95_half_width_over_probability:.8f}"
                    ),
                    "sample_groups": row.sample_groups,
                }
            )

    return path


def write_bridge_plots(
    *,
    output_root: Path,
    period: str,
    grouping: GroupingName,
    tallies: MatchupTallies,
) -> list[Path]:
    output_dir = output_root / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    distribution_rows = compute_bridge_distribution(tallies)
    paths = []

    for upper, lower in ADJACENT_BOUNDARIES:
        rows = [
            row
            for row in distribution_rows
            if row.upper_division == upper and row.lower_division == lower
        ]
        if not rows:
            continue

        rows = sorted(
            rows,
            key=lambda row: GroupKey(
                level=row.focal_division,
                number=row.focal_rank_number,
                side=None,
                annotation=None,
            ).sort_key,
        )
        path = output_dir / f"{period}_{grouping.value}_{upper}_{lower}_bridge.html"
        path.write_text(
            build_bridge_plot_html(
                period=period,
                grouping=grouping,
                upper=upper,
                lower=lower,
                rows=rows,
            ),
            encoding="utf-8",
        )
        paths.append(path)

    return paths


def write_boundary_bridge_plots(
    *,
    output_root: Path,
    period: str,
    grouping: GroupingName,
    tallies: MatchupTallies,
) -> list[Path]:
    output_dir = output_root / "boundary_plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    distribution_rows = compute_boundary_bridge_distribution(tallies)
    paths = []

    for upper, lower in ADJACENT_BOUNDARIES:
        rows = [
            row
            for row in distribution_rows
            if row.upper_division == upper and row.lower_division == lower
        ]
        if not rows:
            continue

        rows = sorted(
            rows,
            key=lambda row: (
                row.focal_division != upper,
                (
                    -row.boundary_distance
                    if row.focal_division == upper
                    else row.boundary_distance
                ),
            ),
        )
        path = output_dir / f"{period}_{grouping.value}_{upper}_{lower}_boundary_bridge.html"
        path.write_text(
            build_boundary_bridge_plot_html(
                period=period,
                grouping=grouping,
                upper=upper,
                lower=lower,
                rows=rows,
            ),
            encoding="utf-8",
        )
        paths.append(path)

    return paths


def build_boundary_bridge_plot_html(
    *,
    period: str,
    grouping: GroupingName,
    upper: str,
    lower: str,
    rows: list[BoundaryBridgeDistributionRow],
) -> str:
    x_values = list(range(len(rows)))
    labels = [
        f"{row.focal_division} {row.boundary_anchor} {row.boundary_distance}"
        for row in rows
    ]
    probabilities = [row.probability for row in rows]
    ci_low = [row.ci95_low for row in rows]
    ci_high = [row.ci95_high for row in rows]
    relative_ci = [row.ci95_half_width_over_probability for row in rows]
    customdata = [
        [
            row.scheduled_bout_count,
            row.interdivision_bout_count,
            row.ci95_low,
            row.ci95_high,
            row.ci95_half_width_over_probability,
            row.opponent_division,
            row.sample_groups,
        ]
        for row in rows
    ]

    data = [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": "probability",
            "x": x_values,
            "y": probabilities,
            "customdata": customdata,
            "line": {"color": "#1f77b4", "width": 3},
            "marker": {"size": 8},
            "hovertemplate": (
                "%{text}<br>"
                "P vs %{customdata[5]}: %{y:.6f}<br>"
                "support: %{customdata[1]} / %{customdata[0]}<br>"
                "CI95: [%{customdata[2]:.6f}, %{customdata[3]:.6f}]<br>"
                "sample groups: %{customdata[6]}"
                "<extra></extra>"
            ),
            "text": labels,
        },
        {
            "type": "scatter",
            "mode": "lines",
            "name": "CI95 low",
            "x": x_values,
            "y": ci_low,
            "line": {"color": "rgba(31, 119, 180, 0.25)", "width": 1},
            "hoverinfo": "skip",
            "showlegend": False,
        },
        {
            "type": "scatter",
            "mode": "lines",
            "name": "CI95 high",
            "x": x_values,
            "y": ci_high,
            "line": {"color": "rgba(31, 119, 180, 0.25)", "width": 1},
            "fill": "tonexty",
            "fillcolor": "rgba(31, 119, 180, 0.10)",
            "hoverinfo": "skip",
            "showlegend": False,
        },
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": "CI half-width / probability",
            "x": x_values,
            "y": relative_ci,
            "customdata": customdata,
            "yaxis": "y2",
            "line": {"color": "#ff4b1f", "width": 3},
            "marker": {"size": 7, "symbol": "diamond"},
            "hovertemplate": (
                "%{text}<br>"
                "relative CI half-width: %{y:.4f}<br>"
                "support: %{customdata[1]} / %{customdata[0]}<br>"
                "sample groups: %{customdata[6]}"
                "<extra></extra>"
            ),
            "text": labels,
        },
    ]
    layout = {
        "title": f"{upper}-{lower} boundary bridge distribution ({period}, {grouping.value})",
        "template": "plotly_white",
        "hovermode": "x unified",
        "xaxis": {
            "title": "boundary coordinate",
            "tickmode": "array",
            "tickvals": x_values,
            "ticktext": labels,
        },
        "yaxis": {"title": "interdivision probability", "rangemode": "tozero"},
        "yaxis2": {
            "title": "relative CI half-width",
            "overlaying": "y",
            "side": "right",
            "rangemode": "tozero",
        },
        "legend": {"orientation": "h", "y": -0.22},
        "margin": {"l": 70, "r": 80, "t": 70, "b": 130},
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{upper}-{lower} boundary bridge distribution</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; }}
    #chart {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div id="chart"></div>
  <script>
    const data = {json.dumps(data)};
    const layout = {json.dumps(layout)};
    Plotly.newPlot("chart", data, layout, {{responsive: true}});
  </script>
</body>
</html>
"""


def build_bridge_plot_html(
    *,
    period: str,
    grouping: GroupingName,
    upper: str,
    lower: str,
    rows: list[BridgeDistributionRow],
) -> str:
    x_values = list(range(len(rows)))
    labels = [row.focal_group for row in rows]
    probabilities = [row.probability for row in rows]
    ci_low = [row.ci95_low for row in rows]
    ci_high = [row.ci95_high for row in rows]
    relative_ci = [row.ci95_half_width_over_probability for row in rows]
    customdata = [
        [
            row.scheduled_bout_count,
            row.interdivision_bout_count,
            row.ci95_low,
            row.ci95_high,
            row.ci95_half_width_over_probability,
            row.opponent_division,
        ]
        for row in rows
    ]

    data = [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": "probability",
            "x": x_values,
            "y": probabilities,
            "customdata": customdata,
            "line": {"color": "#1f77b4", "width": 3},
            "marker": {"size": 8},
            "hovertemplate": (
                "%{text}<br>"
                "P vs %{customdata[5]}: %{y:.6f}<br>"
                "support: %{customdata[1]} / %{customdata[0]}<br>"
                "CI95: [%{customdata[2]:.6f}, %{customdata[3]:.6f}]"
                "<extra></extra>"
            ),
            "text": labels,
        },
        {
            "type": "scatter",
            "mode": "lines",
            "name": "CI95 low",
            "x": x_values,
            "y": ci_low,
            "line": {"color": "rgba(31, 119, 180, 0.25)", "width": 1},
            "hoverinfo": "skip",
            "showlegend": False,
        },
        {
            "type": "scatter",
            "mode": "lines",
            "name": "CI95 high",
            "x": x_values,
            "y": ci_high,
            "line": {"color": "rgba(31, 119, 180, 0.25)", "width": 1},
            "fill": "tonexty",
            "fillcolor": "rgba(31, 119, 180, 0.10)",
            "hoverinfo": "skip",
            "showlegend": False,
        },
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": "CI half-width / probability",
            "x": x_values,
            "y": relative_ci,
            "customdata": customdata,
            "yaxis": "y2",
            "line": {"color": "#ff4b1f", "width": 3},
            "marker": {"size": 7, "symbol": "diamond"},
            "hovertemplate": (
                "%{text}<br>"
                "relative CI half-width: %{y:.4f}<br>"
                "support: %{customdata[1]} / %{customdata[0]}"
                "<extra></extra>"
            ),
            "text": labels,
        },
    ]
    layout = {
        "title": f"{upper}-{lower} bridge distribution ({period}, {grouping.value})",
        "template": "plotly_white",
        "hovermode": "x unified",
        "xaxis": {
            "title": "sideless chii, plotted in chii order",
            "tickmode": "array",
            "tickvals": x_values,
            "ticktext": labels,
        },
        "yaxis": {"title": "interdivision probability", "rangemode": "tozero"},
        "yaxis2": {
            "title": "relative CI half-width",
            "overlaying": "y",
            "side": "right",
            "rangemode": "tozero",
        },
        "legend": {"orientation": "h", "y": -0.22},
        "margin": {"l": 70, "r": 80, "t": 70, "b": 110},
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{upper}-{lower} bridge distribution</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; }}
    #chart {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div id="chart"></div>
  <script>
    const data = {json.dumps(data)};
    const layout = {json.dumps(layout)};
    Plotly.newPlot("chart", data, layout, {{responsive: true}});
  </script>
</body>
</html>
"""


def write_counts_matrix(
    path: Path,
    *,
    day: int,
    groups: list[GroupKey],
    group_ids: dict[GroupKey, int],
    tallies: MatchupTallies,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Group", "GroupId", "RowTotal"] + [group.label for group in groups]
        )
        for focal in groups:
            row = [
                focal.label,
                group_ids[focal],
                tallies.row_totals.get((day, focal), 0),
            ]
            row.extend(
                tallies.counts.get((day, focal, opponent), 0)
                for opponent in groups
            )
            writer.writerow(row)


def write_probability_matrix(
    path: Path,
    *,
    day: int,
    groups: list[GroupKey],
    group_ids: dict[GroupKey, int],
    tallies: MatchupTallies,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Group", "GroupId", "RowTotal"] + [group.label for group in groups]
        )
        for focal in groups:
            row_total = tallies.row_totals.get((day, focal), 0)
            row = [focal.label, group_ids[focal], row_total]
            for opponent in groups:
                count = tallies.counts.get((day, focal, opponent), 0)
                probability = count / row_total if row_total else 0.0
                row.append(f"{probability:.8f}")
            writer.writerow(row)
