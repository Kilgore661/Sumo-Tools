# CSS Rationalisation Proposal

## Status

Proposal, not yet implemented.

This document proposes a modest CSS rationalisation for the web-based outputs.
The aim is to make future pages look like they belong to the same site without
turning the project into a bespoke layout language.

## 1. Context

There are now at least two web-output families:

- Standings by Wins / GSSWD
- Banzuke News

Both use, or are intended to use, a dark visual language. The banzuke-news mock
was deliberately styled dark so it can sit naturally alongside the existing
Wins Digest page.

The current standings CSS is monolithic and contains both site-wide visual
choices and standings-specific layout/table rules. The banzuke-news mock has
its own dark palette and table styling. If left alone, these pages will drift.

The proposed refactor is to extract shared visual grammar into common CSS while
leaving each output free to define its own page-specific structure.

## 2. Non-Goals

This proposal does not attempt to invent a custom layout language.

In particular, it should not create an elaborate class hierarchy where normal
HTML elements such as paragraphs, headings, and tables are re-modelled as an
object system.

HTML already has structure. CSS should provide shared presentation primitives,
not a parallel markup philosophy.

## 3. What We Are Probably Building

The emerging product is not a single-purpose app. It is closer to a personal
sumo site or lab:

```text
Gasopode-san's Sumo Lab
  Standings by Wins
    standard view
    other views
  Banzuke News
    Makuuchi view
    other division views
  future sumo oddities
```

This structure may change when a third or fourth kind of page appears. The CSS
should therefore support common patterns without assuming that all future pages
have the same information architecture.

## 4. Design Principle

Separate:

```text
visual grammar
layout primitives
page-specific styling
```

Do not hard-code today's site map into the CSS.

For example, "many pages may have an options panel and a content panel" is a
good reusable layout primitive. But "every major heading must have an options
left panel and content right panel" is too strong.

The right abstraction is optional:

```text
tool layout = optional options panel + content region
```

Pages that need it can use it. Pages that do not need it should still share the
same colours, fonts, panels, borders, and table language.

## 5. Proposed File Structure

Suggested future shape:

```text
src/analysis/common/files/
  site-wide.css
  tool-layout.css

src/analysis/standings/files/
  standings.css

src/analysis/news/files/
  banzuke-news.css
```

The exact paths can change, but the responsibilities should remain separate.

### `site-wide.css`

Shared visual grammar:

- colour tokens
- font tokens
- base `html` / `body`
- link defaults
- heading defaults
- standard panel surfaces
- standard table border/stripe tokens
- common spacing tokens

It should not know about standings, banzuke, deltas, ranks, menus, or any
particular analysis package.

### `tool-layout.css`

Reusable optional layout:

- `.tool-layout`
- `.tool-options`
- `.tool-content`
- responsive behaviour for collapsing or stacking options/content

This file should define the generic two-panel tool layout, but using it should
be optional.

### Page-Specific CSS

Examples:

```text
standings.css
  standings controls
  standings-specific table columns
  sortable headings
  percentage group separators

banzuke-news.css
  banzuke table geometry
  bz_chii / Rank column
  delta colour classes
  division heading treatment
```

Page CSS should consume shared tokens rather than redefining site colours and
fonts from scratch.

## 6. CSS Inclusion

Prefer explicit `<link>` tags in HTML:

```html
<link rel="stylesheet" href="../common/files/site-wide.css">
<link rel="stylesheet" href="../common/files/tool-layout.css">
<link rel="stylesheet" href="standings.css">
```

This makes dependencies visible to the eventual deployment tool.

CSS `@import` remains possible, but explicit links are easier to reason about
when copying or publishing assets.

## 7. Candidate Shared Tokens

The first extraction should probably define tokens like:

```css
:root {
  color-scheme: dark;

  --site-bg: #081633;
  --site-panel: #0d1f47;
  --site-panel-strong: #132b5c;
  --site-line: #7f95c0;
  --site-line-soft: rgba(127, 149, 192, 0.55);
  --site-text: #ffffff;
  --site-muted: #c9d4ee;
  --site-accent: #d8b86a;

  --site-font: Arial, Helvetica, sans-serif;

  --table-row-odd: rgba(255, 255, 255, 0.02);
  --table-row-even: rgba(255, 255, 255, 0.06);
}
```

Exact values should be chosen by comparing the existing GSSWD page and the
banzuke-news mock. The goal is not to preserve every current value, but to pick
a coherent dark visual grammar and reuse it.

## 8. Proposed Refactor Sequence

Do this in small steps:

1. Create `site-wide.css` with shared colour/font/table/panel tokens.
2. Update the banzuke-news mock to consume those tokens.
3. Update standings CSS to consume those tokens.
4. Extract only clearly generic layout rules into `tool-layout.css`.
5. Leave standings-specific table behaviour in `standings.css`.
6. Leave banzuke-specific table behaviour in `banzuke-news.css`.
7. Only split further if a file becomes difficult to work with.

The first refactor should be token extraction, not a grand redesign.

## 9. Risks

### Over-Generalisation

It is tempting to abstract too much from two examples. Avoid naming CSS around
today's product structure. Prefer small reusable primitives.

Bad:

```text
major-heading-with-left-menu-and-right-content.css
```

Better:

```text
site-wide.css
tool-layout.css
```

### Premature Navigation Assumptions

The current imagined home page has two major items with submenus:

```text
Standings by Wins
Banzuke News
```

A third feature may not fit that model. The home page should be allowed to
evolve independently from the shared page styling.

### WYSIWYG Editing

The banzuke-news HTML/CSS files are intended to remain editable. Shared CSS must
not make these files so indirect that ordinary visual editing becomes painful.

### Deployment Paths

Common CSS introduces path and copying questions for the publishing app. The
deployment tool should treat shared CSS as a first-class asset.

## 10. Recommendation

Proceed with a modest rationalisation:

- extract shared visual tokens and base styles
- create an optional two-panel tool layout
- keep page-specific CSS page-specific
- avoid inventing a custom markup or layout language

This should make the pages feel coherent while preserving the freedom to add
new kinds of sumo output later.
