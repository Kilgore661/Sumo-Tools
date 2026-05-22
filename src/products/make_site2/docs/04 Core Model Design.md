# 04 Core Model Design

## Status

Initial umbrella design document for the core models of `make_site2`.

This document is intentionally short. It does not define every model field or
implementation class. Its purpose is to identify the main model layers, their
ownership boundaries, and the transformations between them.

Detailed model design lives in the companion documents:

```text
04.1 Site Model Design.md
04.2 Publication Plan Model Design.md
04.3 UI Model Design.md
04.4 Artifact Model Design.md
```

---

# 1. Purpose

`make_site2` is designed around explicit model transformations.

The core pipeline is:

```text
SiteDefinition
  -> PublicationPlan
  -> UIModel
  -> RenderedSite
```

Each stage has a distinct responsibility.

The purpose of the core model design is to keep these stages separate so that
public-site structure, publication planning, UI structure, and artifact rendering
do not collapse into one ad hoc rendering procedure.

---

# 2. Model Layers

The core design has four model layers.

```text
Site Model
  declared public intent

Publication Plan Model
  resolved build/publication plan

UI Model
  semantic structure of the public interface

Artifact Model
  analytical objects displayed inside UI Model slots
```

These layers are related but not interchangeable.

A `PageDefinition` is not a `PlannedPage`.

A `PlannedPage` is not a `ContentPanel`.

A `PA` slot is not the same thing as the concrete table, chart, prose, or custom
artifact rendered inside it.

---

# 3. Site Model

The Site Model describes what the public site claims to contain.

It owns declared public intent:

```text
SiteDefinition
NavigationTree
NavigationNode
PageRegistry
PageDefinition
PageStatus
GlobalAsset
BuildDefaults
```

The Site Model answers:

```text
What pages exist?
What is the public navigation structure?
Which pages are promoted, candidate, research, diagnostic, legacy, superseded,
or excluded?
What global assets or defaults belong to the site?
```

The Site Model does not resolve public deep-link representation, dependencies,
rendered output, or artifact internals.

Detailed design:

```text
04.1 Site Model Design.md
```

---

# 4. Publication Plan Model

The Publication Plan Model describes what a particular build will publish.

It owns resolved build structure:

```text
PublicationPlan
PlannedPage
PublicSelectionReference
PublicSelectionTable
DependencySet
ResolvedAsset
ResolvedData
ResolvedArtifactInput
```

The Publication Plan Model answers:

```text
Which declared pages are included in this build?
Where will each page be published?
Which artifact inputs, data, and assets are required?
Which pages are explicitly excluded or non-promoted?
```

The Publication Plan Model is derived from the Site Model and build context.

It does not render HTML and does not decide UI layout.

Detailed design:

```text
04.2 Publication Plan Model Design.md
```

---

# 5. UI Model

The UI Model describes the semantic structure of the public interface before it
is rendered.

It owns:

```text
PublicSiteUI
Sidebar
Navigation
ContentPanel
Heading
Contents
G1Contents
FilterSection
Filter
PA slot
Note ownership
```

The UI Model answers:

```text
What does the user interface structurally contain?
What is the selected page's ContentPanel?
What flat G1 filters are visible?
What PA slot is being shown?
Where do notes belong?
```

The UI Model does not write HTML/CSS/JS.

It is the model consumed by the UI Renderer.

Detailed design:

```text
04.3 UI Model Design.md
```

---

# 6. Artifact Model

The Artifact Model describes the analytical object displayed inside a PA slot.

It owns concrete artifact contracts:

```text
PA
Artifact
TableArtifact
IndexedTableArtifact
ChartArtifact
SectionedTableArtifact
ProseArtifact
CustomArtifact
ArtifactRenderer
```

The Artifact Model answers:

```text
What kind of analytical object is displayed?
What data does it consume?
What renderer kind does it require?
What labels, columns, traces, notes, or provenance are artifact-specific?
Which behavior belongs inside the artifact rather than the surrounding page?
```

