# 06 UI Model Implementation Contract

## Status

This document defines the first implementation-facing contract for the UI Model.

It replaces the earlier implementation-contract draft and incorporates the durable conclusions from:

- the UI Model discussion note;
- the `4.3.1 Banzuke Division by Era` case study;
- the `6.3.1 Win Probability by Standing` case study;
- the `7.3.1 Career Length` case study;
- the `2.2 Standings by Wins` case study;
- the case-study synthesis findings.

This document is not an executable specification. It is not intended to generate the renderer automatically.

The implementation will still be hand-written HTML/CSS/JS, supported by Python producer/model classes and plain JSON manifests.

The purpose of this document is to define the contract between:

```text
UI Model
  -> Python model / producer objects
  -> manifest JSON
  -> JS renderer
  -> HTML/CSS output
```

The old renderer remains prototype evidence. It may supply useful behaviours, data shapes, edge cases, and visual expectations, but it is not the contract.

## Working conclusion from the case studies

The case studies suggest that the existing code already contained much of the right implicit model.

The issue was not that the prototype had no model. The issue was that the model was distributed across:

```text
PA manifest classes
custom renderers
page-specific JavaScript
copied legacy pages
CSS conventions
old table apps
```

The new implementation should therefore not invent an unrelated architecture.

It should make the implicit model explicit and render from it deliberately.

The main implementation direction is:

```text
producer / Python objects
  -> intentional manifest JSON
      -> model-directed JS renderer
          -> semantic HTML/CSS realization
```

## Settled working model

The implementation contract follows this working model:

```text
PublicUI
  = Sidebar + ContentPanel

Sidebar
  = Caption + Navigation + Hider

ContentPanel
  = Heading + Options? + Contents

Contents
  = PA | PASet

PASet
  = PASelector + PA+

PA
  = PATitle? + Artifact + Notes?

PATitle
  = PAHead + PASubHead?

Artifact
  = Chart | Table | Prose

Options
  = OptionGroup+

OptionGroup
  = label?
  + OptionControl*
  + OptionGroup*
```

Current decisions:

```text
Contents is the model name for what a ContentPanel displays.
PASet is the model name for selectable multi-PA contents.
PA means publishable/published artifact.
PASelector is the selector required by PASet.
Options do not have Notes.
Options may have help/popover text.
Notes remain part of PA.
There is no Footing.
Only PASelector is currently a named option role.
Other option effects are descriptive for now, not formal model classes.
```

## What this model means for implementation

The renderer should not be organized around assumptions such as:

```text
table pages have options
chart pages do not
multi-view pages are special cases
multiple CSVs define a page type
page-specific JS owns the public rendering contract
```

Instead, the renderer should be organized around:

```text
ContentPanel
Contents
PASet, if present
PASelector, if present
Options / OptionGroups
selected or resolved PA
Artifact renderer
Notes renderer
```

Artifact kind determines the artifact renderer, not the top-level page model:

```text
Artifact = Chart
  -> chart renderer

Artifact = Table
  -> table renderer

Artifact = Prose
  -> prose renderer
```

A selected PA should always pass through the same PA path:

```text
selected PA
  -> PATitle?
  -> Artifact
  -> Notes?
```

## Layer distinction

The same conceptual entity may appear at several implementation layers.

```text
Model entity
  conceptual thing described by the UI Model

Python class
  construction, validation, defaults, normalization, producer convenience

Manifest object
  plain JSON-ish contract consumed by the JS renderer

Runtime object
  JS state/rendering representation

DOM/CSS
  browser rendering of the model
```

The manifest should be plain data.

Python classes may have methods for construction, validation, normalization, and manifest emission.

JS runtime objects may have rendering and state methods.

The manifest should not depend on Python methods being present in the browser.

## Python objects and manifest emission

Python classes should own construction and validation.

They should emit simple manifest dictionaries or JSON-serializable objects.

Illustrative shape:

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Heading:
    head: str
    subhead: str | None = None

    def to_manifest(self) -> dict[str, Any]:
        return {
            "head": self.head,
            **({"subhead": self.subhead} if self.subhead else {}),
        }

