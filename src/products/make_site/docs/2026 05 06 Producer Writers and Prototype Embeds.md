# Producer Writers and Prototype Embeds

This memo records the current position on incorporating pre-existing project
material into the public site.

It follows from the site stress test and the discussion of the Equelo
`entrant_initial_ratings_v<n>.html` charts.

## 1. The Problem

The project already produces many HTML artefacts.

Some were written before a public site existed as a serious design target.
Their styling, page structure, JavaScript, titles, controls, and assumptions
therefore reflect the needs of the original analysis moment rather than the
needs of a coherent Sumo-Tools public site.

The question is:

> What should happen when one of those artefacts appears to belong under a
> public-site navigation node?

The tempting answer is to copy or iframe the artefact. That is sometimes
useful, but it should not become the general public-site contract.

## 2. Prototype Rule

For a prototype, stress test, or information-architecture experiment, it is
acceptable to stuff an existing HTML artefact into the site with an iframe or a
simple copy.

This is useful when the immediate question is:

* Does this output fit naturally under the proposed navigation?
* Does the subject-led organisation still make sense?
* Does this kind of material need a new section, or does it already have a
  natural home?
* Is the page interesting enough to promote later?

In this mode, the goal is learning, not final integration.

The existing producer should not be rewritten just to answer a navigation
stress-test question.

## 3. Promotion Rule

If a pre-existing artefact is promoted toward being a real public-site page,
the producer should be modified additively.

The producer should gain a new Sumo-Tools/public-site writer that emits the
inputs the site builder needs.

This does not mean deleting the old output. Existing standalone charts,
diagnostic HTML, CSVs, notebook-like reports, and debug artefacts may remain
where they are.

It means adding another writer whose contract is:

```text
analysis package
  computes the analysis
  writes existing outputs as before
  also writes site-facing data/config/metadata

make_site
  consumes the site-facing material
  renders the public page consistently
```

The important point is not whether the final rendering uses Jinja, Plotly,
iframes, or some other mechanism.

The important point is that the public site consumes intentional public-site
inputs rather than reverse-engineering old HTML.

## 4. What a Site-Facing Writer Emits

The exact shape may vary by page type, but a site-facing writer may emit:

* chart data;
* table data;
* page metadata;
* option definitions;
* chart configuration;
* explanatory text fragments;
* references to local assets;
* enough provenance to explain what was computed.

For a chart page, this might be JSON data plus a small metadata/config file.

For a table app, it might be CSV/JSON files plus a site config.

For an essay-like method page, it might be Markdown or an HTML fragment plus
metadata.

The producer owns the analysis-specific knowledge. The site builder owns the
public shell, navigation, theme, route, and common presentation contract.

## 5. What Not To Do

The site builder should not generally parse generated HTML to recover the
meaningful data inside it.

That would make the old HTML an accidental API.

Parsing a generated page may be acceptable for a one-off rescue or migration
tool, but it should not be the normal route for public integration.

Similarly, public routes and final page structure should not be determined by
legacy filenames unless those names have deliberately been promoted into the
public contract.

## 6. Test Case: Fixed-v1 Entrant Initial Rating Charts

The Equelo fixed-v1 entrant initial rating charts are a useful test case.

The existing files are:

```text
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v1.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v2.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v3.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v4.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v5.html
```

They are interesting because they tell part of the story of how the fixed-v1
Equelo entrant rating values were chosen.

They were not originally designed as public-site pages. They have their own
styling and standalone Plotly setup.

For a prototype, they could be copied or iframed directly.

For a promoted public page, the better move is to add an Equelo fixed-v1
site-facing writer. That writer could emit the versioned chart data and
metadata needed by a single public page with a version selector.

The fact that these five charts are structurally similar is helpful, but it is
not the essence of the policy. The same principle applies to one odd chart:
promote by emitting intentional site-facing inputs, not by treating the old
HTML page as the source of truth.

## 7. Need for More Examples

The fixed-v1 entrant charts are only one example, even though they form a small
family.

Before making this a rigid policy, inspect other candidate artefacts.

Useful comparison cases may include:

* existing Plotly pages that are not structurally similar to one another;
* table apps such as Banzuke Changes and Standings by Wins;
* standalone historical charts such as division persistence;
* explanatory/methodology pages;
* legacy Elo v9 pages that may become B1 public material;
* diagnostic pages that should remain excluded.

The aim is to learn whether the producer-writer model is broad enough without
becoming a general content-management system.

## 8. Current Position

Current working policy:

* Prototype inclusion may use copy/iframe.
* Public promotion should use additive producer writers.
* Producers should not be destructively refactored merely to satisfy the site.
* The site builder should consume intentional site-facing inputs.
* Generated HTML should not become the normal API between analysis packages and
  the public site.
* Rendering technology is secondary to the producer/site contract.

