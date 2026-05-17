# UI Model Working Note: Contents, PAs, Artifacts, and Options

## Status

This is a working note arising from discussion of several deployed/prototype pages. It is not yet a replacement for the numbered UI Model documents.

The purpose is to record the emerging proposal clearly enough that we can check alignment before asking what consequences it has for the model, rendering implementation, CSS/HTML structure, manifests, or existing pages.

## Starting point

The existing model has a useful top-level structure:

```text
PublicUI
  = Sidebar + ContentPanel

Sidebar
  = Caption + Navigation + Hider

ContentPanel
  = Heading + Options + PA

PA
  = PATitle? + Artifact + Notes?

PATitle
  = PAHead + PASubHead?

Artifact
  = Chart | Table | Prose
```

This remains broadly useful, especially the distinction between:

* public UI shell;

* navigation-selected content;

* page/content heading;

* options;

* publishable artefact;

* artefact title;

* concrete artefact kind;

* notes.

The main refinement is that the content selected by a navigation node is not always a single PA. Sometimes it is a set of selectable PAs.

## Core observation

A navigation node does not always select one already-resolved chart, table, or prose block.

Instead, a navigation node selects `Contents`, displayed in the `ContentPanel`.

Those `Contents` may be:

```text
Contents
  = PA | PASet
```

A single `PA` is the familiar case.

A `PASet` is a set of named PAs, with a selector choosing which PA is currently visible.

The important relationship is therefore:

```text
Navigation node
  -> ContentPanel
      -> Contents
          -> selected/resolved PA
              -> Artifact
```

The concrete `Artifact` remains one of:

```text
Chart | Table | Prose
```

but the thing selected by the navigation node may be richer than a single artifact.

## Proposed vocabulary

### Contents

`Contents` is the model-level thing selected by a navigation node and displayed in the content panel.

```text
ContentPanel
  = Heading + OptionPanel? + Contents

Contents
  = PA | PASet
```

`Contents` is intentionally broad. It avoids pretending that every navigation node resolves immediately to one PA.

In prose this is slightly awkward, but acceptable when written in code font:

```text
A `Contents` is the thing displayed by a `ContentPanel`.
```

### PA

`PA` means publishable/published artifact. This is an established term in the model.

A PA is the selected/resolved publishable thing that contains a concrete artifact.

```text
PA
  = PATitle? + Artifact + Notes?
```

A PA may also be parameterised or optioned. That does not stop it being a PA.

The PA is the level at which a chart, table, or prose artifact becomes publicly meaningful.

### PASet

A `PASet` is a `Contents` containing multiple named PAs, with a public selector choosing which PA is visible.

```text
PASet
  = PASelector + PA+
```

`PA+` means one or more PAs. In practice, a meaningful `PASet` will usually contain two or more PAs.

The selected PA may be a chart, table, or prose PA. The selected PA may have its own options.

The control used to choose a PA is not semantically decisive. It might render as radio buttons, tabs, a dropdown, or another control. The model-level point is that a public option selects one PA from a set.

### Artifact

`Artifact` remains the concrete rendered artifact kind:

```text
Artifact
  = Chart | Table | Prose
```

This distinction matters for rendering, but it is not sufficient to classify the whole `Contents`.

Charts and tables can both have model-level options. Charts and tables can both be selected PAs. Charts and tables can both be backed by one source or many sources.

### PATitle

`PATitle` remains deliberately specific.

Plain `Title` is unsafe because the UI contains many title-like concepts:

```text
HTML <title>
site title
navigation caption
page heading
PA title
chart title
table caption
popover title
```

`PATitle` names the title/subtitle owned by the PA.

```text
PATitle
  = PAHead + PASubHead?
```

## Options

The earlier working assumption that options were mainly table controls is false.

Charts may also have public model-level options.

The important distinction is between:

```text
model-level Options
```

and:

```text
artifact-internal affordances
```

For example:

* Plotly zoom, hover, legend interaction, and toolbar controls are artifact-internal affordances unless explicitly promoted into the public model.

