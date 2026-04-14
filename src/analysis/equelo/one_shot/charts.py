from pathlib import Path

import plotly.graph_objects as go

from ....sumo_core.Chii import Chii

from .types import TimelineToRatingMap


def write_probe_chart(
    output_path: Path,
    timeline_to_ratings: TimelineToRatingMap,
    probes: list[Chii],
    title: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ordered_times = list(timeline_to_ratings.keys())
    fig = go.Figure()

    for chii in probes:
        xs: list[str] = []
        ys: list[float] = []

        for key in ordered_times:
            ratings = timeline_to_ratings[key]
            if chii in ratings:
                xs.append(key)
                ys.append(ratings[chii])

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines+markers",
                name=str(chii),
                marker={"size": 4},
                hovertemplate="Day=%{x}<br>Rating=%{y:.2f}<extra>%{fullData.name}</extra>",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Competition day",
        yaxis_title="Rating",
        hovermode="closest",
        xaxis=dict(type="category", categoryorder="array", categoryarray=ordered_times),
    )
    fig.write_html(str(output_path), include_plotlyjs="cdn")