The Artifact Model is deliberately below the UI Model.

A custom artifact renderer may be necessary, but it renders only the artifact
slot. It does not own the page shell, navigation, public page-selection semantics, Heading, or surrounding
ContentPanel structure.

Detailed design:

```text
04.4 Artifact Model Design.md
```

---

# 7. Core Transformations

The preferred design style is to understand the package as a sequence of typed
transformations.

At design level, the important transformations are:

```python
def make_publication_plan(
    site_definition: SiteDefinition,
    build_config: BuildConfig,
) -> PublicationPlan:
    ...


def make_ui_model(
    publication_plan: PublicationPlan,
) -> UIModel:
    ...


def render_ui_model(
    ui_model: UIModel,
    render_config: RenderConfig,
) -> RenderedSite:
    ...


def write_output(
    rendered_site: RenderedSite,
    output_config: OutputConfig,
) -> BuildOutput:
    ...
```

These signatures are design contracts, not final implementation commitments.

They express the intended flow:

```text
declared public site
  -> resolved publication plan
  -> semantic UI structure
  -> rendered static site
  -> build output tree
```

---

# 8. Boundary Between UI Model and Artifact Model

The boundary between the UI Model and the Artifact Model is central.

The UI Model owns the surrounding structure:

```text
ContentPanel
Heading
Filters
PA placement
Note ownership
```

The Artifact Model owns artifact internals:

```text
table rows and columns
chart traces and axes
indexed-table loading
sectioned-table layout
custom artifact rendering
artifact-specific labels
artifact-specific provenance
```

This boundary prevents page-specific artifact needs from redefining the entire
page.

Example:

```text
A Banzuke Changes table may need a custom artifact renderer.
That renderer may own banzuke-shaped table internals.
It may not own the page shell, public page-selection semantics, navigation, or ContentPanel grammar.
```

---

# 9. Boundary Between Site Model and Publication Plan

The Site Model is declarative.

The Publication Plan is resolved.

For example:

```text
Site Model:
  Page "Basho Results" exists under a navigation node.

Publication Plan:
  Page "Basho Results" is included in this build with a concrete public
  selection/deep-link reference and artifact-input/data/asset dependencies.
```

This distinction prevents public intent from being confused with build mechanics.

---

# 10. Boundary Between Publication Plan and UI Model

The Publication Plan says what will be published.

The UI Model says what interface structure will be rendered.

For example:

```text
Publication Plan:
  PlannedPage has a stable public selection/deep-link reference and references a
  BRB artifact input.

UI Model:
  Page resolves to G1 contents with a Heading, FilterSection, indexed-table PA,
  and relevant notes.
```

This is the main design seam between build planning and rendering.

---

# 11. Relationship to Existing Evidence

The existing `make_site` package and the previous UI-model experiment are useful
evidence.

They may inform:

```text
required pages
navigation shape
known page types
producer output realities
runtime and styling pressure points
G1 grammar and deferred richer-model pressure
```

They are not design authority for `make_site2`.

`make_site2` is specified and designed afresh.

Code may be copied or adapted only after deciding that the copied code implements
a responsibility that still exists in the new design.

---

# 12. What This Document Does Not Settle

This umbrella document does not settle:

```text
exact Python class definitions
exact field names
site-facing input storage format
JSON versus Python dataclasses
CSS class names
JavaScript module structure
producer-specific artifact schemas
deployment commands
```

Those decisions belong in later design documents or implementation work.

---

# 13. Summary

The core model design separates four concerns:

```text
Site Model:
  what the public site declares

Publication Plan Model:
  what this build will publish

UI Model:
  what interface structure will be rendered

Artifact Model:
  what analytical object appears inside the UI structure
```

The rest of `make_site2` should preserve this separation.

The renderer should consume the UI Model.

The output writer should consume rendered output.

Artifact renderers should remain inside artifact slots.

No promoted page should bypass these model layers by jumping directly from page
declaration to custom HTML.
