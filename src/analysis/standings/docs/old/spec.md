# Specification

## 1. Purpose of the Application

The application publishes rolling sumo standings in a simple browser-based format.

It allows users to inspect recent multi-basho performance through a small set of predefined views without requiring direct access to source data or command-line tooling.

The application is intended to provide clear, current standings rather than a fully general historical analytics platform. This reflects the current project position that the real product is a published standings application built on top of a standings engine, not merely the engine itself. 

---

## 2. Product Scope

The published application shall provide:

* standings over supported retrospective basho windows
* division filtering
* sortable tabular output
* clear display of standings period
* stable metric definitions
* static deployment with precomputed data

The application shall not initially provide:

* arbitrary custom date ranges
* arbitrary anchor dates
* user-entered query parameters
* live server-side computation
* advanced analytical controls
* exhaustive historical exploration tools

Standings shall be computed offline and served as static artefacts, with browser-side JavaScript used only for loading, filtering, sorting, and rendering.

---

## 3. Supported Basho Windows

The application shall support a fixed published set of retrospective windows.

Initial supported values are:

* 1
* 2
* 3
* 4
* 5
* 6
* 12
* 18
* 24
* 36
* 60

These values represent the number of basho included in the standings period. The published site configuration currently exposes exactly this set.

---

## 4. Default Basho Window

The default selected basho window shall be the number of basho in the most recent calendar year represented in `History`.

Operationally, this is determined by scanning backward through the ordered history dates until the most recent January basho is found, then counting from that January basho to the end of the history snapshot.

If no January basho exists in `History`, publication shall terminate immediately with a descriptive error rather than guessing a default. Current publisher behaviour implements this rule. 

This default is then written into the published site configuration and consumed by the browser application.

---

## 5. Standings Period Semantics

For a selected value `N`, the standings period is the latest contiguous set of `N` available basho ending at the published anchor basho.

The effective start and end dates of the selected period shall be published in metadata sidecar files and used by the browser page for display. Current sidecars publish:

* `anchor_date`
* `direction`
* `num_basho`
* `effective_start_date`
* `effective_end_date` 

---

## 6. Division Filtering

The application shall support the following division filters:

* All
* Makuuchi
* Juryo
* Makushita
* Sandanme
* Jonidan
* Jonokuchi

The default visible division shall be Makuuchi. Current HTML and site config both reflect this.

Filtering shall be applied in the browser using the published `chii_ordinal` value associated with each row. Current browser behaviour derives division membership from `Math.floor(chii_ordinal / 100000)`. 

The exact historical semantics of stricter division-membership filtering are deferred.

---

## 7. Row Identity Semantics

Each standings row represents one rikishi.

Displayed identity fields shall include:

* shikona
* chii

Displayed identity shall be sourced from the most recent selected basho within the standings period in which the rikishi appears. Current derived-view behaviour does this by locating the latest selected basho containing the rikishi and taking both `shikona` and `chii` from that basho. 

This means the displayed shikona and chii are representative end-of-period identity labels, not summaries of the whole observed period.

---

## 8. Public Standings Metric Model

The published application shall use one fixed default standings model.

### 8.1 Wins Policy

Wins shall mean **credited wins**.

Credited wins include:

* fought wins
* fusensho or equivalent awarded wins recognised by the source data model

Displayed Wins values are totals across the selected standings period. The current browser displays `credited_wins`.

### 8.2 Basho Basis

The published application shall use **SELECTED** basho basis.

All basho within the chosen standings period are in scope. This basis is part of the formal internal model, though it is not currently exposed as a user control.

### 8.3 Bout Basis

The published application shall use **EXPECTED** bout basis.

Expected bout opportunity shall be determined per basho according to the rikishi’s historical division status in that basho.

Current rules are:

* sekitori basho: 15 expected bouts
* lower-division basho: 7 expected bouts

Current Python view logic computes these expected counts explicitly per basho and aggregates `selected_expected_bout_count` for publication. 

### 8.4 Mean

Mean shall mean the average credited wins per basho across the selected standings period.

Mean is therefore:

```text
total credited wins / selected basho count
```

It is not a wins-per-bout rate. Current browser behaviour displays `selected_average_credited_wins`.

### 8.5 Percentage

The table shall also expose a percentage metric derived from Wins and Bouts.

Percentage shall mean:

```text
credited wins / expected bouts
```

expressed as a percentage over the selected standings period.

This metric provides an opportunity-normalised companion to Wins and Mean.

---

## 9. Ranking and Sorting Semantics

The browser table shall support client-side sorting of sortable visible columns. Current browser behaviour sorts client-side and does not perform standings calculations. 

Default page-load sort shall be:

* key: Mean
* direction: descending

This matches current browser state, which initializes sorting on `selected_average_credited_wins` descending. 

