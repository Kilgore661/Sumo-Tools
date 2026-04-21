# Specification (some minor adjustments; WIP)

## 1. Purpose of the Application

The application publishes rolling sumo standings in a simple browser-based format.

It allows users to inspect recent multi-basho performance through a small set of predefined views without requiring direct access to source data or command-line tooling.

The application is intended to provide clear, current standings rather than a fully general historical analytics platform.

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

These values represent the number of basho included in the standings period.

The standings period shall be retrospective from the latest available published basho unless explicitly revised later.

---

## 4. Default Basho Window

The default selected basho window shall be:

* the number of basho that have occurred in the current calendar year, if one or more have already occurred
* otherwise 6

This provides a natural current-year default while retaining a sensible fallback.

---

## 5. Standings Period Semantics

For a selected value `N`, the standings period is the latest contiguous set of `N` available basho.

Example:

If the latest available basho is 2026/03 and `N = 5`, the standings period consists of the five most recent available basho ending at 2026/03.

The application shall display the effective start and end dates of the selected period.

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

The default visible division shall be Makuuchi.

Filtering shall be applied to each rikishi using the published display-rank identity associated with that standings row.

The exact historical semantics of stricter division-membership filtering are deferred.

---

## 7. Row Identity Semantics

Each standings row represents one rikishi.

Displayed identity fields shall include:

* shikona
* chii

Displayed identity shall be sourced from the most recent relevant basho within the selected standings period in which the rikishi appears.

This keeps displayed identity contemporary relative to the selected standings window.

---

## 8. Public Standings Metric Model

The published application shall use one fixed default standings model.

### 8.1 Wins Policy

Wins shall mean **credited wins**.

Credited wins include:

* fought wins
* fusensho or equivalent awarded wins recognised by the source data model

Displayed Wins values are totals across the selected standings period.

### 8.2 Basho Basis

The published application shall use **SELECTED** basho basis.

All basho within the chosen standings period are in scope.

No adjustment is made in the public default view to remove basho simply because a rikishi was absent from some part of the wider historical timeline.

### 8.3 Bout Basis

The published application shall use **EXPECTED** bout basis.

Expected bout opportunity shall be determined per basho according to the rikishi’s historical division status in that basho.

Initial rules are:

* sekitori basho: 15 expected bouts
* lower-division basho: 7 expected bouts

Expected opportunities are summed across the selected standings period.

### 8.4 Mean

Mean shall mean the average credited wins per basho across the selected standings period.

Mean is therefore:

```text id="7kvvdb"
total credited wins / selected basho count
```

It is not initially a win-rate-per-bout metric.

---

## 9. Ranking and Sorting Semantics

The browser table shall support client-side sorting of sortable visible columns.

Initial default sort order shall be:

* Shikona ascending

Numeric columns may sort numerically. Text columns may sort lexically.

The leftmost row-number column shall not be sortable.

Where ties occur in metric values, deterministic ordering shall be used.

Exact tie-break implementation details are not part of this specification provided outputs remain stable and intelligible.

---

## 10. Table Columns

The primary standings table shall initially display:

* Row number (blank heading)
* Shikona
* Chii
* Wins
* Bouts
* Mean

Where:

* Row number = visible row order after filtering and sorting
* Wins = total credited wins across selected period
* Bouts = total expected bout opportunities across selected period
* Mean = average credited wins per selected basho

The row-number column is presentational and does not imply formal ranking semantics.

---

## 11. Page Titles and Labels

The browser page `<title>` and primary heading shall be:

```text id="zn4u40"
Ozumo Standings
```

The table heading shall be of the form:

```text id="4p4m1t"
Standings for Last N basho (MMM YYYY to MMM YYYY)
```

where:

* `N` is the selected basho count
* the earliest date is shown first
* the latest date is shown second

Example:

```text id="4q8oz5"
Standings for Last 5 basho (Jul 2025 to Mar 2026)
```

---

## 12. Interpretation Notes

The published standings table is intended as one coherent rolling-performance view.

It does not claim to equalise:

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
* corresponding metadata sufficient for browser display

