# 01 Public Site Model

## Status

Canonical conceptual model for `src.products.make_site`.

This document replaces the scattered conceptual material formerly spread across
public-site requirements, specifications, design notes, UI grammar drafts, PA
manifest notes, and semantic-methodology notes.

It defines what the public site *is*. `02 Rendering Model.md` defines how that
model is realized by the standard renderer. `06 UI Model Implementation
Contract.md` defines the implementation-facing contract between the model,
producer objects, manifests, the JS renderer, and HTML/CSS output.

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

The docs therefore describe a publication model:

```text
site
  navigation
  pages
    content panel
      heading
      options
      contents
        published artefact or selectable set of published artefacts
```

The aim is to make explicit:

- semantic categories;
- ownership boundaries;
- admissible composition;
- public-page contracts;
- producer responsibilities;
- renderer responsibilities;
- and stable analytical presentation conventions.

The useful questions are of the form:

```text
What is a Site?
What is Navigation?
What is a Page?
What is a ContentPanel?
What are Contents?
What is an Option?
What is a Published Artefact?
What is a PASet?
What is a Chart?
What is a Table?
What is a Note?
What owns headings, labels, controls, notes, and provenance?
```

These are questions about responsibility, structure, composition, and
realization.

---

# Non-Goals

The model is intentionally constrained.

It is not intended to become:

- a universal UI framework;
- a dynamic analytical application server;
- a generalized frontend component system;
- an executable UI language;
- or a replacement for producer analysis code.

The system should formalize only those distinctions that repeatedly prove
semantically stable and operationally useful.

---

# Site

A public site has:

- a site title;
- a subject-led navigation tree;
- a registry of renderable pages;
- shared static assets;
- generated output suitable for local and remote deployment.

The site definition describes the intended public structure.

It is distinct from:

- runtime UI state, such as selected division or selected source;
- build configuration, such as output or deployment locations;
- legacy/prototype artefact layout;
- incidental filenames produced by analysis packages.

When there is tension, the site definition is authoritative. Existing artefacts
may be included only when they conform to the public-site definition or are
clearly marked as prototype/legacy inclusions.

---

# Publication Model

The core public UI model is:

```text
PublicUI = Sidebar + ContentPanel

Sidebar = Caption + Navigation + Hider

ContentPanel = Heading + Options? + Contents

Contents = PA | PASet

PASet = PASelector + PA+

PA = PATitle? + Artifact + Notes?

PATitle = PAHead + PASubHead?

Artifact = Chart | Table | Prose

Options = OptionGroup+

OptionGroup = label? + OptionControl* + OptionGroup*
```

The `Sidebar` is the persistent site shell structure. It contains site identity,
the navigation tree, and a visibility control for hiding or showing the Sidebar.

Clicking a navigation node selects a page. The selected page is rendered in the
`ContentPanel`.

A selected page follows the same conceptual structure:

```text
Heading + Options? + Contents
```

where:

- `Heading` is page/content-level identity and immediate framing;
- `Options`, when present, are reader-visible state for the page, contents,
  selected PA, or artifact;
- `Contents` is what the `ContentPanel` displays;
- `Contents` may be a single `PA` or a selectable `PASet`;
- `PASet`, when present, contains a `PASelector` and one or more selectable PAs;
- `PA` is the published analytical thing being shown;
- `PATitle`, when present, is artefact-level framing;
- `Artifact` is the chart, table, or prose object being displayed;
- `Notes`, when present, explain or qualify the PA or relevant visible parts of
  its artifact.

The options set may be empty. A non-interactive page is still treated as having
no visible `Options`.

The title/framing ownership hierarchy is:

