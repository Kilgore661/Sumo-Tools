# One-shot Requirements

## Purpose

`one_shot` is a new analysis package under `src.analysis.equelo` whose job is to study **single-pass convergence / initialization sensitivity** of the Elo simulator in the **modern** regime.

It is explicitly **not** the fixed-point solver from `expt2`, and it is **not** primarily a diagnostics wrapper like `expt1`.

## Core question

Given a fixed historical slice and a chosen initialization scheme:

* when the simulator is run forward once, in chronological order,
* do the basho-start ratings associated with selected chii become less sensitive to initial conditions over time?

The first intended regime is:

* **modern only**
* **closed mode only**

## Scope of phase 1

Phase 1 is exploratory and visual.

The first output is not a proof or formal convergence theorem. It is:

* time-series extraction
* interactive charts
* enough bookkeeping to support later metric design

## Historical regime requirements

For phase 1, `one_shot` shall operate on the **modern** regime only, meaning:

* only data from **1989 onward**
* using the same historical/oracle concepts already present in the Equelo codebase, if they are sound enough to reuse

This needs checking, but the current intent is reuse rather than rewrite.

The pre-1989 “naive” and “combined” ideas are out of scope for now.

## Simulation requirements

`one_shot` shall use a **single forward pass** simulator.

Preferred approach:

* reuse the `expt1` simulator unchanged if its contract is sufficient
* only create a separate simulator if the requirements cannot be met cleanly through reuse

The simulator must support:

* closed mode
* externally supplied entrant initialization
* access to **basho-start ratings**
* access to chii at basho start

`expt1.simulate.simulate(...)` appears close to this already. 

## Initialization requirements

The experiment axis for phase 1 is **initial ratings**.

`one_shot` shall support multiple initialization schemes, including random ones.

The exact family of schemes is not fixed yet, but the design must assume:

* there will be more than one scheme
* schemes may have parameters
* repeated runs under the same scheme may differ by seed

## Observational target

The object of interest is not a particular rikishi.

The object of interest is the basho-start rating associated with a **chii** over time.

In phase 1, focus is on a fixed set of probe chii:

* `Y1e`
* `S1e`
* `M1e`
* `M4e`
* `M8e`
* `M12e`
* `M16e`

These are the initial visual probes.

## Plotting requirements

The first analysis products shall be interactive HTML charts using Plotly.

Reason:

* legend click-to-hide/show makes multi-series inspection practical

The first charts should support visual inspection of the probe chii over time.

At minimum, phase 1 needs charts that let you inspect:

* one or more runs
* the seven probe chii
* basho-start ratings over basho date

## Coverage requirements

Although the first visual focus is the seven probe chii, the computation should not be artificially restricted to them.

The system should be capable of computing chii-linked quantities for all chii in the modern era, even if only a subset is plotted initially.

For now, the only mandatory extra bookkeeping per chii is:

* number of observations

No thresholding or exclusion rules are required yet.

If some chii later look unusually behaved, observation count will be used as the first explanatory check.

## Output requirements

All output shall live under the Equelo output tree.

Agreed root:

* `files/output/Equelo/one_shot/`

More specifically, runs should be isolated in timestamped folders, for example:

* `files/output/Equelo/one_shot/runs/2026_04_12_21_09_03/`

Each run folder shall contain all artifacts for that run, such as:

* charts
* data files
* metadata

This is now part of the contract.

## Metadata requirements

Each run must write a metadata file such as `run.json`.

This metadata should record the settings needed to understand the artifacts later.

The exact schema is not fixed yet, but it will need to cover things like:

* regime used
* simulator mode
* initialization scheme
* seed
* probe chii
* date/time of run

## CLI / packaging requirements

`one_shot` shall be a normal package runnable as:

`py -m src.analysis.equelo.one_shot`

So it should follow the existing project convention:

* package folder
* `__main__.py`
* orchestration in a CLI or similarly thin entry point

This mirrors how `expt1` is currently structured.

## Repository placement

New package location:

* `src/analysis/equelo/one_shot/`

This package is conceptually separate from:

* `expt1` single-pass experiment/orchestration
* `expt2` fixed-point solver

## Configuration requirements

No final requirement has been agreed yet on config structure.

The tension is currently:

* shared constants should stay consistent with Equelo-wide definitions such as `INITIAL_Q`
* but `one_shot` should also have a clear local home for its own parameters

What is established so far is only this:

* `config_main.py` currently defines shared Equelo constants such as `INITIAL_ELO`, `INITIAL_Q`, `CONSTANT_K`, `OUTPUT_ROOT`, and input paths. 
* configuration design for `one_shot` is deferred until the requirements are clearer

So config layout is explicitly **not yet decided**.

## Programming-style requirements

You’ve stated a strong design constraint:

* offensive programming
* top-down and by-contract
* no `try/except`, `dict.get()`, or `Optional` unless directly required by the contract

So `one_shot` should be designed around:

* explicit invariants
* explicit preconditions
* narrow, deliberate interfaces

That is a real requirement, not just a style note.

## Non-requirements for phase 1

These are currently out of scope:

* transfer across regimes
* naive/combined experiments
* threshold-based filtering
* formal asymptotic proofs of convergence
* overgeneralized abstractions for all future Equelo work

## Immediate open questions

The main things still undecided are:

* exact definition of the initialization schemes
* exact chart set for phase 1
* whether the oracle can be reused unchanged for modern slicing
* whether `expt1` simulator contract is sufficient as-is
* config structure for `one_shot`
* exact schema of `run.json`

## Condensed statement

If I compress all of this into one contract statement:

`one_shot` is a new Equelo analysis package that runs the closed-mode single-pass Elo simulator on modern-era data from 1989 onward under varying initial conditions, extracts basho-start chii-linked rating series, and writes timestamped Plotly-based interactive outputs plus run metadata under `files/output/Equelo/one_shot/runs/...` for exploratory convergence analysis.
