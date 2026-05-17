# 02 Rendering Model

## Status

Canonical rendering model for `src.products.make_site`.

This document defines how the semantic public-site model in
`01 Public Site Model.md` should be realized by the standard renderer.

It has been updated to reflect the UI Model case studies and the implementation
contract.  In particular, the renderer now works against the following content
shape:

```text
ContentPanel
  = Heading + Options? + Contents

Contents
  = PA | PASet

PASet
  = PASelector + PA+

PA
  = PATitle? + Artifact + Notes?

Artifact
  = Chart | Table | Prose
```

The renderer is still hand-written HTML/CSS/JS.  The model is a rendering
contract, not an executable UI language.

---

# Purpose

The rendering model defines the contract between semantic public-site structures
and rendered public analytical pages.

In short:

```text
semantic publication structures
    -> rendered public analytical pages
```

The renderer should preserve:

- semantic structure;
- ownership boundaries;
- composition relationships;
- public route/page identity;
- option scope;
- notes/provenance scope;
- and artefact status.

The goal is not arbitrary frontend polish.  The goal is a renderer that makes
the publication model visible and consistent.

---

# Core Principle

Rendering is the realization of a semantic model.

The key question is not merely:

```text
How should this look?
```

but:

```text
What semantic structure is being realized here?
```

A rendering decision is good when it clarifies the underlying publication
structure.

A rendering decision is suspect when it hides or confuses:

- ownership;
- hierarchy;
- scope;
- analytical meaning;
- interaction responsibility;
- provenance;
- public status;
- or page structure.

---

# Semantic Model vs Rendering Contract

The renderer does not define the semantic model.  It realizes it.

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

Contents is one of:
    PA
    PASet

PASet comprises:
    PASelector
    one or more PAs
```

```text
PA comprises:
    optional PATitle
    Artifact
    optional Notes

Artifact is one of:
    Chart
    Table
    Prose
```

## Rendering contract

Defines how those things may be acceptably realized.

Examples:

```text
Sidebar is rendered as a persistent site-shell region.
```

```text
Navigation is rendered as a nested public structure inside the Sidebar.
```

```text
PASet renders a selector and one selected PA.
```

```text
PATitle renders as artefact-level framing when the PA requires it.
```

```text
Artifacts do not render their own public captions or titles.
```

```text
Notes render according to PA ownership and renderer layout policy.
```

The renderer must respect the semantic ownership implied by the model.

---

# Standard Page Shell

At the highest level, the standard public UI is rendered as:

```text
PublicUI
  Sidebar region
  ContentPanel region
