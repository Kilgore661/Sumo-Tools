# Proposal: Replace G2 with G2b for Branch-Selected Contents

## Background

The current `make_site2` migration plan defines two grammars:

```text
G1:
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA+ . Note*
PA -> Title . Artifact
```

```text
G2:
ContentPanel -> Heading . Contents
Contents -> PA+ . Note*
PA -> Title . Artifact . FilterSection
```

G1 has worked well for ordinary nav entries.

However, applying G2 to `7.3.1 Career Length` exposed a problem. The grammar says that the contents contain `PA+`, so an implementation naturally rendered both the default-selected chart and the table. That is not the intended structure of Career Length.

Career Length should not show a chart and a table at the same time. It should first choose between **Chart** and **Table**, then show the filters and artifact for the selected branch.

Therefore, G2 should be replaced by a branch-selected grammar. For historical clarity, call this replacement **G2b**.

---

## Problem with G2

G2 models the page as:

```text
Contents -> PA+ . Note*
PA -> Title . Artifact . FilterSection
```

This means:

* there are multiple PAs;
* each PA may have its own filters;
* all PAs are structurally present in the contents.

That makes G2 suitable for “show several PAs, each with local filters.”

But Career Length is not that.

Career Length is:

```text
choose Chart or Table

if Chart:
  choose which chart
  show one chart

if Table:
  choose active/all
  show one table
```

The chart and table are alternative branches, not simultaneous contents.

---

## Replacement grammar: G2b

Replace G2 with:

```text
G2b:
ContentPanel -> Heading . Contents

Contents -> BranchSelector . Branch+ . Note*

Branch -> Tag . FilterSection . PA

PA -> Title . Artifact
```

Definitions:

```text
BranchSelector
  reader-visible control that selects exactly one Branch

Branch
  a named alternative contents branch

Tag
  public branch label, e.g. "Chart" or "Table"

FilterSection
  filters local to the selected Branch

PA
  the presentable artifact rendered for the selected Branch

Note*
  table notes, shown only when relevant to the selected Branch's visible table PA
```

Only the selected branch is rendered as the active contents branch.

The unselected branches may exist in the manifest/model, but their filters, artifacts, and notes are not visible unless their branch is selected. [The human notes: they should be visible but not enabled]

---

## Filter grammar remains unchanged

The filter grammar remains:

```text
FilterSection -> Filter*

Filter -> SimpleFilter | FilterGroup

FilterGroup -> Tag . Filter+
```

Filters still mean reader-visible controls that select/restrict what part of the available view is shown.

Filters do not have Notes.

---

## Notes rule remains unchanged

Notes remain table-specific.

Rules:

```text
Filters do not have Notes.
Charts do not have Notes.
Notes explain visible table content.
A Note is shown only when the relevant table PA is visible and the relevant table feature is visible.
```

Under G2b, this means that notes attached to the table branch are hidden when the chart branch is selected.

---

## Career Length as G2b

`7.3.1 Career Length` should be represented as:

```text
ContentPanel
  Heading: Career Length

  Contents
    BranchSelector:
      Chart | Table

    Branch: Chart
      FilterSection
        chart = distribution | PMF | CDF | survival

      PA
        Title: Charts
        Artifact: selected career-length chart

    Branch: Table
      FilterSection
        active = all rikishi | active only

      PA
        Title: Longest
        Artifact: longest-careers table

    Note*
      table notes only, visible only when the Table branch is selected
      and the relevant table feature is visible
```

This replaces the old flat interpretation:

```text
View = Distribution | PMF | CDF | Survival | Longest
```

with a nested interpretation:

```text
Branch = Chart | Table

if Branch = Chart:
  Chart = Distribution | PMF | CDF | Survival

if Branch = Table:
  Active = All | Active only
```

---

## Why this is not primarily a UX change

A renderer may later choose a compact UI that lets the user jump directly to a specific chart or table state in one click.

For example, the renderer might present:

```text
Distribution | PMF | CDF | Survival | Longest: All | Longest: Active
```

or some other flattened control.

That is a rendering optimization.

The semantic model should still be nested:

```text
select branch
then apply branch-local filters
then render selected branch PA
```

The layout must make clear that only one branch is active at a time.

---

## Updated grammar set

After this change, the active grammar set becomes:

```text
G1:
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA+ . Note*
PA -> Title . Artifact
```

```text
G2b:
ContentPanel -> Heading . Contents
Contents -> BranchSelector . Branch+ . Note*
Branch -> Tag . FilterSection . PA
PA -> Title . Artifact
```

G2 is retired.

Keep the name `G2b` temporarily for historical clarity, because it replaces the earlier G2 attempt.

---

## Updated current partition

Working partition:

```text
G1:
  7.1 Basho Results / BRB
  ordinary chart pages
  ordinary table pages
  finish_by_chii, once migrated

G2b:
  7.3.1 Career Length
```

