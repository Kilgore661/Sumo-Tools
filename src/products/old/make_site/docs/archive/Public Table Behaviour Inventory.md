# Public Table Behaviour Inventory

## Status

Working inventory of table behaviours already present in the public-site code.

This was written while sketching the Basho Results Browser (BRB).  It records
which existing table behaviours are worth treating as precedents before adding
another table-heavy page.

## Existing Table Precedents

### Grand Sumo Standings by Wins Digest

Source:

```text
src/analysis/standings/files/index.html
src/analysis/standings/files/standings.js
src/analysis/standings/files/standings.css
```

Useful behaviours:

* sortable headers using `th[data-column]`;
* repeated header click toggles sort direction;
* default sort direction depends on column type;
* chii sorts by ordinal, not alphabetically;
* chii sort indicator accounts for lower ordinal meaning better rank;
* row-number/display columns can be excluded from sorting;
* sort state is reflected in header indicators;
* URL state covers filters, sort, view mode, and current-only state;
* browser back/forward restores page state;
* view-sensitive notes are shown or hidden according to the active view;
* note popovers are available from selected table headings;
* shikona links support normal click to SumoDB and Alt-click to the
  Gaspode-san graph endpoint.

BRB relevance:

Standings is the best current precedent for sorting, sort indicators, chii
ordinal sorting, URL state, and back/forward behaviour.

### Banzuke Changes

Source:

```text
src/analysis/banzuke_compare/files/index.html
src/analysis/banzuke_compare/files/banzuke_change_report.js
src/analysis/banzuke_compare/files/banzuke_change_report.css
```

Useful behaviours:

* static app shell consumes `site_config.json` plus CSV data;
* browser validates config and CSV shape before rendering;
* division selector filters data in-browser;
* column toggles control previous-basho context, delta, and Equelo columns;
* one-column rendering mode projects the east/west banzuke-shaped CSV into one
  row per rikishi;
* option-sensitive notes are hidden or shown according to visible columns;
* note popovers are available from selected table headings;
* robust CSV parser handles quoted values;
* shikona links support normal click to SumoDB and Alt-click to the
  Gaspode-san graph endpoint.

BRB relevance:

Banzuke Changes is the best current precedent for column toggles, option-linked
notes, config/data validation, and one-row-per-rikishi rendering.  Its
east/west banzuke layout and movement-specific columns should not be copied
wholesale into BRB.

### Career Length -> Longest

Source:

```text
src/products/make_site/render.py
```

Useful behaviours:

* the table view scrolls inside the page content panel;
* column headers remain sticky while the table body scrolls;
* shikona links reuse the normal click / Alt-click semantics.

BRB relevance:

Career Length -> Longest is the reference for long-table scrolling: table body
scrolls in the content panel while column headers remain visible.

### Typical Equelo Ratings

Source:

```text
src/products/make_site/render.py
```

Useful behaviours:

* simple generated tables from page config and CSV data;
* compact table sections with headings;
* content-area scrolling for table grids;
* notes rendered from page config.

BRB relevance:

This is useful mainly as a minimal site-generated table example.  It is not a
strong precedent for BRB's richer interaction model.

## BRB Feature Union

Likely required for BRB v1:

* sortable meaningful columns;
* repeated header click toggles sort direction;
* visible sort direction indicators;
* chii sorts by ordinal, not alphabetically;
* row number is not sortable;
* group-level and individual column visibility controls;
* when a column group is hidden, individual controls in that group are muted or
  disabled but retain their state;
* Shikona and Score are always visible;
* option-sensitive notes;
* heading note popovers;
* normal click / Alt-click shikona link semantics;
* shareable URL state for date, division, visible columns, sort, and other
  meaningful display state;
* browser back/forward restores page state;
* table scrolls inside the content panel with sticky column headers;
* browser-side validation of loaded config/data.

Likely useful but not yet required:

* reset columns to default;
* show all / hide all for a column group;
* explicit sort fallback if the active sort column is hidden;
* visual distinction between actual and projected after/current columns.

## Design Notes

The existing table behaviours are spread across several pages rather than held
in a shared table component.

For BRB, the practical design path is to borrow the strongest behaviours from
each precedent:

* Standings for sort and URL state;
* Banzuke Changes for toggles, notes, validation, and one-column rendering;
* Career Length -> Longest for in-panel scrolling with sticky headers.

Do not treat any one existing table as the complete template for BRB.
