# Career San'yaku Prospect Charts

## Status and package placement

This document specifies the implemented career-chart extension to
`analysis.greatness.sanyaku_prospects`. It does not require a separate package:
the extension uses the same eligible population, exact basho dates, birth
dates, san'yaku endpoint, outcome classification, and history cutoff as the
division-and-age analysis.

## Purpose

Division-state probability naturally leads to a longitudinal question:

> As a rikishi moves through the banzuke and grows older, how does the
> historical probability of eventually reaching san'yaku change?

The chart is intended to show that trajectory across the rikishi's entire
represented ranked career, not only his time in Maegashira.

## Probability state

For a pre-san'yaku banzuke appearance, let:

- `D` be the division or Maegashira group;
- `R` be the numerical rank within that group;
- `A` be completed age on the exact civil date of Day 1; and
- `S` mean first eventual attainment of Komusubi, Sekiwake, Ozeki, or Yokozuna.

The plotted historical cohort proportion is:

\[
P(S \mid D, R, A, \text{no previous san'yaku}).
\]

The supported pre-san'yaku groups are `M`, `J`, `Ms`, `Sd`, `Jd`, and `Jk`.
East and west are pooled by using `Chii.number`. Rank annotations such as
tsukedashi do not form separate rank states; entry route remains a possible
future parameter.

## Observation and aggregation policy

The implementation retains one observation for every eligible pre-san'yaku
banzuke appearance. Observations are grouped by `(D, R, A)`, but each rikishi
counts only once toward the outcome proportion in a cell. This prevents several
basho in the same state from masquerading as independent support. The existing
four outcomes are:

- success;
- failure;
- right-censored;
- unknown.

They use the parent analysis's two-source lifecycle rule. Formal presence in
History or a cutoff career-page status of `Mz`, `Bg`, `Kg`, or `Sj` is active
and right-censored; parsed retirement or absence from both cutoff sources is a
failure. Missing, invalid, unrecognised, or contradictory career-page evidence
remains unknown. This prevents an omitted Maezumo row from looking like a
retirement.

The resolved proportion and censoring bounds use unique rikishi and the same
formulas as the parent analysis. Raw banzuke-observation count is retained as a
separate audit field. No smoothing or automatic pooling of rare ranks is
applied. A cell with no resolved outcomes has no resolved proportion; the chart
must preserve it as missing rather than invent a value.

The observed proportion is an exact description of the resolved historical
cohort. It becomes an estimate only if it is generalised as the chance for
another comparable rikishi.

## Support presentation

Support is the number of unique resolved rikishi in a `(D, R, A)` cell. It is
not the number of banzuke observations. The initial descriptive tiers are:

| Unique resolved rikishi | Presentation |
|---:|---|
| 20 or more | supported; solid green marker |
| 10--19 | low support; solid amber marker |
| 1--9 | very low support; solid red marker |
| 0 | undefined proportion; chart gap |

Twenty is the minimum for an unqualified marker, not a visibility cutoff. Rare
cells remain visible so that unusual careers can still be inspected. The tiers
are descriptive presentation policy rather than formal statistical uncertainty
intervals.

In the canonical 1958--2026 run, 7,410 eligible rikishi supply 258,465
pre-san'yaku banzuke observations across 10,493 `(D, R, A)` cells. The median
cell has seven unique resolved rikishi. Requiring 20 would retain 31.9% of cells
but cover 83.3% of actual career observations; within Maegashira it would cover
69.3% of observations. This is why low-support cells remain visible but are
qualified rather than removed.

## Career series

For each requested eligible rikishi, emit one chart point for every represented
pre-san'yaku basho. A career such as

```text
Jk20 -> Jd70 -> Sd40 -> Ms15 -> J8 -> M14 -> M6
```

therefore produces seven dated probability points. If a rikishi occupies the
same rank in several basho, every basho remains a separate point even when the
looked-up probability is unchanged.

Each point must retain:

- rikishi ID and shikona;
- basho label and exact start date;
- completed age and continuous exact age;
- division, rank number, and full display chii;
- point kind;
- probability;
- raw historical observation count;
- unique rikishi and outcome counts;
- unique resolved-rikishi support; and
- support tier.

The x-axis is continuous age at the exact basho start date and the y-axis is
probability. Continuous age preserves the order of multiple basho within one
completed year. Cohort lookup still uses completed integer age, which remains
in hover metadata together with basho date and rank.

## First san'yaku marker

If the rikishi reaches san'yaku, include his first san'yaku basho as a terminal
point at 100%. This is an observed outcome rather than another cohort estimate.
The point has `point_kind = sanyaku_attainment` and is overlaid with a distinct
Plotly star marker and label.

The ordinary line also includes the terminal point so that it visibly reaches
100%. No later career points are plotted. If a rikishi never reaches san'yaku,
the chart simply ends at his last represented pre-san'yaku observation; it must
not add an artificial retirement point at 0%.

## Artifacts

The producer writes:

- `rank_state_observations.csv`, the basho-level historical observations;
- `probability_by_rank_state_age.csv`, one row per `(D, R, A)`;
- `career_chart_points.csv`, the auditable points for requested careers; and
- `career_charts/<rikishi_id>.html`, one responsive Plotly chart per requested
  rikishi.

The HTML loads pinned Plotly 2.35.2 from `cdn.plot.ly`. Supported, low-, and
very-low-support cells use green, amber, and red solid markers respectively.
Hover text states the underlying
success, resolved, total, unresolved, and observation counts. All chart data
is embedded in the document; network access is needed only to load Plotly.

## CLI

Use the existing package entry point and repeat `--chart-rikishi-id` as needed:

```powershell
python -m src.analysis.greatness.sanyaku_prospects `
  --chart-rikishi-id 12320 `
  --chart-rikishi-id 12226
```

Chart rendering defaults to the cached path: it reads
`rank_state_observations.csv`, `probability_by_rank_state_age.csv`, exact date
coverage, and bios, then writes only the requested chart points and HTML. It
does not load History or recompute the full cohort tables. `--rebuild` is
false by default; specify it to refresh the complete analysis before rendering:

```powershell
python -m src.analysis.greatness.sanyaku_prospects --rebuild `
  --chart-rikishi-id 12320
```

The cached path fails explicitly if the required bundle is absent or if a
requested rikishi is not in its eligible rank-state observations.

Only complete-record rikishi with full birth dates can be charted. An invalid
or ineligible requested ID is an error rather than a silently incomplete chart.

## Interpretation

The chart is not a personalised model of ability. It shows the trajectory of
historical cohorts matching the rikishi's division, rank number, and age. It
does not condition on recent results, injury, heya, exact east/west side, entry
route, or other individual information.

The estimates use the completed supporting history, including information not
necessarily available at the plotted date. Historical charts must therefore
not be described as contemporary forecasts that could have been issued at the
time.

## Validation requirements

Tests must demonstrate that:

1. east and west at the same division, rank number, and age are pooled;
2. repeated appearances by one rikishi count once in the cell proportion while
   remaining separate banzuke observations and chart points;
3. different rank numbers remain distinct;
4. every pre-san'yaku banzuke appearance produces a chart point;
5. exact Day 1 determines completed and continuous age, while basho date is
   retained in hover data;
6. support tiers use unique resolved rikishi and the declared boundaries;
7. undefined resolved proportions remain missing;
8. first san'yaku adds one terminal 100% point with a distinct marker;
9. retirement without san'yaku does not add a 0% point;
10. no post-san'yaku observations appear;
11. CSV rows reconcile with the probability lookup and embedded chart data; and
12. requested ineligible rikishi fail explicitly.

## Deferred work

- formal uncertainty intervals;
- alternative support tiers, smoothing, or rank-banding policies;
- entry-route conditioning;
- leave-one-rikishi-out historical estimates;
- rolling estimates using only information available by each plotted date;
- an index or selector for browsing many generated careers.
