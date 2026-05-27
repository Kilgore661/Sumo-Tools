# Modular browser runtime

This directory is now the authoritative JavaScript source tree for the
`make_site2` browser runtime.

The source remains temporarily under `runtime/site-refactor/` so activation of
the module split is separate from any source-directory rename. During a build,
`build.py` copies this tree into the public output `runtime/` directory, so the
served site sees normal runtime paths:

```text
runtime/site.js
runtime/app.js
runtime/core/...
runtime/data/...
runtime/panels/...
runtime/ui/...
runtime/utils/...
```

The active build copies and executes only this modular runtime tree.

## Loading

The generated page loads the modular entry point as an ES module:

```html
<script type="module" src="runtime/site.js"></script>
```

In development builds, `build.py` applies the build cache-bust token both to the
HTML entry-module reference and to relative ES-module imports written into the
output tree. This preserves the previous expectation that a fresh development
build exposes changed runtime code without stale imported modules being reused.

## Module responsibilities

- `app.js`: application start-up and page selection/routing.
- `core/context.js`: host-derived site context and document title/class setup.
- `core/url-state.js`: page/filter URL persistence.
- `core/dom.js`: shared content-panel host.
- `core/manifest-store.js`: loaded manifest state.
- `data/http.js`, `data/csv.js`: transport and CSV parsing.
- `ui/navigation-toggle.js`: NavigationBar expansion/collapse behaviour.
- `ui/filters.js`: Filter state, controls and Filter event wiring.
- `panels/render-content-panel.js`: panel orchestration by PA kind and the
  explicit `PAPanel` rendering relationship.
- `ui/layout.js`: shared PA-panel layout hooks such as sticky artifact title
  and table-heading offset calculation.
- `ui/tables.js`: table renderers and table-only data shaping.
- `ui/charts.js`: Plotly views, chart trace construction and chart layouts.
- `ui/notes.js`: conditional Note display within `PAPanel`.
- `utils/html.js`: HTML escaping.

The module split does not yet reduce repeated panel markup. The subsequent
`PAPanel` correction has now been applied: Notes render within the PA-owned
region rather than outside the combined Filters/PA content layout.
