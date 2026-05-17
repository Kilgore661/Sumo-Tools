Below is a complete draft of the synthesis doc with the two existing findings cleaned up, plus the missing **#3 framing text** item and the new **#4 Options layout** item.

```markdown
# Case Study Synthesis Findings

## Status

This document records candidate findings that emerge while comparing UI Model case studies.

It does **not** update the UI Model or the implementation contract directly.

The intended workflow is:

```text
case studies
  -> candidate synthesis findings
      -> later comparison
          -> one considered update to the model and/or implementation contract
```

A finding recorded here is therefore provisional. It should be tested against later case studies before being adopted.

For now, this document is allowed to be a bucket for things to know, preserve, or think about while the case studies are being worked through.

---

## Candidate finding 1: options may divide into content selectors and filters

While beginning the `6.3.1 Win Probability by Standing` case study, an important distinction emerged.

Model-level `Options` may fall into two broad kinds:

```text
OptionControl
  = ContentSelector | Filter
```

This is not yet an adopted model change.

### Content selectors

A `ContentSelector` is a control that determines which content, PA, data source, or data instance is being displayed.

It changes what must be resolved or loaded.

Examples so far:

```text
Win Probability by Standing:
  Source = observed | equelo
  selects observed_trace_points.csv or equelo_trace_points.csv

Career Length:
  View = Distribution | PMF | CDF | Survival | Longest
  selects a PA from a PASet

Standings by Wins:
  Number of Basho
  selects the backing CSV / data instance
```

`PASelector` appears to be a special case of `ContentSelector`, because it selects the visible PA from a `PASet`.

### Filters

A `Filter` is a control that modifies the visible representation of already-selected content.

It may filter rows or traces, toggle visibility, select a representation, or show/hide an evidence layer.

Examples so far:

```text
Win Probability by Standing:
  Division
  Error bars

Standings by Wins:
  Division
  Active Rikishi Only
  View = standard | percentages | combined
```

The term `Filter` is being used broadly here. It does not only mean database-style row filtering.

For example:

```text
Error bars
  filters/toggles a visible evidence layer

View = standard | percentages | combined
  changes the visible representation, implemented by column/group visibility
```

### Why this may matter

The distinction appears to have renderer and state implications:

```text
ContentSelector
  may change what PA, data source, or data instance must be loaded or resolved

Filter
  operates within the selected/resolved content
```

This may affect:

```text
state ownership
URL state
option ordering/grouping
reset/remember behaviour
manifest structure
renderer update flow
```

### Current decision

Do not update the UI Model yet.

Keep the current model as:

```text
Options
  = OptionGroup+

OptionGroup
  = label?
  + OptionControl*
  + OptionGroup*
```

For now, `OptionControl` remains general, except for the already-named `PASelector` required by `PASet`.

Test the `ContentSelector | Filter` distinction against additional case studies before adopting it.

---

## Candidate finding 2: case studies should be read sequentially

The case studies should not be treated as isolated checklist entries.

They should be read in order, with each case building on what earlier cases established.

For each new case, use two lenses:

```text
1. Difference lens
   What does this case add that earlier cases did not require?
   Does the new concern appear local to this case,
   or does it suggest a site-wide concern?

2. Similarity lens
   Does the new concern disturb the existing happy path?
   Or does it simply extend the path already established?
```

For example:

```text
4.3.1 Banzuke Division by Era
  establishes the simple chart PA happy path:
    ContentPanel
      Heading
      Contents = PA
        PATitle
        Chart Artifact

6.3.1 Win Probability by Standing
  adds Options to the chart PA happy path:
    ContentPanel
      Heading
      Options
      Contents = PA
        PATitle
        Chart Artifact

  Difference:
    options are now present;
    source selection and filtering must be handled.

  Similarity:
    it remains a single chart PA;
    the structured ChartArtifact path still holds.
```

This method avoids forcing a premature checklist. At this stage, the case studies are not merely documenting known categories; they are helping discover what the categories and checklist should be.

The draft checklist is therefore itself a deliverable from the case-study process.

After the main case studies have been completed, the checklist should be tested against PA examples that were not used as case studies.

If the checklist works on those non-case-study examples, it can become a practical tool for adding new PA items.

If it fails, the failure is useful evidence:

```text
Either:
  the checklist is incomplete;