```text
Caption:
    site identity

Navigation label:
    short locator inside the navigation tree

Heading:
    page/content identity and framing

PATitle:
    PA identity and framing

Artifact:
    owns no publication caption/title
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

The Hider is not an Option. Options affect how the current contents or PA are
viewed. The Hider affects how the site shell itself is realized.

---

# Navigation

Navigation represents the semantic structure of the publication space.

It is a component of the Sidebar, not the whole Sidebar.

Navigation is a rooted labelled tree. A navigation node has:

- a human-facing label;
- a stable slug or key;
- zero or more child nodes;
- optionally, a page reference;
- optionally, status/readiness/depth metadata.

A navigation node need not be a page. Organising nodes may exist only to group
related public subjects.

Important distinctions include:

- labels vs links;
- page nodes vs grouping nodes;
- active vs inactive nodes;
- subject hierarchy vs visual indentation;
- public routes vs legacy file paths.

Routes should be stable public paths derived from the navigation tree and page
registry, not from incidental source filenames.

Navigation is organised primarily by subject, not by user type. Reader expertise
should be handled by page framing, defaults, progressive disclosure, filters,
tabs, notes, and optional detail rather than by making “expert” a top-level
navigation area.

## NavLabel

A navigation label is a locator.

Requirement:

```text
short enough for navigation
```

A `NavLabel` may be compressed and may be somewhat unclear if unavoidable. It is
not responsible for fully explaining the page.

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

- a stable id;
- a human-facing navigation placement;
- a page/content heading or framing text;
- an optional options model;
- contents;
- data dependencies;
- static asset dependencies;
- public status/readiness metadata.

A page owns page-level identity and organization. Charts, tables, prose
artefacts, embeds, or sections inside the page should not silently assume
ownership of page-level concerns. Artefact-level framing belongs to `PATitle`
rather than to the `Artifact` itself.

A typical page contains:

```text
Page
  Heading
  Options?
  Contents
  page-level status/provenance where needed
```

---

# ContentPanel

The ContentPanel is the semantic region where the selected page is presented.

It is responsible for organizing:

- page/content heading;
- page summary or immediate framing;
- reader-visible options;
- contents;
- PAs and PA sets;
- PATitles;
- charts;
- tables;
- prose;
- notes;
- metadata;
- provenance;
- and embedded/prototype material.

The ContentPanel should not be treated as an undifferentiated container of visual
widgets. Its structure expresses the page’s analytical organization.

The ContentPanel displays exactly one `Contents` object:

```text
ContentPanel = Heading + Options? + Contents

Contents = PA | PASet
```

---

# Heading

A Heading is content/page-level framing.

```text
Heading = Head + SubHead?
```

Requirement:

```text
enough page-level framing for the reader to understand what they selected
and why the major options, default column headings, or default chart traces exist
```

The `Head` should ideally be concise. If more context is needed, use `SubHead`.

A Heading is distinct from:

- site identity, owned by Caption;
- navigation labels, owned by Navigation;
- PA framing, owned by PATitle;
- artifact-internal labels, owned by the Artifact.

---

# Contents

`Contents` is the model-level thing selected by a navigation node and displayed
in the `ContentPanel`.

```text
Contents = PA | PASet
```

A single PA is the familiar case.

A PASet is a set of named PAs, with a selector choosing which PA is currently
visible.

The important relationship is:

```text
Navigation node
  -> ContentPanel
      -> Contents
          -> selected/resolved PA
              -> Artifact
```

The concrete Artifact remains one of:

```text
Chart | Table | Prose
```

but the thing selected by the navigation node may be richer than a single
artifact.

---

# Options

Options are state, not widgets.

An option definition records:

- stable id;
- label;
- allowed values where applicable;
- default;
- whether it participates in URL state where relevant;
- optional help/popover text;
- optional presentation hints.

The renderer chooses controls from the option model.

Examples:

- booleans may render as checkboxes or toggles;
- exactly-one choices may render as radio groups, segmented controls, tabs, or
  dropdowns;
- zero-or-more choices may render as checkboxes, menus, or dropdowns;
- numeric values may render as suitable numeric controls.

Default state need not always be spelled out in a URL. Non-default state should
be serialisable into the page URL when it affects shareable page meaning.

Options are organized as:

```text
Options = OptionGroup+

OptionGroup = label? + OptionControl* + OptionGroup*
```

An OptionControl may:

- select a PA from a PASet;
- select a data source or data instance;
- select a representation/view;
- filter rows or traces;
- toggle displayed evidence or uncertainty;
- toggle display of a derived table/chart feature.

These effects are descriptive for now. The only special option role currently
formalized is `PASelector`, because it is structurally required by `PASet`.

## Option help versus Notes

Options do not have Notes.

Option controls may have help or popover text, but that is not `Notes` in the PA
model sense.

The rule is:

```text
Popover/help text may explain an option.
Notes belong to the PA.
```

If a future option needs persistent explanation that is not adequately handled by
help/popover text, that will be a concrete model pressure point.

---

# PASet

A PASet is Contents containing multiple named PAs, with a public selector
choosing which PA is visible.

```text
PASet = PASelector + PA+
```

The selected PA may be a chart, table, or prose PA. The selected PA may have its
own options.

The control used to choose a PA is not semantically decisive. It might render as
radio buttons, tabs, a dropdown, or another control.

The model-level point is that a public option selects one PA from a set.

Existing `MultiViewPA`-style material is best understood as an implementation
precursor to `PASet`.

---

# PASelector

A PASelector is the selector required by a PASet.

It chooses which PA is currently visible.

Examples:

```text
Career Length:
  View = Distribution | PMF | CDF | Survival | Longest