@dataclass(frozen=True)
class PATitle:
    head: str
    subhead: str | None = None

    def to_manifest(self) -> dict[str, Any]:
        return {
            "head": self.head,
            **({"subhead": self.subhead} if self.subhead else {}),
        }

@dataclass(frozen=True)
class Note:
    id: str
    text: str
    pertains_to: tuple[dict[str, str], ...] = ()

    def to_manifest(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            **({"pertainsTo": list(self.pertains_to)} if self.pertains_to else {}),
        }
```

The exact Python class layout is not settled here.

The important rule is:

```text
Python objects may be rich.
Manifest objects should be plain.
```

## Manifest contract overview

A ContentPanel manifest points to exactly one Contents manifest.

```python
ContentPanelManifest = {
    "id": str,
    "heading": HeadingManifest,
    "contents": ContentsManifest,
}
```

A Contents manifest is one of:

```text
PAManifest
PASetManifest
```

```python
ContentsManifest = PAManifest | PASetManifest
```

## Heading manifest

A Heading is page/content-level framing.

```python
HeadingManifest = {
    "head": str,
    "subhead": str | None,
}
```

The Heading belongs to the ContentPanel, not to the PA.

## PA manifest

A single PA manifest has the shape:

```python
PAManifest = {
    "kind": "pa",
    "id": str,
    "title": PATitleManifest | None,
    "options": OptionsManifest | None,
    "artifact": ArtifactManifest,
    "notes": list[NoteManifest],
}
```

A PA may be optioned.

A PA may be rendered directly as the whole Contents, or it may be one selectable PA inside a PASet.

## PASet manifest

A PASet manifest has the shape:

```python
PASetManifest = {
    "kind": "pa_set",
    "id": str,
    "selector": PASelectorManifest,
    "pas": list[PAManifest],
}
```

A meaningful PASet will normally contain two or more PAs, though the notation `PA+` means one or more.

The selected PA is rendered through the normal PA path:

```text
PASet
  -> selected PA
      -> PATitle?
      -> Artifact
      -> Notes?
```

## PATitle manifest

A PATitle is PA-level framing.

```python
PATitleManifest = {
    "head": str,
    "subhead": str | None,
}
```

PATitle belongs to the PA, not to the Artifact.

A PA may omit PATitle when the ContentPanel Heading supplies all needed reader-facing framing.

## Artifact manifest

Artifacts are discriminated by kind:

```python
ArtifactManifest = (
    ChartArtifactManifest
    | TableArtifactManifest
    | ProseArtifactManifest
)
```

The artifact owns concrete chart/table/prose rendering detail.

The artifact does not own public publication framing.

If reader-facing framing is needed, it belongs to the ContentPanel Heading or PA PATitle.

## Options manifest

Options are grouped public controls.

```python
OptionsManifest = {
    "groups": list[OptionGroupManifest],
}

OptionGroupManifest = {
    "id": str,
    "label": str | None,
    "controls": list[OptionControlManifest],
    "groups": list[OptionGroupManifest],
}
```

OptionControl remains general for now:

```python
OptionControlManifest = {
    "id": str,
    "label": str,
    "control": "radio" | "select" | "checkbox" | "toggle",
    "default": str | bool | int | float,
    "values": list[OptionValueManifest] | None,
    "help": str | None,
}
```

Possible control renderings include:

```text
radio buttons
select/dropdown
checkbox
toggle
segmented buttons
tabs
```

The control rendering is not itself the semantic option.

## PASelector manifest

A PASelector is special because it selects the visible PA from a PASet.

```python
PASelectorManifest = {
    "id": str,
    "label": str,
    "control": "radio" | "select" | "tabs",
    "defaultPA": str,
}
```

PASelector is currently the only named special option role in the contract.

It is structurally required by:

```text
PASet = PASelector + PA+
```

## Option effects

The case studies suggest that options may divide into two broad kinds:

```text
ContentSelector
Filter
```

For now this is a candidate synthesis finding, not an adopted model taxonomy.

The only formalized case is:

```text
PASelector
  a selector for the visible PA in a PASet