* Table sorting and column popovers are artifact-internal affordances unless explicitly promoted into the public model.

* Source selection, view selection, data-instance selection, row/trace filtering, and error-bar toggles are model-level options when exposed as public controls.

## OptionPanel and OptionGroup

`OptionGroup` should be reinstated as part of the model.

Options need grouping and sometimes nesting. This is not just a visual layout issue; it expresses the organization of public controls.

A cautious shape is:

```text
OptionPanel
  = OptionGroup+

OptionGroup
  = label?
  + OptionControl*
  + OptionGroup*
```

The exact notation can be refined, but the concept is required.

An `OptionGroup` may render visually in different ways depending on role and layout. The model should not assume that current prototype placement — for example, easy/obvious controls above advanced controls — is final public policy.

The control used to render an option is not semantically decisive:

```text
radio group
dropdown
checkbox
segmented buttons
popover-triggered help
```

These are rendering choices for model-level options.

## Option effects

Options may have different kinds of effects. They should not all be understood as column visibility or display toggles.

Known option effects include:

```text
select PA from PASet
select data source or data instance
select representation/view
filter rows or traces
toggle displayed evidence or uncertainty
toggle display of a derived/table/chart feature
```

The implementation mechanism may differ from the public option meaning.

For example:

* A public `View` option may be implemented by hiding and showing column groups.

* An `Active rikishi only` option may be implemented by hiding rows.

* A chart `Source` option may select between CSV files.

* An `Error bars` option may toggle Plotly trace properties.

The public option is not necessarily the same thing as the implementation mechanism.

## Option ownership and nesting

Options may occur at different levels:

```text
Contents-level
PASet selector level
selected-PA level
artifact/display level
```

This means the available options may depend on the selected PA.

For example, a `Career Length` PASet may have a top-level PA selector:

```text
View = Distribution | PMF | CDF | Survival | Longest
```

The selected `Longest` PA may then have its own option:

```text
Activity filter = all | active only
```

This is a selected-PA option, not necessarily an option that belongs equally to every PA in the PASet.

Changing the selected PA may therefore change the available selected-PA options.

## Option help versus Notes

Options do not have notes.

Option controls may have popover/help text, but that is not `Notes` in the PA model sense.

The rule is:

```text
Popover/help text may explain an option.
Notes belong to the PA.
```

Options may still affect which notes appear, but only indirectly by changing the selected/resolved PA state or the visible artifact components.

For example:

* An option changes which columns are visible; column-linked PA notes change accordingly.

* An option changes the selected PA; the selected PA's notes change accordingly.

* An option changes the chart source or visible traces; source/trace-linked PA notes may change accordingly.

## Notes

`Notes` remain part of `PA`:

```text
PA
  = PATitle? + Artifact + Notes?
```

Notes explain the displayed PA or relevant visible parts of its artifact.

Dynamic notes can be modelled as a mapping from a note to the thing it pertains to.

For tables today:

```text
note -> column
```

A note is shown when the column it pertains to is visible or relevant.

This can generalize to:

```text
note -> column
note -> trace
note -> source
note -> PA
note -> artifact component
```

The runtime assembles the notes relevant to the currently resolved PA state.

Visible placement does not by itself determine semantic ownership, but under the current decision there is no separate `Footing`; the visible notes section is the PA's notes section.

## Data binding and producer contract

The number of CSV files or data sources is implementation-relevant but should not by itself define a page type.

Multiple data sources may arise because:

```text
an option selects a source
an option selects a parameterised data instance
a PA selector selects a PA with its own source
derived displays are precomputed because client-side JS is not expected to compute them
```

The model should distinguish data binding from artifact kind and option rendering.

A useful division is:

```text
UI model / renderer contract:
  What public states exist?
  What controls select those states?
  What artifact kind is shown?
  What data object is loaded for each state?
  What notes are relevant?
  What visual/interaction affordances are required?

Producer contract:
  What files are emitted?
  What schema does each file have?
  What columns/traces/metadata/notes are declared?
  What public states do those files support?
  What provenance/methodology should be exposed?

Producer internals:
  How the data was computed.
  Which intermediate files existed.
  Which code paths generated the output.
```

