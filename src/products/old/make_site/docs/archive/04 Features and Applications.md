# 04 Features and Applications

## Purpose

This document records the main feature-specific applications of the public-site
model for `src.products.make_site`.

It complements:

- `01 Public Site Model.md`, which defines the semantic publication model;
- `02 Rendering Model.md`, which defines renderer responsibilities;
- `03 Implementation State.md`, which describes the current code reality.

This document is deliberately more concrete than the first two.  Its role is to
preserve the feature-level decisions that would otherwise be scattered across
individual design notes, work plans, review CSVs, and migration memos.

In short:

```text
Public Site Model
    -> applied to concrete analytical features
    -> producing feature-specific contracts and migration decisions
```

---

# Current Feature Families

The current make_site feature work falls into these main families:

1. Basho Results Browser;
2. existing public table applications;
3. PA-backed chart pages;
4. career lifecycle pages;
5. Equelo public-facing pages and naming;
6. producer writers and prototype embeds;
7. shared chart/table behaviour and styling.

These feature families are not separate architectural systems.  They are test
cases for the same underlying publication grammar.

---

# 1. Basho Results Browser

## Status

Basho Results Browser, usually abbreviated BRB, is the most important current
feature-specific application of the public-site model.

It belongs under:

```text
Sumo History
    Basho Results
```

It is intended to be a promoted public page rather than a copied standalone
analysis artefact.

In the current codebase it is represented as:

```text
page id: basho_results_browser
view:    CustomView(kind="pa_runtime_page")
PA:      IndexedTablePA / table runtime style
```

## Feature Shape

BRB is a table-first analytical page.

The core page shape is:

```text
Page
    title
    date/division/options area
    results table
    notes and provenance
```

The table is one row per rikishi.  It is not a banzuke-style east/west paired
table by default.

The intended standard layout is close to:

```text
title bar
options panel | table/content panel
```

where the options panel controls page/table state and the content panel owns the
rendered table.

## Date State

The selected basho date is first-class page state.

The canonical state is a valid basho identifier or index, not independent year
and month strings.

The date selector should behave as a controlled representation of that state:

```text
[previous basho] [year] [month] [next basho]
```

Important rules:

- previous/next move through valid basho only;
- missing basho, such as `2022/03` and `2011/05`, are skipped;
- endpoint buttons are hidden or disabled at the relevant history boundary;
- year and month choices should resolve to a valid represented basho;
- URL state should preserve meaningful selected state.

## Rating Source

BRB must use the current fixed_v2 Equelo artefacts for individual rikishi
ratings.

The distinction is important:

- fixed_v2 process ratings are individual bout-derived ratings at represented
  points in the basho timeline;
- `Typical Equelo Ratings` are public scale landmarks;
- public landmarks must not be used as lookup values for individual BRB rows.

Therefore BRB row calculations should not derive an individual rikishi's rating
from a rank/chii label by looking up the public landmark table.

## Table Structure

The initial conceptual table groups are:

```text
row number | Shikona | Before | Score | After/Current
```

Expected columns include some combination of:

- shikona;
- score;
- before-basho chii/rank context;
- before-basho Equelo;
- after/current Equelo;
- Equelo delta;
- after/current chii or projected context where available;
- derived movement or comparison columns.

`Shikona` and `Score` are always-visible core columns.

A row number, if present, is display structure rather than analytical data.  It
should not be treated as a normal sortable data column unless there is an
explicit feature reason.

## Column Visibility

BRB should support both group-level and column-level visibility.

Rules:

- meaningful column groups can be shown or hidden as groups;
- individual columns can also be shown or hidden;
- hiding a group should mute or disable the individual controls inside it;
- restoring the group should restore previous individual-column choices;
- active-sort-hidden-column behaviour needs an explicit fallback policy.

This is a useful stress test for whether table options are represented
semantically rather than as ad hoc DOM state.

## Sorting and URL State

BRB should combine the strongest existing table behaviours:

- Standings by Wins: sort model, URL state, back/forward behaviour;
- Banzuke Changes: column toggles, option-sensitive notes, validation;
- Career Length / Longest: in-panel scrolling and sticky table headers.

Required behaviours:

- meaningful columns are sortable;
- repeated header activation toggles sort direction;
- visible sort indicators are present;
- chii/rank values sort by ordinal rather than alphabetically;
- shareable URL state records meaningful display state;
- browser back/forward restores state;
- browser-side data/config validation happens before rendering.

## Notes and Provenance

BRB needs page-level provenance because some values depend on page state.

Examples:

```text
view_state = final | live
after_chii_kind = actual_next_banzuke | projected | unavailable
```

Such state should not be repeated as if it were row-local data.  It belongs to
the page/table contract and should be surfaced in titles, notes, headings, or
metadata where appropriate.

## Open BRB Questions

Known remaining questions include:

- final default column set;
- exact table title wording for historical vs live/current mode;
- live-basho semantics;
- projected next-banzuke values;
- full fallback behaviour when active sort columns are hidden;
- exact treatment of after/current chii columns when data is unavailable.

The first implementation scope should remain conservative: completed historical
basho first, then expand once the manifest/data path is stable.

---

# 2. Existing Public Table Applications

The two major existing table applications are:

- Standings by Wins;
- Banzuke Changes.

These are important because they contain mature table behaviours, but they also
represent the old integration style.

## Current Position

The long-term promoted public-site model is:

```text
analysis module
    -> writes data/config/PA manifest
make_site
    -> owns public shell, route, shared JS, table behaviour, rendering contract
```

The old standalone table-app shells are not the desired final public-site
integration contract.

They may remain temporarily as reference implementations and comparison points,
but public promotion should move behaviour and metadata into make_site-owned
runtime rendering.

## Standings by Wins

Standings by Wins is valuable as a precedent for:

- sorting;
- shareable URL state;
- browser back/forward restoration;
- view modes;
- table behaviour under changing options.

It is a strong candidate for piloting shared table-runtime behaviour where the
main goal is URL state and sort behaviour.

## Banzuke Changes

Banzuke Changes is valuable as a precedent for:

- option-sensitive columns;
- grouped column visibility;
- banzuke-specific display modes;
- option-sensitive notes;
- validation;
- shikona link behaviour.

It is a strong candidate for piloting shared table-runtime behaviour where the
main goal is rich column visibility and presentation semantics.

## Shared Lesson

Neither existing table app should be treated as the whole template.

The shared table runtime should extract stable behaviours from both without
preserving accidental app-shell structure.

---

# 3. Table Behaviour Contract

The public site should converge on a shared table behaviour contract.

## Core Behaviours

Promoted public tables may need:

- sortable columns;
- sort-kind-specific ordering;
- column groups;
- column visibility controls;
- option-sensitive notes;
- sticky headers;
- in-panel scrolling;
- URL state;
- validation of data/config before rendering;
- shikona links with standard click semantics.

Not every table needs every behaviour.  The behaviour set should be selected by
semantic need, not by copying whichever old application happened to support it.

## Shikona Links

The site convention is:

- normal click opens the relevant SumoDB page;
- Alt-click opens the Gaspode-san graph endpoint.

This should be treated as shared public-site identity/link behaviour, not as a
local table-app trick.

## Scroll Behaviour

Large analytical tables should be able to scroll inside the content panel with
sticky column headers.

The renderer should make clear what scrolls:

- whole page;
- content panel;
- table body;
- notes/provenance area.

Ambiguous nested scrolling is a UI smell and usually indicates an unresolved
ownership/layout decision.

## Notes Behaviour

Notes should be scoped to their semantic owner:

- page-level notes belong outside individual tables;
- table notes belong with the table;
- column notes belong near headings or in a clear note area;
- option-sensitive notes should update with the relevant option state.

---

# 4. Semantic Table Column Styling

Public tables currently contain repeated value kinds whose presentation should
be consistent across pages.

The missing layer is semantic column metadata.

## Value Kind

A table column should be able to say what kind of value it contains.

Candidate value kinds:

```text
row-number
shikona
chii
record
movement
rating
rating-delta
count
percent
text
```

This is distinct from the column's analytical role.

For example, a chii-like value may be previous context, current rank, projected
rank, or comparison value.  In all cases it is still a chii-like value and
should receive the baseline chii treatment unless a page documents an exception.

## Role

A column should also be able to say how the value functions in the table.

Candidate roles:

```text
identity
current
previous
context
metric
comparison
```

The important split is:

```text
value_kind = what kind of value is this?
role       = what job does it do in this table?
```

## Styling Contract

Likely site-wide defaults:

- row numbers are muted and normally not sortable;
- shikona values receive shared rikishi-link styling;
- chii values are compact and consistently aligned;
- records receive consistent centred/tabular treatment;
- movement values receive consistent signed/directional treatment;
- ratings are numeric and usually right-aligned;
- rating deltas are signed numeric values;
- previous/context values may be visually muted.

These defaults belong in shared site CSS.  Page-specific CSS should override
them only for a documented local reason.

## Migration Path

1. Add semantic fields to table manifest definitions.
2. Emit classes such as `value-chii`, `value-rating`, and `role-previous`.
3. Add shared CSS for those classes.
4. Annotate current runtime table manifests.
5. Update hand-built pages to emit compatible classes during migration.
6. Remove local CSS rules that duplicate site-wide semantics.

This is not a broad redesign.  It is a missing vocabulary layer for table
presentation.

---

# 5. PA-Backed Chart Pages

Several chart pages have now moved, or are moving, from standalone generated
HTML toward PA-backed site rendering.

Important examples include:

- Banzuke Division by Era;
- Makuuchi Rank by Era;
- Division Stability;
- First Chii Appearance;
- Win Probability by Standing;
- Career Length chart views;
- Rank at Retirement.

## ChartPA Pattern

A promoted chart page should expose intentional public-site inputs:

- data sources;
- trace definitions;
- axis metadata;
- options;
- notes;
- provenance;
- renderer kind.

The public renderer then owns:

- shell layout;
- chart container conventions;
- title/subtitle placement;
- note placement;
- standard Plotly configuration;
- interaction policy.

The plotting library object is not the semantic chart.  It is the realization of
a ChartPA.

## Plotly Legend Policy

Public Plotly charts with meaningful visible legends should not rely on
Plotly's default double-click legend behaviour.

The public-site policy is:

- ordinary legend click may toggle traces;
- double-click should use site-owned isolation behaviour;
- exceptions should be explicitly documented.

This policy exists because public chart interaction is part of the site contract
rather than an accidental Plotly default.

## Migrated Chart Lesson

The migration of Banzuke Division by Era, Makuuchi Rank by Era, and Division
Stability demonstrates the preferred path:

```text
old standalone HTML/chart output
    -> producer writes site-facing data/config
    -> make_site renders PA-backed public chart
```

This prevents standalone HTML from becoming a long-term API.

---

# 6. Career Lifecycle Pages

The career lifecycle pages are an important multi-view application of the model.

Current or planned pages include:

- Career Length;
- Rank at Retirement;
- related distribution, PMF, CDF, survival, longest-career, and final-rank
  views.

## Multi-View Shape

Career Length is a useful example because it combines multiple analytical views
under one conceptual page family.

Potential views include:

- Distribution;
- PMF;
- CDF;
- Survival;
- Longest;
- Rank at Retirement or related page links.

Some views are chart-like and some are table-like.  The public-site model
should not force them into one rendering type merely because they are
conceptually related.

A multi-view analytical page should preserve:

- page-level identity;
- view-level identity;
- view-specific notes;
- shared provenance;
- consistent option and navigation behaviour.

## Active/Retired Semantics

Career lifecycle pages often distinguish active and retired rikishi.

This distinction is semantic, not merely a trace label.  It may affect:

- chart traces;
- table filters;
- interpretation notes;
- PMF/CDF/survival meaning;
- inclusion/exclusion rules.

Where active/retired status is used, the page should state the interpretation
clearly.

---

# 7. Equelo Public Pages and Naming

Equelo-related pages need especially careful naming and provenance because the
project has historical model stages, diagnostic names, public landmarks, and
current process ratings.

## Current Public Rule

Use canonical names for rating systems, rating series, and landmark curves.

Avoid using local diagnostic names such as `v0`, `v1`, ..., `v5` as public
model names.

Those diagnostic names describe stages in a particular audit trail.  They are
not the same thing as public model names.

## Rating Series vs Rating Landmarks

Public documentation and features must distinguish:

- individual fixed_v2 process ratings;
- public landmark values shown on `Typical Equelo Ratings`;
- historical fixed_v1/Brier-compressed diagnostic material;
- explanatory methodology pages.