When a user first clicks the **Shikona** column, its initial sort direction shall be ascending. Current browser behaviour implements this special case. 

Published row order from the backend is deterministic for developer convenience and stable exports, but shall not be treated as the authoritative semantic ordering of the browser table. Current derived-view code explicitly comments that published row order should not be treated as semantic ranking contract. 

---

## 10. Table Columns

The primary standings table shall initially display:

* `#`
* Shikona
* Chii
* Wins
* Mean
* Bouts
* `%`

The columns are intentionally arranged in two blocks.

### 10.1 Standings block

The left-hand standings block shall be:

* `#`
* Shikona
* Chii
* Wins
* Mean

Where:

* `#` = current published first-column field, presently sourced from backend `position`
* Wins = total credited wins across selected period
* Mean = average credited wins per selected basho

This block presents the primary standings story.

### 10.2 Context and rate block

After Mean there shall be a visual separator, followed by:

* Bouts
* `%`

Where:

* Bouts = total expected bout opportunities across selected period
* `%` = Wins divided by Bouts, expressed as a percentage

This block provides denominator context and efficiency/rate interpretation.

The precise long-term semantics of the first column remain unresolved and are not fixed further by this specification.

---

## 11. Page Titles and Labels

The page shall have a stable product heading and a dynamic table heading.

### 11.1 Product Heading

The primary page heading and browser `<title>` should identify the application as the Ozumo standings page and should be aligned with one another. Current implementation has not yet fully converged on the final preferred wording, so exact final text remains provisional. The presently committed HTML still shows older wording. 

### 11.2 Dynamic Table Heading

The table heading shall show the selected retrospective scope and date range in integrated form.

Current preferred form is:

```text
Standings (Last N basho, MMM YYYY to MMM YYYY)
```

with the earliest date first and the latest date second.

Current browser behaviour already renders this integrated heading using published sidecar dates converted to abbreviated month-year form.

---

## 12. Notes and Interpretation

The page shall provide a notes area or equivalent explanatory space.

The first Notes should explain, at minimum:

1. that the displayed shikona and chii are those held at the end of the reporting period
2. that Bouts is the number of bouts the rikishi was expected to fight over the selected basho, taking account of the division they were in at the time

Short examples may be used where helpful.

The published standings table is intended as one coherent rolling-performance view. It does not claim to equalise:

* strength of schedule
* division difficulty
* total opportunity across all rikishi
* participation continuity
* every possible notion of fairness

It provides one stable and intelligible interpretation of recent standings performance. 

---

## 13. Data Publication Model

Standings shall be computed offline and published as static artefacts.

For each supported basho window, publication shall produce:

* a standings dataset
* a corresponding metadata sidecar
* bootstrap site configuration for the browser client

Current publisher and reporting modules implement exactly this model.

The browser application shall consume published artefacts and shall not perform standings calculations. 

---

## 14. Browser Behaviour

The browser layer shall support:

* selection of supported basho window
* division filtering
* client-side sorting of visible columns
* rendering of standings rows
* display of standings period metadata

The browser layer shall remain a presentation consumer of precomputed data. Current JS responsibilities match this description. 

---

## 15. Internal Model and Deferred Controls

The underlying application model recognises richer concepts than the page currently exposes, including:

* alternative win policies
* BashoBasis (`SELECTED`, `CONTAINING`)
* BoutBasis (`EXPECTED`, `AVAILABLE`)

These internal model concepts are real and useful, but not every such axis belongs in the public UI. Current class definitions already include `WinKind`, `WinPolicy`, `BashoBasis`, and `BoutBasis`. 

The following are explicitly deferred as user-facing controls:

* selectable win policy
* selectable basho basis
* selectable bout basis
* strict division-membership filters
* rate-based metrics beyond the default `%`
* strength-adjusted rankings
* expert or advanced analytical options 

---

## 16. Source of Truth

This specification defines intended behaviour for the published application.

Where implementation diverges from this document, the implementation should be considered provisional and subject to correction.

Where older exploratory documents conflict with the current implementation and current project-position notes, they should be treated as historical rather than authoritative.

## ## Specification Patch 1 — View Selector and Mode-Dependent Table Layout

This patch extends the presentation-layer specification by introducing a user-selectable table view mode.

It supersedes any earlier wording that assumed a single fixed visible table layout.

---

## 1. New User Control: View

In addition to the existing controls for:

- number of basho

- division

the page shall provide a **View** selector.

The selector shall allow the user to choose between three canonical table layouts.

The initial implementation may use a radio-button group.

The exact widget is a design choice, provided the three modes are clearly visible and mutually exclusive.

---

## 2. Supported View Modes

The View selector shall initially support the following values.

### 2.1 Standard (default)

Visible columns:

- row number

- Shikona

- Chii

- Wins

- Mean

- Pos.

Meaning:

A simplified standings view focused on total credited wins and average wins per basho.