The UI Model should define the concepts. The producer contract should define the concrete manifest/data shape by which a producer supplies those concepts to the renderer.

## Examples

### 2.2 Standings by Wins

This is a canonical rich table publication case.

It is not simply “one table with column visibility options.”

It is better understood as a parameterised table PA or `Contents`:

```text
Artifact kind:
  Table

Options include:
  number of basho
  view = standard | percentages | combined
  active rikishi only
  division

Data:
  one CSV per selected number of basho

Implementation mechanisms include:
  column/group hiding for view selection
  row hiding/filtering for active-only and division filters
```

The public options are not the same as the table mechanisms used to implement them.

The page is also important because:

* all columns are sortable;

* columns have popovers;

* some columns have notes;

* notes may respond dynamically to which columns are visible.

### 4.3.1 Banzuke Division by Era

This is a canonical simple chart PA case.

```text
Contents:
  PA

Artifact kind:
  Chart

Model-level options:
  none currently identified
```

Plotly controls are artifact-internal affordances, not public UI model options.

### 6.3.1 Win Probability by Standing

This is a chart with public model-level options.

```text
Contents:
  PA

Artifact kind:
  Chart

Options include:
  source = observed | equelo
  division
  error bars

Data includes:
  observed trace points
  equelo trace points
```

This demonstrates that chart pages may have options.

The options are public controls because they select or modify the chart state, not merely because the artifact is interactive.

### 7.3.1 Career Length

This is a multi-PA `Contents`.

Current selected PAs include:

```text
Distribution  -> Chart
PMF           -> Chart
CDF           -> Chart
Survival      -> Chart
Longest       -> Table
```

Each PA has its own source.

The significant model point is not that charts and tables are mixed. The significant point is that the nav node exposes a PASet, one PA of which is selected for display.

A proposed refinement is that `Longest` should have a selected-PA option:

```text
Activity filter = all | active only
```

This would replace or reduce the need for an activity column in the table.

This is a concrete case of a selected PA contributing its own options.

## Emerging model sketch

A cautious revised sketch is:

```text
PublicUI
  = Sidebar + ContentPanel

Sidebar
  = Caption + Navigation + Hider

ContentPanel
  = Heading + OptionPanel? + Contents

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

OptionPanel
  = OptionGroup+

OptionGroup
  = label?
  + OptionControl*
  + OptionGroup*
```

Open questions:

```text
Do we later need a formal taxonomy of option roles beyond `PASelector`?
```

Some previously open questions now have provisional answers:

```text
`Contents` is the settled name for the thing displayed by `ContentPanel`.
`PASet` is the settled name for selectable multi-PA contents.
`Options` remains the name of the options area; `OptionPanel` is not used.
`Item` is replaced by `PA`.
`PublicationUnit` is replaced by `Contents`.
`OptionGroup` is reinstated.
Options do not have `Notes`; they may have help/popover text.
There is no separate `Footing`; `Notes` remain part of `PA`.
A formal taxonomy of option roles beyond `PASelector` is not introduced yet.
```

## Settled model for now

The working model is now:

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

The only currently named option role is `PASelector`, because it is structurally required by `PASet`.

Other option effects remain descriptive for now. An `OptionControl` may select a data source, select a data instance, select a representation, filter rows/traces, or toggle display/evidence, but these are not yet promoted to formal model classes.

## Implementation implication, not yet adopted

If this proposal holds, the renderer should not be organized around page-specific assumptions such as:

```text
table pages have options
chart pages do not
multi-view pages are special cases
multiple CSVs define a page type
```

Instead, the renderer should be organized around:

```text
content panel
contents
PA selector if present
option panel / option groups
selected/resolved PA
artifact renderer
notes renderer
```

But this is a consequence to consider later, not a decision made by this note.

## Working principle

The old rendering remains prototype evidence. It may show useful behaviours, visual expectations, and edge cases, but it does not define the model.

The model should explain the useful behaviours intentionally, then the HTML/CSS/JS should be written by hand to implement the model.
