# Basho Results Runtime Modules

This directory contains the implementation behind `../basho-results-table.js`.

`../basho-results-table.js` is the public facade used by panel rendering and
tests. Keep caller imports pointed there unless an internal module needs a
direct helper from this directory.

## Files

- `shared.js`: table IDs and default sort path.
- `table-spec.js`: recursive table specification and presentation vocabulary.
- `model.js`: public presentation model, visible-path projection and heading
  state.
- `values.js`: row value derivation, result parsing, rating-order analysis and
  rank movement helpers.
- `render.js`: header, cell and recursive table rendering.
- `sorting.js`: sort state, sort value derivation and click wiring.

## Refactor Rule

This directory is a behaviour-preserving split of the former monolithic
`ui/basho-results-table.js`. Keep the facade export surface stable unless the
public runtime contract is deliberately changed.