---

## Manifest implications

A G2b manifest should make branch selection explicit.

Illustrative shape:

```json
{
  "page": {
    "id": "career_length",
    "title": "Career Length"
  },
  "contentPanel": {
    "heading": {
      "head": "Career Length"
    },
    "contents": {
      "grammar": "G2b",
      "branchSelector": {
        "id": "branch",
        "label": "Show",
        "default": "chart",
        "values": [
          { "id": "chart", "label": "Chart" },
          { "id": "table", "label": "Table" }
        ]
      },
      "branches": [
        {
          "id": "chart",
          "tag": "Chart",
          "filters": [
            {
              "id": "chart",
              "label": "Chart",
              "control": "radio",
              "default": "distribution",
              "values": [
                { "id": "distribution", "label": "Distribution" },
                { "id": "pmf", "label": "PMF" },
                { "id": "cdf", "label": "CDF" },
                { "id": "survival", "label": "Survival" }
              ]
            }
          ],
          "pa": {
            "id": "career_length_chart",
            "title": "Charts",
            "artifact": {
              "kind": "chart"
            }
          }
        },
        {
          "id": "table",
          "tag": "Longest",
          "filters": [
            {
              "id": "active",
              "label": "Rikishi",
              "control": "radio",
              "default": "all",
              "values": [
                { "id": "all", "label": "All rikishi" },
                { "id": "active", "label": "Active only" }
              ]
            }
          ],
          "pa": {
            "id": "longest_careers",
            "title": "Longest Careers",
            "artifact": {
              "kind": "table"
            }
          }
        }
      ],
      "notes": []
    }
  }
}
```

This shape is illustrative, not final. The essential requirements are:

* the contents identify `grammar: "G2b"`;
* there is a branch selector;
* there are named branches;
* each branch owns its local filters;
* each branch owns exactly one PA;
* only the selected branch's PA is rendered;
* table notes are shown only when relevant to the selected table branch.

---

## Rendering implications

A G2b renderer should follow this order:

```text
render heading
render branch selector
resolve selected branch
render selected branch filter section
render selected branch PA
render relevant notes for selected branch, if selected PA is a table
```

It should not render every branch's PA.

Pseudo-code:

```text
renderG2b(contents, state):
    branch = resolveBranch(contents.branchSelector, state)

    renderBranchSelector(contents.branchSelector, state)

    renderFilterSection(branch.filters, state)

    renderPA(branch.pa, state)

    if branch.pa.artifact.kind == "table":
        renderRelevantNotes(contents.notes, branch, state)
```

The renderer may optionally show branch-local filters directly beneath or beside the branch selector. The exact visual layout is separate from the grammar.

---

## Migration-plan edits required

Update the migration plan as follows.

### 1. Replace the G2 section

Replace the old G2 grammar:

```text
G2:
ContentPanel -> Heading . Contents
Contents -> PA+ . Note*
PA -> Title . Artifact . FilterSection
```

with G2b:

```text
G2b:
ContentPanel -> Heading . Contents
Contents -> BranchSelector . Branch+ . Note*
Branch -> Tag . FilterSection . PA
PA -> Title . Artifact
```

Explain that G2 was tried conceptually but allowed simultaneous rendering of chart and table PAs, which is not correct for Career Length.

### 2. Update “Why there are currently two grammars”

Say that there are two active grammars:

```text
G1:
  contents-level filters over one or more simultaneously rendered PAs

G2b:
  one selected branch from a set of branches, with branch-local filters and one PA
```

### 3. Update Phase 6

Rename:

```text
Phase 6: Add the G2 pressure case: Career Length / 7.3.1
```

to:

```text
Phase 6: Add the G2b pressure case: Career Length / 7.3.1
```

State that Career Length is a branch-selected page:

```text
Branch = Chart | Table

Chart branch:
  chart = distribution | PMF | CDF | survival
  artifact = chart

Table branch:
  active = all rikishi | active only
  artifact = longest-careers table
```

### 4. Update the model case-study partition

Replace:

```text
G2:
  7.3.1 Career Length
```

with:

```text
G2b:
  7.3.1 Career Length
```

### 5. Update acceptance criteria

Add:

```text
[ ] Career Length renders only the selected branch.
[ ] Selecting Chart shows chart filters and the selected chart artifact.
[ ] Selecting Table shows table filters and the longest-careers table.
[ ] The chart and table are not rendered simultaneously.
[ ] Table notes are hidden when the Chart branch is selected.
```

---

## Open question

Can G1 and G2b later be merged into one more general grammar?

Probably yes, but not yet.

For now, keeping them separate is helpful:

```text
G1:
  simultaneous PA group with shared filters

G2b:
  mutually exclusive branch selection with branch-local filters
```

This separation prevents implementation ambiguity and keeps the Career Length structure explicit.
