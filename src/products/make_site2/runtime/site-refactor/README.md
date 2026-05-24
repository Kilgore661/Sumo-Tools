# site.js module refactor

This keeps the existing rendering behaviour while making `site.js` a one-line module entry point.

## Loading change required

Load the new entry point as an ES module in the page HTML:

```html
<script type="module" src="site.js"></script>
```

## Module responsibilities

- `app.js`: application start-up and page selection/routing.
- `core/context.js`: host-derived site context and document title/class setup.
- `core/url-state.js`: page/filter URL persistence.
- `core/dom.js`: shared content-panel host.
- `core/manifest-store.js`: loaded manifest state.
- `data/http.js`, `data/csv.js`: transport and CSV parsing.
- `ui/navigation-toggle.js`: navigation expansion/collapse behaviour.
- `ui/filters.js`: filter state, controls and filter event wiring.
- `panels/render-content-panel.js`: panel orchestration by artifact kind.
- `ui/tables.js`: table renderers and table-only data shaping.
- `ui/charts.js`: Plotly views, chart trace construction and chart layouts.
- `ui/notes.js`: conditional note display.
- `utils/html.js`: HTML escaping.

The refactor deliberately does not reduce repeated panel markup yet; preserving responsibility boundaries takes priority.
