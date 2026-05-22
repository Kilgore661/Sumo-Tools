# One Column Prototype

## Status

Experimental implementation note.

The one-column Banzuke Change Report view is intentionally implemented as a
prototype, not as the final design architecture.

## What We Did

The traditional BCR table is an east/west banzuke display:

```text
east context | east shikona | rank | west shikona | west context
```

The current one-column view reuses the centre `rank` column and the right-hand
side column order from the traditional view:

```text
chii | shikona | direction | delta | result | previous chii
```

The first column uses the rikishi's full current `Chii`, such as `M3e` or
`M3w`.  The traditional two-column spine still uses `bz_chii`, such as `M3`,
because that column labels an east/west banzuke row rather than a single
occupied slot.

At runtime, the shared browser JavaScript detects the template with
the `Banzuke Style` checkbox state and flattens each CSV banzuke row into up to
two display rows, east first and west second, when traditional banzuke style is
unchecked.

This keeps `index.html` as the single concrete WYSIWYG-editable template.  It
does not require a second HTML template, second data contract, second CSS
vocabulary, or separate publisher path.

## Why This Is A Hack

This deliberately reuses the west/right-side display shape because that shape
already resembles the desired scan-friendly list.  Some class names and helper
function names therefore describe their original two-column context rather than
the new one-column role.

That is acceptable for discovery work, but it is not a clean product design.
The one-column layout is conceptually a single-rikishi row, not the west half
of a traditional banzuke table.  If the feature becomes permanent, the code
should stop pretending those are the same thing.

## Why We Are Accepting It For Now

The one-column requirement is not yet stable.  The point of this prototype is
to learn whether the scan-friendly view is useful before investing in a more
formal template/layout model.

The current compromise keeps the cost low:

- one CSV/config publication contract
- one shared browser renderer
- one shared stylesheet
- one editable HTML template
- no new publisher data model

## What To Do If This Becomes Permanent

If the one-column view proves useful enough to keep, replace this prototype
with an explicit layout model.

Likely direction:

- introduce neutral single-rikishi row helpers instead of reusing west-side
  helpers;
- rename CSS classes around display roles, not table sides;
- treat the traditional view as a mirrored composition of two side rows plus a
  rank spine;
- treat the one-column view as the canonical single-rikishi row;
- keep the WYSIWYG template contract explicit instead of letting JavaScript
  silently own more of the layout than the template suggests.

The important future invariant should be:

```text
The rendered views should be based on explicit template objects, and shared row
objects and styles should be named after their real semantic role.
```
