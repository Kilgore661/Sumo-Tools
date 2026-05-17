# 07 UI Model Implementation Contract

## Status

This is a first implementation-facing note for the UI Model.

It is not an executable specification and it is not intended to generate the renderer automatically. The implementation will still be hand-written HTML/CSS/JS, supported by Python producer/model classes and plain JSON manifests.

The purpose of this document is to define the contracts between:

```text
UI Model
  -> Python model / producer objects
  -> manifest JSON
  -> JS renderer
  -> HTML/CSS output
```

The old renderer remains prototype evidence. It may supply useful behaviours, data shapes, edge cases, and visual expectations, but it is not the contract.

## Settled UI Model

The working model being implemented is:

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
Options do not have Notes.
Options may have help/popover text.
Notes remain part of PA.
There is no Footing.
Only PASelector is currently a named option role.
Other option effects are described, not promoted to model classes yet.
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

The manifest should be plain data. Python classes may have methods such as validation and manifest emission. JS runtime objects may have rendering and state methods.

## Contract 1: Python model to manifest

Python classes should own construction and validation. They should emit plain manifest dictionaries.

Illustrative Python shape:

```python
from dataclasses import dataclass, field
from typing import Any, Literal

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

The exact Python class layout is not settled here. The important point is that Python objects may be rich, but the emitted manifest should be simple.

## Contract 2: Contents manifest

A `ContentPanel` manifest points to exactly one `Contents` manifest.

```python
ContentPanelManifest = {
    "id": str,
    "heading": HeadingManifest,
    "contents": ContentsManifest,
}
```

A `ContentsManifest` is one of:

```python
PAManifest
PASetManifest
```

A single PA manifest:

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

A PASet manifest:

```python
PASetManifest = {
    "kind": "pa_set",
    "id": str,
    "selector": PASelectorManifest,
    "pas": list[PAManifest],
}
```

A meaningful PASet will normally contain two or more PAs, though the notation `PA+` only means one or more.

## Contract 3: Options manifest

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

`OptionControl` remains general for now:

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

A `PASelector` is special because it selects the visible PA from a PASet:

```python
PASelectorManifest = {
    "id": str,
    "label": str,
    "control": "radio" | "select" | "tabs",
    "defaultPA": str,
}
```

Other option effects are described in the producer/renderer contract for the relevant PA or artifact. They are not currently formal model classes.

## Contract 4: Artifact manifest

Artifacts are discriminated by kind:

```python
ArtifactManifest
  = ChartArtifactManifest
  | TableArtifactManifest
  | ProseArtifactManifest
```

Minimal chart artifact manifest:

```python
ChartArtifactManifest = {
    "kind": "chart",
    "renderer": "plotly",
    "data": list[DataBindingManifest],
    "layout": dict | None,
    "traces": list[dict] | None,
}
```

Minimal table artifact manifest:

```python
TableArtifactManifest = {
    "kind": "table",
    "data": DataBindingManifest,
    "columns": list[TableColumnManifest],
    "columnGroups": list[TableColumnGroupManifest],
    "defaultSort": SortSpecManifest | None,
}
```

Minimal prose artifact manifest:

```python
ProseArtifactManifest = {
    "kind": "prose",
    "html": str | None,
    "markdown": str | None,
}
```

This document does not yet finalize the chart/table/prose internals. The immediate goal is to settle the model boundary:

```text
PA owns PATitle and Notes.
Artifact owns concrete chart/table/prose rendering detail.
DataBinding tells the renderer where data comes from.
```

## Contract 5: Data binding

Data binding belongs at the manifest/producer contract boundary.

The UI Model defines that public states, selected PAs, and artifacts may require data. The producer contract defines which concrete files satisfy those requirements.

A minimal data binding shape:

```python
DataBindingManifest = {
    "id": str,
    "kind": "csv" | "json" | "inline",
    "href": str | None,
    "data": object | None,
}
```

This may need strengthening once table and chart renderers are specified.

## Contract 6: Notes

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
  | {"kind": "trace", "id": str}
  | {"kind": "source", "id": str}
```

The runtime should assemble visible notes from the selected/resolved PA state.

## Contract 7: JS renderer responsibilities

The JS renderer consumes the manifest and renders the UI model.

Top-level responsibilities:

```text
renderContentPanel(panelManifest)
renderContents(contentsManifest)
renderPASet(paSetManifest)
renderPA(paManifest)
renderOptions(optionsManifest)
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
  Options, if present or contributed by Contents/selected PA
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

## Contract 8: DOM and CSS vocabulary

The first CSS vocabulary should mirror the model.

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

Example helper classes:

```css
.ui-scroll-region {}
.ui-control-row {}
.ui-popover {}
```

Page-specific classes should be avoided unless explicitly justified.

## First test case: 4.3.1 Banzuke Division by Era

This is the simplest useful PA test.

Model classification:

```text
ContentPanel
  = Heading + Contents

Contents
  = PA

PA
  = PATitle + Chart Artifact
```

No model-level options are currently required.

No PASet is required.

No table renderer is required.

### Expected model instance

```text
ContentPanel
  Heading
    Head: Banzuke Division by Era
    SubHead: Historical banzuke division structure by era.

  Contents
    PA
      PATitle
        PAHead: Average banzuke composition by era
        PASubHead: Average banzuke composition by division (1958-2026), 10-year era buckets except the final bucket.

      Artifact
        Chart
```

### Example manifest sketch

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
      "data": [
        {
          "id": "banzuke_division_by_era_data",
          "kind": "json",
          "href": "data/banzuke_division_by_era.json"
        }
      ],
      "layout": null,
      "traces": null
    },
    "notes": []
  }
}
```

The exact data path and whether the Plotly spec is stored as JSON, traces/layout, or producer-specific data remains to be checked against the existing PA manifest work.

### Expected DOM skeleton

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

### What this test proves

This first slice should prove only:

```text
manifest loading
ContentPanel rendering
Heading rendering
Contents = PA rendering
PATitle rendering
Chart artifact mount
model-aligned CSS scopes
```

It should not try to solve:

```text
PASet
Options
Table rendering
Dynamic notes
URL-state complexity
```

## Second test case: 6.3.1 Win Probability by Standing

This should be the next chart test because it adds model-level options to a chart PA.

It should prove:

```text
PA options
OptionGroup rendering
chart state changes from options
data/source switching
trace filtering
evidence/display toggle for error bars
```

## Third test case: 7.3.1 Career Length

This should test `Contents = PASet`.

It should prove:

```text
PASet
PASelector
selected PA rendering
selected-PA-specific options
mixed chart/table PAs
```

## Fourth test case: 2.2 Standings by Wins

This should be the rich table stress test.

It should prove:

```text
Table artifact renderer
column groups
row filtering
view selection implemented by column visibility
column popovers
dynamic PA notes based on visible columns
```

## Next reconciliation task

Before writing much new renderer code, map existing PA manifest classes to this contract.

```text
Existing PA manifest term
  -> model/contract role
  -> keep/adapt/replace
```

Likely mappings to inspect:

```text
MultiViewPA   -> PASet?
ChartPA       -> PA with Chart Artifact?
TablePA       -> PA with Table Artifact?
EssayPA       -> PA with Prose Artifact?
Option        -> OptionControl?
Note          -> PA Note?
DataSource    -> DataBinding?
```

The goal is not to preserve the existing code, but to reuse useful answers where the prototype already found them.

