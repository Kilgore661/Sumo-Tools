# Rendering Change Review - 04 Work Groups and Routing

## 4. Natural Work Groups

| Group | Items | Nature | Status |
| --- | --- | --- | --- |
| Diagnostic display affordances | `debug_show_notes` URL state, info symbol, possible debug CSS variants | Runtime presentation state / debug policy | Implemented for marker visibility; production build diagnostic policy moved to main open issues |
| Shared table visual language | spacing, borders, row colours, muted colour, date-like display format | Rendering policy/CSS plus shared formatter | Implemented for the reviewed slice: table bounding boxes, title-block spacing, body-start heading/data separator, collapsed group-boundary borders, 6.2.1 heading treatment, muted row-number foreground, date-like public display formatting and alternating row colour tokens |
| Interim table structure metadata | 2.1/7.1/9.1 column groups, 6.2.1 custom handling | Ad hoc PA-local metadata, easiest-to-remove later | Partially implemented: 6.2.1 side-by-side restored; 9.1 Row number/Context/Wins group metadata provisionally implemented; 2.1 row-number and banzuke-style Row number/East/Rank/West group metadata provisionally implemented |
| Table semantic model | row numbers, superlative `#` columns | Published Artifact/table model | Partially implemented: row-number/ranking distinction in 7.1, 7.4-style tables, 9.1 and 2.1; broader row-number-as-table-skeleton model remains provisional |
| Link/popover/notes interactions | shikona Alt-click, link popover text, clickable Notes popovers | Runtime interaction plus explicit metadata/text rule | Partially implemented: clickable Notes popovers complete; shikona link help and Alt-click implemented; Notes validation/tightening open |
| Basho Results control model | year/month selector and navigation buttons, URL-addressable no-basho state | PA-specific runtime control inside existing FilterSection | Implemented |
| Career Length Longest control | Longest-only Show Active control and produced ranked populations | PA-specific chart/table semantics | Implemented |
| Shared chart rendering | tick-angle rule, bold axis titles | Chart rendering policy | Partially implemented: bold axis titles implemented and incorporated into Rendering Design; conditional x-axis tick rotation remains open |
| PA-specific chart semantics | line-vs-column chart changes, 6.3.1 error-bar colour | PA contract / chart renderer selection | Open |
| Bad URL handling | reject bad URL, message, route Home; richer handler | Runtime routing / UX policy | Minimal implemented; richer policy TBD |

## 5. Implementation-Routing Notes

These notes are intentionally non-final. They preserve likely routes without
settling implementation design prematurely.

### 5.1 `debug_show_notes`

The proposed immediate control for visible info-here indicators is the URL
parameter `debug_show_notes`.

Required behavior:

```text
absent                 -> no info-here indicator
debug_show_notes=false -> no info-here indicator
debug_show_notes=true  -> show info-here indicator
```

The visible marker should be the circled-info style symbol rather than `?`.

This parameter shows diagnostic affordance markers. It does not open the Notes
panel on page load.

Implemented note: help/popover markers are hidden unless `debug_show_notes=true`
is present in the URL. When visible, they use a circled-info marker rather than
`?`. This does not change whether the underlying hover/click popovers work.

### 5.2 `--prod`

The production-build policy question has moved to
`10.4 Open Issues - Defects and Deferred Matters.md` as "Production build
diagnostic display policy." The implemented `debug_show_notes` URL-state rule
defines marker display behavior; the open issue asks whether production builds
should disable diagnostic URL modes regardless of that runtime rule.

### 5.3 `debug_layout`

The existing `debug_layout=true` overlay is useful for structure inspection. A
future extension such as `debug_layout=headings_v4` could support experimental
CSS or rendering diagnostics, but that should be treated as debug/development
instrumentation rather than as public rendering policy.

### 5.4 Column groups in non-7.1 tables

For tables other than 7.1 Basho Results, implement a mechanism for declaring
column groups. The default state is explicitly no declared groups.

The renderer should not infer a column group for every individual column. Column
boundary treatment should appear only where a group is declared, while the table
still receives the general bounding box and heading underline rules.

Because this mechanism is expected to be removed if/when a general table model is
introduced, prefer the easiest-to-remove implementation. A small ad hoc
configuration close to the current make_site2 rendering/manifest boundary is
preferable to a broad model migration.

Current status: 6.2.1 side-by-side sectioned-table layout is restored. 9.1 has
provisional Row number, Context, Wins per Basho and Wins per Bout group metadata
and visible grouped headings. Banzuke Changes 2.1 row-number work is implemented
for both banzuke-style and scan-table views. The banzuke-style view also has
provisional Row number, East, Rank and West group metadata. The scan-table view
remains intentionally flat except for the mechanical row-number column.

### 5.5 Visual tokens

Exact visual token choices are delegated to implementation and review. Choose
reasonable initial values for muted foreground, row backgrounds, border colour,
border weight and spacing. If the result looks wrong, revise the tokens after
visual inspection.

Implemented table-scaffolding note: split artifact tables now have an explicit
`artifact-table-frame`, which is the rendered table entity that carries the
bounding box. Sectioned tables such as 6.2.1 remain unsplit and carry the same
box directly. The heading/data separator is rendered from the first body row
rather than the last header row, and collapsed table borders allow adjacent group
boundaries to render as one shared line. The artifact title block owns its
trailing whitespace and is followed by a defined gap before the table entity.
Mechanical row-number columns use the shared muted foreground token. Public
date-like display strings use `-` separators at known table/chart display
points without rewriting URLs, paths or source data. Remaining visual-token work
for this reviewed slice is complete: alternating table rows use the revised row
background tokens.