```

Other option effects remain descriptive:

```text
select a data source
select a data instance
select a representation/view
filter rows
filter traces
toggle an evidence layer
toggle a displayed feature
```

This distinction may later become formal if it proves useful for state, URL, validation, grouping, or rendering.

## Option help versus Notes

Options do not have Notes.

Options may have help or popover text:

```python
OptionControlManifest = {
    "help": str | None,
    ...
}
```

The rule is:

```text
Popover/help text may explain an option.
Notes belong to the PA.
```

If a future option needs persistent explanation that cannot be handled by help/popover text, that will be a concrete model pressure point.

Until such an example appears, Notes remain PA-owned.

## Notes manifest

Notes belong to PA.

```python
NoteManifest = {
    "id": str,
    "text": str,
    "pertainsTo": list[NoteTargetManifest] | None,
}
```

A note without `pertainsTo` is shown whenever the PA is selected.

A note with `pertainsTo` is shown when the relevant target is active, visible, or selected.

Initial target kinds:

```python
NoteTargetManifest =
    {"kind": "pa", "id": str}
  | {"kind": "column", "id": str}
  | {"kind": "columnGroup", "id": str}
  | {"kind": "visibilityPreset", "id": str}
  | {"kind": "trace", "id": str}
  | {"kind": "source", "id": str}
  | {"kind": "artifactComponent", "id": str}
```

The runtime assembles visible notes from the selected/resolved PA state.

Examples:

```text
note -> column
  shown when the column is visible or relevant

note -> trace
  shown when the trace is visible or relevant

note -> source
  shown when the source is selected

note -> PA
  shown whenever the PA is selected
```

Visible placement does not by itself determine semantic ownership.

For this contract, however, there is no separate Footing. The visible notes section is the PA's notes section.

## Data binding

Data binding belongs at the manifest/producer contract boundary.

The UI Model defines that public states, selected PAs, and artifacts may require data.

The producer contract defines which concrete files satisfy those requirements.

Minimal shape:

```python
DataBindingManifest = {
    "id": str,
    "kind": "csv" | "json" | "inline",
    "href": str | None,
    "data": object | None,
    "mediaType": str | None,
}
```

Data source count does not define a page type.

Multiple data sources may arise because:

```text
an option selects a source
an option selects a parameterized data instance
a PASelector selects a PA with its own source
derived displays are precomputed by producers
```

## Chart artifact contract

A ChartArtifact is a chart-specific artifact manifest.

A minimal structured chart manifest is:

```python
ChartArtifactManifest = {
    "kind": "chart",
    "renderer": "plotly",
    "dataSources": list[DataBindingManifest],
    "primarySource": str | None,
    "traces": list[TraceSpecManifest],
    "xAxis": AxisSpecManifest | None,
    "yAxis": AxisSpecManifest | None,
    "renderPolicy": dict,
    "displayPolicy": dict,
    "parameters": dict,
    "ordering": dict,
}
```

Not every field is required for every chart.

The important direction is:

```text
structured chart artifact manifest
  -> generic chart renderer
      -> Plotly traces/layout
```

rather than:

```text
full Plotly JSON as the public contract
```

or:

```text
page-specific JS as the public contract
```

The JS renderer may lower structured chart specs to Plotly traces/layout.

## Trace specs

Initial trace kinds needed by the case studies:

```text
stacked_bar
scatter
```

Illustrative trace spec:

```python
TraceSpecManifest = {
    "id": str,
    "label": str | None,
    "kind": str,
    "source": str,
    "x": str,
    "y": str,
    "groupBy": str | None,
    "errorY": dict | None,
    "visibleByDefault": bool | None,
}
```

The chart renderer should fail clearly or render a diagnostic if it encounters an unsupported trace kind.

## Axis specs

Illustrative axis spec:

```python
AxisSpecManifest = {
    "id": str,
    "sourceField": str,
    "orderField": str | None,
    "label": str | None,
    "minimum": int | float | None,
    "maximum": int | float | None,
    "tickformat": str | None,
}
```

Axis specs define analytical chart axes, not page or PA framing.

## Chart policies and metadata

The case studies suggest that old `provenance` buckets sometimes contain unlike things.

These should be separated when possible:

```text
renderPolicy
  chart rendering behaviour, such as categorical tick angle or legend interaction

displayPolicy
  default traces, default visible groups, or other display-state conventions

parameters
  semantic/data parameters, such as era bucket size

ordering
  explicit category/group orders

