# Case Study - 2.2 Standings by Wins

## Status

This is a case-study note for nav item `2.2 Standings by Wins`.

It records what we have learned from the screenshot, prototype behaviour, existing PA manifest work, and comparison with earlier case studies.

It does **not** update the UI Model or the implementation contract directly.

The purpose is to work this case down toward actual HTML/CSS/JS, then later compare it with the other case studies before making one considered update to the implementation contract.

## Case-study order

This is the fourth case study.

Earlier case studies established:

```text
4.3.1 Banzuke Division by Era
  Contents = PA
  Artifact = Chart
  Options = no

6.3.1 Win Probability by Standing
  Contents = PA
  Artifact = Chart
  Options = yes

7.3.1 Career Length
  Contents = PASet
  selected PA may be Chart or Table
  selected PA may have its own options
```

`2.2 Standings by Wins` tests the rich table path.

The main new concern is:

```text
Artifact = Table
```

more specifically:

```text
rich TableArtifact
  with data-source selection
  column groups
  view presets
  row filters
  sortable columns
  column popovers
  dynamic notes
```

## Case-study role

`2.2 Standings by Wins` is the canonical rich table PA case.

It is valuable because it combines:

```text
parameterized table data
model-level options
table view modes
row filtering
column/group visibility
sortable columns
column popovers
state-sensitive notes
```

It should stress-test the table artifact contract.

It should not be used to invent a new top-level page model unless the table evidence forces one.

## Screenshot reading

The deployed screenshot shows:

```text
Heading
  Grand Sumo Standings by Wins digest
  Rolling recent-performance standings by wins.

Options
  View
  Number of Basho
  Active Rikishi Only
  Division

PA title
  Standings for May 2025 to Mar 2026 (6 Basho)

Artifact
  table
```

The visible table includes sortable-looking columns and grouped headings.

The screenshot shows the `standard` view with a selected number of basho and division filter.

Notes are not prominent in the screenshot crop, but the prototype behaviour includes notes that respond to visible columns/views.

## Current model classification

This case does not require a change to the UI Model.

Classification:

```text
ContentPanel
  = Heading + Options + Contents

Contents
  = PA

PA
  = PATitle + Table Artifact + Notes?
```

There is no `PASet`.

The artifact is a table.

The new pressure is inside:

```text
Table Artifact
```

not at the level of:

```text
ContentPanel
Contents
PA
Options
Notes
```

## Difference lens: what this case adds

Compared with `6.3.1`, this case does not appear to add a new kind of option.

The new concern is:

```text
rich table artifact behaviour
```

Specifically:

```text
TableArtifact
  data source selected by option
  column groups
  visibility presets
  row filtering
  sortable columns
  column popovers
  dynamic notes based on visible columns / views
```

This is the first case study where the artifact is a complex table rather than a chart or a selected chart/table inside a PASet.

## Similarity lens: does this disturb the earlier happy path?

No.

`2.2` remains a single PA:

```text
ContentPanel
  Heading
  Options
  Contents
    PA
      PATitle
      Table Artifact
      Notes?
```

The options still fit the candidate cross-case distinction:

```text
ContentSelector
Filter
```

The fact that some filters are implemented by hiding rows or columns does not change their public meaning.

The case extends the artifact contract rather than disturbing the model.

## Options interpretation

The visible options are:

```text
View
Number of Basho
Active Rikishi Only
Division
```

A useful classification is:

```text
ContentSelector:
  Number of Basho
    selects the backing CSV / data instance

Filters:
  View
    changes visible representation via column-group visibility

  Active Rikishi Only
    filters rows

  Division
    filters rows
```

`View` is a filter in the broad synthesis sense. It does not filter rows, but it modifies the visible representation of the selected content.

The implementation mechanism may be column/group hiding, but the public option is not simply “column visibility.”

This supports the existing synthesis finding:

```text
Options may divide into ContentSelectors and Filters.
```

No model change is made here.

## Prototype evidence: data and options

The prototype is not simply “one table.”

It is better understood as a parameterized table PA.

For a selected number of basho, there is a backing data instance, represented as a CSV.

The selected table state then includes:

```text
view = standard | percentages | combined
active-only row state
division row state
column/group visibility implied by view
sort state
```

The important distinction is:

```text
public option meaning
  != implementation mechanism
```

Examples:

```text
View option
  public meaning: choose representation/view
  implementation mechanism: show/hide column groups

Active Rikishi Only
  public meaning: restrict to active rikishi
  implementation mechanism: hide/filter rows

Division
  public meaning: restrict to division or show all divisions
  implementation mechanism: hide/filter rows
```

## Prototype evidence: existing PA manifest

The existing PA manifest for this page is already close to the desired direction.

It is a `TablePA` with concepts such as:

```text
options
data sources
columns
column groups
group visibility presets
default sort
notes
consumes options
```

This maps cleanly to the revised model as:

```text
PA with Table Artifact
```

The table-specific details belong inside the TableArtifact contract.

## What to adopt from the PA manifest

Adopt the core ideas:

```text
TablePA as PA with Table Artifact
data sources selected by option
columns as semantic table definitions
column groups as semantic table structure
visibility presets as public view definitions
default sort as table state
notes linked to columns / presets / table state
consumed options
```

Especially important:

```text
column groups and visibility presets are table semantics,
not arbitrary DOM tricks.
```

Also important:

```text
notes may be declared on table/column concepts
and rendered as PA notes when relevant.
```

## What to adapt, not adopt verbatim

### Heading and PATitle

The existing manifest/code may use a single ambiguous heading-like field.

The revised model distinguishes:

```text
ContentPanel Heading
PA PATitle
```

For this case, the page/content heading is something like:

```text
Grand Sumo Standings by Wins digest
Rolling recent-performance standings by wins.
```