```

On desktop-width displays, this is normally realized as:

```text
left Sidebar region
right ContentPanel region
```

Responsive layouts may collapse or move regions, but the semantic distinction
must remain.

The Sidebar region is responsible for site identity, publication navigation, and
Sidebar visibility controls.

The ContentPanel region is responsible for the active analytical page.

---

# Sidebar Rendering

The Sidebar realizes:

```text
Sidebar = Caption + Navigation + Hider
```

The standard desktop renderer should treat the Sidebar as a fixed-width vertical
site-shell region.

## Caption

Caption renders site identity.  In the current standard renderer it consists of:

```text
line 1: "Gaspode-san's"
line 2: "Sumo Lab"
line 3: deployment timestamp
```

The deployment timestamp uses the format:

```text
YYYY/MM/DD HH:MM:SS
```

Caption uses Sidebar typography and colour defaults.  The first two lines use
large site-title typography; the timestamp is visually muted.

## Hider

Hider allows the user to hide, collapse, or restore the Sidebar.

Hider is not an Option.  It affects the site shell, not the current PA state.

The Hider must not obscure Caption text, the deployment timestamp, or page
heading text.

## Sidebar overflow

The Sidebar should scroll independently when its contents exceed available
vertical space.  Scrolling the Sidebar should not scroll the ContentPanel.

---

# Navigation Rendering

Navigation renders the publication structure.

It is not merely a decorative sidebar.

The renderer should preserve the distinction between:

- hierarchy;
- labels;
- page links;
- active page state;
- collapsed or expanded groups;
- non-clickable structural headings;
- and readiness/status metadata where exposed.

Navigation is conceptually a rooted labelled tree.  Rendering should make that
tree understandable.

## Navigation nodes

| Node role | Rendering expectation |
|---|---|
| Page link | Clickable public navigation target |
| Active page link | Clickable target with active-page state |
| Section label | Non-clickable grouping label |
| Collapsible group | Expandable structural grouping |
| Leaf item | Terminal page or label |
| Prototype/legacy item | Visibly statused where appropriate |

The renderer should not collapse all node types into identical links.

## Navigation label

A navigation label is a locator, not the full explanation of a page.

Requirement:

```text
short enough for navigation
```

It may be compressed and may be somewhat unclear if unavoidable.  The content
Heading and PATitle carry the explanatory burden after navigation has selected a
page.

## Active state

The active page should be visually identifiable.

Users should be able to determine:

- where they are;
- which page is active;
- and how that page sits within the wider publication hierarchy.

## Navigation depth

Nested structure should be clear but not overwhelming.

Very deep trees should be handled through grouping, indentation, collapsibility,
or other conventions that preserve hierarchy without flooding the page.

---

# ContentPanel Rendering

The ContentPanel is the primary rendered region for analytical content.

It realizes:

```text
ContentPanel = Heading + Options? + Contents
```

The renderer should clearly distinguish:

- page/content heading;
- page/content subheading;
- page-level or content-level options;
- PASet selector, where present;
- PA framing;
- artifacts;
- notes;
- metadata;
- provenance;
- prototype/legacy embeds.

The ContentPanel should not become an undifferentiated list of visual widgets.
Its rendered structure should communicate the semantic organization of the
active page.

## Heading

Heading renders page/content-level identity and framing.

```text
Heading = Head + SubHead?
```

Requirement:

```text
enough page-level framing for the reader to understand what they selected
and why the major options, default column headings, or default chart traces exist
```

The Head should ideally be concise.  If more context is needed, use SubHead.

Heading belongs to the ContentPanel, not to the PA or Artifact.

## Options region

Options render after the Heading and before the Contents.

Options may be absent for simple pages.

When Options are present, they render the public controls that resolve or modify
the current Contents or selected PA.

Examples:

```text
Source selector for a chart
Division filter for a chart or table
View selector for a table representation
Number of Basho selector for a table data instance
PASelector for a PASet
```

## Contents region

Contents is rendered as either:

```text
PA
```

or:

```text
PASet
```

The renderer must not assume that every ContentPanel contains exactly one PA.

---

# Options Rendering

Options are reader-visible state, not merely widgets.

The standard shape is:

```text
Options
  = OptionGroup+

OptionGroup
  = label?
  + OptionControl*
  + OptionGroup*
```

Options should be rendered according to their semantic tree.

The current standard direction is:

- grouped controls;
- clear labels;
- visible scope;
- stable ordering;
- no unexplained widget clutter.

## OptionControl rendering

A control may render as:

- radio buttons;
- a dropdown/select;
- a checkbox;
- a toggle;
- segmented buttons;
- tabs.

The control type is a rendering decision.  It is not the option's semantic
meaning.

## PASelector rendering

PASelector is the selector required by:

```text
PASet = PASelector + PA+
```

It selects the visible PA from a PASet.

The prototype may render a PASelector as radio buttons, but that is not a model
rule.

Likely rendering policy:

```text
Use radio buttons when the choice set is small.
Use a dropdown when there are too many choices.
```

This may later require presentation metadata, but such metadata should not be
added until real cases require it.

## Candidate option kinds

The case studies suggest that options may divide into:

```text
ContentSelector
Filter
```

where:

```text
ContentSelector
  selects content, PA, data source, or data instance

Filter
  modifies the visible representation of already-selected content
```

This distinction is not yet adopted as a formal model taxonomy, except that
PASelector is explicitly named because PASet requires it.

For rendering, however, the distinction is useful to keep in mind:

```text
Content selectors may change what must be loaded or resolved.
Filters operate within selected/resolved content.
```

## Options layout policy

A candidate cross-case policy exists:

```text
simple / obvious / primary options at the top
gnarly / expert / advanced options at the bottom
```

Defaults should normally correspond to the simplest or most expected choices.

This is not yet a settled rendering rule.  It should be tested across optioned
case studies before becoming formal.

Do not add formal `priority`, `complexity`, or `advanced` fields until the need
is proven.

## Option help

Options do not have Notes.

Option controls may have help or popover text.

The rule is:

```text
Popover/help text may explain an option.
Notes belong to the PA.
```

If a future option needs persistent explanation that cannot be handled by help
or popover text, that will be a concrete model pressure point.

---

# Contents Rendering

Contents is the model-level thing displayed by the ContentPanel.

```text
Contents = PA | PASet
```

## Contents = PA

A single PA is rendered directly through the PA renderer:

```text
ContentPanel
  Heading
  Options?
  Contents
    PA
      PATitle?
      Artifact
      Notes?
