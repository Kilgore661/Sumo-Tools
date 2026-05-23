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
`.nav-list { line-height: 1.4; }`

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