provenance
  source, generation, method, or audit metadata
```

Do not use `provenance` as a catch-all for renderer policy, display policy, and semantic parameters.

## Chart policies from case studies

From `4.3.1 Banzuke Division by Era`:

```text
TraceSpec(kind="stacked_bar")
CSV source: divisions
x = era
y = average_rikishi
groupBy = division
category order = division order
x tick angle = -45
legend interaction = custom isolation
parameters include eraBucketYears = 10
```

From `6.3.1 Win Probability by Standing`:

```text
TraceSpec(kind="scatter")
source option selects observed/equelo CSV
x = opponent_chii
y = p_selected_wins
groupBy = selected_chii
errorY controlled by error_bars option
x axis ordered by opponent_ordinal
y axis 0..1 with percent formatting
Division option filters traces
```

## Table artifact contract

A TableArtifact is a table-specific artifact manifest.

A minimal table manifest is:

```python
TableArtifactManifest = {
    "kind": "table",
    "dataSources": list[DataBindingManifest],
    "primarySource": str | None,
    "columns": list[TableColumnManifest],
    "columnGroups": list[TableColumnGroupManifest],
    "visibilityPresets": list[VisibilityPresetManifest],
    "rowFilters": list[RowFilterManifest],
    "defaultSort": SortSpecManifest | None,
}
```

The exact field names remain subject to implementation pressure, but the concepts are established by the rich table case study.

## Table columns

Table columns are semantic table definitions, not merely rendered `<th>` elements.

Candidate column fields:

```python
TableColumnManifest = {
    "id": str,
    "label": str,
    "sourceField": str | None,
    "group": str | None,
    "sortable": bool,
    "sortKind": str | None,
    "valueKind": str | None,
    "role": str | None,
    "align": "left" | "center" | "right" | None,
    "format": str | None,
    "help": str | None,
    "notes": list[str] | None,
}
```

This is intentionally more concrete than the UI model.

It belongs to the table artifact contract.

## Column groups and visibility presets

The `2.2 Standings by Wins` case study shows the need for:

```text
columnGroups
visibilityPresets
```

A visibility preset is a named public representation, not merely a low-level column-hiding operation.

Example:

```text
View = standard | percentages | combined
```

may be implemented by showing/hiding column groups, but the public option is a view/representation choice.

## Row filters

Row filters are table-artifact behaviour controlled by Options.

Examples from `2.2`:

```text
Active Rikishi Only
Division
```

These may be implemented by hiding rows, filtering an in-memory row set, or re-rendering the table.

That is renderer detail.

The public option meaning should remain explicit.

## Sorting

Sorting belongs to the table artifact contract.

Likely requirements:

```text
sortable columns declare sort behaviour
first-click direction is deliberate
chii-like values sort by ordinal, not alphabetically
orientation columns such as row numbers are not normal sortable data columns
default sort may depend on selected view/preset
```

The table renderer should treat sort semantics as part of the table manifest rather than infer them from display text alone.

## Column popovers and compact headings

Column headings should remain compact.

If meaning cannot fit in the heading, use column help/popovers and PA Notes.

Column popovers are artifact-internal affordances unless they become public model state.

They are not Options.

## Table notes

Table notes remain PA Notes.

They may pertain to:

```text
columns
column groups
visibility presets
row filters
the table/PA generally
```

Options may affect which notes are visible by changing the visible table state.

This does not make them option notes.

## Prose artifact contract

A ProseArtifact is a prose-specific artifact manifest.

A minimal shape is:

```python
ProseArtifactManifest = {
    "kind": "prose",
    "html": str | None,
    "markdown": str | None,
}
```

The case studies did not focus on prose.

The prose contract remains minimal until a prose case exposes concrete pressure.

## Renderer responsibilities

The JS renderer consumes the manifest and renders the UI model.

Top-level responsibilities:

```text
renderContentPanel(panelManifest)
renderHeading(headingManifest)
renderContents(contentsManifest)
renderPASet(paSetManifest)
renderPASelector(selectorManifest)
resolveSelectedPA(paSetManifest, runtimeState)
renderPA(paManifest)
renderOptions(optionsManifest)
renderOptionGroup(optionGroupManifest)
renderOptionControl(optionControlManifest)
renderArtifact(artifactManifest)
renderChartArtifact(chartArtifactManifest)
renderTableArtifact(tableArtifactManifest)
renderProseArtifact(proseArtifactManifest)
renderNotes(notes, runtimeState)
```

Rendering order follows the model:

```text
ContentPanel
  Heading
  Options, if present or contributed by Contents / selected PA
  Contents
    selected/resolved PA
      PATitle
      Artifact
      Notes
