# System and Run Model (Expt1)

## Overview

The simulator (`simulate` in `simulate.py`) is the core deliverable of this
module. Expt1 defines a **specific configuration and usage of that simulator**
over historical sumo data.

This document describes how the simulator is actually used in Expt1, including:

- the data preparation pipeline
- parameter resolution
- fixed modelling choices
- diagnostic collection

The command-line interface in `cli.py` exists as a convenience entry point, but
is not the primary interface to the system.

---

## Pipeline

A complete Expt1 run follows the pipeline:

```

raw history → oracle → simulate → diagnostics

````

### 1. Raw history

Loaded via infrastructure code (`connect(...)`), producing a `History` mapping
from `Date` to `BashoState`.

This stage determines:

- the time interval of the run
- the raw source of bout data

---

### 2. Oracle (preprocessing)

Implemented in `Oracle.py` via `make_oracle(...)`.

This stage transforms raw history into a **cleaned, observable history** suitable
for Elo simulation.

Key rules applied:

- discard data before 1958
- before 1989:
  - retain only bouts with at least one sekitori
  - retain all raw-banzuke sekitori in the rating banzuke, even when they
    have no retained bouts in that basho
- from 1989 onward:
  - retain only bouts consistent with the banzuke
- collapse rank representation (`Chii`) according to a chosen mode
  - default: remove annotations only

This stage determines **which bouts are visible to the simulator** and which
rikishi are in the active rating universe. The two are deliberately distinct:
whole-basho absent sekitori have no bout updates, but they remain in the rating
universe instead of being treated as departures and later fresh entrants.

---

### 3. Parameter resolution

Implemented in `params.py`.

The CLI resolves:

- baseline rating `b`
- logistic scale `q`
- K-factor function `k(ordinal)`

Two K-factor policies are supported:

- constant K
- divisional K loaded from JSON

The result is an `EloParams` object passed into `simulate(...)`.

---

### 4. Entrant initialisation

Defined in `initialisation.py`.

In Expt1, this is fixed to:

```
constant_initialiser(b)
````

Implication:

* all previously unseen rikishi are initialised at exactly the baseline rating

This is a **modelling assumption**, not a requirement of the simulator.

---

### 5. Simulation

Executed via:

```
simulate(
    history=oracle.history,
    params=params,
    entrant_initialiser=...,
    mode=...,
    observer=...,
)
```

This produces rating trajectories over basho and days.

---

### 6. Diagnostics

Implemented in `diagnostics.py` via `DiagnosticsCollector`.

The observer is attached to the simulation and records:

* per-basho summaries (population, mean, update scale)
* retirement events and redistribution
* conservation checks
* counts of ignored bouts (`fusen`, `blank`)
* entry and retirement counts

Outputs are written to CSV and log files.

---

## What is specific to Expt1

Expt1 is defined not just by the simulator, but by the following fixed choices:

### Preprocessing

* Oracle-based cleansing is always applied
* default collapse mode: `"annotation_only"`

### Entrant model

* all entrants are initialised at the baseline rating

### Population model

* selectable:

  * OPEN (standard Elo)
  * CLOSED (Elo+ redistribution)

### Diagnostics

* diagnostics observer is always attached
* output artefacts are always produced

---

## Mapping from CLI to simulator

The CLI (`cli.py`) performs orchestration and maps command-line arguments into
the simulator inputs.

Key mappings:

* `--b`, `--q`, `--k-policy`, `--k-value`, `--k-config`
  → `EloParams`

* `--closed`
  → `SimulationMode`

* `--start`, `--end`, `--zip`
  → affect the raw history passed into the oracle

The CLI also fixes:

* entrant initialiser (`constant_initialiser`)
* oracle construction (`make_oracle(...)`)
* diagnostics attachment (`DiagnosticsCollector`)

---

## Role of the CLI

The CLI is a **thin orchestration layer** that:

* loads data
* constructs the oracle
* resolves parameters
* invokes the simulator
* prints a summary

It exists primarily for convenience and reproducibility.

The primary interface to the system is the simulator API itself.

---

## Notes on module boundaries (TBD)

The current module structure reflects the history of the experiment rather than
a fully clean separation of concerns.

Potential boundary issues:

* `Oracle.py` lives under `expt1` but represents a reusable preprocessing layer
* `diagnostics.py` mixes experiment-specific reporting with general observer logic
* `cli.py` combines orchestration with experiment definition

TBD:

* whether preprocessing and diagnostics should be promoted to shared
  infrastructure
* whether Expt1 should be reduced to a thin configuration layer over a more
  general simulation package

---

## Summary

Expt1 is best understood as:

> A specific configuration of a general Elo simulation engine, defined by a
> particular preprocessing pipeline, parameterisation, entrant model, and
> diagnostic layer.

The simulator itself is reusable; Expt1 fixes one particular way of using it.

```