or:
  the new PA exposes a genuinely new model or renderer concern.
```

For now, the synthesis document can act as a bucket for both:

```text
model / renderer findings
method / process findings
```

Later, these can be reorganized into a cleaner implementation method or checklist.

---

## Candidate finding 3: framing text needs ownership-specific names

Several case studies expose the same underlying structure:

```text
Head + SubHead?
```

but at different ownership levels.

The important distinction is not the shape of the text block, but who owns it and what job it does.

### Navigation label

```text
NavLabel
```

Requirement:

```text
short enough for navigation
```

A navigation label is a locator. It may be compressed and may be somewhat unclear if unavoidable. It is not responsible for fully explaining the page.

### Content heading

```text
Heading = Head + SubHead?
```

Requirement:

```text
enough page-level framing for the reader to understand what they selected
and why the major options, default column headings, or default chart traces exist
```

The `Head` should ideally be concise. If more context is needed, use `SubHead`.

### PA title

```text
PATitle = PAHead + PASubHead?
```

Requirement:

```text
the PA plus its heading/subheading should be copy-pasteable
as a largely self-contained analytical object
```

`PATitle` is artefact-level framing. It is distinct from the page/content heading.

### Artifact-internal labels

Examples:

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

If the meaning cannot be made clear inside the label itself, use a PA `Note`.

For tables, column headings should remain compact, especially when they do not span sub-columns. Explanatory burden belongs in notes rather than bloated column labels.

### Notes

Notes remain part of the PA.

They may carry meaning that cannot fit into compact artifact labels. This is especially important if the table/chart should be copy-pasteable with enough context to remain intelligible.

### Avoid bare “Title”

Bare `Title` is unsafe as a model term because it collides with several different concepts:

```text
HTML <title>
browser title
site title
navigation label/title attributes
content heading
PA title
Plotly layout.title
table caption
popover title
```

The model should therefore use ownership-specific names:

```text
NavLabel
Heading / Head / SubHead
PATitle / PAHead / PASubHead
Artifact labels
```

The current model can keep:

```text
ContentPanel = Heading + Options? + Contents

PA = PATitle? + Artifact + Notes?

PATitle = PAHead + PASubHead?
```

but should explicitly state that `Heading` and `PATitle` have similar internal shape while having different owners and different jobs.

### Open pressure point

Options currently may have help/popover text but not Notes.

This remains acceptable for now.

If a future option needs persistent explanation that is not adequately handled by help/popover text, that will be a concrete model pressure point. Until such an example is found, Notes remain PA-owned.

---

## Candidate finding 4: Options layout may need a public ordering policy

The case studies should preserve and test an existing intended option-layout policy:

```text
simple / obvious / primary options at the top
gnarly / expert / advanced options at the bottom
```

The intention is that readers encounter the easiest and most important choices first.

Defaults should normally correspond to the simplest or most expected choices.

This is currently a policy candidate, not a settled rendering rule.

### Why this matters

`Options` are not just a bag of widgets.

Their order and grouping communicate how the page is meant to be read.

A poor option layout can make a page feel more complex than it is, or can foreground expert/diagnostic controls before the reader understands the basic public view.

### Things to test across case studies

For each optioned case, ask:

```text
Which options are simple or primary?
Which options are advanced or expert?
Are defaults the simplest/most expected choices?
Does current visual order match that intended interpretation?
Does grouping help or obscure the intended order?
Does the distinction still work when options include both ContentSelectors and Filters?
Does the distinction still work for selected-PA-specific options?
```

### Examples to review

```text
6.3.1 Win Probability by Standing
  Source
  Error bars
  Division

7.3.1 Career Length
  PASelector / View
  selected-PA-specific options such as Longest -> Show active only

2.2 Standings by Wins
  Number of Basho
  View
  Active Rikishi Only
  Division
```

### Possible future model/rendering implications

This may imply that `OptionGroup` or `OptionControl` needs presentation metadata such as:

```text
priority
complexity
primary / advanced
default-visible / collapsed
preferred order
```

But this should not be added to the model yet.

For now, record it as a cross-case-study issue.

### Current decision

Do not update the UI Model yet.

During case-study review, check whether the current pages actually follow the intended simple-to-advanced ordering, and whether that policy remains workable.
