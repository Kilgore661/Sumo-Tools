# Public Site Design

This note records the provisional design direction for implementing the public
site specified in `2026 05 06 Public Site Specification.md`.

It is not a commitment to final code. It is the current design hypothesis.

## 1. Design Goal

The site should be a generated static site assembled from public page bundles.

The implementation should be simple enough to inspect and maintain, but
structured enough to avoid each analysis package becoming its own mini-site.

## 2. Preferred Implementation Weight

A small Python site builder is the preferred implementation weight.

Full web frameworks or application frameworks appear heavier than the current
requirements justify.

The design should not require:

* Django, Flask, or FastAPI;
* React, Vue, Svelte, Next, Nuxt, or similar app frameworks;
* Streamlit, Dash, Panel, or other live analytical app servers;
* a database or public API.

Those may become relevant only if later requirements change.

## 3. Template Engine

Jinja is a strong candidate for the static rendering layer.

It fits:

* shared site shell rendering;
* shared page layout;
* navigation rendering from metadata;
* title/options/body page grammar;
* consistent asset includes;
* static output;
* Python-native generation.

Jinja should be treated as the rendering tool, not as the entire frontend
architecture.

Client-side JavaScript remains appropriate for interactive tables and charts.

## 4. Core Data Structures

The design should likely use explicit Python data structures or structured
metadata for the main site concepts.

Possible conceptual model:

```text
Site
  title
  navigation: NavigationTree
  pages: PageRegistry

NavigationNode
  label
  slug
  children
  page_id optional
  metadata optional

Page
  id
  title
  summary
  options_model optional
  view_spec
  assets
  data
  status/readiness
```

The exact class names are not important yet.

The important distinction is that a navigation node is not necessarily a page.

## 5. Page Bundle Shape

A page bundle might be represented as a small manifest plus files.

Example shape:

```text
page_bundle/
  page.json
  index.html or template.html
  data/
  assets/
```

or:

```text
PageBundle(
    id="finish_by_chii",
    title="Finish by Chii",
    navigation_path=[
        "Performance",
        "Rank Outcomes",
        "Finish by Chii",
    ],
    view_type="standalone_html",
    source_files=[...],
)
```

In the current Python definition, route-defining information lives in the
navigation tree rather than in the page object. A future manifest may express
navigation placement directly, but it should still avoid defining a separate
page route that can disagree with the navigation tree.

The design should not decide too early whether manifests are Python objects,
JSON, YAML, or another simple format.

The first requirement is to define what information a bundle must provide.

## 6. View Types

The design should support a small number of initial view types.

Likely initial view types:

* `standalone_html`
* `html_fragment`
* `plotly_json`
* `table_app`
* `essay`
* `custom`

`custom` is the escape hatch.

It should exist, but it should not become the default answer to every awkward
page.

## 7. Options Model and Controls

The options model should describe page state.

The controls that render that state are part of the page design.

Example:

```text
options_model:
  division:
    type: enum
    values: [all, makuuchi, juryo]
  show_error_bars:
    type: boolean
```

A template or page renderer can choose controls:

* dropdowns for enum choices;
* checkboxes/toggles for booleans;
* tabs for sibling views;
* sliders or numeric inputs for numeric parameters.

Pages with no options should have `options_model = null` or equivalent.

## 8. Navigation UI

The stress test used a large hierarchical left navigation panel.

That was useful for seeing the full scope, but it is probably not the final
public UI.

The final design should consider:

* exposing only one or two levels globally;
* using local page navigation for deeper levels;
* using tabs for sibling views such as Observed/Equelo;
* using quick entry points for common casual-reader paths;
* avoiding a separate top-level "expert section";
* making implemented pages visually distinct from planned/unimplemented pages
  during development only.

## 9. Page Layout

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

The site shell itself can be treated as a page-shaped object:

```text
site title
site navigation
selected page body
```

This recursive model remains useful, but should not be overengineered into a
universal content system.

## 10. Plotly and Existing HTML

Plotly-heavy outputs may initially be easiest to incorporate as standalone
HTML or HTML fragments.

Longer term, a cleaner contract may be:

```text
chart data + chart config + shared page template
```

rather than large self-contained HTML files.

However, the stress test showed that simple copying works today. That is a
useful fact, not the design aim.

## 11. Legacy v9 Migration Design

For v9 B1 deliverables, the design should be:

1. identify the page concept from v9;
2. specify the public question and navigation placement;
3. reimplement the computation/output under Sumo-Tools;
4. emit a Sumo-Tools page bundle;
5. let the site builder consume that bundle.

Old v9 HTML may be used as a reference or temporary comparison, but should not
be the permanent delivered artefact.

## 12. Open Design Questions

Open questions:

* Should page bundles be declared in Python, JSON, YAML, or generated metadata?
* Should the final site use iframes for standalone pages, or render pages
  directly into the shell?
* How much of the navigation should be global versus page-local?
* How should research/candidate/internal status be displayed, if at all?
* What is the first route hierarchy that should be treated as stable?
* Should Plotly pages be regenerated into a shared template, or copied until
  there is a strong reason to change?
* How should local and remote deployment be represented in the final package?

## 13. Design Guardrails

The implementation should avoid:

* designing for hypothetical future media types before real use cases exist;
* turning the site builder into a general CMS;
* allowing analysis packages to bypass the shared public-site contract;
* letting legacy file names define public routes;
* publishing raw/internal HTML just because it renders in a browser.

The design should be enough to support the current known pages and the likely
v9 migrations, while leaving a controlled escape hatch for future pages.
