# Case Study - 4.3.1 Banzuke Division by Era

## Status

This is a case-study note for nav item `4.3.1 Banzuke Division by Era`.

It records what we have learned from the prototype, the current PA manifest work, and the UI Model discussion. It does **not** update the implementation contract directly.

The purpose is to work this case down toward actual HTML/CSS/JS. Later, this case study can be compared with other case studies to identify commonality and differences before making a single considered update to the implementation contract.

## Case-study role

`4.3.1 Banzuke Division by Era` is the first simple PA case study.

It is useful because it appears to be:

```text
ContentPanel
  = Heading + Contents

Contents
  = PA

PA
  = PATitle + Chart Artifact
```

There are currently no model-level `Options` for this case.

There is no `PASet`.

There is no table renderer.

There are no dynamic notes currently under consideration.

So this case should test only the simplest useful path:

```text
manifest loading
ContentPanel rendering
Heading rendering
Contents = PA rendering
PATitle rendering
Chart artifact rendering
model-aligned HTML/CSS scopes
```

It should not be used to settle the full renderer.

## Screenshot reading

The deployed screenshot shows:

```text
Heading
  Banzuke Division by Era
  Historical banzuke division structure by era.

PA title
  Average banzuke composition by era

PA subhead
  Average banzuke composition by division (1958-2026), 10-year era buckets except the final bucket.

Artifact
  stacked bar chart
```

No public option controls are visible.

No notes are visible in the screenshot.

Plotly-internal controls, if present, are artifact-internal affordances, not UI Model `Options`.

## Prototype evidence: deployed/custom page path

The deployed/custom page does not consume a full Plotly JSON specification.

The old/custom renderer loads:

```text
data/page.json
data/divisions.csv
data/metadata.json
```

Then page-specific browser JS:

```text
parses CSV
builds Plotly traces
builds Plotly layout
calls Plotly.newPlot(...)
```

So the deployed prototype path is not:

```text
producer emits full Plotly JSON
```

and not exactly:

```text
producer emits traces + layout
```

It is closer to:

```text
producer emits structured data + page config;
page-specific JS lowers that to Plotly.
```

This is useful evidence, but not a design obligation.

## Prototype evidence: PA manifest path

The existing PA manifest work gives a cleaner steer.

For this page, the manifest-style description is approximately:

```text
ChartPA
  id = banzuke_division_by_era
  renderer = banzuke_division_by_era_chart
  primary source = divisions
  data source = data/divisions.csv
  trace = stacked_bar
  x = era
  y = average_rikishi
  group_by = division
  x axis = Era
  y axis = Average rikishi per basho
  provenance / parameters / rendering details include:
    division order
    x tick angle
    custom legend double-click behavior
    era bucket years
```

This suggests a structured chart artifact contract rather than full Plotly JSON or page-specific JS.

## Current model classification

This case does not require a change to the UI Model.

The pressure is inside `Chart Artifact`, not at the level of:

```text
ContentPanel
Contents
PA
Artifact
Notes
Options
```

Current classification:

```text
ContentPanel
  Heading
  Contents
    PA
      PATitle
      Artifact
        Chart
```

No `Options`.

No `PASet`.

No `Notes`, unless later evidence shows otherwise.

## Working implementation direction

For this case study, the preferred direction is:

```text
structured chart artifact manifest
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

The JS may still do work, but it should do generic renderer work, not page-specific thinking.

In other words:

```text
old prototype JS:
  knows the page
  knows the CSV columns
  knows the grouping
  knows how this chart works

new renderer JS:
  knows stacked_bar lowering
  reads source/x/y/groupBy/order from the manifest
  builds Plotly traces/layout mechanically
```

## Settled local decisions for this case study

### Plotly loading

Use CDN for the first implementation slice.

This is acceptable for the case-study prototype. Production asset policy can be revisited later.

### Manifest loading

Use a separate manifest JSON file, not inline manifest JSON.

A possible local structure:

```text
case-study-4-3-1/
  index.html
  manifest.json
  data/
    divisions.csv
