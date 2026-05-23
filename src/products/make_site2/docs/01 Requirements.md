# 01 Requirements

## Status

Draft requirements document for `src/products/make_site2`.

This document states what `make_site2` is required to achieve as a public-site
product. It deliberately does not prescribe the formal public-page grammar,
model structure, rendering architecture, or implementation mechanism. Those
belong in later specification and design documents.

---

## 1. Purpose

`make_site2` shall generate the public Sumo-Tools website.

The site shall publish curated professional sumo analysis as a coherent static
public website suitable for local inspection and public deployment.

The site shall make analytical material legible to readers who do not have
private project context. It shall present public questions, analytical outputs,
controls where needed, explanatory notes and stable public views as parts of one
recognisable publication rather than as unrelated tools.

---

## 2. The Growth and Coherence Requirement

Sumo-Tools can produce an increasing number of useful analytical artefacts. As
more of those artefacts are promoted for public use, the public website shall
remain coherent, navigable and understandable.

The site shall not be allowed to spiral into a collection of independently
designed pages or tools with inconsistent navigation, framing, controls,
terminology, notes and visual presentation.

New promoted material shall fit into a coherent public site rather than simply
become visible because an output file or browser-readable report exists.

---

## 3. Required Public Website

The generated website shall provide:

- a visible site identity;
- subject-led navigation through the public material;
- a selected-page content display;
- page-level title and framing where appropriate;
- controls where readers need to select or restrict the visible analytical
  view;
- one or more deliberately published analytical artefacts as the site grows;
- explanatory notes, caveats or provenance where needed to understand visible
  material;
- stable public views that can be restored through public links where the
  selected page or analytical state is material.

The website shall present these elements with a consistent and intelligible
relationship across promoted pages.

The required website is not defined by the file layout of producer outputs, by
legacy HTML pages, or by whichever rendered artefacts happen to be available in
the repository.

---

## 4. Reader Requirement

The public site shall support a mixed audience.

For readers seeking a clear public view, it shall provide:

- clear defaults;
- ordinary-language framing;
- legible tables and charts where appropriate;
- low unnecessary cognitive load.

For readers seeking deeper analysis, it shall be capable of providing:

- richer controls;
- caveats and explanatory notes;
- provenance;
- methodology;
- research material;
- deeper analytical views.

The public navigation shall be organised primarily by subject, not by reader
type. Different depths of engagement shall be supported within the coherent
public site rather than by creating separate competing sites.

---

## 5. Curation Requirement

`make_site2` shall distinguish public material from internal project material.

Content shall not become part of the public site merely because it exists, has
been generated, or can be viewed in a browser.

Material such as the following shall be non-public unless deliberately promoted
or explicitly presented under an appropriate public status:

- raw downloaded HTML;
- parser diagnostics;
- warnings and internal audit reports;
- cache files;
- source-data archives;
- stale experiments;
- debug artefacts;
- legacy generated pages.

The site shall support explicit public status for candidate material, including
where relevant statuses such as:

- promoted;
- candidate;
- research;
- diagnostic;
- legacy;
- superseded;
- excluded.

Promoted material shall meet the normal public-site requirements. Any inclusion
of legacy, diagnostic or provisional material shall be explicit and shall not
silently define the normal public-site behaviour.

---

## 6. Navigation Requirement

The public site shall provide subject-led navigation.

Navigation shall expose the information structure intended for readers, rather
than exposing every implementation subdivision or output file merely because it
exists.

The site may provide quick routes to material of immediate interest, such as
current banzuke changes, standings or basho results, provided that such routes
lead into the coherent public information structure rather than defining a
competing organisation of the site.

---

## 7. Public Page and View Requirement

A public page shall be a curated publication unit presented by the website.

A public page shall have, as applicable:

- a stable identity;
- public title and framing;
- a place in the public navigation or another deliberate public entry route;
- an explicit public status;
- deliberately selected analytical material;
- relevant data and asset dependencies;
- controls and default state where needed;
- relevant notes, caveats or provenance.

A public page is not merely an HTML file, a producer output path, a copied
report, or an incidental URL encoding.

Where page selection or analytical state materially affects the displayed public
view, that state shall be reproducible through a stable public link.

---