```

This is the path exercised by:

- `4.3.1 Banzuke Division by Era`;
- `6.3.1 Win Probability by Standing`;
- `2.2 Standings by Wins`.

## Contents = PASet

A PASet renders one selected PA from a structured set.

```text
PASet
  PASelector
  PA+
```

The renderer should:

1. render PASelector as part of the Options area;
2. resolve the selected PA;
3. render any selected-PA-specific Options;
4. render the selected PA through the normal PA path.

This is the path exercised by:

- `7.3.1 Career Length`.

## Selected-PA-specific options

A selected PA may contribute its own options.

Example:

```text
Career Length
  PASelector: View = Distribution | PMF | CDF | Survival | Longest

Selected PA: Longest
  option: Show active only
```

Changing the selected PA may therefore change the available selected-PA options.

The renderer must make this scope clear.

---

# PA Rendering

A PA renders according to:

```text
PA = PATitle? + Artifact + Notes?
```

PA rendering responsibilities include:

- applying default state;
- resolving data sources as needed by the Artifact;
- rendering PATitle where supplied;
- rendering the Artifact;
- rendering PA Notes where relevant;
- applying validation rules;
- preserving public status and provenance where exposed.

Different PA classes may have different visual forms, but they should share
common ownership and page-integration conventions.

## PATitle rendering

PATitle provides artefact-level framing for the currently displayed Artifact.

```text
PATitle = PAHead + PASubHead?
```

Requirement:

```text
the PA plus its heading/subheading should be copy-pasteable
as a largely self-contained analytical object
```

PATitle belongs to the PA, not to the Artifact.

In the current standard renderer:

```text
PAHead: h4 scale
PASubHead: h5 scale
```

These are typography scales/tokens rather than mandatory HTML heading levels.

## Artifact rendering

The Artifact is rendered within the Artifact viewport allocated by the renderer.

The Artifact must not own or duplicate public captions/titles.  If public
framing is needed, it must be supplied by PATitle or ContentPanel Heading.

## Notes rendering

Notes are optional.

Notes belong to the PA.

Notes may be rendered as an ordered list of prose notes.  The Notes heading is:

```text
Notes
```

using h5 scale in the current standard renderer.

Notes may occupy a reserved region at the bottom of the PA realization.  When
that happens, Notes determine the remaining viewport available to PATitle and
Artifact.

Semantic association does not imply document-flow order: Notes belong to the
PA, but the renderer decides how to allocate space and scrolling.

---

# Notes Rendering

Notes are semantic annotation structures owned by the PA in the current model.

A note may pertain to:

- the PA generally;
- a table column;
- a column group;
- a table visibility preset;
- a chart trace;
- a chart source;
- an artifact component.

A note is rendered when its target is active, visible, selected, or otherwise
relevant to the current PA state.

Examples:

```text
note -> column
  render when the column is visible

note -> trace
  render when the trace is visible/relevant

note -> source
  render when the source is selected

note -> PA
  render whenever the PA is selected
```

Options may affect which notes appear by changing visible artifact state.

This does not make them option notes.

There is no separate Footing in the current model.

---

# Chart Rendering

Charts are semantic analytical artefacts.

A chart is not merely a Plotly object or generated HTML file.

The renderer should preserve the distinction between:

- the Chart as an analytical Artifact;
- the plotting-library figure;
- PATitle framing supplied outside the Chart;
- surrounding explanatory text;
- chart-local affordances;
- model-level Options;
- producer-specific data/config.

## Chart title ownership

Charts do not own public captions or titles.

A Plotly title or title-like annotation should not be used as publication or
artefact framing.  If such framing is needed, it belongs in Heading or PATitle.

Charts may still contain internal chart syntax such as axis labels, legend
labels, trace labels, tick labels, hover text, and annotations tied to the visual
analysis.

## Chart artifact contract

A promoted chart should normally be rendered from a structured ChartArtifact
manifest, not from page-specific JS or copied standalone Plotly HTML.

Preferred direction:

```text
structured chart artifact manifest
  -> generic chart renderer
      -> Plotly traces/layout