```

A PASelector is a special case of a content-selecting option, but the model does
not yet introduce a full taxonomy of option roles.

Changing the selected PA may change the available selected-PA options.

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

A PA may be displayed directly as `Contents`, or it may be one selectable PA
inside a `PASet`.

A PA may include optional artefact-level framing through `PATitle`. This is
useful when a page Heading remains stable but Options change which Artifact is
shown, or when the selected Artifact needs its own framing distinct from the
page Heading.

The Artifact itself does not own a publication caption or title. If a chart,
table, or prose artefact needs public framing, that framing is supplied by
`PATitle`.

Supported target kinds include:

```text
static-html
data-table
data-chart
multi-view / PASet
essay/prose
```

A PA manifest describes what the public renderer needs in order to show the
artefact. It is not itself the rendered HTML.

At minimum, a PA manifest records:

- stable id;
- manifest class or artifact kind;
- renderer id or renderer kind;
- data sources;
- options consumed by the PA or artifact;
- default state relevant to the PA;
- optional PATitle or artefact framing metadata;
- notes/caveats;
- provenance;
- validation requirements.

Target PA classes currently include:

- `TablePA`;
- `IndexedTablePA`;
- `ChartPA`;
- `MultiViewPA` / `PASet`;
- `EssayPA`.

`ExcludedPA` may be used as a marker for active navigation items that remain
outside the direct PA architecture.

---

# PATitle

PATitle provides PA-level framing for the currently displayed Artifact.

It is distinct from:

- site identity, owned by Caption;
- navigation labels, owned by Navigation;
- page/content identity, owned by Heading;
- internal labels owned by the Artifact.

PATitle has the form:

```text
PATitle = PAHead + PASubHead?
```

Requirement:

```text
the PA plus its heading/subheading should be copy-pasteable
as a largely self-contained analytical object
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

Artifacts do not own publication captions or titles. Any title-like or
caption-like public framing inside a chart/table/prose artifact is
non-conforming unless it is part of the artifact's internal syntax rather than
publication framing.

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

If meaning cannot be made clear inside the label itself, use help/popovers and
PA Notes rather than bloating artifact labels.

---

# Tables

Tables are semantic analytical presentations of structured information.

A table is not merely a dataframe dump or HTML table element.

Important distinctions include:

- raw data vs analytical table;
- semantic columns vs visual columns;
- identifiers vs metrics vs labels vs status values;
- table-local controls vs page-level controls;
- diagnostic tables vs public explanatory tables;
- navigational tables vs analytical result tables.

A table manifest may define:

- data sources;
- columns;
- column groups;
- group visibility;
- visibility presets;
- row filters;
- sorting policy;
- notes;
- provenance;
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

- analytical meaning;
- traces or series;
- axes;
- axis labels;
- legends;
- hover text;
- annotations;
- options;
- notes;
- provenance;
- supporting data sources;
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

The older term `multi-view artefact` corresponds to the model-level idea of a
`PASet` when the views are selectable PAs.

A PASet presents one selected PA from a structured set.

The model should distinguish between:

- the PASet;
- the PASelector that chooses the selected PA;
- the selected PA;
- options owned by the selected PA;
- URL state needed to share the selected PA;
- notes owned by the selected PA.

Selection UI should make the available alternatives clear without pretending
that diagnostic stages are public concepts unless they have been promoted.

---

# Essays and Prose

Some public pages are primarily explanatory rather than tabular or graphical.

Essay/prose pages may include:

- Markdown or structured prose;
- embedded charts or tables;
- method explanation;
- public research narrative;
- glossary-like material;
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

- what data files exist;
- how the analysis is computed;
- what columns, traces, or labels mean;
- which options are meaningful;
- page-specific notes and caveats;
- provenance.

`make_site` owns the public-site contract:

- navigation;
- public routes;
- page chrome;
- shared renderer behavior;
- option widgets;
- shared styling;
- URL state conventions;
- validation of site-facing manifests;
- link behavior.

The boundary is additive. Producers may continue writing existing standalone
outputs, diagnostics, CSVs, reports, and debug artefacts. Promotion to the public
site means adding intentional site-facing outputs, not deleting old outputs.