```

For a PASet:

```text
Render PASelector as part of Options.
Resolve selected PA.
Render selected PA's own Options, if any.
Render selected PA.
```

## Option rendering and state

The renderer should be able to render:

```text
Options
OptionGroup
OptionControl
PASelector
```

It should read option state and pass the relevant state to the artifact renderer.

Examples:

```text
Source option
  selects chart data source

Division option
  filters chart traces or table rows

View option
  selects table visibility preset

Number of Basho option
  selects table data source / data instance

PASelector
  selects visible PA from a PASet
```

URL-state policy is not fully defined in this contract.

However, meaningful public display state should be serializable where shareability matters.

## DOM and CSS vocabulary

The first DOM/CSS vocabulary should mirror the model.

Model classes:

```css
.public-ui {}

.sidebar {}
.sidebar .caption {}
.sidebar .navigation {}
.sidebar .hider {}

.content-panel {}
.content-panel .heading {}
.content-panel .options {}
.content-panel .contents {}

.pa-set {}
.pa-selector {}

.pa {}
.pa .pa-title {}
.pa .pa-head {}
.pa .pa-subhead {}
.pa .artifact {}
.pa .notes {}

.options .option-group {}
.options .option-control {}

.artifact.chart {}
.artifact.table {}
.artifact.prose {}
```

Implementation helper classes are allowed, but should be named as helpers rather than model concepts.

Examples:

```css
.ui-scroll-region {}
.ui-control-row {}
.ui-popover {}
.chart-mount {}
.table-scroll-region {}
.data-table {}
```

Page-specific classes should be avoided unless explicitly justified.

## Semantic HTML mapping

Use modern semantic HTML where it maps directly to the UI Model.

Typical mapping:

```text
ContentPanel -> <main>
Heading      -> <header>
Contents     -> <section>
PA           -> <article>
PATitle      -> nested <header>
Artifact     -> <div>
Notes        -> <section>
```

Example PA DOM:

```html
<main class="content-panel" data-panel-id="example">
  <header class="heading">
    <h1>...</h1>
    <p class="heading-subhead">...</p>
  </header>

  <section class="options">
    ...
  </section>

  <section class="contents">
    <article class="pa" data-pa-id="example_pa">
      <header class="pa-title">
        <h2 class="pa-head">...</h2>
        <p class="pa-subhead">...</p>
      </header>

      <div class="artifact chart" data-artifact-kind="chart">
        <div class="chart-mount"></div>
      </div>

      <section class="notes">
        ...
      </section>
    </article>
  </section>
</main>
```

The inner chart/table mount may be an implementation helper so that third-party libraries can mutate it without owning the model-level artifact wrapper.

## Framing text policy

The implementation must preserve ownership-specific framing text.

Do not collapse the following into one generic `title` field:

```text
NavLabel
Heading
PATitle
Artifact-internal labels
HTML <title>
```

### NavLabel

A navigation label is a locator.

Requirement:

```text
short enough for navigation
```

It may be compressed and may be somewhat unclear if unavoidable.

### Heading

Heading is content/page-level framing.

```text
Heading = Head + SubHead?
```

Requirement:

```text
enough page-level framing for the reader to understand what they selected
and why the major options, default column headings, or default chart traces exist
```

### PATitle

PATitle is PA-level framing.

```text
PATitle = PAHead + PASubHead?
```

Requirement:

```text
the PA plus its heading/subheading should be copy-pasteable
as a largely self-contained analytical object
```

### Artifact-internal labels

Artifact-internal labels include:

```text
column headings
trace labels
axis labels
legend labels
hover labels
```

Requirement:

```text
short enough to work inside the artifact
```

If meaning cannot be made clear inside the label itself, use help/popovers and PA Notes.

## Options layout policy

A candidate cross-case policy exists:

```text
simple / obvious / primary options at the top
gnarly / expert / advanced options at the bottom
```

Defaults should normally correspond to the simplest or most expected choices.

This is not yet a settled rendering rule.

Do not add formal model fields such as `priority`, `complexity`, or `advanced` until the case-study review proves they are needed.

For now, preserve this as a design pressure and test it across optioned pages.

## Reconciliation with existing PA manifest classes

The existing code already contains much of the implicit model.

Likely mappings:

```text
ChartPA
  -> PA with ChartArtifact

