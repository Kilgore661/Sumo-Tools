# Rendering Change Review - 04 Work Groups and Routing

## 4. Natural Work Groups

| Group | Items | Nature | Status |
| --- | --- | --- | --- |
| Diagnostic display affordances | `debug_show_notes` URL state, info symbol, possible debug CSS variants | Runtime presentation state / debug policy | Open |
| Shared table visual language | spacing, borders, row colours, muted colour, date-like display format | Rendering policy/CSS plus shared formatter | Partially implemented: table bounding boxes, title-block spacing, body-start heading/data separator, collapsed group-boundary borders and 6.2.1 heading treatment implemented; colour/token and date-like display policy remain open |
| Interim table structure metadata | 2.1/7.1/9.1 column groups, 6.2.1 custom handling | Ad hoc PA-local metadata, easiest-to-remove later | Partially implemented: 6.2.1 side-by-side restored; 9.1 Row number/Context/Wins group metadata provisionally implemented; 2.1 row-number and banzuke-style Row number/East/Rank/West group metadata provisionally implemented |
| Table semantic model | row numbers, superlative `#` columns | Published Artifact/table model | Partially implemented: row-number/ranking distinction in 7.1, 7.4-style tables, 9.1 and 2.1; broader row-number-as-table-skeleton model remains provisional |
| Link/popover/notes interactions | shikona Alt-click, link popover text, clickable Notes popovers | Runtime interaction plus explicit metadata/text rule | Partially implemented: clickable Notes popovers complete; shikona link help and Alt-click implemented; Notes validation/tightening open |
| Basho Results control model | year/month selector and navigation buttons, URL-addressable no-basho state | PA-specific runtime control inside existing FilterSection | Implemented |
| Career Length Longest control | Longest-only Show Active control and produced ranked populations | PA-specific chart/table semantics | Implemented |
| Shared chart rendering | tick-angle rule, bold axis titles | Chart rendering policy | Open |
| PA-specific chart semantics | line-vs-column chart changes, 6.3.1 error-bar colour | PA contract / chart renderer selection | Open |
| Bad URL handling | reject bad URL, message, route Home; richer handler | Runtime routing / UX policy | Minimal implemented; richer policy TBD |
| Build-mode policy | whether `--prod` suppresses stylistic debugging | Open build/operations decision | Open |

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

### 5.2 `--prod`

There is an existing `--prod` CLI flag. An open issue remains: should `--prod`
imply that stylistic debugging features are removed or disabled?

This question should be resolved separately from the `debug_show_notes` URL-state
rule. The `debug_show_notes` rule defines when the info-here marker is displayed;
the `--prod` issue asks whether a production build should make such diagnostic
display modes unavailable regardless of URL parameters.

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
Remaining visual-token work should focus on row-colour contrast, muted foreground
and date-like display formatting.

### 5.6 Basho selector URL state

Implemented as an interim PA-specific runtime control. The current public URL
shape uses `year=YYYY` and `month=MM`, and the runtime accepts the six sumo
months only. `year=latest&month=latest` may be emitted as an initial/default
view and is canonicalized after the index loads.

The no-basho case is intentionally simple: if a supported sumo calendar slot has
no indexed basho, the ContentPanel is blank except for the no-basho message.

### 5.7 Bad URLs

A general bad-URL handler has not been designed. The current minimal behavior is:

```text
Bad URL -> JS message "Bad URL" -> replace/navigate to Home
```

This is sufficient for the Basho selector work but should be revisited as a
separate routing/UX design topic.

### 5.8 Notes popover interaction

Implemented as runtime interaction. A help popover whose text contains the exact
word `Notes` is clickable. The source help item may remain a normal table header
or sort control; the floating popover owns the Notes click. The runtime opens the
Notes panel if needed, finds the target note inside that panel, scrolls/focuses
it and applies a five-second highlight. Missing rendered targets produce the
message `No such note`.

Open validation/tightening pass: test Banzuke Delta and Result, Basho movement
and result popovers, generic Clean popovers, and 9.1 popovers; confirm popup
timing, clickability, note opening and highlight. Replace placeholder Basho
movement notes with meaningful text and keep a validation pass for popovers
containing `Notes` but lacking a corresponding rendered note.

### 5.9 Career Length Longest routing

Implemented as PA-specific chart/table semantics. Build-time materialization
creates ranked Longest populations from full producer spans. Runtime selects the
appropriate produced population based on the Longest-only `Show Active` control.
Checked/default true shows the all-rikishi population; unchecked false shows the
non-active population. Active Last values render as `-`.

### 5.10 Row-number and ranking routing

Partially implemented as shared table-rendering semantics. A mechanical
`row_number` column is distinct from a meaningful `#` ranking/ordinal column. The
mechanical column is blank-headed, muted and non-sortable; it is recomputed after
sort/filter where applicable. This is currently implemented for 7.1, 7.4-style
generic tables, 9.1 and Banzuke Changes 2.1. In 2.1, banzuke-style rendering
uses a leading blank row-number header spanning the two-row East/Rank/West
heading structure; scan-table rendering uses a leading blank, non-sortable
row-number column.

### 5.11 Shikona link affordance

Implemented as shared shikona-link runtime behavior. Normal click retains the
existing SumoDB link behavior. The link exposes the popover text `Click for
SumoDB; Alt-click for chart.` Alt-click opens the make_site2 Career Comparisons
route:

```text
index.html?page=career_comparisons&skill=chii&x=date&log=true&rikishi=<rik id>
```

## 6. Review Conclusion

The proposed changes are understandable and mostly precise enough to begin
design. They should not be implemented as an undifferentiated CSS tweak pass.

Basho selector work is now complete as an interim PA-specific/runtime solution.
Clickable Notes popovers, shikona link affordance and Career Length Longest Show
Active are complete as runtime/PA-specific interactions. The highest-risk
remaining items are Notes-popover validation/tightening and the remaining shared
table visual-language token work. The current column-group work is intentionally
interim and ad hoc; it should not become the first step toward a general table
theory.
