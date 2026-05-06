# Public Site Specification

This note specifies the system shape needed to satisfy the public site
requirements.

It is not a final implementation design. It describes the entities and
behaviour the site system shall provide.

Related notes:

* `2026 05 06 Public Site Requirements.md`
* `2026 05 06 Public Site Design.md`

## 1. Site

The site shall be a generated static site.

It shall have:

* a site title;
* a navigation tree;
* a registry of pages;
* shared static assets;
* a generated output directory suitable for local and remote deployment.

## 2. Navigation Tree

The site shall have a hierarchical navigation tree.

Navigation is subject-led.

A navigation node shall have:

* a human-facing label;
* a stable slug or key;
* zero or more child nodes;
* optionally, a reference to a page;
* optionally, status/readiness/depth metadata.

A navigation node need not be a page.

For example:

```text
Banzuke & Rank
  Banzuke Structure Over Time
    Banzuke Division by Era
```

The first two nodes may be organising nodes. The final node may be a page node.

## 3. Page Registry

The site shall maintain a registry of renderable pages.

A page shall have:

* a stable id;
* a human-facing title;
* a summary;
* an optional options model;
* a view or body specification;
* data dependencies;
* static asset dependencies;
* public status/readiness metadata.

The page registry does not define the public route of a page. Public routes
are derived from the navigation tree.

## 4. Slugs and Routes

A slug is a URL-safe identifier derived from a label or chosen explicitly.

Examples:

```text
Standings by Wins -> standings-by-wins
Banzuke Division by Era -> banzuke-division-era
Win Probability by Standing -> win-probability-by-standing
```

Routes shall be stable public paths derived from the navigation and page
registry, not from incidental source filenames.

## 5. Page Nodes and Organising Nodes

The system shall distinguish organising nodes from page nodes.

An organising node groups related subjects but may have no renderable page of
its own.

A page node references a page in the page registry.

An organising node may later gain a landing page without changing the fact that
it also groups children.

## 6. Page Options Model

A page may define an options model.

The options model is the abstract definition of the page states and parameters,
not the HTML controls used to display them.

Examples:

```text
division: all | makuuchi | juryo | ...
source: observed | equelo
show_error_bars: true | false
selected_standings: list[standing]
```

The options model may be absent for pages that have no user-adjustable state.

The control rendering is a design concern, not part of the abstract model.

## 7. Page View

A page shall define a view or body.

The view may be one of several types, including but not limited to:

* table tool;
* Plotly chart;
* explanatory essay;
* static HTML artefact;
* custom interactive page.

The specification does not require all future view types to be known now.

Unknown future page types should be accommodated through explicit view type
metadata and a limited escape hatch for custom rendering.

## 8. Page Bundle

A package that wants to publish a page shall expose a page bundle or equivalent
metadata.

A page bundle shall identify:

* page metadata;
* navigation placement;
* options model, if any;
* view type;
* files required to render the page;
* data files required by the page;
* static assets required by the page;
* whether the page is public, candidate, research, or internal.

The exact file format for this bundle is a design decision.

## 9. Builder Behaviour

The site builder shall:

1. read the site/navigation definition;
2. read page bundles or page metadata;
3. derive page routes from the navigation tree;
4. generate the site shell and page routes;
5. copy or render required static assets, data files, and page bodies;
6. write a static output tree;
7. support deployment of that output tree to local and remote targets.

The builder shall trust the site definition and page metadata as contract
inputs. It shall not defensively validate page ids or check that files exist
when those facts are required by contract. A broken contract should fail
loudly through ordinary Python/file-system errors.

## 10. Static Output Tree

The generated output tree shall be self-contained enough to be served by a
static web server.

It shall include:

* site index;
* generated page HTML;
* JavaScript;
* CSS;
* data files;
* images and other static assets;
* copied third-party-free local assets required by pages.

External CDN use may be permitted for some libraries, but this should be a
deliberate page dependency rather than an accidental detail.

## 11. Deployment

Build and deployment shall be separable.

The system shall be able to:

* build the static output tree;
* deploy the built tree to a local web root;
* deploy the built tree to the remote public web root.

## 12. Current Prototype Lessons

The current prototype showed that existing HTML artefacts can be copied into a
site output tree and displayed under a subject-led navigation model.

This is a useful implementation finding, but not a specification requirement.

The real requirement is that public deliverables expose enough metadata and
files for the site builder to incorporate them coherently.

## 13. Legacy v9 Deliverables

Legacy v9 B1 deliverables shall not be permanently integrated by copying old
site pages as-is.

They shall be reimplemented as Sumo-Tools page bundles or equivalent outputs.

The v9 site may provide:

* the public question;
* the page concept;
* data lineage hints;
* UI ideas;
* explanatory language;
* examples of what not to preserve.

## 14. Non-Specified Details

This specification does not yet fix:

* the template engine;
* exact file formats for page bundles;
* exact CSS architecture;
* mobile navigation behaviour;
* the final route hierarchy;
* the complete set of page types;
* whether Plotly pages are represented as full HTML, fragments, or data plus
  renderer.

Those belong in design and may evolve.
