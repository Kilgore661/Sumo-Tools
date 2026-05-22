# 01 Public Site Model

## Status

Canonical conceptual model for `src.products.make_site`.

This document replaces the scattered conceptual material formerly spread across
public-site requirements, specifications, design notes, UI grammar drafts, PA
manifest notes, and semantic-methodology notes.

It defines what the public site *is*.  `02 Rendering Model.md` defines how that
model is realized by the standard renderer.

---

# Purpose

The public site exists to make professional sumo more legible through curated,
public-facing analytical outputs.

It should present selected analysis, explanatory tools, research narratives,
tables, charts, and method material in a coherent public structure.

It should not publish every artefact the repository can generate merely because
that artefact is browser-readable. Raw downloads, parser diagnostics, warning
reports, cache files, source-data archives, stale experiments, and internal audit
outputs are not public-site content unless deliberately promoted.

The system is best understood as:

```text
a constrained semantic publication system
for analytical public sites
```

The central architectural problem is semantic before it is technical:

```text
What are the stable semantic categories
of the publication system?
```

---

# Core View

The public site is a generated analytical publication, not a generic web app or
a frontend framework.

The docs therefore describe a publication grammar:

```text
site
  navigation
  pages
    heading
    options
    published artefact
```

The aim is to make explicit:

- semantic categories,
- ownership boundaries,
- admissible composition,
- public-page contracts,
- producer responsibilities,
- renderer responsibilities,
- and stable analytical presentation conventions.

The useful questions are of the form:

```text
What is a Site?
What is a Page?
What is Navigation?
What is an Option?
What is a Published Artefact?
What is a Chart?
What is a Table?
What is a Note?
What owns titles, controls, notes, and provenance?
```

These are questions about responsibility, structure, composition, and
realization.

---

# Non-Goals

The model is intentionally constrained.

It is not intended to become:

- a universal UI framework,
- a dynamic analytical application server,
- a generalized frontend component system,
- an executable UI language,
- or a replacement for producer analysis code.

The system should formalize only those distinctions that repeatedly prove
semantically stable and operationally useful.

---

# Site

A public site has:

- a site title,
- a subject-led navigation tree,
- a registry of renderable pages,
- shared static assets,
- generated output suitable for local and remote deployment.

The site definition describes the intended public structure.

It is distinct from:

- runtime UI state, such as selected division or selected source,
- build configuration, such as output or deployment locations,
- legacy/prototype artefact layout,
- incidental filenames produced by analysis packages.

When there is tension, the site definition is authoritative. Existing artefacts
may be included only when they conform to the public-site definition or are
clearly marked as prototype/legacy inclusions.

---

# Publication Grammar

The core public UI model is:

```text
PublicUI = Sidebar × ContentPanel

Sidebar = Caption + Navigation + Hider

ContentPanel = Heading + Options + Published Artefact

Published Artefact = PATitle? + Artifact + Notes?

PATitle = PAHead + PASubHead?

Artifact = Chart | Table | Prose
```

The `Sidebar` is the persistent site shell structure.  It contains site identity,
the navigation tree, and a visibility control for hiding or showing the Sidebar.

Clicking a navigation node selects a page. The selected page is rendered in the
ContentPanel.

Every selected page follows the same conceptual grammar:

```text
Heading + Options + Published Artefact
```

Where:

- `Heading` is page-level identity and immediate framing.
- `Options` are reader-visible state for the page or artefact.
- `Published Artefact` is the analytical thing being shown.
- `PATitle`, when present, is artefact-level framing.
- `Artifact` is the chart, table, or prose object being displayed.
- `Notes`, when present, explain or qualify the Artifact.

The options set may be empty. A non-interactive page is still treated as a page
with:

```text
Options = empty
```

This keeps the page grammar uniform.

The title ownership hierarchy is:

```text
Caption:
    site identity

Heading:
    page identity

PATitle:
    artefact identity

Artifact:
    owns no caption/title
```

---

# Sidebar

The Sidebar is the site-shell structure that normally appears alongside the
ContentPanel.

It is not identical to Navigation.

```text
Sidebar = Caption + Navigation + Hider
```

## Caption

The Caption represents site identity, publication identity, or installation
identity. It does not represent the current page or current artefact.

## Hider

The Hider is a UI-shell visibility control that hides, collapses, or restores
the Sidebar.

The Hider is not an Option. Options affect how the current PA is viewed. The
Hider affects how the site shell itself is realized.

---

# Navigation

Navigation represents the semantic structure of the publication space.

