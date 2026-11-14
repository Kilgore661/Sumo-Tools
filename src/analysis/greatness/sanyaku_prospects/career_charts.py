from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

from src.analysis.site89.rikishi_bio_data import completed_years
from src.infra.get_bios.api import BioStore
from src.sumo_core.BasicPrimitives import RikId
from src.sumo_core.History import History

from .model import CareerChartPoint, Population, RankStateObservation, RankStateProbabilityRow


PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def build_career_chart_points(
    rikishi_ids: tuple[int, ...],
    *,
    observations: tuple[RankStateObservation, ...],
    probabilities: tuple[RankStateProbabilityRow, ...],
    first_sanyaku,
    history: History,
    bios: BioStore,
    population: Population,
    coverage,
) -> tuple[CareerChartPoint, ...]:
    requested = tuple(dict.fromkeys(rikishi_ids))
    invalid = [rid for rid in requested if RikId(rid) not in population.birth_dated_ids]
    if invalid:
        labels = ", ".join(str(rid) for rid in invalid)
        raise ValueError(f"Career charts require eligible birth-dated rikishi IDs: {labels}")

    lookup = {
        (row.division, row.rank_number, row.age): row
        for row in probabilities
    }
    by_rikishi: dict[int, list[RankStateObservation]] = {rid: [] for rid in requested}
    for row in observations:
        if row.rikishi_id in by_rikishi:
            by_rikishi[row.rikishi_id].append(row)

    points: list[CareerChartPoint] = []
    for rid in requested:
        career = by_rikishi[rid]
        if not career:
            raise ValueError(f"No pre-san'yaku rank-state observations for rikishi ID {rid}")
        for row in career:
            probability = lookup[(row.division, row.rank_number, row.age)]
            birth_date = bios[RikId(rid)].birth_date.value
            start_date = date.fromisoformat(row.start_date)
            points.append(
                CareerChartPoint(
                    rikishi_id=rid,
                    shikona=row.shikona,
                    basho=row.basho,
                    date=row.start_date,
                    age=row.age,
                    exact_age=_exact_age(birth_date, start_date),
                    division=row.division,
                    rank_number=row.rank_number,
                    chii=row.chii,
                    point_kind="cohort_probability",
                    probability=probability.resolved_probability,
                    cohort_observations=probability.observations,
                    cohort_rikishi=probability.unique_rikishi,
                    cohort_success=probability.success,
                    cohort_failure=probability.failure,
                    cohort_unresolved=probability.right_censored + probability.unknown,
                    cohort_resolved=probability.resolved,
                    support_tier=_support_tier(probability.resolved),
                )
            )

        event = first_sanyaku.get(RikId(rid))
        if event is not None:
            event_index, event_chii = event
            basho = population.dates[event_index]
            banzuke = history[basho].banzuke
            start_date = coverage[basho].start_date
            birth_date = bios[RikId(rid)].birth_date.value
            points.append(
                CareerChartPoint(
                    rikishi_id=rid,
                    shikona=str(banzuke.rikshik[RikId(rid)]),
                    basho=str(basho),
                    date=start_date.isoformat(),
                    age=completed_years(birth_date, start_date),
                    exact_age=_exact_age(birth_date, start_date),
                    division=event_chii.level.as_abbreviation(),
                    rank_number=event_chii.number,
                    chii=str(event_chii),
                    point_kind="sanyaku_attainment",
                    probability=1.0,
                    cohort_observations="",
                    cohort_rikishi="",
                    cohort_success="",
                    cohort_failure="",
                    cohort_unresolved="",
                    cohort_resolved="",
                    support_tier="attained",
                )
            )
    return tuple(points)


def write_career_charts(
    output_directory: Path,
    points: tuple[CareerChartPoint, ...],
) -> tuple[Path, ...]:
    output_directory.mkdir(parents=True, exist_ok=True)
    ids = tuple(dict.fromkeys(point.rikishi_id for point in points))
    paths = []
    for rid in ids:
        career = tuple(point for point in points if point.rikishi_id == rid)
        path = output_directory / f"{rid}.html"
        path.write_text(_chart_html(career), encoding="utf-8")
        paths.append(path)
    return tuple(paths)


