# Rikishi Skill Trajectory Chart Proposal

## Status

Proposal note.

This document records a proposed Plotly chart for comparing rikishi skill
trajectories over time. It belongs in `src/products/docs` while the shape is
still being settled. Once the model is stable, the relevant contract should be
integrated into `src/products/make_site2/docs`.

---

## 1. Purpose

The chart shows the shape of one or more rikishi skill histories over a period
of years.

It is especially intended for comparing trajectories:

- how one rikishi's skill changes over calendar time;
- how two or more rikishi compare over the same calendar period;
- how two or more rikishi compare from the start of their banzuke careers.

The chart is not primarily a fine-grained banzuke-position inspection tool. For
`chii`, the important visible object is the broad shape of the trace.

---

## 2. Chart Form

The chart shall be a Plotly.js chart, consistent with other charts published by
`make_site2`. It should follow the shared Plotly chart presentation rules in
`src/products/make_site2/docs/05 Rendering Design.md`.

Custom legend handling is required for this chart. It should use or promote the
shared Plotly legend-helper work tracked in the make_site2 open issues rather
than copy PA-local legend code.

Inputs:

- one or more rikishi ids;
- skill rating: `chii` or `equelo`;
- time base: basho date or number of basho from first appearance;
- y-axis transform: linear or log-like.

This gives four rating/axis combinations:

- `equelo` on a linear y-axis;
- `equelo` on a log-like y-axis;
- `chii` on a linear transformed rank scale;
- `chii` on a log-like transformed rank scale.

For rating values such as `equelo`, the log y-axis shall use log base `b`,
where `b` is a constant named in a config file. The default base is `e`.

---

## 3. Time Base

When the time base is date, each point is plotted at the basho date.

When the time base is number of basho from first appearance, each point is
plotted relative to the rikishi's first banzuke appearance. By construction,
this is also the first basho with a rating.

The first point may be represented as either 0 or 1. That display convention is
still to be settled.

---

## 4. FilterPanel Controls

The chart controls belong in the FilterPanel.

Chart type selection should appear above the rikishi selector. This keeps the
chart type controls stable while the selected-rikishi list grows downward.

The rikishi selector is expected to be non-trivial and may become a mini-project
in itself.

The proposed selector has:

- a text box for shikona search;
- a dropdown of matching shikona while the user types;
- a list of currently selected rikishi below the search box;
- a remove button for each selected rikishi, probably marked `X` until a final
  icon/control convention is chosen;
- a `Go` button that produces or updates the chart.

Selecting a rikishi adds that rikishi id to the current chart selection. The
chart then produces one trace per selected rikishi.

---

## 5. Master Data File

The first implementation priority is to build and measure the master trajectory
data file.

The file should give the browser convenient static data for all represented
rikishi in the relevant rating history:

```text
rikishi id -> points
point -> date, shikona, full chii, equelo
```

The initial implementation writes:

```text
files/output/perf_chart/career_comparisons/trajectory_master.json
files/output/perf_chart/career_comparisons/trajectory_master_report.json
```

`make_site2` stages those files to:

```text
files/output/make_site2/rikishi/career-comparisons/data/
```

Because `equelo` is a fixed_v2 process rating, the master file is built from
the fixed_v2 Oracle-cleaned rating history and the simulator's true
basho-start rating snapshots. It does not reconstruct start ratings from
persisted day-end ratings, because that loses no-bout/no-day cases.

First full-build measurement:

```text
rikishi_count: 4994
point_count: 173428
max_points_per_rikishi: 197
raw_bytes: 8687627
gzip_bytes: 2710778
```

---

## 6. Normalised Shikona

Shikona are not unique.

The selector should present normalised shikona as display/search values. The
underlying selected value is always the rikishi id.

The current policy proposal lives in
`src/products/docs/Shikona Normalisation Proposal.md`. The chart selector should
consume the settled normalised-shikona policy rather than define its own
disambiguation rule.

---

## 7. Rating Snapshot

