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

## Section 12. Filter Rendering

### Filter-section list markers
Lists emitted within a FilterSection are structural representations of filter
controls or their choices. They do not display list markers. Browser-default
indentation remains unless a later layout rule replaces it.

Current implementation:
`.filter-section ul { list-style: none; }`
