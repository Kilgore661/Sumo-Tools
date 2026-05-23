# make_site2 Package Requirements

## Status

Draft package-level requirements statement for the successor public-site builder.

This document describes what `make_site2` is for at the product/package level.
It is deliberately broader than the UI model. The UI model is one important
solution component, but the package requirement is to generate a coherent public
site from curated Sumo-Tools analytical material.

---

# Core Requirement

`make_site2` assembles the public Sumo-Tools website as one stage in the
publication pipeline.

It consumes curated page definitions, navigation definitions, producer-generated
site-facing artefacts, data files, artifact inputs, and shared runtime assets. It
generates a coherent static website that presents professional sumo analysis to
a mixed audience: casual readers should get clear defaults and ordinary-language
framing; expert readers should be able to access richer filters, caveats,
methodology, and research detail without the site becoming a pile of unrelated
tools.

The package owns the public-site structure: navigation, stable deep-linkable
public page/view selection, page framing, shared rendering grammar, filters,
notes, public status, static output, and deployment shape. Producers own analysis-specific computation and site-facing
artefact data. Legacy/prototype HTML may be used as evidence or temporary
compatibility material, but promoted public pages must move toward intentional
site-facing inputs and the shared publication model.

`make_site2` is not a from-scratch analysis producer. It does not own the
calculation of standings, banzuke comparisons, probability traces, Equelo
ratings, or historical summaries. Those outputs are prepared earlier by analysis
and miscellaneous producer modules. `make_site2` consumes their site-facing
CSV/JSON/artifact outputs, stages them in the public static output tree,
renders the shared site shell and runtime model, and hands the completed static
output to deployment.

The older `make_site` product has the same pipeline position: it consumes
previously prepared producer outputs rather than manufacturing the whole public
site data world from scratch.

`make_site2` must stand on its own. It must remain valid if the old
`src/products/make_site` package has been deleted. The old `make_site` product
may be used as historical evidence while discovering requirements, but
`make_site2` code, runtime assets, tests, and active contracts must not import
from, call into, wrap, or depend on `make_site`.

---

# Purpose

The public site must make professional sumo more legible through data.

It should present curated analysis outputs, explanatory tools, selected research
narratives, public-facing tables, public-facing charts, and method material in a
way that can be understood without private project context.

The site should not publish every artefact the repository can generate merely
because that artefact is browser-readable.

---

# Reader Requirement

The site must support a mixed audience.

Some readers want clear defaults, official-looking tables, plain language, and
low cognitive load.

Other readers want deeper filters, model caveats, provenance, methodology,
research detail, and enough control to inspect the analytical machinery.

This should be handled inside the page model through:

- clear defaults;
- good page framing;
- progressive disclosure;
- filters;
- notes;
- public status markers;
- method pages;
- and research/caveat material where needed.

The main navigation should not be organized primarily by user type. It should be
organized by subject. Readers should self-select depth through page structure and
filters.

---

# Package Responsibilities

`make_site2` owns the public-site layer.

It is responsible for:

1. Declaring or consuming the public site definition.
2. Declaring or consuming subject-led navigation.
3. Maintaining a registry of promoted, candidate, research, diagnostic, legacy,
   superseded, and excluded pages.
4. Providing stable deep-site URLs that restore the selected public page and
   its material analytical state.
5. Connecting page definitions to site-facing artefacts, data, artifact inputs, and
   runtime assets.
6. Rendering pages through a shared publication grammar.
7. Rendering filters as the public mechanism for visible analytical state.
8. Rendering notes, caveats, and provenance according to explicit ownership.
9. Writing the static output tree.
10. Supporting local and remote deployment workflows.
11. Keeping prototype and legacy inclusion paths explicit and temporary.
12. Failing clearly when required producer outputs are missing or stale enough
    to violate the selected build contract.

---

# Producer Responsibilities

Producer modules own analysis-specific knowledge.

They are responsible for:

- computing analytical outputs;
- defining the meaning of their data;
- producing site-facing artefacts where a page is promoted;
- providing data files, artifact inputs, notes, provenance, and caveats needed by the
  public site;
- preserving diagnostic or legacy outputs where useful, without forcing those
  outputs into public navigation.

Promotion to the public site should be additive. A producer may keep existing
standalone outputs, but a promoted page should expose intentional site-facing
inputs rather than expecting `make_site2` to reverse-engineer generated HTML.

---

# Static Site Requirement

The generated site must be statically deployable.

The public web server should not require:

- a database;
- a Python runtime;
- an application server;
- a dynamic public API;
- user accounts;
- server-side runtime computation.

Client-side JavaScript is allowed for interactive pages and for restoring the
selected public page and material analytical state from a deep link. The static
site may use one application shell or multiple HTML entry pages; neither shape
is required merely by static deployment.

---

# Curation Requirement

`make_site2` must distinguish public content from internal project material.

Raw downloaded HTML, parser diagnostics, warning reports, cache files, source
data archives, stale experiments, and internal audit outputs must not appear in
public navigation merely because they exist.

Candidate pages should have explicit status, such as:

- promoted;
- candidate;
- research;
- diagnostic;
- legacy;
- superseded;
- excluded.

The exact status vocabulary may change, but accidental publication is not
allowed.

---

# Navigation Requirement

The public site must use subject-led navigation.

Navigation should expose public information structure, not every implementation
subdivision.

The site may also provide quick entry points for casual readers, such as:

- latest standings;
- banzuke changes;
- basho results;
- rikishi lookup;
- rank outcomes;
- ratings/model explanation.

Quick entry points should lead into the canonical subject structure, not replace
it.

---

# Rendering Requirement

Promoted pages should render through the shared publication model.

The successor model uses `Filter`, not `Option`, as the formal public UI-model term.
This vocabulary rule governs the model and implementation identifiers for the
concept; it does not prevent reader-facing UI copy such as `Options` where that
word is clearer to ordinary users.

A filter is reader-visible state that restricts, selects, projects, or otherwise
narrows what part of the available analytical view is shown. This intentionally
extends the database meaning of "filter" to cover projection-like and
selection-like behavior.

Filters may internally correspond to:

- row filtering;
- column projection;
- source selection;
- measure selection;
- representation selection;
- PA or representation selection;
- PA selection;
- visibility preset selection.

The public concept remains:

> show this slice or view of the available analytical content.

Filters do not own notes. Filters may have concise help text. Notes belong to
published artefacts or visible artefact features.

---

# Legacy and Prototype Requirement

Legacy/prototype HTML may be used as evidence or as a temporary compatibility
path.

It should not permanently define:

- public deep-link semantics;
- page grammar;
- styling;
- data contracts;
- navigation structure;
- public wording;
- rendering architecture.

A promoted page should move toward intentional site-facing inputs and the shared
publication model.

---

# Non-Requirements

The first real successor package does not require:

- a general web framework;
- a CMS;
- a live analytical application server;
- user accounts;
- a database-backed public API;
- a full single-page application framework;
- one generated HTML page per public page;
- complete migration of all legacy v9 ideas;
- publication of all generated Sumo-Tools artefacts.

These should be reconsidered only if later requirements justify them.

---

# Guiding Principle

`make_site2` is a static analytical publication builder.

It should make the public surface coherent without hiding the data-driven nature
of the project.

The package should let the site say:

> Here is the public question, here is the curated analytical artefact, here are
> the filters that change what is visible, here are the caveats and provenance,
> and here is a stable deep link that restores this public analytical view.