```

### CSV parsing

Do not add a new CSV parsing dependency for this first slice.

The existing project already uses hand-written CSV parsers in the prototype/runtime code. The first slice can reuse/adapt that approach.

A proper CSV parser may become desirable later, but it is not required to start.

### Chart lowering

For this case, support only:

```text
TraceSpec(kind="stacked_bar")
```

The renderer should fail clearly or show a diagnostic if another trace kind is encountered.

### Tick angle

`x_tickangle` should not be treated as a vague layout hint.

It is better understood as chart rendering policy:

```text
long-ish categorical x-axis labels shall render at -45 degrees
```

For this case, the renderer should honour the tick angle required by the manifest/prototype evidence.

### Legend double-click behavior

The custom double-click legend behaviour is not optional polish.

It is required because Plotly's default behaviour is not acceptable for this chart/use case.

For this case, the renderer should install the custom behaviour if the manifest says to do so.

### Era bucket years

`era_bucket_years` is not layout.

It is a parameter that determined what is being shown.

It should be preserved in the manifest as semantic/data provenance or parameter metadata. Whether it is visibly rendered in the first slice remains open.

## Local manifest sketch

This is scratch-case-study material only. It is not yet an adopted contract.

```json
{
  "id": "banzuke_division_by_era",
  "heading": {
    "head": "Banzuke Division by Era",
    "subhead": "Historical banzuke division structure by era."
  },
  "contents": {
    "kind": "pa",
    "id": "banzuke_division_by_era",
    "title": {
      "head": "Average banzuke composition by era",
      "subhead": "Average banzuke composition by division (1958-2026), 10-year era buckets except the final bucket."
    },
    "artifact": {
      "kind": "chart",
      "renderer": "plotly",
      "dataSources": [
        {
          "id": "divisions",
          "label": "Average banzuke composition by era",
          "kind": "csv",
          "href": "data/divisions.csv",
          "mediaType": "text/csv"
        }
      ],
      "primarySource": "divisions",
      "traces": [
        {
          "id": "division_average",
          "label": "Division average",
          "kind": "stacked_bar",
          "source": "divisions",
          "x": "era",
          "y": "average_rikishi",
          "groupBy": "division",
          "visibleByDefault": true
        }
      ],
      "defaultTrace": "division_average",
      "xAxis": {
        "id": "x",
        "sourceField": "era",
        "label": "Era"
      },
      "yAxis": {
        "id": "y",
        "sourceField": "average_rikishi",
        "label": "Average rikishi per basho",
        "minimum": 0
      },
      "renderPolicy": {
        "categoricalXAxisTickAngle": -45,
        "legendInteraction": "custom_isolate_trace"
      },
      "parameters": {
        "eraBucketYears": 10
      },
      "ordering": {
        "division": [
          "Makuuchi",
          "Juryo",
          "Makushita",
          "Sandanme",
          "Jonidan",
          "Jonokuchi"
        ]
      }
    },
    "notes": []
  }
}
```

## Candidate DOM skeleton

This is also scratch-case-study material only.

```html
<main class="content-panel" data-panel-id="banzuke_division_by_era">
  <header class="heading">
    <h1>Banzuke Division by Era</h1>
    <p>Historical banzuke division structure by era.</p>
  </header>

  <section class="contents">
    <article class="pa" data-pa-id="banzuke_division_by_era">
      <header class="pa-title">
        <h2 class="pa-head">Average banzuke composition by era</h2>
        <p class="pa-subhead">Average banzuke composition by division (1958-2026), 10-year era buckets except the final bucket.</p>
      </header>

      <div class="artifact chart" data-artifact-kind="chart">
        <!-- Plotly chart mounts here -->
      </div>
    </article>
  </section>
</main>
```

There is no `.options` section for this case.

## What actual HTML/CSS/JS must prove

The first actual implementation should prove:

```text
separate manifest JSON load
CSV data source load
basic ContentPanel DOM construction
Heading rendering
Contents = PA rendering
PATitle rendering
Chart artifact mount
stacked_bar lowering
Plotly rendering from CDN
x tick angle policy
custom legend double-click behaviour
model-aligned CSS scopes
```

It should not attempt to prove:

```text
Options
PASet
Tables
Notes
URL state
full chart taxonomy
production asset policy
final Python model classes
```

## Settled local decisions

### Manifest field names

Use the new case-study field names from the manifest sketch, rather than preserving old PA-manifest names verbatim.

Important names include:

```text
dataSources
primarySource
groupBy
xAxis
yAxis
renderPolicy
parameters
ordering
```

These names are still case-study material, not yet a global implementation contract.

### Era bucket years

`eraBucketYears` is retained as parameter/metadata:

```json
"parameters": {
  "eraBucketYears": 10
}
```

It does not need to be rendered separately in the first working page, because the PA subhead already says:

```text
10-year era buckets except the final bucket
```

Later rendering may decide to surface this metadata more systematically.

### Custom legend interaction

The custom legend interaction is required.

The prototype disables Plotly's default legend double-click behaviour and installs custom legend click/double-click handling.

Required behaviour for this case:

```text
single legend click:
  toggle selected trace

double legend click:
  isolate selected trace

Plotly default legend behaviour:
  suppressed
```

The JS implementation should copy/adapt the existing custom behaviour from the current chart renderers.

### CSV parser

Use the robust simple parser pattern from `files/pa-runtime.js`.

Do not add a new CSV parsing dependency for this case study.

Avoid the page-specific `line.split(",")` style parser from the old custom renderer.

### HTML generation strategy

The first working page should have a minimal HTML shell. JS should build the whole `ContentPanel` from `manifest.json`.

This tests the intended path:

```text
manifest JSON
  -> JS renderer
      -> model-aligned DOM