TablePA
  -> PA with TableArtifact

IndexedTablePA
  -> PA with indexed TableArtifact / table-runtime variant

MultiViewPA
  -> PASet

MultiViewPA.view_option
  -> PASelector

MultiViewPA.views
  -> PA+

EssayPA
  -> PA with ProseArtifact

Option
  -> OptionControl

Note
  -> PA Note

DataSource
  -> DataBinding / dataSources
```

The goal is not to preserve the existing code verbatim.

The goal is to reuse useful answers where the prototype already found them.

## Case-study coverage

### 4.3.1 Banzuke Division by Era

Tests:

```text
Contents = PA
Artifact = Chart
Options = no
```

Findings:

```text
simple chart PA happy path
structured ChartArtifact preferable to full Plotly JSON or page-specific JS
stacked_bar trace lowering
renderPolicy / parameters / ordering should not be dumped into provenance
```

### 6.3.1 Win Probability by Standing

Tests:

```text
Contents = PA
Artifact = Chart
Options = yes
```

Findings:

```text
chart PAs may have Options
source option selects data source
division option filters traces
error_bars option toggles evidence layer
scatter trace lowering
candidate ContentSelector / Filter distinction
```

### 7.3.1 Career Length

Tests:

```text
Contents = PASet
```

Findings:

```text
MultiViewPA maps to PASet
view option maps to PASelector
selected PA may be Chart or Table
selected PA may have its own Options
Notes remain PA-owned
```

### 2.2 Standings by Wins

Tests:

```text
Contents = PA
Artifact = Table
Options = yes
```

Findings:

```text
rich TableArtifact contract
Number of Basho selects data source / data instance
View selects visibility preset / representation
Active Rikishi Only filters rows
Division filters rows
column groups and visibility presets are table semantics
dynamic PA notes depend on visible table components
```

## Open issues for later documents

This contract deliberately leaves some issues open.

These should be tracked in the open-issues register or synthesis material rather than being solved prematurely here.

```text
1. Whether ContentSelector / Filter should become formal option roles.
2. Whether Options layout needs formal priority/complexity metadata.
3. Full URL-state and shareability policy.
4. Full chart taxonomy beyond stacked_bar and scatter.
5. Full table contract after comparison with BRB and Banzuke Changes.
6. Production asset policy for Plotly and shared JS/CSS.
7. Final Python class layout.
8. Exact migration order from CustomView/page-specific renderers to model renderer.
9. Whether any real case requires option-owned Notes.
10. Whether any real case requires PASet-level Notes.
```

## Implementation principle

The renderer should be generic where the model is generic and specific where the artifact contract is specific.

Good genericity:

```text
renderContentPanel
renderContents
renderPA
renderPASet
renderArtifact
renderNotes
```

Good artifact specificity:

```text
renderChartArtifact
renderTableArtifact
renderProseArtifact
stacked_bar lowering
scatter lowering
table visibility presets
table sort behaviour
```

Bad genericity:

```text
an over-general UI framework
widgets whose only justification is visual similarity
page-specific hacks promoted into public semantics
```

Bad specificity:

```text
one-off page renderers when the manifest contains enough semantics
page-specific JS that knows public concepts not present in the manifest
local CSS names for recurring model concepts
```

## Working conclusion

The next implementation should not preserve the old renderer.

It should preserve the useful model that the old renderer and PA manifests were implicitly working toward.

The immediate task is to write hand-made HTML/CSS/JS that realizes this explicit model:

```text
manifest JSON
  -> JS renderer
      -> semantic DOM
          -> scoped CSS
              -> rendered public analytical page
```

The old implementation remains valuable as a source of evidence, but the new implementation contract is the authority.

