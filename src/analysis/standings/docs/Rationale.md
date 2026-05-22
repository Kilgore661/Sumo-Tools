# GSSWD Architecture & Rationale Appendix

## Status

Companion document to the current GSSWD Requirements, Specification, and Design & Implementation Notes.

This appendix is explanatory rather than normative. It records the reasoning, historical context, architectural choices, and conceptual discoveries that shaped the current product definition.

Its purpose is to preserve useful knowledge that does not naturally belong in formal requirements or specification text.

---

# 1. Project Evolution

## 1.1 Original Starting Point

The project began as the development of a **standings engine** operating over canonical historical professional sumo data.

The early focus was computational rather than product-oriented. Primary concerns included:

* selecting basho windows
* counting wins under defined policies
* ranking rikishi
* producing structured outputs
* supporting command-line workflows
* generating reusable reports

This phase successfully produced a capable analytical subsystem.

## 1.2 Later Realisation

Subsequent reflection clarified that the standings engine was **not itself the final product**.

The real user-facing goal was a simple published standings application allowing ordinary users to inspect recent rolling standings in a browser.

This later understanding did not invalidate the engine work. Rather, it repositioned the engine as one layer within a larger system.

## 1.3 Consequence

The documentation set was therefore revised from the top down so that:

* user needs drive requirements
* browser behaviour is clearly specified
* publication workflows are recognised explicitly
* engine responsibilities remain properly bounded

---

# 2. Governing Product Philosophy

## 2.1 Practical Usefulness Over Theoretical Completeness

The product exists to help real users answer practical questions such as:

* who is doing well lately?
* who leads my division?
* how has a rikishi performed over recent basho?

It does not initially exist to expose every possible analytical degree of freedom.

When trade-offs arise:

> usefulness to ordinary users takes priority over theoretical completeness.

## 2.2 Simplicity Without Dishonesty

The page should be simple, but not misleading.

If a metric depends on conventions, those conventions should be explainable.

If a limitation exists, it should be clear.

## 2.3 Stable Behaviour Matters

Users should be able to learn the page once and return confidently.

Stable terminology, predictable controls, and consistent ranking behaviour are valuable product features.

---

# 3. Why Static Publication Was Chosen

## 3.1 Nature of the Product

The standings application is fundamentally:

* read-mostly
* periodic rather than continuous
* table-oriented
* modestly interactive
* not dependent on per-user state
* suitable for batch refresh rather than live transaction processing

## 3.2 Benefits of Static Publication

Publishing precomputed artefacts offers substantial advantages:

* no database required
* no runtime standings computation
* no application server required
* low hosting complexity
* strong reliability
* easy deployment to simple web hosts
* easy mirroring between local and remote environments

## 3.3 Performance Benefit

Because standings calculations are completed offline, the browser can feel immediate and lightweight during normal use.

Routine actions such as:

* changing reporting windows
* sorting
* filtering
* switching views

should feel responsive because no historical recomputation is occurring.

---

# 4. Layered System Responsibilities

The project is intentionally divided into clear responsibilities.

## 4.1 Standings Engine

Responsible for:

* correctness of standings calculations
* interpretation of historical data
* metric generation
* ranking logic
* output datasets

## 4.2 Publication Layer

Responsible for:

* producing supported datasets
* naming and packaging artefacts
* copying assets to hosting locations
* refresh workflows

## 4.3 Browser Layer

Responsible for:

* loading published data
* filtering
* sorting
* view switching
* visible ranking recalculation where required
* rendering tables and notes

## 4.4 Why This Matters

This separation avoids mixing:

* domain logic with presentation logic
* hosting concerns with calculation concerns
* user interaction code with historical data logic

---

# 5. Template-First Front-End Philosophy

## 5.1 Rejected Direction

A fully JS-generated shell with little meaningful HTML was considered and rejected.

## 5.2 Preferred Direction

The page should be a **real HTML document first**, enhanced by JavaScript.

Meaning:

* HTML contains real structure
* headings exist before JS runs
* representative content may exist
* page source remains inspectable
* template can be edited directly
* CSS can be developed visually
* JS upgrades dynamic regions

## 5.3 Why This Is Valuable

This preserves:

* maintainability
* debuggability
* graceful degradation
* compatibility with traditional web workflows
* a tangible page rather than an empty shell

