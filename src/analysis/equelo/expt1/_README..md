# Expt1 — Historical Sumo Elo Simulator

## Overview

Expt1 is a **historical Elo simulation over professional sumo**, producing rating trajectories for rikishi across basho and days.

The simulator operates on a prepared history and supports two population models:

* **Open system** (standard Elo): departing rikishi leave the system
* **Closed system (Elo+)**: departures are redistributed to preserve the active-population mean

The result is a deterministic rating time series together with diagnostics that verify conservation properties and entry/exit effects.

---

## Model outline

* Ratings evolve via **pairwise Elo updates** applied to historical bouts
* Simulation proceeds **basho-by-basho, day-by-day**
* The active population is defined by each basho’s **banzuke**
* At basho boundaries:

  * new rikishi are initialised at a baseline rating
  * departing rikishi are either removed (open) or redistributed (closed)

Historical data is preprocessed before simulation to enforce a consistent observability policy.

---

## Running the simulation

Run via the package entry point:

```
python -m src.analysis.equelo.expt1
```

Example (closed-system run over full history):

```bash
python -m src.analysis.equelo.expt1 --closed
```

---

## Options

* `--start <int>`
  First year of the historical slice to simulate.
  Default: project epoch (`EPOCH`)

* `--end <int>`
  Final year of the historical slice to simulate.
  Default: current year

* `--zip`
  Load input data from a local archive instead of the default source.

* `--closed`
  Use closed-system (Elo+) semantics.
  Departures are redistributed so that the active-population mean is preserved at basho boundaries.

---

### K-factor configuration

Exactly one K-policy is selected via `--k-policy`.
Each policy enables a different set of parameters.

#### `--k-policy constant` (default)

Use a single constant K for all bouts.

* `--k-value <float>`
  Constant K value.
  If omitted, the default (`CONSTANT_K`) is used.

* `--k-config`
  Invalid with this policy.

---

#### `--k-policy divisional`

Use rank-dependent K values loaded from a JSON configuration.

* `--k-config <path>`
  Path to the configuration file.
  If omitted, the default config path is used.

* `--k-value`
  Invalid with this policy.

---

### Elo parameters

* `--b <float>`
  Baseline rating.
  Also used as the entrant initialisation level in Expt1.
  Default: `INITIAL_ELO`

* `--q <float>`
  Elo logistic scale parameter.
  Default: `INITIAL_Q`

---

## Outputs

Outputs are written to:

```
files/output/Equelo/
```

Each run produces:

* `basho_summary_<mode>.csv`
  Per-basho aggregates (population size, rating mass, mean rating, update scale)

* `retirements_<mode>.csv`
  One row per departure event, including any redistribution applied

* `run_log_<mode>.txt`
  Summary diagnostics (conservation checks, counts, parameter settings)

The simulator also returns in-memory rating snapshots:

* ratings at basho start
* ratings at end of each day

---

## Interpreting results (quick guide)

* **Open mode**
  Mean rating may drift over time

* **Closed mode (Elo+)**
  Mean rating remains approximately constant

* **Diagnostics**
  Verify zero-sum updates and quantify entry/exit effects

Ratings should be interpreted **relatively**, not as absolute measures.

---

## Project structure

* `simulate.py` — core simulation engine
* `Oracle.py` — historical preprocessing (tells you who retires when)
* `params.py` — Elo parameter definitions
* `initialisation.py` — entrant initialisation
* `diagnostics.py` — diagnostics and outputs
* `cli.py` — command-line entry point
