# Persistence Design

## Status

Draft design note.

The Persistence tool is small enough that design and implementation are close.
This document records only the design choices that matter before code.

## 1. Overall Shape

The tool is a batch analysis pipeline:

```text
History
  -> ordered basho dates
  -> retrospective windows
  -> rikishi-level persistence values
  -> division-level aggregate rows
  -> CSV and Plotly HTML output
```

The pipeline is retrospective only. For anchor date `t`, the relevant window is
the `num_basho` basho ending at `t`.

## 2. Module Boundaries

The implementation should keep pure analysis separate from reporting and CLI
orchestration.

Suggested module shape:

```text
src/analysis/persistence/
  __main__.py
  division_persistence.py
  reports.py
```

Responsibilities:

```text
division_persistence.py
    Domain logic: division mapping, retrospective windows, rikishi-level
    persistence, division-level aggregate rows.

reports.py
    Output logic: CSV writing and Plotly HTML chart writing.

__main__.py
    CLI parsing, History loading, orchestration.
```

The public surface should be small. The three top-level API functions are:

```python
compute_division_persistence(history, num_basho) -> PersistenceResults

write_persistence_csv(results, output_path) -> Path

write_persistence_chart(results, output_path, title) -> Path
```

The computation function is the domain boundary:

```text
History + num_basho -> PersistenceResults
```

The reporting functions should consume `PersistenceResults` without
recomputing domain facts.

The chart title is not part of the domain result. It is supplied by the caller
because the caller knows run context such as CLI start/end years and preferred
wording.

The orchestrating module should therefore:

```text
parse CLI arguments
load History
compute PersistenceResults
construct output paths and chart title
write CSV and chart
```

## 3. Result Boundary Object

`PersistenceResults` is the boundary object between domain computation and
reporting.

It should contain the computed rows and the analysis parameter needed to
interpret them:

```text
num_basho
rows
```

Each division persistence row should contain reporting-ready values, including:

```text
date
division
num_basho
frequency
mean_persistence
stdev_persistence
```

The reports should not need to know how to map ranks to divisions, which
dates have full windows, or how persistence is computed.

## 4. Contract Style

The implementation should follow the project style: design by contract, trust
inputs that satisfy the contract, and avoid defensive clutter.

The code may assume:

```text
num_basho is positive after CLI parsing
LiveStore returns a coherent History
dates are comparable and sortable
computed anchor dates have full retrospective windows
supported divisions have non-empty banzuke populations
rikishi in R(D, t) have non-empty active denominators
```

If one of these assumptions is wrong, an ordinary Python failure is preferable
to a polite but information-poor recovery path. Such a failure indicates that
the requirements or contracts need correction.

## 5. Division Mapping

The tool works at division level.

In this codebase, Makuuchi ranks are represented by `MSD` values:

```text
Yokozuna
Ozeki
Sekiwake
Komusubi
Maegashira
```

For this tool, all `MSD` values map to:

```text
Makuuchi
```

This is because `MSD` means Makuuchi subdivision. Yokozuna, Ozeki, Sekiwake,
Komusubi, and Maegashira are not divisions for this analysis.

Lower divisions map directly from their `Division` enum values:

```text
Juryo
Makushita
Sandanme
Jonidan
Jonokuchi
```

## 6. Persistence Aggregation

The rikishi-level value is the primitive.

The division-level row is an aggregation over the rikishi who comprise the
division at the anchor date.

```text
R(D, t) = current members of division D at t
```

For each `r in R(D, t)`, compute:

```text
p(r, D, t, num_basho)
```

Then aggregate those values into:

```text
frequency
mean_persistence
stdev_persistence
```

`frequency` is the current division size and provides context for the standard
deviation.

## 7. Output Design

Outputs are fixed under:

```text
files/output/persistence/
```

Each run writes:

```text
one monolithic CSV
one Plotly HTML chart
```

The CSV is the primary data product.

The chart is a convenience view over the CSV-shaped data:

```text
x-axis: date
y-axis: mean_persistence
one line per division
```

All persistence values remain probabilities in `[0, 1]`.

## 8. Deliberate Non-Designs

The first version does not design for:

```text
forward-looking persistence
centred windows
multiple num_basho values in one run
rikishi-level output files
directional movement summaries
browser controls
custom output locations
```

These can be added later if they become real requirements.
