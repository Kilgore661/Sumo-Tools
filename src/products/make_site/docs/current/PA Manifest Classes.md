# PA Manifest Classes

## Status

Target model, created 2026-05-09.

This document defines the Published Artefact (PA) manifest class idea used by
the public UI grammar.

## Why We Need PA Manifest Classes

The public site needs to show different kinds of analysed results through one
coherent UI model.

The common page grammar is:

```text
Heading + Options + Published Artefact
```

That grammar is useful, but it is too abstract to implement directly.  The site
builder needs to know what kind of artefact it is rendering, which options the
artefact consumes, which files it needs, and which behaviours apply.

A PA manifest class supplies that missing layer.

It lets us say:

```text
this artefact is a table with column groups and sort policy
this artefact is a chart with traces and axis config
this artefact is a multi-view artefact whose selected item is another PA
```

without letting each producer invent its own browser app shell.

## Definition

A PA manifest is an instance of a PA manifest class.

At minimum, every PA manifest records:

* stable id;
* manifest class;
* renderer id;
* data sources;
* options consumed by the PA;
* default state relevant to the PA;
* notes/caveats;
* provenance;
* validation requirements.

The manifest describes what the public renderer needs to show the artefact.  It
is not itself the rendered HTML.

## Ownership

Producer modules own analysis-specific manifest content:

* which data files exist;
* what columns or traces mean;
* what options are meaningful;
* notes and caveats;
* provenance.

`make_site` owns:

* manifest validation;
* public page chrome;
* option widgets;
* shared renderers;
* shared styling;
* URL state;
* link behaviour.

## Base Shape

Conceptually:

```text
PAManifest
  id
  class
  renderer
  data_sources
  consumes_options
  default_state
  notes
  provenance
```

Concrete classes add class-specific fields. The target PA classes currently
identified are `TablePA`, `IndexedTablePA`, `ChartPA`, `MultiViewPA`, and
`EssayPA`. `ExcludedPA` is a non-target marker for active navigation items that
remain outside the direct PA architecture.

## TablePA

Use for one table artefact rendered from producer-written row data.

Core fields:

```text
TablePA
  id
  renderer
  data_sources
  columns
  column_groups
  group_visibility
  group_visibility_presets
  sort_policy
  notes
  provenance
```

### Columns

A column definition records:

* stable id;
* display label;
* source field or computed value;
* group membership;
* sortable flag;
* sort key;
* formatting rule;
* optional note target;
* optional link behaviour, such as rikishi links.

### Column Groups

Column groups describe the visible table structure.  They can support:

* grouped headers;
* show/hide behaviour;
* always-visible identity columns;
* table-specific layout rules.

### Visibility Presets

A table may define visibility presets.  A preset is not a different PA.  It is
a named table state.

For example, Standings by Wins should be understood as one combined table with
metric-group presets:

```text
standard     -> identity + wins_per_basho
percentages  -> identity + wins_per_bout
combined     -> identity + wins_per_basho + wins_per_bout
```

The same table class can also support BRB-style group toggles without using
presets.

### Sort Policy

Sort policy records:

* default sort;
* per-preset default sort, where needed;
* first-click direction rules;
* unsortable columns;
* chii ordinal sorting;
* fallback when a hidden column is the active sort.

## ChartPA

Use for one chart artefact rendered from producer-written data.

Core fields:

```text
ChartPA
  id
  renderer
  data_sources
  chart_config
  trace_config
  consumes_options
  notes
  provenance
```

The chart renderer may be Plotly or another browser renderer.  Plotly's own
toolbar interactions are not site-owned options, but chart PAs may still
consume site-owned options such as source, division, error bars, or theme.

Chart-specific config may include:

* x/y fields;
* axis labels;
* axis ranges;
* trace grouping;
* legend policy;
* error bar policy;
* hover text policy;
* chart notes.

## MultiViewPA

Use when one page option selects among several PA items.

Core fields:

```text
MultiViewPA
  id
  selector_option
  items
  default_item
  notes
  provenance
```

Each item is itself a PA manifest, usually a `ChartPA` or `TablePA`.

Career Length is the current forcing example:

```text
view=distribution -> ChartPA
view=pmf          -> ChartPA
view=cdf          -> ChartPA
view=survival     -> ChartPA
view=longest      -> TablePA
```

The defining feature is not that different files are loaded.  The defining
feature is that the selected option changes the artefact identity or renderer
identity.

Different files can also be loaded by a single PA, for example a BRB table that
loads one file per basho date.

## IndexedTablePA

Use when the public artefact is still a table, but its rows are selected from a
large or sparse set of payload files via an index.

This is the target shape for Basho Results Browser (BRB):

```text
IndexedTablePA
  index_source
  selector_option
  payload_path_field
  columns
  column_groups
  sort_policy
  notes
  provenance
```

The index source is loaded first.  The selected option value identifies an
index entry, and that entry supplies the payload path to load.  The payload is
then rendered using the same column, grouping, note, and sort ideas as a
regular table.

The manifest class should stay generic.  Basho-specific behaviour such as
valid basho dates, missing basho, current-basho state, and previous/next basho
navigation belongs in the producer-written index/payload metadata and in the
page control contract, not in the base class itself.

## EssayPA

Use for explanatory content rendered by `make_site`.

Core fields:

```text
EssayPA
  id
  renderer
  content_source
  notes
  provenance
```

The content source may be Markdown or structured prose metadata.  Semi-rendered
HTML snippets are not a target integration contract.

## Static HTML

Static HTML is not a target PA manifest class.

Existing complete HTML artefacts can be excluded while the direct-rendering
model is built.  If a static artefact becomes important enough to restore, it
should receive a manifest and a direct renderer, or be deliberately handled as
a temporary migration exception outside the target model.

## Active PA Constants

As of 2026-05-09, the first code-level pressure test is:

```text
ACTIVE_PA_MANIFESTS: dict[page_id, PA manifest instance]
```

with one constant for every currently active page id:

```text
banzuke_changes              -> TablePA
standings_by_wins            -> TablePA
win_probability_by_standing  -> ChartPA
career_length                -> MultiViewPA
rank_at_retirement           -> ChartPA
typical_equelo_values        -> TablePA
v5_landmark_policy           -> EssayPA
lower_rank_rating_stability  -> EssayPA
finish_by_chii               -> ExcludedPA
banzuke_division_by_era      -> ExcludedPA
makuuchi_rank_by_era         -> ExcludedPA
division_stability           -> ExcludedPA
```

The excluded entries are deliberately total over the active nav tree while
still making the target architecture honest: the old static HTML pages are not
being silently treated as if they satisfied the PA model.

## URL State

PA manifest classes must support explicit URL state.

The page route identifies the page.  The option state identifies what the PA
shows.  Missing options may be interpreted from defaults on arrival, but the
canonical URL should spell out the explicit state after normalisation.

## Current First Implementation

The current provisional table manifest file is named:

```text
page_bundle.json
```

and uses schema:

```text
sumo-tools.table-page-bundle.v0
```

The name predates the manifest-class terminology.  Future schema and file names
should prefer `manifest`.

Standings by Wins and Banzuke Changes now emit first-pass table PA manifests in
that provisional format.  These manifests are migration artefacts, not final
schemas.
