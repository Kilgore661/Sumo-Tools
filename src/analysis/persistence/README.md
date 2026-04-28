# Persistence

The Persistence tool will measure how persistently the current members of a
sumo division have belonged to that same division over a retrospective window.

This tool is about **division persistence**, not churn.

## Purpose

For each basho date, division, and retrospective window length, the tool will
answer:

> Of the rikishi who currently comprise this division, how consistently have
> they been in this same division over the last `num_basho` basho?

The first version is deliberately narrow:

- input comes from the LiveStore `History`
- the window is retrospective only
- all reported persistence values are probabilities in `[0, 1]`
- output is one CSV plus one Plotly HTML chart per run

## Core Definitions

Let:

```text
r = rikishi
D = division
t = anchor basho/date
num_basho = retrospective window length
```

Supported divisions are:

```text
Makuuchi
Juryo
Makushita
Sandanme
Jonidan
Jonokuchi
```

Division membership at the anchor date:

```text
R(D, t) = { r : r is on the banzuke at t and division(r, t) = D }
```

Retrospective window:

```text
W(t, num_basho) = the num_basho basho ending at t, inclusive
```

The metric is defined only when the full retrospective window exists.

Rikishi-level persistence:

```text
A(r, t, num_basho) =
    { b in W(t, num_basho) : r is on the banzuke at b }

p(r, D, t, num_basho) =
    count { b in A(r, t, num_basho) : division(r, b) = D }
    ------------------------------------------------------
    count { b in A(r, t, num_basho) }
```

Absence from the banzuke is not treated as being in another division. It is
excluded from the rikishi-level denominator. Being in another division while on
the banzuke counts against persistence in `D`.

Division-level persistence:

```text
mean_persistence(D, t, num_basho) =
    mean { p(r, D, t, num_basho) : r in R(D, t) }
```

The companion dispersion statistic is:

```text
stdev_persistence(D, t, num_basho) =
    population standard deviation of the same rikishi-level persistence values
```

## Initial CLI

Planned command shape:

```powershell
python -m src.analysis.persistence --start 1958 --end 2026 --num-basho 6
```

There is no planned `--zip` parameter. The tool should use the LiveStore
history source directly.

## Outputs

Outputs should be written under:

```text
files/output/persistence/
```

For a run over `1958..2026` with `num_basho=6`, planned output names are:

```text
division_persistence (1958-2026, num_basho=6).csv
division_persistence (1958-2026, num_basho=6).html
```

The CSV should be monolithic for the run: one row per `(date, division)` for the
chosen `num_basho`.

Initial CSV columns:

```text
date
division
num_basho
frequency
mean_persistence
stdev_persistence
```

Where:

```text
frequency = |R(D, t)|
```

That is, `frequency` is the number of rikishi in that division at that date. It
is included as a sanity check and context for interpreting the standard
deviation.

## Chart

The initial chart should be a Plotly HTML file.

Chart requirements:

- x-axis: basho/date
- y-axis: `mean_persistence`
- y-axis range: `[0, 1]`
- one line per division
- hover should show date, division, mean persistence, stdev, and frequency
- title should include `num_basho`

All chart values should remain probabilities in `[0, 1]`, not percentages.

## Scope Boundaries

The first version should not include:

- forward-looking windows
- centred windows
- multiple `num_basho` values in one run
- directional movement analysis
- promotion/demotion cause modelling
- rikishi-level output files
- UI controls or a browser app beyond the static Plotly chart

## Possible Future Extensions

Later versions may add:

- median persistence
- quartiles
- min/max persistence
- SEM
- CI95
- RMSE from full persistence
- support thresholds
- rikishi-level CSV output
- multi-window comparison charts
- directional movement summaries

These are intentionally out of scope for the first implementation.
