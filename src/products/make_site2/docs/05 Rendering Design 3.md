## 14. Rendering `PA` Terminal Forms

### 14.1 General PA Rule

**Owner:** `PAPanel -> PA . Notes`

**Rule:** A PA renderer shall render the terminal form and declared PA-visible
features within the PA region of its PAPanel. It may use terminal-form-specific
structure, but shall not render Page headings, global Navigation, sibling
FilterSection layout or Notes outside the PAPanel ownership relationship.

PA framing distinct from Page Heading shall be rendered consistently where it is
modelled.

When a PA terminal form uses a Plotly chart, the chart should resize to fill the
remaining PA slot space after ordinary layout changes, including Notes-panel
show/hide changes and NavigationBar content hide/restore changes, subject to
any chart-specific minimum useful size.

---

## 15. Rendering Table-Like PAs

This section applies to `<table>`, `<indexed table>` and table-like portions of
`<sectioned table>` PAs unless an explicit PA-specific rule justifies an
exception.

### 15.1 Shared Table Container

**Owner:** table-like PA terminal forms

**Rule:** Table-like PAs shall use shared table rendering treatment for ordinary
readability decisions rather than page-specific table styling.

Individual PAs may define column meaning, groups, links, optional visible
features and specialised structure. Those meanings do not prevent shared table
legibility treatment from applying where compatible.

### 15.2 Cell Padding

**Owner:** table-like PA terminal forms

**Rule:** Table cells shall use shared internal padding so adjacent values remain
visually distinguishable and rows have modest breathing room.

**Current treatment:**

```css
.artifact-table th,
.artifact-table td {
  padding: 2px 0.25em;
}
```

**Scope:** Applies to shared table-like PA cells. It does not define spacing in
Navigation, Filters, Notes or charts.

**Value status:** Exact padding values are revisable table-density values. The
shared treatment is settled as a table-rendering rule.

### 15.3 Alternating Data-Row Backgrounds

**Owner:** table-like PA terminal forms

**Rule:** Successive data rows shall use alternating background treatment to help
readers track values across table columns and successive rows. The treatment
shall apply to data rows, not heading rows.

**Current treatment:**

```css
:root {
  --artifact-row-odd-bg: #12234b;
  --artifact-row-even-bg: #1b2c52;
}

.artifact-table tbody tr:nth-child(odd) {
  background: var(--artifact-row-odd-bg);
}

.artifact-table tbody tr:nth-child(even) {
  background: var(--artifact-row-even-bg);
}
```

**Value status:** The existence and scope of data-row differentiation are shared
policy. The exact theme colours are revisable presentation tokens and should be
reviewed when alternative site-context themes are normalised.

### 15.4 Continuous Row Treatment

**Owner:** table-like PA terminal forms

**Rule:** Shared data-row background treatment shall read as a continuous row
rather than as separately tinted cells divided by unintended page-background
gutters.

**Current treatment:**

```css
.artifact-table {
  border-collapse: separate;
  border-spacing: 0;
}
```

This is a shared rendering treatment rather than a semantic claim about table
data.

### 15.5 Sticky Table Context

**Owner:** table-like PA terminal forms

**Rule:** When table content overflows the PA slot vertically, the PA title or
caption and table column headings should remain visible at the top of the PA
slot while data rows scroll.

The current runtime realizes this by making the artifact title block, table
section headings and table header cells sticky within the PA slot scroll
container. This is a rendering treatment for reader orientation; it does not
change table data, sorting semantics or PA ownership.

**Current treatment:** Ordinary table-like PAs are upgraded at runtime into a
table shell containing a non-scrolling header region and a scrolling body
region. The body region owns the vertical scrollbar, so the scrollbar begins
below the table headings while the PA title/caption and headings remain visible.

This is currently a rendering realization rather than a distinct semantic PA
model entity. If future pressure requires producer-visible table chrome/body
semantics, the Published Artifact model may be refined to represent that split
directly.

### 15.6 Alignment, Emphasis and Semantic Signals

Column alignment, link styling, font weight, muted text and status colours may
communicate meaning. Where such treatments are common shared table behaviour,
they shall be declared here. Where they express PA-specific meaning, they shall
be declared with that PA or feature.

Browser-default emphasis shall not be retained merely by accident when it
communicates an unintended semantic distinction.

The current table heading/cell horizontal alignment policy is not settled.
Basho Results (7.1) exposed the issue because its recursive renderer does not
obviously inherit the same alignment treatment as ordinary flat tables. The
open question is whether heading alignment and cell alignment should be explicit
model properties applied uniformly across flat and recursive table renderers.
Until that decision is made, alignment differences remain an open rendering/model
issue rather than a settled Basho Results exception.

### 15.7 Sortable Heading Treatment

**Owner:** table-like PA terminal forms

**Rule:** A sortable table column heading shall render as an interactive heading
control. The active sorted heading shall show the current sort direction with a
trailing up/down indicator and expose equivalent accessible sort state.

Row-number headings shall not render as sortable controls.

