## Preamble / Context

The project originally began as the development of a **standings capability** operating over historical sumo data.

The early focus was therefore on the computational engine: defining requirements for standings calculations, specifying ranking behaviour, implementing basho-window aggregation, supporting alternative win definitions, and producing structured outputs suitable for further use.

That work was successful and produced a coherent standings subsystem with clear separation between calculation logic and reporting outputs.

At that earlier stage, however, the requirements concerning the **final user-facing product** were intentionally vague. Presentation, publication, and ordinary user interaction were not yet fully understood, and were therefore not strongly represented in the original requirements, specification, or implementation.

Subsequent reflection approached the problem from the perspective of a potential end user rather than from the perspective of an analyst or developer. This clarified that the intended outcome was not merely a standings engine, but a **simple published standings application** allowing users to view current standings conveniently in a browser.

That later understanding led to the concept of a presentation layer built around:

* a static website
* precomputed standings data
* limited user controls
* clear tabular presentation
* practical deployment to a constrained legacy host

The present document has therefore been written to record the implementation consequences of adding that presentation layer to an already-existing standings project.

It is not intended as a perfect historical account of the whole project, nor as a complete re-specification of every earlier decision.

Rather, its purpose is to provide **traceability**:

* how the project moved from standings engine to standings application
* what new requirements emerged
* how those requirements affect implementation
* how the presentation layer fits alongside the existing engine

In that sense, this document describes the **retrofitting of a presentation layer onto a mature computational core**, while preserving the original strengths of the underlying standings capability.

# Implementation Overview (Current Understanding)

This section describes how the presentation layer is to be implemented in support of the standings capability and the revised presentation-layer specification.

The implementation is divided into a small number of clear responsibilities.

---

## 1. Data Publication

The standings engine remains the source of standings calculations.

An offline publication step shall generate the datasets required by the website for each supported retrospective basho count.

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

For each supported value, the publisher shall run standings generation using the agreed fixed policy:

* latest available data
* backwards-looking scope
* chosen wins mode
* chosen output columns

The result shall be a published dataset for browser consumption.

---

## 2. Published Artefacts

For each supported basho-window value, publication shall produce:

### 2.1 Standings Data File

A machine-readable standings dataset (initially CSV unless revised).

This file shall contain the columns required by the page.

### 2.2 Metadata Sidecar File

A corresponding metadata file shall be produced for the same dataset.

This shall contain information such as:

* retrospective basho count
* effective start date
* effective end date
* anchor date
* wins mode
* any title text or descriptive labels [Ed.: Design or implementation?]

The browser page shall use published metadata rather than reconstructing standings periods itself.

---

## 3. Publication Contract

The publisher and browser page depend on a stable contract.

This includes:

* dataset naming conventions
* sidecar naming conventions
* required columns
* metric meanings
* identity semantics
* metadata fields

Where filenames are used to pair data files with sidecar files, code comments shall warn against uncoordinated changes.

---

## 4. HTML Template

The website page shall be implemented as a real HTML template rather than an empty JavaScript shell.

The template shall contain:

* page title / heading area
* selector for basho-window size
* selector for division
* standings table
* notes area
* stable element IDs / classes for JavaScript hooks

Representative placeholder rows may be included for development convenience.

Notes content is initially fixed and part of the template.

---

## 5. CSS

Styling shall be separated into external CSS.

This shall control:

* overall page layout
* title area
* control panel
* table appearance
* sorting indicators
* notes area
* responsive behaviour [Ed.: Requirement, design choice, or unnecessary ambition?]

The current design intent is desktop-first presentation.

---

## 6. JavaScript Behaviour

JavaScript shall provide browser-side interaction only.

It shall not calculate standings.

Its responsibilities include:

* loading the selected standings dataset
* loading corresponding metadata
* populating the standings table
* updating the displayed title/range
* filtering by division
* sorting visible columns
* rendering shikona links
* updating any dynamic notes text if later required

The JavaScript layer should remain small and subordinate to the template.

---

## 7. Division Filtering

Supported division values are:

* All
* Makuuchi (default)
* Juryo
* Makushita
* Sandanme
* Jonidan
* Jonokuchi

Filtering shall be derived from published `chii_ordinal` values using the agreed mapping.

---

## 8. Sorting

The page shall support sorting of visible columns.

Initial default sort is expected to be:

* Mean descending

Other sort behaviours shall be determined by column type.

[Ed.: Exact tie-break and persistence behaviour may belong in Design.]

---

## 9. External Links

Displayed shikona values may link to external rikishi pages (for example SumoDB).

[Ed.: Exact URL format and target site belong in Design / Implementation.]

---

## 10. Deployment / Refresh

A publication step shall copy updated assets to the hosted environment.

This includes:

* HTML
* CSS
* JavaScript
* standings datasets
* metadata sidecars

The host is assumed to be simple and storage-constrained.

Accordingly, only supported current datasets are published.

---

## 11. Verification

Verification in this project means checking that contracts are satisfied, not adding defensive runtime complexity.

Checks may include:

* each configured basho-window value produces outputs
* datasets and sidecars pair correctly
* metadata dates are correct
* division filtering matches `chii_ordinal`
* sorting behaves as intended
* titles reflect metadata
* links are formed correctly

This may occur as developer checks or publication-step assertions rather than runtime error-handling.

---

## 12. Guiding Principle

The implementation should preserve the project’s existing architectural strengths:

* standings logic in the engine
* presentation logic in the browser
* publication logic offline
* clear contracts between layers
* minimal unnecessary complexity

---

## 13. Immediate Work Items

1. Finalise published file formats.
2. Finalise metadata sidecar schema.
3. Finalise HTML IDs/classes/hooks.
4. Implement JavaScript loader/filter/sort/render logic.
5. Finalise CSS polish.
6. Add shikona external links.
7. Script publication/update process.
8. Test end-to-end publication and page behaviour.