The visible `Pos.` column in this mode is the ranking on **Mean**.

This shall be the default page view.

---

### 2.2 Percentages

Visible columns:

- row number

- Shikona

- Chii

- Wins

- Bouts

- %

- Pos.

Meaning:

A comparative efficiency view focused on wins relative to expected bout opportunity.

The visible `Pos.` column in this mode is the ranking on **%**.

---

### 2.3 Full

Visible columns:

- row number

- Shikona

- Chii

- Wins

- Mean

- Pos.

- Bouts

- %

- Pos.

Meaning:

A combined view showing both production-rate and efficiency metrics.

The first `Pos.` column is the ranking on **Mean**.

The second `Pos.` column is the ranking on **%**.

---

## 3. Row Number Column

The first visible column shall remain a presentational row-number column.

Its properties are:

- blank heading

- not sortable

- values `1, 2, 3, ...` over the currently displayed rows

- regenerated after filtering and sorting

- styled so as to remain readable without drawing attention away from the substantive metrics

This column is not itself a standings metric.

---

## 4. Sorting Semantics by View

The active visible `Pos.` column or columns shall sort on the metric from which they are derived.

Therefore:

### Standard

- `Pos.` sorts on **Mean**

### Percentages

- `Pos.` sorts on **%**

### Full

- first `Pos.` sorts on **Mean**

- second `Pos.` sorts on **%**

The default page-load sort remains:

- key: **Mean**

- direction: descending

If the current sort key ceases to be visible after a view change, the page shall revert to the default sort.

If the current sort key remains visible in the new view, it may be preserved.

---

## 5. Notes and View Mode

The page Notes remain part of the page contract.

At this stage, the Notes may remain fixed across all view modes.

However, the implementation shall not assume that Notes are permanently mode-independent.

Future revisions may vary visible Notes according to the selected View.

This possibility is acknowledged now, but no formal Notes model is required at this stage.

---

## 6. Implementation Boundary

This View selector is a **presentation-layer concern only**.

No standings-engine or publisher changes are required provided all displayed metrics are already present in the published dataset.

The browser layer shall control:

- which columns are shown

- which `Pos.` columns are shown

- how row numbering is displayed

- sort fallback behaviour when view changes

---

## 7. Current Position

The introduction of View modes reflects the distinction between at least two user needs:

- a simpler headline standings view

- a more comparative, denominator-aware view

The default shall favour simplicity.

The richer views remain available without becoming the initial burden on every user.

## Spec patch #2 - don't go there!

## Deferred Idea Note — Ellipsis / Compressed Table Mode

### Actual Idea

Some users are put off by **large tables**.

A table can feel “large” simply because it contains many visible rows, even when the data is straightforward.

Therefore:

> Can a long standings table be presented as a shorter table?

One possible answer is to show selected rows and replace the omitted middle section with an ellipsis row.

Example:

```text
Standings (Last 60 basho, Mar 2016 to Mar 2026)

1   Daieisho    ...
2   Mitakeumi   ...
3   Takayasu    ...
...
42  Midorifuji  ...
```

This is a **psychological simplification** idea rather than a geometry/layout idea.

---

## Why the Idea Appeared Attractive

The concern is not lack of screen space.

The concern is that some users may see many rows and think:

- too much information

- too many numbers

- too complicated

- I do not want to process this

A shorter-looking table may feel more approachable.

---

## Relation to Viewport Height

Viewport height is only one factor.

If compressed mode existed, a short viewport might strengthen the case for using it, because fewer rows are visible comfortably.

But even with a tall viewport, the same idea might still appeal if the table has many rows.

So the true question is:

> how many rows should a simplified table show?

not:

> how short is the viewport?

---

## Why the Idea Is Not an Obvious Winner

### 1. Many Users Prefer Complete Tables

Some users will reasonably say:

> I can scroll.

or:

> Show me all rows and let me decide what matters.

For them, ellipses feel like unnecessary concealment.

---

### 2. Hidden Rows Require Rules

Compressed mode immediately raises questions:

- top how many rows?

- bottom how many rows?

- fixed number or adaptive number?

- should current sort key matter?

- should ties be preserved?

- what if there are only 12 rows total?

These are design choices, not neutral mechanics.

---

### 3. It May Address Symptoms, Not Causes

If users are intimidated, the real causes may instead be:

- too many columns

- unfamiliar metrics

- dense styling

- unclear defaults

Shortening the row count may not solve the real issue.

---

## Current Project Position

This idea is **deferred**.

The project currently prefers:

- complete table

- normal scrolling

- simplified default columns where helpful

rather than automatic row compression.

---

## If Revisited Later

Treat as an explicit presentation mode, e.g.:

- Compact View

- Summary View

- Top & Bottom Only

rather than hidden automatic behaviour.

Or find something else to do. Really.

---

## 
