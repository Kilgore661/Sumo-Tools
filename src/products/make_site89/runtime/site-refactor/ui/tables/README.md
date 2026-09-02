# Table Runtime Modules

This directory contains the implementation behind `../tables.js`.

`../tables.js` is the public facade used by panel rendering and chart modules.
Keep caller imports pointed there unless a module in this directory is
intentionally sharing an internal helper with another table module.

## Files

- `shared.js`: shared sort state, sort value helpers, table heading rendering,
  decimal formatting and rikishi links.
- `generic.js`: generic indexed and sectioned table renderers.
- `banzuke-changes.js`: Banzuke Changes style and scan table renderers.
- `standings.js`: Standings row filtering, visible columns, headings and cell
  rendering.

## Refactor Rule

This directory is a behaviour-preserving split of the former monolithic
`ui/tables.js`. Keep the facade export surface stable unless the public runtime
contract is deliberately changed.