This distinction directly affects feature implementation.

For example:

- BRB uses individual fixed_v2 process ratings;
- Typical Equelo Ratings displays public scale landmarks;
- historical entrant-initial-rating charts are diagnostic/methodology material,
  not current row-level lookup sources.

## Public Wording

Public-facing wording should be stable and reader-oriented.

Technical names may remain in metadata, notes, and provenance, but page titles
and explanatory text should not expose internal diagnostic stage names unless
that diagnostic history is the subject of the page.

---

# 8. Producer Writers and Prototype Embeds

The project already has many generated artefacts.  Not all of them should be
rewritten before they can be inspected inside the public-site IA.

The policy is therefore split into prototype inclusion and public promotion.

## Prototype Rule

For a prototype, stress test, or IA experiment, it is acceptable to include an
existing generated artefact by copy or iframe.

This is useful when the question is:

- does this output belong in the public site?
- where would it sit in navigation?
- is the subject interesting enough to promote?
- does it reveal a missing public-site category?

The goal in this mode is learning.

## Promotion Rule

If an artefact is promoted to a real public-site page, the producer should gain
an additive site-facing writer.

The producer should emit intentional public-site inputs such as:

- chart data;
- table data;
- metadata;
- option definitions;
- chart or table config;
- structured prose or notes;
- local asset references;
- provenance.

The site builder should consume those inputs and render the public page using
shared site contracts.

## What Not To Do

The public site should not normally parse generated HTML to recover meaning.

Generated HTML should not become the accidental API between analysis packages
and the public site.

Legacy filenames should not determine final public routes unless they have been
explicitly promoted into the public contract.

---

# 9. Feature Review Findings

The table/chart review notes reveal repeated UI questions that should be treated
as semantic/rendering questions rather than isolated bugs.

Examples include:

- Why does this chart have a box?
- Should charts have internal titles, or should PA/page titles own that text?
- Should tables have captions?
- Should notes be sticky or fixed within the available panel space?
- Which region should scroll?
- Why are muted values not visually consistent across pages?
- Should charts occupy the available vertical space?
- How should option controls be styled consistently?
- Are horizontal/vertical table rules part of the public style?

These questions belong mainly to `02 Rendering Model.md`, but they are
feature-discovered.  They should remain visible here because concrete features
are where abstract rendering contracts are tested.

---

# 10. Application-Level Anti-Patterns

## Treating Old HTML as the API

Old generated HTML may be useful as a prototype or migration reference, but it
should not become the stable contract for promoted pages.

## Copying One Feature's UI Wholesale

BRB should borrow from Standings, Banzuke Changes, and Career Length, but it
should not become a disguised copy of any one of them.

## Confusing Public Landmarks with Process Ratings

Typical Equelo landmark values are for public scale explanation.  They are not
individual rikishi ratings.

## Preserving Plotly Defaults as Public Policy

Plotly defaults are implementation defaults.  Public chart behaviour should be
site-owned where it affects user interpretation.

## Styling Columns by Local Names Only

Column ids are not enough.  Tables need semantic value kinds and roles to avoid
page-by-page styling drift.

---

# 11. Relationship to the Implementation State

The features in this document are at different migration stages.

Current implementation includes a mixture of:

- legacy table app views;
- standalone HTML views;
- custom native renderers;
- PA-backed chart and table manifests;
- PA runtime table pages;
- placeholder/TBD pages.

That mixture is expected during migration.

The direction is clear:

```text
legacy/prototype artefact
    -> intentional producer writer
    -> PA manifest or equivalent site-facing contract
    -> make_site-owned rendering
```

`03 Implementation State.md` should describe what exists today.

This document describes what the major features require and why they matter.

---

# Current Direction

The feature layer should move toward:

- BRB as the major table-runtime proving ground;
- shared table behaviour extracted from existing apps;
- PA-backed charts for promoted chart pages;
- consistent Plotly legend behaviour;
- semantic table column metadata;
- strict separation between Equelo process ratings and public landmarks;
- additive producer writers for promoted artefacts;
- prototype embeds only as temporary or exploratory inclusions.

The aim is not to make every page identical.

The aim is to ensure that differences between pages are semantic and intentional,
rather than accidental consequences of their implementation history.
