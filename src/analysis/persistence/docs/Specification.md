# Persistence Specification

## Status

Draft baseline specification.

This document specifies the first implementation of the Persistence analysis
tool. The README is treated as the requirements-level document.

## 1. Purpose

The tool shall compute retrospective division persistence for professional sumo
divisions.

For each supported division and anchor basho, it shall summarise how
persistently the rikishi currently in that division have belonged to that same
division over a fixed retrospective window.

The tool shall not use the term "churn" in output fields, chart text, or code
names introduced for this package.

## 2. Input

The tool shall read a `History` from the LiveStore history source.

The first implementation shall not provide a `--zip` option.

The command-line interface shall accept:

```text
--start
--end
--num-basho
```

`--start` and `--end` shall select the inclusive year range used from the
LiveStore `History`.

`--num-basho` shall be a positive integer.

## 3. Supported Divisions

The tool shall report the following divisions:

```text
Makuuchi
Juryo
Makushita
Sandanme
Jonidan
Jonokuchi
```

Makuuchi shall be derived from `MSD` rank levels:

```text
Yokozuna
Ozeki
Sekiwake
Komusubi
Maegashira
```

The lower divisions shall be derived from the corresponding `Division` enum
values.

## 4. Retrospective Window

For an anchor basho/date `t` and integer `num_basho`, define:

```text
W(t, num_basho)
```

as the anchor basho `t` plus the previous `num_basho` basho.

The window therefore contains `num_basho + 1` basho.

The tool shall only compute output rows for anchor dates where the full
retrospective window exists.

For example, if `num_basho = 6`, the first six dates in the selected history
range shall not produce rows.

## 5. Anchor Division Membership

For division `D` and anchor date `t`, define:

```text
R(D, t) = { r : r is on the banzuke at t and division(r, t) = D }
```

`R(D, t)` is the population over which division-level persistence is computed.

## 6. Rikishi-Level Persistence

For rikishi `r`, division `D`, anchor date `t`, and a retrospective lookback of
`num_basho` previous basho, define:

```text
A(r, t, num_basho) =
    { b in W(t, num_basho) : r is on the banzuke at b }
```

Then:

```text
p(r, D, t, num_basho) =
    count { b in A(r, t, num_basho) : division(r, b) = D }
    ------------------------------------------------------
    count { b in A(r, t, num_basho) }
```

The denominator shall exclude basho in which `r` is not on the banzuke.

A basho in which `r` is on the banzuke in another division shall count against
persistence in `D`.

For rows produced by this tool, `r` is drawn from `R(D, t)`, so the denominator
is non-zero by contract.

Persistence values shall be represented as probabilities in `[0, 1]`.

The tool shall not convert persistence values to percentages in CSV or chart
output.

## 7. Division-Level Statistics

For each `(date, division)` row, let:

```text
P = [p(r, D, t, num_basho) for r in R(D, t)]
```

`P` is non-empty by contract.

The tool shall compute:

```text
frequency = len(P)
mean_persistence = mean(P)
stdev_persistence = population_standard_deviation(P)
```

If `len(P) = 1`, `stdev_persistence` shall be `0.0`.

## 8. CSV Output

The tool shall write one CSV file per run.

The default filename shall include the run parameters:

```text
division_persistence (<start>-<end>, num_basho=<num_basho>).csv
```

The CSV shall contain one row per computed `(date, division)` pair.

Required columns:

```text
date
division
num_basho
frequency
mean_persistence
stdev_persistence
```

Rows shall be ordered by date ascending, then by `Division` enum order.

## 9. Chart Output

The tool shall write one Plotly HTML chart per run.

The default filename shall include the run parameters:

```text
division_persistence (<start>-<end>, num_basho=<num_basho>).html
```

The chart shall plot `mean_persistence` over time.

Chart requirements:

```text
x-axis: date
y-axis: mean_persistence
y-axis range: [0, 1]
one line per division
```

Hover text shall include:

```text
date
division
mean_persistence
stdev_persistence
frequency
```

The chart title shall include `num_basho`.

The chart shall display probabilities in `[0, 1]`, not percentages.

## 10. Output Directory

The tool shall write outputs under:

```text
files/output/persistence/
```

The output directory shall be created if it does not exist.

## 11. Non-Goals For First Implementation

The first implementation shall not include:

```text
forward-looking windows
centred windows
multiple num_basho values in one run
directional movement analysis
promotion or demotion cause modelling
rikishi-level output files
browser controls beyond the static Plotly chart
percent-formatted persistence values
```

## 12. Possible Future Extensions

Future versions may add:

```text
median persistence
quartiles
min/max persistence
SEM
CI95
RMSE from full persistence
support thresholds
rikishi-level CSV output
multi-window comparison charts
directional movement summaries
```

These are outside the first implementation.