It is a component of the Sidebar, not the whole Sidebar.

Navigation is a rooted labelled tree. A navigation node has:

- a human-facing label,
- a stable slug or key,
- zero or more child nodes,
- optionally, a page reference,
- optionally, status/readiness/depth metadata.

A navigation node need not be a page. Organising nodes may exist only to group
related public subjects.

Important distinctions include:

- labels vs links,
- page nodes vs grouping nodes,
- active vs inactive nodes,
- subject hierarchy vs visual indentation,
- public routes vs legacy file paths.

Routes should be stable public paths derived from the navigation tree and page
registry, not from incidental source filenames.

Navigation is organised primarily by subject, not by user type. Reader expertise
should be handled by page framing, defaults, progressive disclosure, filters,
tabs, notes, and optional detail rather than by making “expert” a top-level
navigation area.

---

# Pages

A Page is a semantic publication unit.

It is not merely:

```text
an HTML file
```

or:

```text
a route
```

A page has:

- a stable id,
- a human-facing title,
- a summary or framing text,
- an optional options model,
- a body/view specification,
- data dependencies,
- static asset dependencies,
- public status/readiness metadata.

A page owns page-level identity and organization. Charts, tables, prose artefacts, embeds, or
sections inside the page should not silently assume ownership of page-level
concerns. Artefact-level framing belongs to PATitle rather than to the Artifact
itself.

A typical page contains:

```text
Page
  title
  summary/framing
  options
  sections or artefacts
  notes/provenance
```

---

# ContentPanel

The ContentPanel is the semantic region where the selected page is presented.

It is responsible for organizing:

- page title,
- page summary,
- page-level options,
- sections,
- PAs,
- PATitles,
- charts,
- tables,
- prose,
- notes,
- metadata,
- provenance,
- and embedded/prototype material.

The ContentPanel should not be treated as an undifferentiated container of
visual widgets. Its structure expresses the page’s analytical organization.

---

# Options

Options are state, not widgets.

An option definition records:

- stable id,
- kind,
- label,
- allowed values where applicable,
- default,
- whether it participates in URL state,
- optional presentation hints.

The renderer chooses controls from the option model.

Examples:

- booleans may render as checkboxes or toggles,
- exactly-one choices may render as radio groups, segmented controls, tabs, or dropdowns,
- zero-or-more choices may render as checkboxes, menus, or dropdowns,
- numeric values may render as suitable numeric controls.

Default state need not always be spelled out in a URL. Non-default state should
be serialisable into the page URL when it affects shareable page meaning.

---

# Published Artefacts

A Published Artefact, or PA, is the analytical object a public page presents.

The core PA grammar is:

```text
PA = PATitle? + Artifact + Notes?

PATitle = PAHead + PASubHead?

Artifact = Chart | Table | Prose
```

A PA is a renderer contract, not necessarily a physical HTML file.

The PA may include optional artefact-level framing through `PATitle`.  This is
useful when a page heading remains stable but Options change which Artifact is
shown, or when the selected Artifact needs its own caption distinct from the
page heading.

The Artifact itself does not own a caption or title. If a chart, table, or prose
artefact needs framing, that framing is supplied by `PATitle`.

Supported target kinds include:

```text
static-html
data-table
data-chart
multi-view
essay/prose
```

A PA manifest describes what the public renderer needs in order to show the
artefact. It is not itself the rendered HTML.

At minimum, a PA manifest records:

- stable id,
- manifest class,
- renderer id,
- data sources,
- options consumed by the PA,
- default state relevant to the PA,
- optional PATitle or artefact framing metadata,
- notes/caveats,
- provenance,
- validation requirements.

Target PA classes currently include:

- `TablePA`,
- `IndexedTablePA`,
- `ChartPA`,
- `MultiViewPA`,
- `EssayPA`.

`ExcludedPA` may be used as a marker for active navigation items that remain
outside the direct PA architecture.

---

# PATitle

PATitle provides artefact-level framing for the currently displayed Artifact.

It is distinct from:

- site identity, owned by Caption;
- page identity, owned by Heading;
- internal labels owned by the Artifact.

PATitle has the form:

```text
PATitle = PAHead + PASubHead?
```

PATitle may be empty. An empty PATitle means that the page Heading supplies all
needed reader-facing framing for the current PA.

---

# Artifact

An Artifact is the chart, table, or prose object displayed by a PA.

```text
Artifact = Chart | Table | Prose
```

Artifacts are opaque to the publication grammar. The grammar does not inspect
Plotly internals, table implementation details, or rendering-library structures
in order to discover public-site meaning.