Skill ratings are taken at the start of a basho.

The chart should use the existing rating-at-start machinery. It should not
invent a new derivation of start-of-basho ratings merely for this chart.

Absent ratings are runtime defects. Under the project house style, impossible
internal states should fail immediately and disgracefully. The chart-maker
should not defensively recover from a missing rating, insert gaps, invent
fallback values, or domesticate the defect with a polite custom error.

---

## 8. Chii Scale

Raw `chii` values are not a useful direct y-axis for this chart.

Two problems motivate a transformed scale:

1. The set of observed `chii` positions varies by basho, and the number of
   rikishi in each division has varied widely.
2. The chart is mainly interested in sekitori-level shape, while much of the
   variation in observed `chii` positions occurs in the lower divisions.

The proposed scale is based on all human chii labels represented in the
chart-maker's current data universe, including obsolete ranks. It is not limited
to the selected rikishi histories.

Obsolete low-division ranks remain part of the scale. If a rikishi has an
interesting journey through now-obsolete lower ranks, the log-like compression
may hide much of that detail. If another rikishi fought when those ranks did not
exist, his trace may appear to jump across the missing range. This is acceptable
for this chart because lower-division detail is not the main visual target.

---

## 9. Human Chii

The y-axis uses human chii labels.

The current working definition is:

- sanyaku ranks use title only, such as `Y`, `O`, `S`, or `K`;
- other ranks use sideless chii, such as `M2` or `Jd27`.

Full chii detail is mapped to the human chii by deleting right-side detail until
the human form is reached.

Examples:

- `M2e` maps to `M2`;
- `M2wHD` maps to `M2`;
- `O3wHD` maps to `O`.

Side does not matter for the y-position. If two rikishi are `M2e` and `M2wHD`
in the same basho, both points map to the same `M2` y-position.

Full chii detail still matters in the hover display.

---

## 10. Chii Y-Values

The linear `chii` y-value is based on the ordered position of the human chii in
the full human-chii ladder.

The proposal is:

```text
y = N - position
```

where:

- `N` is the number of human chii labels in the chart-maker's data universe;
- `position` is the descending ordinal position of the human chii;
- higher-ranked chii have higher y-values.

The log-like `chii` y-value is not a literal logarithm. It is intended to
compress the lower divisions and make more visual space for upper-division
trajectory shape.

The first candidate transform is a two-band human-chii scale controlled by a
named constant:

```text
TOP_CHART_PROP = 0.6

Y through J occupy TOP_CHART_PROP of the chart.
Ms through Jk occupy 1 - TOP_CHART_PROP of the chart.
```

Within each band, human chii positions may initially be spaced linearly by
human-chii order.

There is no proposed special visual anchor at the sekitori boundary. The
boundary is embodied in the scale.

---

## 11. Axis Labels

The chii y-axis should display human chii labels, not transformed numeric
values.

Plotly may thin the labels, but the label format is fixed by the chart-maker:
titles for sanyaku and sideless chii for all other ranks.

The exact tick-selection strategy for the log-like chii scale remains open.

---

## 12. Hover Display

The default hover display should show:

- shikona;
- date;
- full chii or rating.

For `chii`, the hover display should use the full chii, not merely the human
axis label. This preserves distinctions such as `M2e` versus `M2wHD` even when
both map to the same y-position.

The transformed y-value is an internal plotting coordinate and need not be part
of the default hover display.

---

## 13. Open Questions

- Should basho-from-first-appearance start at 0 or 1?
- Where should the rating log-base and `TOP_CHART_PROP` constants live?
- Is the `TOP_CHART_PROP = 0.6` two-band scale the right first compressed
  `chii` transform?
- How should ticks be selected for the compressed `chii` y-axis?
- Which existing helper names should be used for full chii, annotation-free
  chii, sideless chii, title, human chii, and rating-at-start?
- Should selector matching use prefix match, substring match, or another
  search rule?
- What keyboard behavior should the autocomplete selector support?
