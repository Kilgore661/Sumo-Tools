# Semantic Table Column Styling Proposal

## Problem

Public tables currently have styling rules attached mostly to local table
columns and page-specific renderers. This makes the same kind of value drift
between pages.

Examples observed during the UI consistency pass:

* chii values may be left-aligned in one table and centred in another;
* chii-like strings used in Banzuke Changes rank/context columns are styled
  locally rather than as chii;
* Equelo ratings may be centred or right-aligned depending on the page;
* previous-basho/context columns are muted by local CSS in some tables and by
  runtime group classes in others;
* row-number columns are quiet in some pages but not yet expressed as a
  site-wide semantic rule.

The underlying issue is that the table model knows a column id, heading,
source field, group, formatter, and alignment, but it does not consistently
state what kind of value the column represents.

## Proposal

Add semantic column metadata to public table definitions and use that metadata
to emit shared CSS classes.

A column should be able to say, for styling and behaviour purposes, that it is
a `chii`, `record`, `rating`, `movement`, `row-number`, `shikona`, or other
recognised value kind.

The guiding principle is that a chii is a chii. Full chii values such as
`M3eHD`, ordinary values such as `J10w`, and chii-like rank/context strings in
Banzuke Changes should use the same site-wide chii treatment unless a page has
a documented exception.

This is separate from the table's analytical meaning. A value may be previous,
current, contextual, or primary, but its value kind still determines the
baseline presentation.

## Suggested Metadata

Extend `TableColumn` with optional fields such as:

```text
value_kind: row-number | shikona | chii | record | movement | rating | rating-delta | count | percent | text
role: identity | current | previous | context | metric | comparison
```

The exact names are not final. The important split is:

* `value_kind` says what kind of value is in the cell;
* `role` says how the value functions in this table.

If only one field is introduced initially, start with `value_kind`. It is the
more important missing layer.

## Initial Styling Contract

Candidate site-wide defaults:

* `value-row-number`: muted; not sortable unless explicitly justified.
* `value-shikona`: shared rikishi link styling and click/alt-click behaviour.
* `value-chii`: centred; consistent typography and compact spacing.
* `value-record`: centred; tabular numeric treatment where useful.
* `value-movement`: centred, bold, compact; blank for neutral/no movement when
  the page contract says so.
* `value-rating`: right-aligned; tabular numeric treatment.
* `value-rating-delta`: right-aligned; signed numeric treatment.
* `value-count`: right-aligned or centred by policy, but consistent.
* `value-percent`: right-aligned or centred by policy, with consistent percent
  formatting.
* `role-previous` or `role-context`: muted.

These defaults should live in the shared site CSS. Page-specific CSS should
override them only for a documented local reason.

## Implementation Sketch

1. Add optional semantic fields to the table manifest dataclasses.
2. Update the runtime table renderer to emit classes such as
   `value-chii`, `value-rating`, `value-row-number`, `role-previous`.
3. Add shared CSS rules for those classes.
4. Annotate current runtime table manifests, starting with Standings by Wins
   and Basho Results Browser.
5. Update hand-built pages, especially Banzuke Changes, to emit the same
   semantic classes even before they migrate fully to the runtime renderer.
6. Remove or reduce local CSS rules that duplicate the new site-wide semantic
   treatment.
7. Visually inspect representative pages after each pass.

## Notes and Risks

The implementation is not technically large, but it touches presentation
contracts across many pages. The main risk is visual regression caused by
surfacing old local assumptions.

Do not treat this as a broad redesign. It is a missing vocabulary layer for
tables, intended to make future styling changes site-wide rather than
attribute-by-attribute.

The proposal should be coordinated with:

* the shared CSS rationalisation item;
* the table behaviour inventory;
* the embedded page migration assessment;
* the Chii naming policy, because chii/chii-like display needs consistent
  terminology and styling.