Artifacts do not own captions or titles. Any title-like or caption-like public
framing inside a chart/table/prose artifact is non-conforming unless it is part
of the artifact's internal syntax rather than publication framing.

---

# Tables

Tables are semantic analytical presentations of structured information.

A table is not merely a dataframe dump or HTML table element.

Important distinctions include:

- raw data vs analytical table,
- semantic columns vs visual columns,
- identifiers vs metrics vs labels vs status values,
- table-local controls vs page-level controls,
- diagnostic tables vs public explanatory tables,
- navigational tables vs analytical result tables.

A table manifest may define:

- columns,
- column groups,
- group visibility,
- visibility presets,
- sorting policy,
- notes,
- provenance,
- validation requirements.

Tables may internally contain column headings, row labels, group labels, sorting
indicators, and other structural labels. These are internal table structure, not
publication framing.

Tables do not own captions or titles. If a table needs artefact-level framing,
it is supplied by PATitle.

Rendering consistency matters because tables communicate semantic structure.

---

# Charts

Charts are semantic analytical artefacts.

A chart is not merely a Plotly object or generated HTML file.

A chart may have:

- analytical meaning,
- traces or series,
- axes,
- axis labels,
- legends,
- hover text,
- annotations,
- options,
- notes,
- provenance,
- supporting data sources,
- rendering requirements.

Charts do not own captions or titles. If a chart needs artefact-level framing,
it is supplied by PATitle.

Plotting-library properties such as `layout.title` are implementation features,
not public-site ownership rules. If a Plotly title is being used as publication
or artefact framing, it should be removed and represented as Heading or PATitle.

Questions such as:

```text
Why does this chart have a box?
Who owns the caption?
Where do notes belong?
What does this control affect?
```

are semantic questions before they are styling questions.

---

# Multi-View Artefacts

A multi-view artefact presents one selected item from a structured set of
artefacts.

Examples might include:

- a selectable table family,
- chart variants over the same analysis,
- diagnostic stages,
- comparison views,
- grouped outputs selected by page options.

The model should distinguish between:

- the multi-view container,
- the selected child artefact,
- options owned by the container,
- options owned by the child artefact,
- and URL state needed to make a selected view shareable.

---

# Essays and Prose

Some public pages are primarily explanatory rather than tabular or graphical.

Essay/prose pages may include:

- Markdown or structured prose,
- embedded charts or tables,
- method explanation,
- public research narrative,
- glossary-like material,
- assumptions and caveats.

Even prose pages still participate in the public-site model: they have page
identity, navigation location, public status, ownership boundaries, and rendering
expectations.

---

# Static HTML and Prototype Embeds

Existing generated HTML may be included for prototypes, stress tests, or legacy
compatibility.

This is a useful inclusion path when asking:

- Does this output belong in the public information architecture?
- Does the navigation still make sense?
- Is this artefact interesting enough to promote later?

However, static/prototype inclusion is not the preferred promoted-page contract.

If an artefact becomes a real public-site page, the producer should normally add
a site-facing writer that emits intentional public-site inputs: data, metadata,
options, notes, provenance, and configuration.

The site builder should not usually parse generated HTML to recover meaning.
That would turn old HTML into an accidental API.

---

# Producer and make_site Ownership

Producer modules own analysis-specific knowledge:

- what data files exist,
- how the analysis is computed,
- what columns, traces, or labels mean,
- which options are meaningful,
- page-specific notes and caveats,
- provenance.

`make_site` owns the public-site contract:

- navigation,
- public routes,
- page chrome,
- shared renderer behavior,
- option widgets,
- shared styling,
- URL state conventions,
- validation of site-facing manifests,
- link behavior.

The boundary is additive. Producers may continue writing existing standalone
outputs, diagnostics, CSVs, reports, and debug artefacts. Promotion to the public
site means adding intentional site-facing outputs, not deleting old outputs.

---

# Notes and Provenance

Notes are semantic annotation structures.

They may include:

- explanatory commentary,
- caveats,
- interpretation guidance,
- method comments,
- provenance,
- source-data information,
- version or status information.

Ownership matters. A note may belong to:

- a page,
- a section,
- a chart,
- a table,
- a control group,
- a data source,
- or a producer output.

Rendering should preserve this ownership relationship.

Provenance should distinguish public explanatory metadata from internal
diagnostic history. Not every internal stage should become public terminology.

---

# Public Naming and Status

Public pages need stable names and routes.

Internal diagnostic names should not leak into public semantics unless they are
explicitly promoted.

