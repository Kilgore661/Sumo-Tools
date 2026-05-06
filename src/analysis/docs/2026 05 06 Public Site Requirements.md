# Public Site Requirements

This note records requirements for the eventual public Sumo-Tools site.

It is intentionally separate from specification and design. Requirements say
what must be true from the product, project, and reader point of view. They do
not prescribe the final implementation.

Related notes:

* `2026 05 03 Presentation Layer.md`
* `2026 05 05 Site Navigation Overview.md`
* `2026 05 06 The Site - Provisional Model and Stress Test.md`

## 1. Purpose

The public site must make professional sumo more legible through data.

It should present curated analysis outputs, explanatory tools, and selected
research narratives in a way that can be understood without private project
context.

The site should not publish every artefact the repository can generate.

## 2. Content Sources

The site must be able to draw from three sources of possible content.

### A. Sumo-Tools

The current project.

This is the primary source of public-facing artefacts and the home for the
final implementation.

### B. Elo v. 9

The legacy project/site.

Legacy v9 content may be valuable, but final B1 deliverables should be
reimplemented under Sumo-Tools rather than permanently copied as old HTML.

### C. Future Ideas

The site must leave room for future pages and questions not represented in
either current codebase.

## 3. Relevance Status

Candidate content must be classified by relevance to Sumo-Tools as a
public-facing entity.

### 1. Directly Relevant

Current or legacy outputs that answer, or nearly answer, a clear public
question.

### 2. Could Be Relevant

Outputs, experiments, or ideas that may become public after more framing,
design, or implementation work.

### 3. Not Relevant

Diagnostics, raw source artefacts, pipeline outputs, warning reports, and
superseded experiments that should not become public navigation.

## 4. Navigation Principle

The public site must be organised primarily by subject, not by user type.

Earlier thinking used casual/interested/expert users as a primary axis. That
axis remains useful for presentation, but not for the main navigation.

Readers should self-select by subject and by page-level controls, explanations,
and depth.

## 5. Reader Range

The site must accommodate readers with different levels of numerical comfort.

Some readers will prefer official-looking tables, plain language, and minimal
chart exposure. Other readers will want details, controls, caveats, and
model/research views.

This should be handled inside pages through framing, progressive disclosure,
tabs, filters, defaults, and explanations rather than by creating a separate
"expert section" as the primary organisational model.

## 6. Public Versus Internal Artefacts

The site must distinguish public deliverables from internal project artefacts.

Raw downloaded HTML, parser diagnostics, warning reports, cache files, and
source data archives must not appear in public navigation merely because they
are HTML or browser-readable.

## 7. Static Hosting

The public site must be deployable as static files.

The public web server should not need a database, Python runtime, application
server, or dynamic API to serve the normal site.

Client-side JavaScript is allowed for interactive pages.

## 8. Interactive Pages

The site must support interactive tables and charts.

Examples include:

* sortable standings tables
* banzuke change reports
* Plotly charts
* page-level options such as division selectors, trace selectors, and toggles

The data and behaviour needed for such pages should be generated before
deployment.

## 9. Package Independence

Analysis packages should not each become unrelated mini-sites with their own
navigation, styling, deployment assumptions, and public language.

Packages may generate public deliverables, but those deliverables should be
incorporated through a common site layer.

## 10. Legacy Migration

Legacy v9 deliverables should be treated as product and analytical sources, not
as final implementation units.

For a B1 artefact, the desired path is:

1. identify the public question;
2. understand what v9 computed or presented;
3. reimplement the deliverable under Sumo-Tools;
4. expose it through the same public-site contract as other Sumo-Tools pages.

## 11. Prototype Status

The current `src/analysis/site` package is disposable.

It is useful as evidence about information architecture and page-fitting, but
it should not constrain the final implementation.

## 12. Theme and Coherence

The final public site should feel coherent.

Pages may differ by type, but they should not feel like unrelated HTML files
randomly placed in one frame.

Shared navigation, page framing, typography, colour, and explanatory language
are part of the public product.

## 13. Explainability and Caveats

Public pages must make interpretation honest.

Observed descriptive outputs should not be presented as stronger claims than
they support. Modelled outputs should make their assumptions visible.

Where sample size, support, calibration, or method caveats matter, the page
must expose them in some appropriate form.

## 14. Non-Requirements for the First Real Site

The first real site does not require:

* user accounts;
* server-side runtime computation;
* a database-backed public API;
* a full single-page application framework;
* complete migration of all v9 ideas;
* publication of all generated Sumo-Tools artefacts.

Those can be reconsidered only if later requirements justify them.