---

# 6. Progressive Enhancement Principle

The page should exist before JavaScript runs.

JavaScript improves the page; it does not create the universe.

Where possible:

* if live data fails, the page should still be a page
* if scripts fail, structure should remain intelligible
* if enhancements are unavailable, core content should degrade gracefully

This principle should guide future changes even where implementation details evolve.

---

# 7. Why Supported Windows Are Fixed

The application currently publishes predefined retrospective basho counts rather than arbitrary user-defined ranges.

Reasons include:

* operational simplicity
* predictable dataset set
* low UI complexity
* faster browser behaviour
* clearer product scope
* sufficient usefulness for most users

This does not deny future expansion, but it is an intentional present choice.

---

# 8. Metric Model Discoveries

## 8.1 Early Simplicity

Early standings thinking focused mainly on wins totals.

Later work revealed that apparently simple columns such as counts and averages carry multiple hidden policy choices.

## 8.2 Distinct Conceptual Axes

Three separate dimensions emerged.

### Win Basis

Examples:

* fought wins only
* credited wins including fusensho

### Basho Basis

Examples:

* selected reporting window
* basho in which the rikishi actually appeared

### Bout Opportunity Basis

Examples:

* expected bouts
* actually available recorded bouts

These dimensions should not be casually conflated.

## 8.3 Why This Matters

A figure such as “59 wins from 59 bouts” and a figure such as “59 wins from 60 expected bouts” may both be valid, but answer different questions.

Good product behaviour depends on choosing and explaining one basis clearly.

---

# 9. Why Notes Matter

The Notes section is not decorative.

It exists because concise tables cannot carry all semantic nuance without becoming cluttered.

Notes may explain matters such as:

* wins include fusensho
* bouts are expected bouts
* displayed rank/name are representative end-period values
* ranking basis depends on view
* current reporting period conventions

This supports both casual and serious users.

---

# 10. Known Product Tensions

These tensions are normal and should be managed consciously.

## 10.1 Simplicity vs Power

Casual users prefer obvious rankings.

Advanced users often want richer metrics and controls.

## 10.2 Static Publishing vs Flexibility

Static artefacts simplify operations.

Some future features may favour richer runtime behaviour.

## 10.3 Uniform Tables vs Purpose-Specific Views

One universal table simplifies code.

Separate views often better match user intent.

## 10.4 Density vs Clarity

Serious users often tolerate dense tables.

Broader audiences may prefer less cognitive friction.

---

# 11. Scope Discipline

Useful projects often drift toward becoming monsters.

The standings application should resist uncontrolled expansion.

Not every interesting analytical possibility belongs in the first product.

Features should generally be added when they satisfy real user value, not merely because they are possible.

---

# 12. Relationship Between Code and Requirements

The current codebase is valuable, but existing implementation should not dictate future requirements automatically.

Where tension exists:

* requirements should reflect genuine product needs
* specification should describe intended behaviour
* implementation should evolve toward those goals

This avoids accidental lock-in to historical expedients.

---

# 13. Desktop-First Position

The current product primarily optimises for desktop/laptop browser use.

Reasons include:

* tabular data density
* comparative scanning across columns
* comfortable sorting/filtering interactions
* available screen width

Mobile usability is desirable, but not the primary initial design centre.

---

# 14. Why The Engine Still Matters

Although users encounter the browser page, the underlying standings engine remains strategically important.

It provides:

* correctness
* reproducibility
* future extensibility
* alternate publication possibilities
* confidence in published outputs

The browser page should be seen as a consumer of a valuable core capability.

---

# 15. Future Directions (Non-Committed)

Possible future developments may include:

* richer filtering
* alternate metric views
* expert mode controls
* historical archive browsing
* additional explanatory tooling
* improved mobile presentation
* automated publication pipelines
* comparative analytics beyond wins

These remain possibilities, not promises.

---

# 16. Final Position

The current architecture is intentionally pragmatic.

It combines:

* a serious analytical core
* simple publication workflows
* lightweight browser delivery
* user-centred presentation

This balance should be preserved unless future evidence justifies greater complexity.

The standing rule for future decisions should be:

> keep what is simple, clear, fast, and trustworthy unless a stronger reason exists to change it.

