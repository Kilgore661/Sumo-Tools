# Styling Changes

## Purpose

Record agreed rendering/styling rules that should later be folded into
`05 Rendering Design.md`.

## Section 9. Sidebar and Navigation Rendering

### Navigation-tree vertical rhythm

Navigation tree items have a navigation-local vertical rhythm to improve
legibility across top-level and nested entries. This treatment does not
determine table or other artifact density.

Current implementation:
`.nav-list { line-height: 1.45; }`

## Section 11. Heading Rendering

### Action item: choose ownership of heading typography

The current renderer uses HTML heading elements as provisional typography
handles for several distinct modelled heading roles.

Current provisional implementation:

```css
.site-title {
  font-size: 24px;
}

h2 {
  font-size: 20px;
}

h3 {
  font-size: 18px;
}
```

This is not yet a settled rendering rule.

The current provisional implementation is inconsistent in ownership terms:
`.site-title` applies typography according to a modelled rendered role, whereas
`h2` and `h3` apply typography according to HTML heading level.

Choose whether intentional heading typography is owned by:

1. HTML heading hierarchy, so shared rules such as `h1`, `h2`, and `h3`
   determine visible treatment; or
2. modelled rendered roles, so distinct roles such as `site-title`,
   `content-title`, and `content-summary` receive explicit typography, while
   HTML heading elements are retained only where justified for document
   structure and accessibility; or
3. an explicit combination, where heading hierarchy supplies defaults and
   selected modelled roles override them.

This choice should be made before further typography is imported from legacy
CSS or additional heading-specific styling is added.

## Section 12. Filter Rendering

### Filter-section list markers

Lists emitted within a FilterSection are structural representations of filter
controls or their choices. They do not display list markers. Browser-default
indentation remains unless a later layout rule replaces it.

Current implementation:
`.filter-section ul { list-style: none; }`

## Section 16. Artifact Rendering

### Banzuke Changes movement direction

Banzuke Changes distinguishes the direction of a rikishi's movement from the
magnitude of that movement.

In both the banzuke-style and scan-style table renderings, movement direction is
a visible part of the artifact. The column is headed `⇅` and displays `↑` for
upward movement, `↓` for downward movement, and no symbol for neutral movement.

The optional `Delta` filter controls the display of numeric movement magnitude;
it does not control visibility of the direction column.

Current implementation:

- `banzukeSideColumns()` always includes a `direction` column headed `⇅` for
  each side of the banzuke-style table.
- `banzukeScanColumns()` always includes a `direction` column headed `⇅` in the
  scan-style table.
- `banzukeSideValue()` renders direction by deriving `↑` or `↓` from the signed
  side delta value.
- The numeric `delta` column remains conditional on `state.delta`.

### Table-like artifact cell padding

Table-like artifacts use shared internal cell padding so adjacent column values
remain visually distinct and table rows have a small amount of vertical
breathing room.

This is a site-wide table-like artifact rule, not a page-specific or
artifact-specific exception. The current value is provisional and should
eventually be represented as a shared table-density token if explicit rendering
configuration is introduced.

Current implementation:

```css
.artifact-table th,
.artifact-table td {
  padding: 2px 0.25em;
}
```

### Table-like artifact alternating data-row backgrounds

Table-like artifacts distinguish successive data rows using alternating
background colours. This treatment applies to rows in `tbody` only; table
headings are not striped.

The alternating row treatment is a shared table-like artifact rule rather than
a Banzuke Changes exception. The current colours are provisional theme values.

Current implementation:

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

### Table-like artifact collapsed cell borders

Table-like artifacts suppress browser-default gaps between adjacent cells so
shared row-background treatment reads as a continuous row rather than as
separate cells divided by background-coloured gutters.

Current implementation:

```css
.artifact-table {
  border-collapse: collapse;
}
```

### Action item: choose the semantic treatment of Banzuke Changes rank cells

In the banzuke-style table, the central Rank value describes the banzuke row
occupied by the East and West rikishi. The former rendering represented that
value as a row-header cell and styled it at normal font weight.

The current provisional implementation emits the value as `<td scope="row">`
to avoid browser-default bold rendering. The `scope` attribute does not give an
ordinary data cell row-header semantics.

Choose whether the Rank value is:

1. a semantic row header, in which case it should render as `<th scope="row">`
   with an explicit normal-weight presentation rule if required; or
2. an ordinary table value, in which case it should render as `<td>` without a
   `scope` attribute.