For example, Equelo diagnostic stage names such as `v0`, `v1`, etc. are local
audit-stage names, not public model names. Public wording should use canonical
model or artefact names with semantic force.

Public status/readiness metadata may be used to distinguish:

- canonical public pages,
- work-in-progress pages,
- prototype embeds,
- diagnostic pages,
- legacy inclusions,
- excluded or non-target artefacts.

---

# Semantic Specification vs Rendering Contract

A fundamental distinction exists between the semantic model and the rendering
contract.

## Semantic specification

Defines what exists.

Examples:

```text
PublicUI comprises:
    Sidebar
    ContentPanel

Sidebar comprises:
    Caption
    Navigation
    Hider
```

```text
Navigation is a rooted labelled tree.
```

```text
A table column may have semantic role: metric, identifier, label, status, delta.
```

The semantic layer defines:

- entities,
- composition,
- ownership,
- invariants,
- admissible structure.

## Rendering contract

Defines acceptable realization.

Examples:

```text
The standard renderer presents Sidebar
as a site-shell region containing Caption, Navigation, and Hider.

The standard renderer presents Navigation
as a nested tree within that Sidebar or responsive equivalent.
```

```text
PATitle renders as artefact-level framing when the PA requires it.

Notes render according to PA ownership and renderer layout policy.
```

```text
Page-level controls render at page scope, not inside a single artefact.
```

The rendering layer defines:

- layout,
- interaction conventions,
- presentation rules,
- responsive behavior,
- and visual realization strategies.

The renderer should preserve semantic structure and ownership relationships
rather than obscure or replace them.

---

# Ownership

Ownership boundaries are central to the system.

Repeated friction usually indicates implicit or confused ownership:

- who owns the title or caption,
- who owns controls,
- who owns notes,
- who owns legends,
- who owns provenance,
- who owns URL state,
- who owns links,
- who owns visual grouping.

The objective is to make these boundaries explicit enough that rendering,
validation, and producer integration become discussable.

---

# Composition

Composition rules should emerge from stable semantics, not incidental visual
similarity.

A useful abstraction is one that names a real recurring semantic category.

A questionable abstraction is one that exists only because several things happen
to look similar in HTML or CSS.

The preferred direction is:

```text
formalize only the distinctions
that repeatedly prove semantically stable
```

---

# Formalism

The preferred style is semi-formal and specification-oriented.

Useful forms include:

- prose,
- algebraic signatures,
- grammar-like notation,
- predicates/invariants,
- admissible composition rules,
- canonical rendering descriptions.

For example:

```text
make_PublicUI : Sidebar × ContentPanel -> PublicUI
make_Sidebar : Caption × Navigation × Hider -> Sidebar
```

or:

```text
Navigation is a rooted labelled tree.
```

These expressions are primarily intended as specification, communication, and
conceptual clarification.

They are not necessarily intended as Python classes, parser inputs, or runtime
data structures, though implementation may later be influenced by them.

---

# Conformance Questions

The model should support questions such as:

- Does this page have a stable public identity?
- Does the navigation node represent a page or a grouping label?
- Are route names public concepts or legacy filenames?
- Is this option page-level, section-level, or artefact-level?
- Is this note owned by the page, a chart, a table, or a data source?
- Is this table a public analytical table or a diagnostic data dump?
- Is this chart a public artefact or a prototype embed?
- Does this producer emit intentional site-facing inputs?
- Does the renderer preserve the semantic hierarchy?

These are specification questions, not merely implementation questions.

---

# Relationship to Implementation

The public-site model may influence:

- Python data structures,
- manifest classes,
- producer writer contracts,
- renderer APIs,
- Jinja templates,
- CSS organization,
- validation tooling,
- URL handling,
- builder architecture.

However, executable realization is not the primary purpose of this document.

The immediate goal is:

```text
make implicit semantic structure explicit
```

so that rendering decisions become discussable, inconsistencies become
identifiable, and future implementation abstractions emerge from stable
semantics rather than accidental implementation patterns.

---

# Current Direction

The current architectural direction emphasizes:

- subject-led public navigation,
- stable public pages and routes,
- explicit page grammar,
- intentional Published Artefact manifests,
- clear producer/site-builder ownership,
- semantic options rather than arbitrary widgets,
- explicit notes and provenance,
- renderer consistency,
- and constrained specification-first thinking.

The model should be judged by whether it clarifies public-site meaning, reduces
ambiguity, supports coherent analytical publication, and keeps implementation
abstractions grounded in durable project semantics.