For a recursive table, this rule applies to visible terminal/leaf headings.
Group headings that span more than one data column are not sortable unless a
PA-specific model declares single-column sort meaning for them.

### 15.8 Basho Results Recursive Table Rendering

**Owner:** Basho Results (7.1) recursive presentation table, as specified in
`04.5 Basho Results Model.md`.

**Rule:** Basho Results may render a specialised recursive table with grouped
Before Basho, Current/After Basho and Next Basho headings. Reference columns
remain present without a visible group caption. The renderer shall remain inside
the PA region of its PAPanel and shall not redefine Page Heading, FilterSection,
Notes placement or shell layout.

Basho Results result values are logically decomposed into wins, losses,
absences, prizes and Division Change. Rendering may still bridge from compact
producer fields while the producer shape is transitional, but the public model is
the decomposed form specified in `04.5`.

Basho Results Shikona cells may render as public rikishi links when rikishi ids
are supplied. Basho Results recursive terminal paths are the visible column
identities for leaf-heading sorting.

---

## 16. Rendering Indexed-Table PAs

**Owner:** `PA -> <indexed table>`

An indexed-table PA shall render its currently selected table instance within
the PA region and consume relevant Filter/public state declared for selecting
that instance.

The fact that an indexed table loads or selects among payloads is PA-terminal
behaviour. It shall not cause the PA renderer to redefine ContentPanel,
FilterSection or Notes placement.

Where the visible output is table-like, shared table treatments in Section 15
apply unless a declared exception is required.

---

## 17. Rendering Chart PAs

**Owner:** `PA -> <chart>`

A chart PA shall render declared analytical series, axes, labels and relevant
visible features within its PA region.

Chart-library implementation choices, palette, size, legend position and hover
presentation are rendering choices unless a particular feature carries declared
analytical meaning. Chart Notes remain Notes in the PAPanel rather than ad hoc
Filter help or unrelated footer text.

### 17.1 Shared Plotly Chart Presentation

When a chart PA is rendered with Plotly, it shall use the shared chart runtime
configuration unless a declared PA-specific exception is required.

Shared Plotly chart presentation includes:

- Plotly charts shall be responsive.
- Plotly charts shall resize after ordinary layout changes that alter the PA
  slot, including Notes-panel show/hide changes and NavigationBar
  hide/restore changes.
- Plotly mode bars shall be available without showing the Plotly logo.
- Plotly x-axis and y-axis titles shall render in bold text as shared axis-title
  presentation, so axis captions remain visibly distinct from tick labels.
- Long x-axis tick labels may be rotated, with `45` degrees as the normal
  first candidate when horizontal labels are not legible.
- X-axis tick rotation is a chart artifact/layout property, not an ad hoc local
  renderer decision.
- Legend interaction that changes analytical visibility should use a shared
  runtime handler where default Plotly behaviour is not the intended public
  interaction.

The current runtime implements the shared Plotly configuration in
`runtime/site-refactor/ui/charts/shared.js`. Current chart layouts use the
shared `axisTitle` helper for axis-title emphasis. Current generic chart layouts
read `x_tickangle` from artifact provenance. Standing Win Probability currently
has PA-specific legend behaviour; if the same legend interaction is wanted by
more chart PAs, it should be promoted into a shared chart helper rather than
copied locally.

Shared chart presentation rules shall continue to be added as real promoted
chart cases require them and are agreed.

---

## 18. Rendering Sectioned-Table and Prose PAs

### 18.1 Sectioned Tables

**Owner:** `PA -> <sectioned table>`

A sectioned-table PA shall render its modelled sections within the PA region.
Section labels and local table structure are PA-internal visible features.
Shared table treatment applies to its table-like content where compatible.

### 18.2 Prose

**Owner:** `PA -> <prose>`

A prose PA shall render deliberately published narrative or explanatory material
within the PA region. It shall not function as a route for copied arbitrary HTML
that replaces Page Heading, Filters, PAPanel or Notes ownership.

Prose typography and inline structure shall be specified as promoted prose cases
require a settled shared treatment.

---

## 19. Rendering Custom-Artifact PAs

**Owner:** `PA -> <custom artifact>`

A custom-artifact renderer may realise genuine PA-specific analytical structure
where generic terminal rendering cannot express it honestly. It shall remain
within the PA region of `PAPanel`.

Custom PA rendering may declare feature-specific rendering rules where those
features carry public analytical meaning. Such rules shall identify their PA
owner and shall not be disguised as generic site styling.

### 19.1 Banzuke Changes Movement Direction

**Owner:** Banzuke Changes custom PA visible movement features

**Rule:** Banzuke Changes distinguishes direction of movement from magnitude of
movement. In both banzuke-style and scan-style renderings, movement direction is
a visible feature headed `⇅`, displaying `↑` for upward movement, `↓` for
downward movement and no symbol for neutral movement.

The numeric `Delta` feature is separate. Its visibility may be controlled by the
relevant Filter; that Filter does not remove the direction feature.

**Rationale:** Direction is part of the default public reading of banzuke
change, while numeric magnitude is optional further detail.