```

Useful chart manifest concepts include:

- data sources;
- trace definitions;
- axis metadata;
- ordering/category policy;
- render policy;
- display policy;
- parameters;
- notes/provenance.

## Chart policies

The renderer should avoid using `provenance` as a catch-all for unlike things.

Prefer distinctions such as:

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

## Chart responsiveness

Charts are responsive.

Charts are fitted to the available Artifact viewport.

Charts scale to occupy the available width and height while preserving usability
and semantic content.

Chart sizing is determined by the Artifact viewport allocated by the renderer.

## Chart controls and affordances

Plotly interaction affordances, such as zoom, pan, hover, autoscale, legend
clicking, and trace visibility, are chart/library affordances.  They are not
capital-O Options unless they represent reader-adjustable semantic state that
belongs to the page or PA contract.

Examples of model-level chart Options include:

```text
Source = observed | equelo
Division = Makuuchi | Juryo | ...
Error bars = on | off
```

## Plotly legend policy

Public Plotly charts with meaningful legends should not rely on Plotly defaults
when those defaults conflict with the public interaction contract.

Known policy:

- ordinary legend click may toggle traces;
- double-click should use site-owned isolation behaviour where needed;
- exceptions should be explicitly documented.

---

# Table Rendering

Tables are semantic analytical presentations of structured information.

A table is not merely a dataframe dump or HTML table element.

The renderer should preserve the difference between:

- raw data;
- analytical table;
- navigational table;
- diagnostic table;
- layout table.

## Table title ownership

Tables do not own public captions or titles.

If a table needs artefact-level framing, that framing belongs in PATitle.

Tables may contain internal structural labels such as column headings, row
labels, group labels, and sorting indicators.  These are internal table
structure, not publication captions/titles.

## Table artifact contract

A rich table artifact may include:

- data sources;
- columns;
- column groups;
- visibility presets;
- row filters;
- default sort;
- sort kinds;
- column help/popovers;
- formatting/alignment metadata;
- note relevance rules.

These are table artifact concerns, not top-level page-model concerns.

## Column semantics

Columns may carry semantic meaning beyond their displayed labels.

For example, a column may represent:

- identifier;
- metric;
- category;
- rank/chii;
- score;
- label;
- status;
- delta;
- link target;
- explanatory text.

Stable column-level styling and behavior should follow recurring semantics, not
one-off formatting preference.

Useful metadata may include:

```text
value_kind
role
alignment
sort_kind
link_kind
```

## Column headings and popovers

Column headings should remain compact.

If meaning cannot fit in the heading, use column help/popovers and PA Notes.

Column popovers are artifact-internal affordances unless they become public
model state.

They are not Options.

## Column groups and visibility presets

Where a table has column groups, presets, or visibility rules, the renderer
should make these understandable as table semantics rather than arbitrary UI
switches.

Example:

```text
View = standard | percentages | combined
```

may be implemented by showing and hiding column groups, but the public option is
a view/representation choice.

Visible columns should support the public analytical purpose of the page.

## Row filters

Row filters are table-artifact behaviour controlled by Options.

Examples:

```text
Active Rikishi Only
Division
```

They may be implemented by hiding rows, filtering an in-memory row set, or
re-rendering the table.  That is renderer detail.

## Sorting

Sorting belongs to the table artifact contract.

Rules:

- meaningful columns should be sortable where sorting supports analysis;
- non-data orientation columns such as row numbers should not be sortable;
- chii-like values must sort by model/order ordinal, not alphabetically;
- hidden or optional columns need explicit fallback behavior if involved in
  default sort;
- first-click direction should be deliberate.

## Table viewport and overflow

A table is rendered into the Artifact viewport.

If there are more rows than the viewport can show, scrolling should be available
for the row area.

For analytical tables, the preferred behaviour is:

- row data scrolls;
- column headings remain visible;
- PATitle, when present, remains visible.

The renderer may realize PATitle and column headings as a sticky header stack.
This is a rendering technique, not a semantic structure.

## Table notes

Table-specific notes should be represented as PA Notes whose relevance may be
linked to columns, groups, presets, or table state.

They should not be used as a substitute for page-level explanation.

---

# PASet / Multi-View Rendering

A PASet renders one selected PA from a structured set.

This is the model-level version of the implementation pattern previously called
`MultiViewPA`.

The renderer should distinguish:

- the PASet container;
- the PASelector;
- the selected PA;
- controls owned by the selected PA;
- URL state needed to share the selected PA;
- notes for the selected PA.

The selected PA may contain a Chart, Table, or Prose artifact.

The fact that a PASet mixes chart and table PAs does not disturb the model.  The
renderer dispatches after PA selection.

---

# Essay and Prose Rendering

Essay/prose pages should be rendered as first-class public pages, not as
unstructured text dumps.

The renderer should support:

- headings;
- explanatory paragraphs;
- lists;
- callouts or notes;
- embedded charts/tables where semantically owned;
- provenance or method metadata;
- references to related pages.

Prose should integrate with the same page title, navigation, status, and note
ownership conventions as other public content.

---

# Static HTML and Prototype Embed Rendering

Static/prototype HTML may be included for stress tests, legacy material, or
short-term public-site experiments.

When rendering embedded or copied HTML, the renderer should make status clear
where appropriate:

- canonical public page;
- prototype embed;
- legacy inclusion;
- diagnostic view;
- external/semi-external artefact.

Prototype content should not silently appear to have the same status as a
canonical PA-backed public page.

The renderer should avoid letting embedded HTML determine public shell,
navigation, page title, route, or ownership conventions.

---

# Metadata and Provenance Rendering

Analytical public pages often need to communicate provenance.

Metadata may include:

- source data;
- generation date;
- model or artefact version;
- curve/version naming policy;
- audit trail;
- assumptions;
- diagnostic stage;
- publication status.

The renderer should distinguish provenance from ordinary explanatory prose and
from renderer/display policy.

Where provenance is important for interpretation, it should be visible enough
to be useful.

Where provenance is secondary, it may be placed in a quieter metadata area.

Internal diagnostic names should not be foregrounded as public names unless
they have been deliberately promoted.

---

# URL State and Shareability

Rendered state that changes public page meaning should be serialisable where
appropriate.

Examples include:

- selected option values;
- selected PA in a PASet;
- selected table view or preset;
- selected chart variant;
- public filters that materially change interpretation.

Default state need not always appear in the URL.

Non-default state should be represented when shareability matters.

Renderer-owned URL state should not be confused with producer-internal file
names or diagnostic stage names.

The full route/query policy remains an implementation/open-issues topic.

---

# Visual Grouping

Visual grouping should reflect semantic grouping.

Cards, boxes, borders, panels, spacing, and background treatments should clarify
structure, not merely decorate the page.

Before adding a visual boundary, ask:

```text
What semantic boundary does this represent?
```

Before removing a visual boundary, ask:

```text
Will the semantic boundary still be clear?
```

Over-boxing can make pages feel fragmented.

Under-grouping can make ownership unclear.

The renderer should aim for stable, predictable grouping conventions.

---

# Layout

The standard layout should prioritize analytical readability.

Important goals include:

- clear page hierarchy;
- readable chart and table widths;
- stable navigation;
- predictable spacing;
- minimal visual noise;
- clear ownership boundaries;
- coherent relationship between page, Contents, PA, and Artifact levels.

Layout should not be driven primarily by individual artefact implementation.

The page should feel like a coherent analytical publication, not a collection of
unrelated embedded widgets.

---

# Responsive Rendering

Responsive behavior may change visual layout, but not semantic structure.

For example:

- navigation may collapse;
- sidebars may become drawers;
- multi-column layouts may stack;
- tables may scroll;
- chart dimensions may adapt;
- option groups may reflow.

However, the renderer should preserve:

- navigation hierarchy;
- active page state;
- title/caption ownership;
- note ownership;
- control scope;
- artefact boundaries;
- public status/provenance.

---

# Interaction Model

Interactions should be predictable and semantically scoped.

Examples include:

- expanding navigation groups;
- selecting PAs from a PASet;
- changing a chart source;
- filtering a table;
- toggling an evidence layer;
- sorting a table;
- opening column popovers;
- opening prototype embeds.

The renderer should avoid interactions whose scope is unclear.

If an interaction affects multiple artefacts, that relationship should be
visible.

---

# Error, Empty, and Missing States

Rendering contracts should include non-happy paths.

Common states include:

- no data;
- missing chart;
- empty table;
- unavailable embed;
- unsupported option;
- unsupported trace kind;
- stale generated artefact;
- failed data load;
- manifest validation failure.

These should be rendered as explicit publication states rather than accidental
blank space or broken layout.

A missing artefact is still semantically meaningful.

The page should communicate what is missing and, where possible, why.

---

# CSS, Templates, and Components

CSS classes, templates, and components are implementation mechanisms.

They should follow the semantic model rather than define it.

A useful component realizes a stable semantic category.

A questionable component exists only because several things happen to look
similar.

The first model-aligned CSS vocabulary should include:

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

Implementation helper classes are allowed, but should be named as helpers rather
than model concepts.

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

---

# Semantic HTML Mapping

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

Artifact mount elements may be implementation helpers so that third-party
libraries can mutate them without owning the model-level Artifact wrapper.

---

# Renderer Conformance Checklist

A renderer conforms to the model when it preserves the semantic structure of the
publication system.

Use these questions as a practical checklist.

## Site and navigation

- Does navigation preserve hierarchy?
- Does it distinguish labels from links?
- Does it expose active-page state?
- Does it avoid deriving public meaning from legacy filenames?
- Does it make prototype/legacy status clear where needed?

## ContentPanel and Contents

- Is Heading owned by the ContentPanel?
- Does the renderer distinguish Contents from PA?
- Does it handle both `Contents = PA` and `Contents = PASet`?
- If a PASet is present, is PASelector visible and scoped correctly?
- Does the selected PA render through the normal PA path?

## Options

- Is it clear what each control affects?
- Are PASet selectors distinguished from selected-PA options?
- Are options rendered as state, not arbitrary widgets?
- Are help/popovers distinguished from PA Notes?
- Does option ordering support the intended simple-to-advanced reading path?

## Artefacts

- Are charts, tables, prose, embeds, and PASet-selected artefacts visually distinct where needed?
- Does each PA preserve PATitle, Artifact, and Notes without letting the Artifact own public captions/titles?
- Are table column semantics reflected consistently?
- Are Plotly/generated outputs wrapped so that they follow public-site conventions?

## Notes and provenance

- Are PA Notes rendered according to PA ownership?
- Are dynamic notes tied to visible/relevant artifact components?
- Is provenance visible enough for interpretation?
- Are internal diagnostic names kept out of public semantics unless promoted?

## Failure states

- Are empty, missing, failed, or unsupported states rendered explicitly?
- Does the page avoid silent blank regions and broken layout?

---

# Anti-Patterns

The following patterns should be avoided.

## Implementation-first rendering

Rendering should not be determined only by what a library, template, or helper
function happens to emit.

## Ownership confusion

Avoid pages where it is unclear who owns:

- titles/captions;
- notes;
- controls;
- legends;
- metadata;
- visual grouping;
- URL state.

## Arbitrary widgetization

Do not turn every repeated visual pattern into a generic widget unless the
underlying semantic category is stable.

## Over-generalized framework design

The goal is not to create a universal UI framework.

The goal is to render this publication grammar clearly.

## Accidental public semantics

Do not let diagnostic file names, old chart stages, or legacy HTML structure
become public concepts by accident.

## Visual inconsistency from implicit semantics

If similar artefacts render differently, the reason should be semantic.

If the reason is accidental implementation history, the rendering model should
be clarified.

---

# Relationship to Other Documents

`01 Public Site Model.md` defines entities, ownership, and page grammar.

This document defines expected realization.

`06 UI Model Implementation Contract.md` defines the implementation-facing
manifest, renderer, and DOM/CSS contract.

The three documents should evolve together:

```text
01 = what exists
02 = how it is rendered
06 = how implementation carries it
```

When a rendering question repeatedly arises, it may indicate that the semantic
model is missing a category, boundary, or invariant.

When a semantic distinction is added, this document should explain how it is
made visible.

---

# Current Direction

The rendering system should move toward:

- explicit semantic-to-visual mapping;
- stable ownership conventions;
- predictable chart and table treatment;
- explicit Contents / PA / PASet rendering;
- clear navigation structure;
- consistent control placement;
- deliberate PA-owned note placement;
- explicit public/prototype/diagnostic status;
- visible provenance where useful;
- reduced accidental styling variation.

The aim is not maximal abstraction.

The aim is a renderer that makes the publication model visible.