def _chart_html(points: tuple[CareerChartPoint, ...]) -> str:
    title = (
        f"{points[-1].shikona}: historical probability of eventually attaining "
        "a san'yaku rank, given rank and age"
    )
    x = [point.exact_age for point in points]
    y = [None if point.probability == "" else point.probability for point in points]
    custom = [
        [
            point.basho,
            point.age,
            point.chii,
            point.cohort_observations,
            point.cohort_rikishi,
            point.cohort_success,
            point.cohort_failure,
            point.cohort_unresolved,
            point.cohort_resolved,
            point.point_kind,
            point.support_tier,
            point.date,
        ]
        for point in points
    ]
    trajectory = {
        "type": "scatter",
        "mode": "lines",
        "name": "Observed historical proportion",
        "x": x,
        "y": y,
        "customdata": custom,
        "connectgaps": False,
        "line": {"color": "#315a7d", "width": 1},
        "hoverinfo": "skip",
    }
    traces = [trajectory]
    support_styles = {
        "supported": ("Supported (20+ resolved rikishi)", "#00a651"),
        "low": ("Low support (10–19)", "#ffb000"),
        "very_low": ("Very low support (<10)", "#e31a1c"),
    }
    for tier, (name, color) in support_styles.items():
        selected = [
            (point, index)
            for index, point in enumerate(points)
            if point.point_kind == "cohort_probability"
            and point.support_tier == tier
            and point.probability != ""
        ]
        if not selected:
            continue
        traces.append(
            {
                "type": "scatter",
                "mode": "markers",
                "name": name,
                "x": [point.exact_age for point, _ in selected],
                "y": [point.probability for point, _ in selected],
                "customdata": [custom[index] for _, index in selected],
                "marker": {
                    "symbol": "circle",
                    "size": 10,
                    "color": color,
                    "line": {"color": "#ffffff", "width": 1.25},
                },
                "hovertemplate": (
                    "<b>%{customdata[2]}</b><br>"
                    "Basho: %{customdata[0]} (%{customdata[11]})<br>"
                    "Age at basho: %{x:.2f} years<br>"
                    "Completed age used for cohort: %{customdata[1]}<br>"
                    "Observed proportion: %{y:.1%}<br>"
                    "Successes: %{customdata[5]} / %{customdata[8]} resolved rikishi<br>"
                    "Unique rikishi: %{customdata[4]} "
                    "(%{customdata[7]} unresolved)<br>"
                    "Banzuke observations: %{customdata[3]}<extra></extra>"
                ),
            }
        )
    terminal = next((point for point in points if point.point_kind == "sanyaku_attainment"), None)
    if terminal is not None:
        traces.append(
            {
                "type": "scatter",
                "mode": "markers",
                "name": "First san'yaku",
                "x": [terminal.exact_age],
                "y": [1.0],
                "marker": {
                    "symbol": "star",
                    "size": 18,
                    "color": "#d4a017",
                    "line": {"color": "#5b4300", "width": 2},
                },
                "hovertemplate": (
                    f"<b>First san'yaku</b><br>{html.escape(terminal.basho)}<br>"
                    f"{html.escape(terminal.chii)}<br>Attained: 100%<extra></extra>"
                ),
            }
        )

    layout = {
        "template": "plotly_white",
        "title": {"text": title, "x": 0.02, "xanchor": "left"},
        "xaxis": {"title": "Age at basho (years)", "type": "linear", "tickformat": ".1f"},
        "yaxis": {
            "title": "Observed proportion eventually reaching san'yaku",
            "tickformat": ".0%",
            "range": [0, 1.08],
        },
        "hovermode": "closest",
        "margin": {"l": 80, "r": 30, "t": 80, "b": 70},
        "legend": {"orientation": "h", "y": -0.2},
    }
    config = {"responsive": True, "displaylogo": False}
    traces_json = json.dumps(traces, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    layout_json = json.dumps(layout, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    config_json = json.dumps(config, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <script src="{PLOTLY_CDN}"></script>
  <style>
    html, body {{ margin: 0; min-height: 100%; font-family: system-ui, sans-serif; color: #17212b; }}
    #chart {{ width: 100%; min-height: 620px; }}
    .explanation {{
      box-sizing: border-box;
      max-width: 1100px;
      margin: 0 auto 3rem;
      padding: 0 1.5rem 1.5rem;
      line-height: 1.55;
    }}
    .explanation h2 {{ font-size: 1.25rem; margin: 0 0 .65rem; }}
    .explanation h3 {{ font-size: 1rem; margin: 1.25rem 0 .35rem; }}
    .explanation p {{ margin: .35rem 0; }}
    .explanation dl {{ display: grid; grid-template-columns: max-content 1fr; gap: .45rem 1rem; }}
    .explanation dt {{ font-weight: 700; }}
    .explanation dd {{ margin: 0; }}
    .formula {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    @media (max-width: 640px) {{
      .explanation dl {{ display: block; }}
      .explanation dt {{ margin-top: .65rem; }}
    }}
  </style>
</head>
<body>
  <div id="chart"></div>
  <section class="explanation" aria-labelledby="how-to-read">
    <h2 id="how-to-read">How to read this chart</h2>
    <p>
      This chart asks: given a rikishi's rank and completed age at a basho, what
      proportion of historically comparable rikishi eventually reached
      san'yaku? Each ordinary point uses that rank and completed age to select
      its cohort. East and west are pooled, and the cohort can contain rikishi
      from any represented year—not only the period of the plotted career.
      Each rikishi counts once within a rank-age cohort.
    </p>
    <p>
      The x-axis shows the rikishi's continuous age, calculated from his exact
      birth date and the tournament's exact Day 1. This keeps successive basho
      distinct. Cohorts use completed integer age; hover text shows both the
      exact date and completed age used for the calculation.
    </p>
    <p>
      The plotted value is the observed proportion of resolved rikishi who
      eventually reached san'yaku:
      <span class="formula">successes / (successes + failures)</span>.
      Unresolved careers are shown in the hover counts but are not included in
      that denominator. The line joins the points as a visual guide; it is not
      a smoothed or personalised forecast.
    </p>
    <dl>
      <dt>Eligible rikishi</dt>
      <dd>Rikishi for whom the represented career is complete from its beginning and an exact birth date is available.</dd>
      <dt>Success</dt>
      <dd>The rikishi later reached san'yaku at least once.</dd>
      <dt>Failure</dt>
      <dd>The rikishi retired without reaching san'yaku.</dd>
      <dt>Resolved</dt>
      <dd>A success or failure: the eventual outcome is known.</dd>
      <dt>Unresolved</dt>
      <dd>Normally a rikishi still active at the analysis cutoff, so he may yet reach san'yaku; it can also include a case whose lifecycle evidence is unknown.</dd>
      <dt>Support</dt>
      <dd>The number of unique resolved rikishi in the cohort. Green means 20 or more, amber 10–19, and red fewer than 10.</dd>
      <dt>Banzuke observations</dt>
      <dd>The raw number of appearances in the cohort; repeated basho by one rikishi increase this count but not support.</dd>
      <dt>Basho</dt>
      <dd>A tournament. Its exact Day 1 date places the point and determines completed age.</dd>
      <dt>Chii</dt>
      <dd>The displayed rank, such as <code>Jk15w</code> for Jonokuchi 15 West.</dd>
      <dt>San'yaku</dt>
      <dd>Komusubi, Sekiwake, Ozeki or Yokozuna. The gold star is the rikishi's observed first attainment, fixed at 100%, not another cohort probability.</dd>
    </dl>
    <p>
      A career that ends without san'yaku simply stops; the chart does not add
      an artificial 0% retirement point.
    </p>
  </section>
  <script>
    const traces = {traces_json};
    const layout = {layout_json};
    const config = {config_json};
    Plotly.newPlot("chart", traces, layout, config);
  </script>
</body>
</html>
"""


def _support_tier(resolved: int) -> str:
    if resolved == 0:
        return "undefined"
    if resolved < 10:
        return "very_low"
    if resolved < 20:
        return "low"
    return "supported"


def _exact_age(birth_date: date, as_of: date) -> float:
    completed = completed_years(birth_date, as_of)
    last_birthday = _birthday_in_year(birth_date, birth_date.year + completed)
    next_birthday = _birthday_in_year(birth_date, birth_date.year + completed + 1)
    fraction = (as_of - last_birthday).days / (next_birthday - last_birthday).days
    return completed + fraction


def _birthday_in_year(birth_date: date, year: int) -> date:
    try:
        return birth_date.replace(year=year)
    except ValueError:
        # Match completed_years: a 29 February birthday advances on 1 March in
        # a non-leap year.
        return date(year, 3, 1)
