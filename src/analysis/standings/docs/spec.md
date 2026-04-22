Here is a revised **Specification** section/doc aligned with the current direction and the files now in the conversation.

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

It is not initially a win-rate-per-bout metric. Current browser behaviour displays `selected_average_credited_wins`.

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
* Bouts
* Mean

Current HTML uses exactly these headings. 

Where:

* `#` = current published first-column field, presently sourced from backend `position`
* Wins = total credited wins across selected period
* Bouts = total expected bout opportunities across selected period
* Mean = average credited wins per selected basho

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

This area should explain, at minimum:

* what Wins means
* what Bouts means
* what Mean means
* that the page presents one chosen standings interpretation rather than every possible one

Current HTML includes a Notes section, though its content is not yet finalised. 

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
* rate-based metrics
* strength-adjusted rankings
* expert or advanced analytical options 

---

## 16. Source of Truth

This specification defines intended behaviour for the published application.

Where implementation diverges from this document, the implementation should be considered provisional and subject to correction.

Where older exploratory documents conflict with the current implementation and current project-position notes, they should be treated as historical rather than authoritative.