## 8. Terminology Requirement for Reader Controls

The formal public concept for a reader-visible control that changes the visible
analytical view shall be **Filter**.

A Filter may select, restrict, project or otherwise alter the visible slice or
representation of available analytical content. It may correspond internally to
row filtering, column visibility, source selection, measure selection,
representation selection or a visibility preset.

Reader-facing copy may use ordinary wording such as `Options` where that is
clearer to readers. The formal concept remains `Filter`.

Filters shall not own explanatory notes. Notes explain published analytical
material or visible features of that material, even where a Filter affects
whether a note is relevant.

---

## 9. Published Analytical Material Requirement

The site shall publish analytical material deliberately chosen for public use.
A deliberately published analytical artefact is referred to as a **Published
Artifact** or **PA**.

A PA may take forms including:

- a table;
- an indexed table;
- a chart;
- a sectioned table;
- prose;
- a custom analytical artefact.

A PA shall expose public analytical meaning rather than implementation accident.
It shall have sufficient identity, data, labelling and explanatory support for
its public presentation to be intelligible.

Notes, caveats and provenance shall be provided where they are necessary to
interpret the PA or a visible feature of it.

---

## 10. Responsibility Boundary

`make_site2` owns the public-site product. It is responsible for:

- the public site identity and organisation;
- reader-facing navigation;
- public page presentation;
- coherent treatment of controls, Published Artifacts and notes;
- stable public-page and material-view selection;
- public status handling;
- assembling and writing a static public output;
- supporting local and remote publication workflows.

Producer modules own analysis-specific computation and meaning. They are
responsible for matters including:

- computing analytical outputs;
- defining what their data means;
- supplying deliberate site-facing data or artefact inputs for promoted public
  use;
- identifying meaningful columns, traces, labels, caveats and provenance.

`make_site2` shall not ordinarily recover public meaning by reverse-engineering
legacy rendered HTML. Promotion should be based on intentional site-facing
inputs.

---

## 11. Independence from Legacy `make_site`

The old `src/products/old/make_site` product may be used as historical evidence
when identifying behaviour worth retaining, correcting or deliberately
replacing.

`make_site2` shall stand on its own. Its active code, normal public rendering,
models, data contracts and tests shall not depend on the old product as an
operational component.

Legacy behaviour shall not define the new public site merely because it existed
previously. Where legacy behaviour is retained, it shall be retained because it
satisfies the current public-site requirements or later specification and design
rules.

---

## 12. Static Publication Requirement

The completed public website shall be statically deployable.

The public serving environment shall not require:

- Python;
- a database;
- an application server;
- server-side analytical computation;
- user accounts;
- a dynamic public API.

Client-side JavaScript may be used for interactive public pages, Filter state,
restoring material public views, and rendering data supplied in the static
output.

Build and deployment shall be separable operations.

---

## 13. Error and Missing-Material Requirement

The public site and the build process shall handle missing or invalid required
material explicitly.

A promoted public page shall not silently display blank or misleading content
when required data, artefact inputs or public state are invalid or unavailable.

The system shall distinguish predictable user-facing invalid state, such as an
invalid requested public view, from build-time failures, such as missing inputs
required to publish a promoted page.

---

## 14. Non-Requirements

`make_site2` is not required to be:

- a general web framework;
- a content-management system;
- a live analytical application server;
- a database-backed public API;
- a repository-wide artefact browser;
- a compatibility wrapper around old generated HTML;
- a clone of the old `make_site` implementation;
- a publisher of every artefact Sumo-Tools can generate.

The first production version is not required to migrate every legacy page or
every historical rendering idea.

---

## 15. Relationship to Later Documents

This document states the required public-site product and the problem it must
solve: publishing a coherent public analytical website that remains manageable
as more artefacts are added.

Later documents shall define the chosen solution in increasing detail:

- `02 Specification.md` shall formally specify the public website and its
  observable behaviour, including the public page grammar;
- `03 Architecture and Design Thesis.md` shall explain the model-first approach
  chosen to preserve coherence and make rendering auditable;
- model, rendering, build, integration and deployment documents shall describe
  how that solution is realised.

The requirements in this document remain requirements on the public result.
They do not depend on a particular HTML structure, CSS selector, Python class or
JavaScript implementation.