```

The HTML shell should provide only an app mount and script/style loading.

## Settled HTML direction

Use modern semantic HTML where it maps directly to the UI Model.

For this case:

```text
ContentPanel -> <main>
Heading      -> <header>
Contents     -> <section>
PA           -> <article>
PATitle      -> nested <header>
Artifact     -> <div>
Chart mount  -> inner <div>
```

Candidate DOM produced by JS:

```html
<main class="content-panel" data-panel-id="banzuke_division_by_era">
  <header class="heading">
    <h1>Banzuke Division by Era</h1>
    <p class="heading-subhead">Historical banzuke division structure by era.</p>
  </header>

  <section class="contents">
    <article class="pa" data-pa-id="banzuke_division_by_era">
      <header class="pa-title">
        <h2 class="pa-head">Average banzuke composition by era</h2>
        <p class="pa-subhead">Average banzuke composition by division (1958-2026), 10-year era buckets except the final bucket.</p>
      </header>

      <div class="artifact chart" data-artifact-kind="chart">
        <div class="chart-mount"></div>
      </div>
    </article>
  </section>
</main>
```

There is no `.options` section for this case.

The inner `.chart-mount` keeps the model-level `.artifact.chart` wrapper separate from the element Plotly mutates.

## Settled CSS direction

The first CSS should establish model-aligned scopes. It does not need to be final visual policy.

Candidate CSS bodies:

```css
.content-panel {
  max-width: 1180px;
  margin: 0 auto;
  padding: 2rem;
}

.heading {
  margin-bottom: 1.5rem;
}

.heading h1 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.15;
}

.heading-subhead {
  margin: 0.35rem 0 0;
  color: #555;
}

.contents {
  display: block;
}

.pa {
  border-top: 1px solid #ddd;
  padding-top: 1.25rem;
}

.pa-title {
  margin-bottom: 1rem;
}

.pa-head {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.2;
}

.pa-subhead {
  margin: 0.35rem 0 0;
  color: #555;
}

.artifact.chart {
  min-height: 520px;
}

.chart-mount {
  width: 100%;
  min-height: 520px;
}
```

These values are provisional. The important point is the scoped vocabulary:

```text
content-panel
heading
contents
pa
pa-title
pa-head
pa-subhead
artifact chart
chart-mount
```

## Settled JS direction

The first working JS should do the following:

```text
1. Load manifest.json.
2. Build the ContentPanel DOM from the manifest.
3. Load data/divisions.csv.
4. Parse CSV using the robust simple parser pattern from pa-runtime.js.
5. Render Contents = PA.
6. Render PATitle.
7. Render Artifact = Chart.
8. Lower TraceSpec(kind="stacked_bar") to Plotly traces.
9. Apply axis labels and tick-angle policy.
10. Apply division ordering.
11. Call Plotly.newPlot().
12. Install the custom legend click/double-click behaviour.
```

Suggested function names:

```text
loadJson
loadText
parseCsv
renderContentPanel
renderHeading
renderContents
renderPA
renderPATitle
renderArtifact
renderChartArtifact
buildStackedBarTraces
installLegendInteraction
```

For this case, the chart renderer only needs to support:

```text
TraceSpec(kind="stacked_bar")
```

Trace lowering rule:

```text
source CSV rows
  group by trace.groupBy, using manifest ordering where present
  one Plotly bar trace per group
  x = trace.x
  y = Number(trace.y)
  layout.barmode = "stack"
```

Implementation-level choices:

```text
Unknown trace kind:
  throw or render a clear diagnostic

Numeric parsing:
  parse y values with Number(...)
  keep x/group fields as strings

Missing ordered groups:
  append after declared ordering, or warn in console

Loading failure:
  render a small error block in #app
```

These are ordinary coding decisions, not conceptual blockers.

## Readiness assessment

This case study is ready for actual HTML/CSS/JS implementation when desired.

Resolved for this case:

```text
UI model classification
manifest-loading strategy
Plotly loading strategy
CSV parsing strategy
DOM strategy
CSS scope strategy
stacked_bar chart lowering
legend interaction requirement
metadata treatment for eraBucketYears
```

Not addressed by this case, and intentionally deferred:

```text
Options
PASet
Tab

## Working principle for this case

If prototype evidence requires changes to `ContentPanel`, `Contents`, `PA`, `Artifact`, `Options`, or `Notes`, that would challenge the UI Model.

If prototype evidence only adds detail inside `Chart Artifact`, `DataBinding`, or chart renderer policy, then the UI Model is likely fine and the implementation contract simply needs detail.

So far, this case is on the happy path: the model does not need to change.
```