The browser application shall consume published artefacts and shall not perform standings calculations.

---

## 14. Browser Behaviour

The browser layer shall support:

* selection of supported basho window
* division filtering
* client-side sorting of visible columns
* rendering of standings rows
* display of standings period metadata

The browser layer shall remain a presentation consumer of precomputed data.

---

## 15. Non-Goals (Initial Release)

The following are explicitly deferred:

* selectable win policy
* selectable basho basis
* selectable bout basis
* strict division-membership filters
* statistical confidence displays
* arbitrary historical anchor-date browsing
* custom user-defined standings formulas

---

## 16. Source of Truth

This specification defines intended behaviour.

Where implementation diverges from this document, the implementation should be considered provisional and subject to correction.

----------------------
Looks good to me. Thinking ahead, where is the specification not correctly implemented?
----------------------
Quite a few places, in fact. The new spec is ahead of the current UI.

## Clear mismatches

### 1. Page title / primary heading

The spec says the page title and primary heading should be **“Ozumo Standings”**. The current HTML still uses **“Simple Standings”** in both the `<title>` and the page title element. 

### 2. Table heading text

The spec says the table heading should be of the form:

> Standings for Last N basho (MMM YYYY to MMM YYYY)

The current page only renders a generic **“Standings”** heading, while the date range is shown separately in another element as raw `YYYY/MM` strings.

### 3. Leftmost column semantics

The spec says the first column should be:

* blank heading
* row number
* not sortable

The current HTML still labels it **“Pos”**, and the JS renders `row.position`, i.e. competition rank from the dataset, not visible row number after sort/filter. It is also still declared as a sortable header because it has a `data-column` attribute.

### 4. Column heading “Bouts”

The spec now says the heading should be **“Bouts”**. The current HTML still says **“Count”**. 

### 5. Default sort

The spec now says default sort should be **Shikona ascending**. The current JS still initialises sorting with:

* `sortColumn: "containing_average_fought_wins"`
* `sortDescending: true`

So the actual default sort is still the old mean-style descending basis, not Shikona ascending. 

### 6. Header sort keys no longer match rendered semantics

The rendered data has been partly updated to the new standard:

* Wins = `credited_wins`
* Bouts value = `selected_expected_bout_count`
* Mean = `selected_average_credited_wins`

But the HTML headers still advertise old sort columns:

* Wins header: `data-column="fought_wins"`
* Count header: `data-column="bout_count"`
* Mean header: `data-column="containing_average_fought_wins"`

So even where the displayed values match the new model, the clickable sort semantics do not.

### 7. Default basho window

The spec now says the default should be:

* number of basho so far in the current calendar year, else 6

The current site config still hard-codes `default_num_basho` to **6**.

### 8. Notes section

The Notes are now badly out of sync with the spec. In particular they still say:

* **Mean is Wins divided by Count**
* relevant basho set is currently basho **containing** the rikishi
* selected-basho mode is something for later 

All of that conflicts with the current intended spec, where the public model is already **CREDITED + SELECTED + EXPECTED**, and Mean is per selected basho, not Wins divided by expected bouts.

## Partial matches

Some things are already aligned, at least partly.

### 1. Displayed Wins / Bouts / Mean values

The JS now renders:

* `credited_wins`
* `selected_expected_bout_count`
* `selected_average_credited_wins`

which does match the core public metric model in the spec.

### 2. Division list and default division

The available divisions and default `makuuchi` are consistent with the spec.

### 3. Static publication model

The publisher/browser split remains consistent with the spec.

## One possible spec/code tension to watch

The spec says Mean is:

> average credited wins per basho across the selected standings period

That matches `selected_average_credited_wins`, so that is fine. But it no longer has any direct mathematical link to **Bouts**, which users may assume from the table layout. That is not an implementation mismatch, but it is a presentational tension you may want the Notes to explain clearly.

## In short

The main gaps are:

* branding/title
* heading/range formatting
* first-column semantics
* column label “Bouts”
* default sort
* sortable header bindings
* default `num_basho`
* Notes text

The core metric values are much closer to spec than the surrounding UI chrome is.

