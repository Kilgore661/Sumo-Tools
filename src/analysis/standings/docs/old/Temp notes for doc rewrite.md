# Current Project Position (Temporary Working Note)

This document records the present understanding of the standings project following recent implementation and policy decisions.

It is a temporary working note intended to stabilise the repository until a full coherent rewrite of Requirements, Specification, Design, and Implementation documents is completed.

It supersedes informal notes where inconsistent, but is not itself intended as the final permanent documentation.

---

# 1. What the Project Is

The project is no longer best understood as merely a standings engine.

It is now a **simple published standings application** built on top of an existing standings engine.

The intended user-facing product is:

* a browser-based standings page
* showing current rolling standings
* backed by precomputed published data
* hosted statically
* simple to operate
* understandable to ordinary users
* capable of modest future extension

The standings engine remains an important subsystem, but is not itself the whole product.

---

# 2. Current Architecture

The project currently consists of four broad layers.

## 2.1 Standings Engine

Responsible for:

* standings calculations
* basho-window selection logic
* win counting logic
* ranking logic
* derived metrics generation

## 2.2 Publication Layer

Responsible for:

* generating supported standings datasets
* generating metadata sidecar files
* packaging outputs for deployment
* copying assets to the web host

## 2.3 Static Website Assets

Responsible for:

* HTML structure
* CSS presentation
* JavaScript interaction

## 2.4 Browser Layer

Responsible for:

* loading published datasets
* changing supported basho windows
* division filtering
* sorting visible columns
* rendering table content

The browser layer does not calculate standings.

---

# 3. Fixed Public Metric Choices

The published standings page now uses one deliberate default model.

## 3.1 Wins Policy: CREDITED

Wins are counted as credited wins:

* fought wins
* fusensho

This reflects official standings credit rather than only physically fought bouts.

## 3.2 Basho Basis: SELECTED

The user chooses a retrospective window of `N` basho.

All basho in that selected window are in scope.

Examples:

* last 5 basho
* last 12 basho
* last 24 basho

## 3.3 Bout Basis: EXPECTED

Opportunity is counted historically per basho:

* sekitori basho = 15 expected bouts
* lower-division basho = 7 expected bouts

This reflects historical division status during the selected window.

## 3.4 Mean

Mean is the selected-window average credited wins per selected basho.

It is not currently a wins-per-bout rate.

---

# 4. Why These Choices Were Made

These choices provide:

* one clear public standings metric
* stable outputs
* simple interpretation
* recent-form emphasis
* historically aware denominators
* no need for advanced user controls

They suit the intended lightweight published standings page.

---

# 5. What These Choices Do Not Claim to Do

The current page does **not** claim to provide:

* equal denominators for every rikishi
* equal strength of schedule
* division-pure comparisons
* research-grade causal inference
* every possible standings interpretation

It provides one coherent rolling standings view.

---

# 6. Internal Model Richness vs Public Simplicity

The underlying engine is richer than the page currently exposes.

Internally, the project recognises concepts such as:

* alternative win policies
* alternative basho bases
* expected vs available counts
* richer comparative metrics
* future filtering semantics

Not every valid internal axis belongs in the public UI.

This distinction is intentional.

---

# 7. BashoBasis Position

`BashoBasis` remains analytically real:

* `SELECTED`
* `CONTAINING`

However, for typical users examining recent upper-division performance, the difference is often negligible.

Therefore BashoBasis is currently treated as:

* an internal modelling concept
* a documented methodology issue
* a possible future expert option

It is **not** currently a main-page user control.

---

# 8. Future Candidate Controls

More natural future enhancements may include:

* fought wins only
* strict division membership filters
* full-window participation filters
* rate-based metrics
* strength-adjusted rankings
* advanced/expert options

These remain optional and deferred.

---

# 9. Identity Semantics

Displayed identity fields such as:

* shikona
* chii

should reflect the most recent relevant basho within the selected standings period, unless explicitly revised later.

This keeps displayed identity contemporary relative to the chosen standings window.

---

# 10. Current Source of Truth

Where legacy notes conflict with committed code and this document:

1. committed implementation behaviour
2. this working note

take precedence over older exploratory documents.

Older documents may remain historically useful, but are not automatically authoritative.

---

# 11. Documentation Cleanup Position

The repository now contains material from multiple phases of thinking.

The next major documentation task should be a coherent top-down rewrite covering:

* Requirements
* Specification
* Design
* Implementation

After that rewrite, legacy and duplicate documents should be retired aggressively.

---

# 12. Final Position

The project currently has:

* a functioning standings engine
* a functioning publication model
* a functioning browser presentation layer
* a fixed public standings metric
* a clearer understanding of future extensibility

The immediate need is no longer conceptual exploration.

It is consolidation.

