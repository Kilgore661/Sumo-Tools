# Public Site Contract

## Status

Current consolidated contract for the generated public Sumo-Tools site.

This document consolidates the requirements, specification, and design notes
that previously lived as separate current docs.  Those source notes are
preserved under `reference/`:

* `reference/Public Site Requirements.md`
* `reference/Public Site Specification.md`
* `reference/Public Site Design.md`

The intention is not to erase the working history.  The intention is to provide
one live document that says what the site is meant to be, while leaving the
source notes available for audit and reconstruction.

## 1. Purpose

The public site must make professional sumo more legible through data.

It should present curated analysis outputs, explanatory tools, selected
research narratives, and public-facing tables/charts in a way that can be
understood without private project context.

The site should not publish every artefact the repository can generate.  Raw
downloaded HTML, parser diagnostics, warning reports, cache files, source data
archives, and superseded experiment outputs must not appear in public
navigation merely because they are browser-readable.

## 2. Implementation Shape

The site is a generated static site.

The public web server should not need:

* a database;
* a Python runtime;
* an application server;
* a dynamic public API;
* user accounts;
* server-side runtime computation.

Client-side JavaScript is allowed for interactive pages.

The implementation weight should remain small.  A Python site builder and a
template engine such as Jinja are appropriate.  Full web frameworks,
application frameworks, Streamlit/Dash-style analytical servers, and
database-backed public APIs are not part of the current contract.

## 3. Site Model

The site has:

* a site title;
* a subject-led navigation tree;
* a registry of renderable pages;
* shared static assets;
* generated output suitable for local and remote deployment.

The site definition describes the intended public structure.  It is distinct
from:

* runtime UI state, such as selected division or selected source;
* build config, such as output and deployment locations;
* legacy/prototype artefact layout.

When there is tension, the site definition is authoritative.  Existing
artefacts may be used to implement it only when they conform to the definition.
Compatibility hacks should be local, explicit, and temporary.

## 4. Navigation

Navigation is organised primarily by subject, not by user type.

Reader expertise remains important, but it should be handled by page framing,
defaults, progressive disclosure, tabs, filters, notes, and optional detail,
not by making "expert" a top-level navigation area.

A navigation node has:

* a human-facing label;
* a stable slug or key;
* zero or more child nodes;
* optionally, a page reference;
* optionally, status/readiness/depth metadata.

A navigation node need not be a page.  Organising nodes may exist only to group
related public subjects.  A page node references a page in the page registry.

Routes are stable public paths derived from the navigation tree and page
registry, not from incidental source filenames or legacy generated paths.

## 5. Pages

A page has:

* a stable id;
* a human-facing title;
* a summary;
* an optional options model;
* a view/body specification;
* data dependencies;
* static asset dependencies;
* public status/readiness metadata.

The provisional page grammar remains:

```text
title / options / body
```

or:

```text
title bar
options panel
main view
```

The site shell itself may be understood as:

```text
site title
site navigation
selected page body
```

This model is useful, but should not be overengineered into a general content
management system.

## 6. Options and Controls

The options model describes page state.

It is not the same thing as the HTML controls used to expose that state.

Examples:

```text
division: all | makuuchi | juryo | ...
source: observed | equelo | combined
show_error_bars: true | false
selected_standings: list[standing]
```

Controls are a design concern:

* dropdowns or radio groups for enum choices;
* checkboxes/toggles for booleans;
* tabs for sibling views;
* sliders or numeric inputs for numeric parameters.

Pages with no adjustable state should have no options model, or an explicit
empty/null equivalent.

## 7. View Types

The site should support a small set of view types, including:

* table tools;
* Plotly charts;
* explanatory essays;
* standalone HTML artefacts where still appropriate;
* custom interactive pages.

`custom` is the escape hatch.  It should exist, but it should not become the
default answer to every awkward page.

Unknown future page types should be represented through explicit metadata and a
limited custom-rendering escape hatch.

HTML-fragment view support was removed on 2026-05-09 because it had no current
users and blurred ownership between producer-rendered markup and `make_site`
rendered pages.  Producers that naturally emit prose should prefer Markdown or
structured metadata consumed by an explicit `make_site` renderer.

## 8. Page Bundles and Producers

Analysis packages may publish public-site material through a page bundle or
equivalent metadata.

A bundle should identify:

* page metadata;
* navigation placement, if the producer owns it;
* options model, if any;
* view type;
* files required to render the page;
* data files required by the page;
* static assets required by the page;
* public/candidate/research/internal status;
* enough provenance to explain what was computed.

The exact file format may evolve.  Python objects, JSON, YAML, or generated
metadata are all implementation choices.  The important contract is semantic:
the producer owns the analysis-specific knowledge, and `make_site` owns the
public shell, navigation, route, theme, and common presentation grammar.

## 9. Prototype Embeds and Promotion

Embedding or copying existing HTML is acceptable for prototypes, stress tests,
and information-architecture experiments.

That mode is useful for asking:

* whether an output fits naturally under a proposed navigation node;
* whether the subject-led organisation makes sense;
* whether a page is interesting enough to promote;
* whether a topic needs a new section.

It is not the general public-site contract.

When an artefact is promoted toward a real public page, the producer should be
modified additively to emit site-facing data/config/metadata.  The site builder
should consume intentional public-site inputs rather than reverse-engineering
old generated HTML.

Existing standalone charts, diagnostic HTML, CSVs, notebook-like reports, and
debug artefacts may remain.  They do not become the API.

## 10. Legacy v9 Migration

Legacy Elo v.9 deliverables are product and analytical sources, not final
implementation units.

For each candidate legacy page:

1. identify the public question;
2. understand what v9 computed or presented;
3. specify the navigation placement and page shape;
4. reimplement the deliverable under Sumo-Tools where appropriate;
5. expose it through the same public-site contract as other pages.

Old v9 HTML may provide:

* public-question clues;
* page concepts;
* data lineage hints;
* UI ideas;
* explanatory language;
* examples of what not to preserve.

It should not permanently define public routes, styling, page grammar, or data
contracts.

## 11. Interactive Tables and Charts

The site must support interactive tables and charts, including:

* sortable standings tables;
* banzuke change reports;
* Plotly charts;
* page-level options such as division selectors, trace selectors, and toggles.

The data and behaviour needed for such pages should be generated before
deployment.

For public charts, design and site-wide review should consider:

* axis ranges;
* labels;
* legends;
* default traces;
* note placement;
* sample-size visibility;
* confidence intervals or equivalent uncertainty indicators where appropriate;
* interaction affordances for Plotly controls.

Plotly pages should ideally move toward:

```text
chart data + chart config + shared page template
```

rather than large standalone HTML files, once promotion to public page status
is justified.

## 12. External Links and Shikona Links

External links inside embedded or custom-rendered content must not navigate the
Sumo-Tools content frame.  They should open outside the frame in a new tab or
window according to the visitor's browser configuration.

All shikona links should have consistent appearance and behaviour across public
tables, charts, and notes:

* normal click opens the rikishi's SumoDB page;
* Alt-click opens the corresponding Gaspode-san graph page;
* both targets open outside the Sumo-Tools content frame;
* titles/tooltips should advertise the click and Alt-click behaviour;
* non-unique shikona should use the shared qualified-shikona contract when the
  graph token differs from the displayed shikona.

## 13. Chii and ChiiLabel Wording

Do not use "rank" as a substitute for `Chii`, chii, or `ChiiLabel` in technical
documentation, page contracts, generated metadata, code comments, or policy
notes.

Use:

* `Chii` for the class/object;
* `chii` for full human-facing chii values such as `M3eHD`;
* `ChiiLabel` for project-defined chii-like labels such as `M3`, `O`, or
  `Jd100`.

This matters especially for Equelo rating landmarks, where a `ChiiLabel` is
mapped to a rating landmark but is not itself a rating.

## 14. Equelo Naming and Rating Landmarks

The current public Equelo rating-landmark curve is:

```text
Mark 3.2.1(2000)
```

The `Typical Equelo Ratings` page uses this curve.

Names such as `v0`, `v1`, ..., `v5` are local diagnostic chart stages in the
fixed-v1 audit trail.  They are not model names and should not appear in public
navigation or ordinary page titles.

Use `Equelo Rating Landmark Policy`, not `V5 Landmark Policy`, for public or
site-level wording.

The full naming policy lives in `Equelo Version Naming.md`.

## 15. Theme and Presentation Coherence

The public site should feel coherent.

Pages may differ by type, but they should not feel like unrelated HTML files
randomly placed in one frame.

Shared navigation, page framing, typography, colour, link behaviour, table
styling, chart conventions, and explanatory language are part of the public
product.

Tables should generally be no wider than their columns require and should be
horizontally centred unless a page has a documented reason for full-width
layout.

Public labels should read naturally for ordinary visitors where possible, while
technical docs preserve precise terminology where precision matters.

## 16. Explainability and Caveats

Public pages must make interpretation honest.

Observed descriptive outputs should not be presented as stronger claims than
they support.  Modelled outputs should make their assumptions visible.

Where sample size, support, calibration, missing data, data-source limits, or
method caveats matter, the page must expose them in an appropriate form.

## 17. Static Output and Deployment

The site builder shall:

1. read the site/navigation definition;
2. read page bundles or page metadata;
3. derive page routes from the navigation tree;
4. generate the site shell and page routes;
5. copy or render required static assets, data files, and page bodies;
6. write a static output tree;
7. support deployment of that output tree to local and remote targets.

The generated output tree should include:

* site index;
* generated page HTML;
* JavaScript;
* CSS;
* data files;
* images and other static assets;
* copied local assets required by pages.

Build and deployment are separable.

## 18. Current Non-Requirements

The first real site does not require:

* user accounts;
* server-side runtime computation;
* a database-backed public API;
* a full single-page application framework;
* complete migration of all v9 ideas;
* publication of all generated Sumo-Tools artefacts.

Those should be reconsidered only when later requirements justify them.
