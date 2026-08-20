# Fixed-Supported Equelo

## Status

Current production replacement for `fixed_v2`.

This package owns the production fixed-supported Equelo artifact path. It
replaces the old raw fixed-point `fixed_v2` path because that path could assign
spurious extreme ratings to rarely supported low-ranked chii, most visibly in
the Highest Equelo table.

## How It Differs From `fixed_v2`

`fixed_v2` attempted to produce fixed-point entrant-initial ratings directly
for the full represented chii domain. Sparse temporary low-rank chii could be
underidentified, allowing repeated normalisation shifts to produce implausible
initial ratings and therefore implausible process ratings for rikishi occupying
those chii.

Fixed-supported Equelo instead:

- selects a supported chii domain using the accepted minimum-appearance policy;
- runs the fixed-point solve over that supported domain;
- completes the master chii initial-rating map for unsupported chii by RFSC;
- builds day-end/process ratings from the completed master map;
- writes the site-facing Equelo artifacts consumed by `make_site2`.

The package boundary is the artifact set, not the solver internals. Consumers
should use `src.analysis.equelo.api` or the generated files, not experiment
folders or legacy implementation modules.

## Main Entry Points

Run the full fixed-supported refresh with:

```text
python -m src.analysis.equelo.fixed_supported
```

The refresh writes:

```text
files/output/Equelo/fixed_supported/master_chii_initial_rating_map.csv
files/output/Equelo/fixed_supported/master_chii_initial_rating_map_metadata.json
files/output/Equelo/fixed_supported/day_end_ratings.json
files/output/Equelo/fixed_supported/landmarks/site/typical_equelo_values/typical_equelo_values.csv
```

Each solver run also writes a responsive, page-width Plotly chart beside its
combined statistics CSV:

```text
files/output/Equelo/fixed_supported/solver_runs/.../supported_fixed_point_estimates.html
```

This chart contains only the solver-native supported estimates. It does not
contain nearest-supported master-map completion or presentation smoothing.
Its x-axis retains every pre-filter collapsed chii, so unsupported chii appear
as empty positions rather than invented rating points. Each run also persists
that complete support domain as `all_chii_support.csv`.

To chart an existing solver statistics CSV without rerunning the solver:

```text
python -m src.analysis.equelo.smoothing.chart `
    path/to/combined_final_with_stats.csv `
    --support-csv path/to/all_chii_support.csv
```

For runtime lookup, use `src.analysis.equelo.api`. For validation of chii that
remain outside the rating domain, use:

```text
python -m src.analysis.equelo.validate
```
