# Output and Diagnostics (Expt1)

## Overview

Expt1 produces two kinds of output:

1. **In-memory rating data** returned by the simulator
2. **Diagnostic artefacts** written to disk via `DiagnosticsCollector`

The simulator itself returns only rating snapshots. All summary statistics,
checks, and logs are produced through the diagnostics layer.

---

## 1. Simulation output (in memory)

The `simulate(...)` function returns:

```python
SimulationResult
````

containing:

* `basho_start_ratings`
* `day_end_ratings`

### `basho_start_ratings`

Mapping:

```
Date → {RikId → rating}
```

Snapshot taken:

* after departures are processed
* after entrants are initialised
* before the first scored bout of the basho

---

### `day_end_ratings`

Mapping:

```
Date → Day → {RikId → rating}
```

Snapshot taken after all scored bouts for each day.

---

### Notes

* These structures contain the full rating trajectory
* No aggregation or interpretation is performed at this level

---

## 2. Diagnostics layer

Diagnostics are implemented in `diagnostics.py` via `DiagnosticsCollector`,
which is attached as a simulation observer.

The collector records events during the simulation and writes summary outputs.

---

## 3. Output files

All diagnostic outputs are written under:

````
files/output/Equelo/
``` id="m0n7w2"

File names include a suffix based on mode:

- `_open`
- `_closed`

---

### 3.1 `basho_summary_<mode>.csv`

One row per basho.

Columns:

- `date`  
- `n_rikishi` — number of active rikishi  
- `rating_mass` — sum of ratings  
- `mean_rating` — average rating  
- `mean_abs_bout_update` — average absolute update per scored bout  

#### Interpretation

- **Mean behaviour**
  - open mode: mean may drift
  - closed mode: mean ≈ baseline

- **Scale of updates**
  - `mean_abs_bout_update` provides a reference magnitude for Elo changes

---

### 3.2 `retirements_<mode>.csv`

One row per retirement (departure) event.

Columns:

- `date`  
- `rikid`  
- `rating` — rating at exit  
- `n` — number of survivors  
- `delta` — deviation from mean  
- `delta_per_rikishi` — redistribution applied  
- `abs_delta_per_rikishi` — absolute magnitude  

#### Interpretation

- **Open mode**
  - no redistribution (`delta_per_rikishi = 0`)

- **Closed mode (Elo+)**
  - redistribution applied uniformly across survivors

- **Key quantity**
  - compare `abs_delta_per_rikishi` to `mean_abs_bout_update`
  - if much smaller, redistribution has limited practical impact

---

### 3.3 `run_log_<mode>.txt`

Text summary of a simulation run.

Includes:

- parameter settings (`b`, `q`, K policy)
- conservation checks
- event counts
- redistribution magnitudes

Key fields:

- **max abs basho-end mean deviation from baseline**
  - should be near zero in closed mode

- **max abs rating-mass change across scored bout**
  - should be near zero (verifies zero-sum updates)

- **entry and retirement counts**

- **ignored bouts**
  - `fusen` and `blank`

- **max redistribution per rikishi**
  - reported separately for pre- and post-1989

---

## 4. What matters most

For understanding system behaviour, the key quantities are:

1. **Mean rating over time** (`basho_summary`)
2. **Redistribution magnitude** (`retirements`)
3. **Conservation checks** (`run_log`)

Together these establish:

- whether drift occurs (open system)
- whether Elo+ removes it (closed system)
- whether the correction is significant

---

## 5. What is not covered

These outputs do not directly provide:

- ranking comparisons
- trajectory comparisons between models
- predictive performance metrics

These require additional analysis of the in-memory rating data.

---

## 6. Notes on diagnostics (TBD)

The diagnostics layer is tied to Expt1 and may not represent a clean separation
of concerns.

Potential issues:

- coupling between simulation events and reporting format
- CSV schema is fixed rather than configurable
- diagnostics are always enabled in the CLI path

TBD:

- whether diagnostics should be a reusable infrastructure component
- whether output formats should be standardised or parameterised
````

---

# You now have a complete, clean set

* README (entry point)
* 01 — simulator API (core)
* 02 — system/run model (Expt1 wiring)
* 03 — Elo+ design (research note)
* 04 — output/diagnostics (interpretation)

