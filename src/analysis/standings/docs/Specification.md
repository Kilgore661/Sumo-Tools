# GSSWD Specification

## Version

Revised Working Specification

## Status

Current Baseline Specification

---

# 1. Product Identity

The application shall be called, provisionally:

**Grand Sumo Standings by Wins Digest**

Informal references such as **the standings page** are acceptable in supporting documentation.

---

# 2. Purpose

The application shall present rolling professional sumo standings over selectable retrospective periods.

It shall allow users to inspect comparative rikishi performance over recent basho using clear browser-based tables.

---

# 3. Publication Model

The application shall consume precomputed published standings artefacts.

The browser layer shall be responsible for presentation behaviour only, including:

* loading published data
* filtering
* sorting
* view selection
* visible ranking recalculation where specified
* display rendering

The browser layer shall not calculate core standings metrics from raw bout history.

---

# 4. Controls

The page shall provide the following user controls:

## 4.1 Number of Basho

A selector allowing the user to choose from the supported retrospective basho counts.

## 4.2 Division Filter

A selector allowing the user to restrict displayed rows by division.

Supported values shall include:

* All
* Makuuchi
* Juryo
* Makushita
* Sandanme
* Jonidan
* Jonokuchi

## 4.3 View

A selector allowing the user to choose one of three table views:

* Standard
* Percentages
* Combined

The default view shall be **Standard**.

## 4.4 Activity Filter

A binary control allowing the user to choose between:

* Current rikishi only
* All rikishi

The default activity setting shall be **Current rikishi only**.

For this purpose, a current rikishi is one who appears on the terminal banzuke of the selected reporting period.

---

# 5. Reporting Period

The page shall clearly identify the currently selected reporting period.

This shall include:

* selected basho count
* start of period
* end of period

---

# 6. ActivityBasis

`ActivityBasis` is a comparison-population dimension. It determines which rikishi are eligible to participate in displayed standings comparisons.

It is distinct from metric-definition dimensions such as `WinPolicy`, `BashoBasis`, and `BoutBasis`. Those dimensions govern metric interpretation after eligibility has been determined.

Initial supported values shall be:

* `CURRENT`
* `ALL`

## 6.1 `ActivityBasis.CURRENT`

Only rikishi appearing on the terminal banzuke of the selected reporting period are eligible for display.

“Terminal banzuke” means the banzuke of the most recent basho in the selected reporting period.

## 6.2 `ActivityBasis.ALL`

All rikishi represented in the standings result set for the selected reporting window are eligible for display.

This corresponds to unrestricted historical inclusion.

## 6.3 Scope

`ActivityBasis` affects:

* which rows are eligible for display
* displayed standings positions
* displayed row numbering

`ActivityBasis` does not affect:

* wins
* averages
* bout counts
* percentages
* other metric calculations for eligible rikishi

---

# 7. Metrics

## 7.1 Wins

**Wins** shall mean credited wins over the selected reporting period.

Wins include fusensho.

## 7.2 Average

**Average** shall mean:

> Wins divided by the selected number of basho

## 7.3 Bouts

**Bouts** shall mean expected bouts over the selected reporting period.

Expected bouts depend on the division in which the rikishi was scheduled to compete during each basho of the period.

## 7.4 Win %

**Win %** shall mean:

> Wins divided by Bouts, multiplied by 100

---

# 8. Display Identity

Each row shall identify a rikishi using:

* Shikona
* Chii

Displayed Shikona and Chii shall be taken from the end of the reporting period.

---

# 9. Sorting

All sortable visible metric columns shall support ascending and descending ordering.

The default page-load sort shall be:

* key: Average
* direction: descending

If a change of view removes the currently active sort key from visibility, the table shall revert to the default sort.

---

# 10. Position Semantics

A displayed position value shall always be calculated over the rows currently displayed after filtering.

Filtering includes division filtering and activity filtering.

Where ties occur, equal values may share the same position.

---

# 11. View Specifications

## 11.1 Standard View

Purpose:

A simple leaderboard based on average wins per basho.

Columns shall be:

| Pos. | Shikona | Chii | Wins | Average |

Semantics:

* `Pos.` means ranking by **Average**
* no row number column shall be shown

This shall be the default view.

---

## 11.2 Percentages View

Purpose:

A leaderboard based on wins relative to expected bout opportunity.

Columns shall be:

| Pos. | Shikona | Chii | Wins | Bouts | Win % |

Semantics:

* `Pos.` means ranking by **Win %**
* no row number column shall be shown

---

## 11.3 Combined View

Purpose:

A comparative analytical view showing both ranking systems simultaneously.

Columns shall be:

|   | Shikona | Chii | Wins | Average | Posn. (Average) | Bouts | Win % | Posn. (Win %) |

The first blank-heading column shall be a row number over the currently displayed rows.

Semantics:

* no single ranking is privileged
* both ranking systems shall be shown simultaneously
* the row number is presentational only

The Average block and Win % block should be visually separated.

---

# 12. Notes Section

The page shall contain a Notes section.

The Notes shall explain at minimum:

1. Displayed Shikona and Chii are those held at the end of the reporting period.
2. Wins include fusensho.
3. Bouts are expected bouts over the selected period and depend on division history.
4. Win % equals Wins divided by Bouts.

Notes may vary by selected view where useful.

---

# 13. Row Number Column

Where present, the row number column:

* shall begin at 1
* shall increase consecutively over displayed rows
* shall regenerate after filtering or sorting
* shall not be sortable
* shall be visually less prominent than ranking columns

---

# 14. Visual Behaviour

The interface shall prioritise clarity and readability.

Comparative metric blocks in Combined view shall be visually distinguishable.

No styling rule in this specification constrains exact colours, fonts, or CSS techniques unless explicitly stated.

---

# 15. Scope Boundaries

The current specification does not require:

* arbitrary custom date ranges
* user-defined formulas
* selectable win-policy variants
* advanced statistical dashboards
* opponent-strength adjustment
* predictive modelling

These may be considered in future revisions.

---

# 16. Authority

This document defines the intended externally visible behaviour of the application.

Implementation details, code structure, deployment mechanics, and current completion status are outside the scope of this specification.

---

# Appendix A — Probably Bad Ideas (Non-Normative)

The following ideas are recorded for future caution rather than adoption.

## A.1 Automatic Ellipsis / Truncated Table Mode

Replacing middle rows of long tables with ellipsis rows to reduce visual overload.

Reasons for caution include:

* many users prefer scrolling
* hidden rows create behavioural complexity
* may solve the wrong problem
* better addressed through optional summary modes if ever needed

This idea is deferred and not part of the current specification.
