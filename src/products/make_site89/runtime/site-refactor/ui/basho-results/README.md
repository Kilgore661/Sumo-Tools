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

## Result Layout

Wins, losses and absences remain separate sortable columns with centred
headings and values. Narrow, non-sortable separator columns render the record
as `W - L - A`; the second separator is blank when the absence count is blank
or zero. Result-count and separator columns opt out of the shared 24-pixel
minimum column width and have no horizontal cell or sort-button padding or
margin, so the record remains compact at wide viewport sizes.

## Refactor Rule

This directory is a behaviour-preserving split of the former monolithic
`ui/basho-results-table.js`. Keep the facade export surface stable unless the
public runtime contract is deliberately changed.
