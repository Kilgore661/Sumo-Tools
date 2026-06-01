# Chart Runtime Modules

This directory contains the implementation behind `../charts.js`.

`../charts.js` is the public facade. Keep caller imports pointed there unless a
module in this directory is intentionally sharing an internal helper with
another chart module.

## Files

- `shared.js`: common Plotly config, chart element IDs, row selection and axis
  helpers.
- `generic.js`: artifact-driven stacked bar, grouped line, ordered bar and
  category bar chart renderers.
- `finish-by-chii.js`: Finish by Chii title, row selection and Plotly bar chart.
- `career-length.js`: Career Length table/chart view handling.
- `standing-win-probability.js`: Standing Win Probability traces, layout,
  source handling and Plotly legend behaviour.

## Refactor Rule

This directory is a behaviour-preserving split of the former monolithic
`ui/charts.js`. Keep the facade export surface stable unless the public runtime
contract is deliberately changed.