---

# Notes and Provenance

Notes are semantic annotation structures.

For the core PA model:

```text
PA = PATitle? + Artifact + Notes?
```

Notes belong to the PA.

A PA note may pertain to:

- the PA as a whole;
- a table column;
- a column group;
- a visibility preset;
- a chart trace;
- a data source;
- another visible artifact component.

Options may affect which notes are relevant by changing selected content or
visible artifact state. This does not make them option notes.

Examples:

```text
note -> column
  shown when the column is visible or relevant

note -> trace
  shown when the trace is visible or relevant

note -> source
  shown when the source is selected
```

Provenance should distinguish public explanatory metadata from internal
diagnostic history. Not every internal stage should become public terminology.

Where provenance is important for interpretation, it should be represented in
PA notes, metadata, method material, or another explicit public-site structure,
not hidden in implementation filenames.

---

# Public Naming and Status

Public pages need stable names and routes.

Internal diagnostic names should not leak into public semantics unless they are
explicitly promoted.

For example, Equelo diagnostic stage names such as `v0`, `v1`, etc. are local
audit-stage names, not public model names. Public wording should use canonical
model or artefact names with semantic force.

Public status/readiness metadata may be used to distinguish:

- canonical public pages;
- work-in-progress pages;
- prototype embeds;
- diagnostic pages;
- legacy inclusions;
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
ContentPanel comprises:
    Heading
    optional Options
    Contents
```

```text
Contents is either:
    PA
    PASet
```

```text
A table column may have semantic role: metric, identifier, label, status, delta.
```

The semantic layer defines:

- entities;
- composition;
- ownership;
- invariants;
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
PATitle renders as PA-level framing when the PA requires it.

Notes render according to PA ownership and renderer layout policy.
```

```text
Options render at the smallest semantic scope that owns the affected state.
```

The rendering layer defines:

- layout;
- interaction conventions;
- presentation rules;
- responsive behavior;
- and visual realization strategies.

The renderer should preserve semantic structure and ownership relationships
rather than obscure or replace them.

---

# Ownership

Ownership boundaries are central to the system.

Repeated friction usually indicates implicit or confused ownership:

- who owns the navigation label;
- who owns the Heading;
- who owns PATitle;
- who owns controls;
- who owns notes;
- who owns legends;
- who owns provenance;
- who owns URL state;
- who owns links;
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

- prose;
- algebraic signatures;
- grammar-like notation;
- predicates/invariants;
- admissible composition rules;
- canonical rendering descriptions.

For example:

```text
make_PublicUI : Sidebar × ContentPanel -> PublicUI
make_Sidebar : Caption × Navigation × Hider -> Sidebar
make_ContentPanel : Heading × Options? × Contents -> ContentPanel
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
- What are the selected page's Contents?
- Are the Contents a PA or a PASet?
- If a PASet is present, what is the PASelector?
- Is this option page-level, contents-level, PA-level, selected-PA-level, or
  artifact-level?
- Is this note owned by the selected PA?
- What artifact component does this note pertain to?
- Is this table a public analytical table or a diagnostic data dump?
- Is this chart a public artefact or a prototype embed?
- Does this producer emit intentional site-facing inputs?
- Does the renderer preserve the semantic hierarchy?

These are specification questions, not merely implementation questions.

---

# Relationship to Implementation

The public-site model may influence:

- Python data structures;
- manifest classes;
- producer writer contracts;
- renderer APIs;
- Jinja templates;
- CSS organization;
- validation tooling;
- URL handling;
- builder architecture.

However, executable realization is not the primary purpose of this document.

The immediate goal is:

```text
make implicit semantic structure explicit
```

so that rendering decisions become discussable, inconsistencies become
identifiable, and future implementation abstractions emerge from stable
semantics rather than accidental implementation patterns.

`06 UI Model Implementation Contract.md` describes the implementation-facing
contract for manifests, JS rendering, and DOM/CSS realization.

---

# Current Direction

The current architectural direction emphasizes:

- subject-led public navigation;
- stable public pages and routes;
- explicit page/content grammar;
- intentional PA manifests;
- clear producer/site-builder ownership;
- semantic options rather than arbitrary widgets;
- explicit PA notes and provenance;
- renderer consistency;
- and constrained specification-first thinking.

The model should be judged by whether it clarifies public-site meaning, reduces
ambiguity, supports coherent analytical publication, and keeps implementation
abstractions grounded in durable project semantics.