The PA title is state-sensitive, for example:

```text
Standings for May 2025 to Mar 2026 (6 Basho)
```

This distinction is important and should be preserved.

### View as column hiding

The prototype implements the `View` option through column/group visibility.

That implementation detail is useful, but the manifest should expose the public view/preset meaning rather than force users or future renderers to think in low-level column-hiding terms.

The renderer may still implement the view by showing/hiding column groups.

### Notes

The prototype has state-sensitive notes.

The model rule remains:

```text
Notes belong to PA.
```

However, notes may pertain to specific columns, column groups, or presets, and therefore only render when those table components are visible/relevant.

So the table artifact needs a note-relevance mechanism.

This does not require option notes.

## Table artifact concerns

This case identifies the first substantial TableArtifact contract.

Likely table-specific concepts include:

```text
TableArtifact
  dataSources
  columns
  columnGroups
  visibilityPresets
  rowFilters
  defaultSort
  sortKinds
  column popovers/help
  note relevance
  formatting/alignment metadata
```

The exact field names should not be adopted from this case alone.

The purpose of the case is to identify table-rendering concerns that must be compared with later table pages and existing table apps.

## Column groups and view presets

The `View` option appears to select among public table representations:

```text
standard
percentages
combined
```

These views correspond to different visible column/group sets.

This suggests a table artifact structure like:

```text
columnGroups
visibilityPresets
```

where:

```text
visibility preset
  = named public representation
  = set of visible groups/columns
```

The renderer may implement this as column hiding, but the manifest should name the public representation.

## Row filters

`Active Rikishi Only` and `Division` are row filters.

They should be represented as public options whose effects are interpreted by the table renderer.

They may be implemented by hiding rows, filtering an in-memory row set, or re-rendering the table.

That is a renderer implementation detail.

## Sorting

Sorting is part of the table artifact, not a separate top-level model feature.

This case should preserve the prototype precedent that meaningful columns are sortable.

Likely requirements:

```text
sortable columns declare sort behaviour
first-click direction is deliberate
chii-like values sort by ordinal, not alphabetically
orientation columns such as row numbers are not normal sortable data columns
default sort may depend on selected view/preset
```

This should be compared with other table examples before becoming a final shared table contract.

## Column popovers and compact headings

Column headings should remain compact.

If the meaning cannot fit in the heading, the table should use popovers/help and PA notes.

Policy alignment:

```text
column headings
  short enough to work inside the artifact

PA notes
  carry meaning that cannot fit in compact labels
```

Column popovers are artifact-internal affordances unless they become public model state.

They are not `Options`.

## Notes behaviour

This case is the strongest example so far of dynamic PA notes.

The useful model is:

```text
note -> table component
```

For example:

```text
note -> column
note -> column group
note -> visibility preset
note -> table/PA generally
```

A note is rendered when its target is visible or relevant in the current table state.

This supports the broader working rule:

```text
Notes belong to PA.
Options may affect which Notes are relevant by changing visible artifact state.
```

## Candidate DOM extension

Compared with chart cases, the artifact region contains a table wrapper and table element.

Candidate DOM shape:

```html
<main class="content-panel" data-panel-id="standings_by_wins">
  <header class="heading">
    <h1>Grand Sumo Standings by Wins digest</h1>
    <p class="heading-subhead">Rolling recent-performance standings by wins.</p>
  </header>

  <section class="options">
    <fieldset class="option-group" data-option-group-id="main">
      <!-- View, Number of Basho, Active Rikishi Only, Division -->
    </fieldset>
  </section>

  <section class="contents">
    <article class="pa" data-pa-id="standings_by_wins">
      <header class="pa-title">
        <h2 class="pa-head">Standings for May 2025 to Mar 2026 (6 Basho)</h2>
      </header>

      <div class="artifact table" data-artifact-kind="table">
        <div class="table-scroll-region">
          <table class="data-table">
            <!-- generated table -->
          </table>
        </div>
      </div>

      <section class="notes">
        <!-- state-sensitive PA notes -->
      </section>
    </article>
  </section>
</main>
```

This is scratch-case-study material only.

The exact table DOM may change once the table renderer is designed.

## JS implications

Compared with previous cases, the JS renderer needs a table artifact renderer.

New responsibilities include:

```text
renderTableArtifact
load selected data source
parse CSV
apply row filters
apply column/group visibility preset
render table header groups
render column headings
render rows
format cell values
install sort handlers
install column popovers/help
assemble visible notes
update table when options change
```

The existing chart renderer path remains separate.

The shared model path remains:

```text
renderContentPanel
renderOptions
renderContents
renderPA
renderArtifact
  -> renderTableArtifact
renderNotes
```

## What actual HTML/CSS/JS must prove

This case should prove:

```text
Contents = PA with Table Artifact
Options controlling data source and filters
TableArtifact rendering
column group rendering
visibility presets
row filtering
sortable columns
column popovers/help
dynamic PA notes based on visible table components
same ContentPanel/PA path as earlier cases
```

It should not attempt to prove:

```text
PASet
chart rendering
all possible table behaviours
production asset policy
final Python model classes
```

## Readiness assessment

This case is conceptually ready as the rich table case study.

Resolved for this case:

```text
UI model classification
main difference from previous cases
similarity to earlier happy path
option interpretation
PA manifest consistency
heading/PATitle distinction
table-specific pressure points
notes remain PA-owned
```

Items to check during implementation:

```text
exact existing TablePA manifest shape
exact data source mapping for each number of basho
exact column and column group definitions
exact visibility presets for standard / percentages / combined
exact default sort rules
exact current note declarations and relevance rules
exact current column popover content
exact row-filter semantics for active-only and division
current URL-state behaviour fro