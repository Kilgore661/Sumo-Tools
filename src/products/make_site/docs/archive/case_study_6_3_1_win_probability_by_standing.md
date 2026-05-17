# Case Study - 6.3.1 Win Probability by Standing

## Status

This is a case-study note for nav item `6.3.1 Win Probability by Standing`.

It records what we have learned from the screenshot, prototype code, existing PA manifest work, and comparison with `4.3.1 Banzuke Division by Era`.

It does **not** update the UI Model or the implementation contract directly.

The purpose is to work this case down toward actual HTML/CSS/JS, then later compare it with the other case studies before making one considered update to the implementation contract.

## Case-study order

This is the second chart case study.

The first case study, `4.3.1 Banzuke Division by Era`, established the simple chart PA happy path:

```text
ContentPanel
  = Heading + Contents

Contents
  = PA

PA
  = PATitle + Chart Artifact
```

`6.3.1` tests whether the same path still holds when the chart PA has model-level options.

## Screenshot reading

The deployed screenshot shows:

```text
Heading
  Win Probability by Standing
  Probability of winning as a function of standing.

Options
  Source
  Error bars
  Division

PA title
  Win Probability by Standing

PA subhead
  Empirical win probability by opponent standing; one line per selected-chii division.

Artifact
  Plotly line/scatter chart
```

The important new visible element compared with `4.3.1` is the `Options` area.

## Current model classification

This case does not require a change to the UI Model.

Classification:

```text
ContentPanel
  = Heading + Options + Contents

Contents
  = PA

PA
  = PATitle + Chart Artifact
```

There is no `PASet`.

The artifact is a chart.

The new pressure is inside:

```text
Options
Chart Artifact
Data source selection
Trace filtering / display filtering
```

not at the level of `ContentPanel`, `Contents`, `PA`, or `Artifact`.

## Difference lens: what this case adds

Compared with `4.3.1`, the new concern is:

```text
Options for a chart PA
```

The options are:

```text
Source
Division
Error bars
```

The important distinction is that not all options do the same kind of work.

For this case:

```text
Source
  selects which data source is displayed

Division
  filters or controls visible traces within the selected source

Error bars
  filters/toggles a visible evidence layer within the selected source
```

This gave rise to the first candidate synthesis finding:

```text
OptionControl
  may divide into ContentSelector and Filter
```

That is not yet an adopted model change.

## Similarity lens: does this disturb the 4.3.1 happy path?

No.

`6.3.1` remains a single chart PA:

```text
ContentPanel
  Heading
  Options
  Contents
    PA
      PATitle
      Chart Artifact
```

The chart can still be described by structured artifact data:

```text
data sources
trace spec
axis specs
chart policy / display policy
metadata / parameters
```

The difference is that option state participates in chart rendering:

```text
options state
  -> select data source
  -> filter traces
  -> toggle error bars
```

This extends the `4.3.1` path. It does not break it.

## Prototype evidence: data sources

The current page data bundle contains:

```text
data/page.json
data/observed_trace_points.csv
data/equelo_trace_points.csv
data/metadata.json
```

The important point is:

```text
There are two source CSVs:
  observed_trace_points.csv
  equelo_trace_points.csv
```

The `Source` option selects between them.

Each CSV contains all relevant divisions. The `Division` option is not a source selector; it filters or controls which traces are visible within the selected source.

So the shape is:

```text
Source
  -> choose CSV

Division
  -> filter traces within that CSV

Error bars
  -> toggle uncertainty display within selected traces/source
```

## Prototype evidence: existing PA manifest

The existing PA manifest is close to the desired direction.

It describes the page approximately as:

```text
ChartPA
  id = win_probability_by_standing
  renderer = standing_win_probability_chart

  options:
    source
    division
    error_bars

  data sources:
    observed -> data/observed_trace_points.csv
    equelo   -> data/equelo_trace_points.csv

  trace:
    kind = scatter
    x = opponent_chii
    y = p_selected_wins
    group_by = selected_chii
    error_y = ci95_lower, ci95_upper

  axes:
    x = opponent_chii, ordered by opponent_ordinal
    y = p_selected_wins, range 0..1, percent tick format

  consumes options:
    source
    division
    error_bars
```

This is useful prototype evidence and should be partially adopted.

## What to adopt from the PA manifest

Adopt the following ideas:

```text
multiple data sources declared in the manifest
an option selecting among data sources
structured trace spec
axis specs
error_y declaration
explicit link between options and chart artifact behaviour
```

Especially useful is the data-source selection pattern:

```text
source option value
  -> selected data source
```

In the new field style this might become something like:

```json
{
  "id": "observed",
  "href": "data/observed_trace_points.csv",
  "selectedBy": {
    "option": "source",
    "value": "observed"
  }
}
```

This is scratch-case-study material, not adopted contract.

## What to adapt, not adopt verbatim

### Heading and PATitle

The existing PA manifest has a heading-like field, but the new model distinguishes:

```text
ContentPanel Heading
PA PATitle
```

For this case they may be textually similar, but they remain different model concepts.

### Renderer name

The old manifest uses a page-specific renderer identity such as:

```text
standing_win_probability_chart
```

This is useful prototype evidence but should not become the final pattern if a generic chart renderer can handle the case.

The preferred direction is:

```text
Artifact
  kind = chart
  renderer = plotly
  traces = scatter trace spec
```

### Provenance bucket

Some values currently living in provenance-like structures are not necessarily provenance.

They may be:

```text
default display policy
trace/category inclusion policy
chart rendering policy
semantic/data metadata
```

This is similar to what was observed in `4.3.1`, where values such as tick angle, legend behaviour, and era bucket years needed better conceptual homes.

## Option interpretation

For this case:

```text
Source
  candidate kind: ContentSelector
  effect: selects observed or equelo data source

Division
  candidate kind: Filter
  effect: filters visible traces / selected-chii divisions

Error bars
  candidate kind: Filter
  effect: toggles visible uncertainty/evidence layer
```

This supports the synthesis finding that options may divide into:

```text
ContentSelector
Filter
```

Current decision:

```text
Do not update the UI Model yet.
```

The distinction is recorded in the synthesis findings doc and should be tested against later case studies.

## Working implementation direction

For this case study, the preferred direction is:

```text
structured chart artifact manifest
  + options state
    -> generic chart renderer
        -> Plotly traces/layout
```

rather than:

```text
full Plotly JSON manifest
```

or:

```text
page-specific JS renderer
```

The JS renderer should do generic chart work:

```text
load selected data source
parse CSV
build scatter traces from TraceSpec
apply division filter
apply error-bar filter
render with Plotly
```

The renderer should not contain page-specific assumptions such as:

```text
this is the Win Probability page
these are always the exact source names
these are always the exact division values
```

Those should come from manifest/config where possible.

## Local manifest sketch

This is scratch-case-study material only. It is not yet an adopted contract.

```json
{
  "id": "win_probability_by_standing",
  "heading": {
    "head": "Win Probability by Standing",
    "subhead": "Probability of winning as a function of standing."
  },
  "contents": {
    "kind": "pa",
    "id": "win_probability_by_standing",
    "title": {
      "head": "Win Probability by Standing",
      "subhead": "Empirical win probability by opponent standing; one line per selected-chii division."
    },
    "options": {
      "groups": [
        {
          "id": "main",
          "controls": [
            {
              "id": "source",
              "label": "Source",
              "control": "radio",
              "default": "observed",
              "values": [
                { "value": "observed", "label": "Observed" },
                { "value": "equelo", "label": "Equelo" }
              ]
            },
            {
              "id": "error_bars",
              "label": "Error bars",
              "control": "checkbox",
              "default": true
            },
            {
              "id": "division",
              "label": "Division",
              "control": "select",
              "default": "Makuuchi",
              "values": [
                { "value": "Makuuchi", "label": "Makuuchi" },
                { "value": "Juryo", "label": "Juryo" },
                { "value": "Makushita", "label": "Makushita" },
                { "value": "Sandanme", "label": "Sandanme" },
                { "value": "Jonidan", "label": "Jonidan" },
                { "value": "Jonokuchi", "label": "Jonokuchi" },
                { "value": "All", "label": "All" }
              ]
            }
          ],
          "groups": []
        }
      ]
    },
    "artifact": {
      "kind": "chart",
      "renderer": "plotly",
      "dataSources": [
        {
          "id": "observed",
          "kind": "csv",
          "href": "data/observed_trace_points.csv",
          "mediaType": "text/csv",
          "selectedBy": { "option": "source", "value": "observed" }
        },
        {
          "id": "equelo",
          "kind": "csv",
          "href": "data/equelo_trace_points.csv",
          "mediaType": "text/csv",
          "selectedBy": { "option": "source", "value": "equelo" }
        }
      ],
      "primarySource": "observed",
      "traces": [
        {
          "id": "standing_trace",
          "kind": "scatter",
          "source": "selected",
          "x": "opponent_chii",
          "y": "p_selected_wins",
          "groupBy": "selected_chii",
          "errorY": {
            "lower": "ci95_lower",
            "upper": "ci95_upper",
            "controlledBy": "error_bars"
          }
        }
      ],
      "xAxis": {
        "id": "x",
        "sourceField": "opponent_chii",
        "orderField": "opponent_ordinal",
        "label": "Opponent standing"
      },
      "yAxis": {
        "id": "y",
        "sourceField": "p_selected_wins",
        "label": "P(selected standing wins)",
        "minimum": 0,
        "maximum": 1,
        "tickformat": ".0%"
      },
      "filters": [
        {
          "id": "division",
          "option": "division",
          "field": "selected_chii",
          "allValue": "All"
        }
      ],
      "displayPolicy": {
        "defaultDisplayTrace": "Y1",
        "sanyakuDisplay": ["Y1", "O1", "S1", "K1"]
      }
    },
    "notes": []
  }
}
```

This sketch intentionally uses the new field-name style from the `4.3.1` case study.

## Candidate DOM extension

Compared with `4.3.1`, the DOM gains an `.options` section between `.heading` and `.contents`.

Candidate DOM shape:

```html
<main class="content-panel" data-panel-id="win_probability_by_standing">
  <header class="heading">
    <h1>Win Probability by Standing</h1>
    <p class="heading-subhead">Probability of winning as a function of standing.</p>
  </header>

  <section class="options">
    <fieldset class="option-group" data-option-group-id="main">
      <!-- Source, Error bars, Division controls -->
    </fieldset>
  </section>

  <section class="contents">
    <article class="pa" data-pa-id="win_probability_by_standing">
      <header class="pa-title">
        <h2 class="pa-head">Win Probability by Standing</h2>
        <p class="pa-subhead">Empirical win probability by opponent standing; one line per selected-chii division.</p>
      </header>

      <div class="artifact chart" data-artifact-kind="chart">
        <div class="chart-mount"></div>
      </div>
    </article>
  </section>
</main>
```

This preserves the same happy-path structure as `4.3.1` while adding the `Options` area.

## JS implications

Compared with `4.3.1`, the JS renderer needs to add:

```text
renderOptions
renderOptionGroup
renderOptionControl
read option state
update chart when option state changes
select data source from source option
filter traces from division option
toggle error bars from error_bars option
```

The chart renderer needs to support:

```text
TraceSpec(kind="scatter")
```

Scatter lowering rule:

```text
selected source CSV rows
  group by trace.groupBy
  optionally filter groups by Division option
  one Plotly scatter trace per group
  x = trace.x
  y = Number(trace.y)
  order x by xAxis.orderField where supplied
  attach error_y if enabled and available
```

The same CSV parser strategy as `4.3.1` applies:

```text
use robust simple parser from pa-runtime.js
no new CSV dependency yet
```

Plotly loading remains:

```text
CDN for the case-study implementation
```

## What actual HTML/CSS/JS must prove

This case should prove:

```text
Options section rendering
OptionGroup rendering
OptionControl rendering
option state reading
option-driven data source selection
option-driven trace filtering
option-driven error-bar toggling
scatter trace lowering
axis ordering from order field
same ContentPanel/PA/ChartArtifact path as 4.3.1
```

It should not attempt to prove:

```text
PASet
Tables
Notes
URL state, except perhaps later
full chart taxonomy
production asset policy
final Python model classes
```

## Readiness assessment

This case is conceptually ready once the exact old custom behaviours are checked during implementation.

Resolved for this case:

```text
UI model classification
main difference from 4.3.1
similarity to 4.3.1
source data structure at a conceptual level
option interpretation
partial adoption of existing PA manifest ideas
preferred renderer direction
candidate manifest shape
candidate DOM extension
JS responsibilities
```

Items to check during implementation:

```text
exact current custom renderer behaviour for default visible traces
exact sanyaku/default trace policy
whether error bars should be disabled/hidden automatically for equelo source
exact axis/category ordering behaviour
current hover text policy, if any
current legend behaviour, if applicable
```

These are chart-rendering details, not UI Model blockers.

## Working conclusion

`6.3.1` extends the `4.3.1` chart-PA happy path by adding `Options`.

The option behaviour appears general enough to record as a synthesis finding:

```text
Options may divide into ContentSelectors and Filters.
```

This finding should not be adopted into the model yet, but should be tested against later case studies.

The case does not undermine the similarity between `6.3.1` and `4.3.1`. Both remain single-PA chart pages rendered through a structured `ChartArtifact`.
