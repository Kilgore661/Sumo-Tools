# Simulator API

## Overview

The core deliverable of Expt1 is a historical Elo simulation engine defined by
the function:

```
def simulate(
    history: History,
    params: EloParams,
    entrant_initialiser: EntrantInitialiser,
    mode: SimulationMode = SimulationMode.OPEN,
    observer: SimulationObserver | None = None,
) -> SimulationResult
````

This function performs a deterministic forward simulation of ratings over a
prepared sumo history.

The simulator itself is **data-agnostic** and **policy-agnostic**:

* it does not load or filter data
* it does not define preprocessing rules
* it does not define entrant initialisation
* it does not persist outputs

All such concerns are handled by the caller.

---

## Inputs

### `history: History`

A chronologically indexed mapping from `Date` to `BashoState`.

Each `BashoState` must contain:

* `banzuke`: the active rikishi and their `Chii`
* `summary`: day-indexed bout results

The simulator assumes that `history` is already:

* loaded
* filtered to the desired date range
* cleaned according to the desired observability policy

No validation or repair is performed internally.

---

### `params: EloParams`

Resolved Elo parameter bundle:

```
@dataclass(frozen=True)
class EloParams:
    b: float
    q: float
    k: Callable[[int], float]
```

* `b` — baseline rating (not used directly in updates)
* `q` — logistic scale parameter
* `k` — function mapping rank ordinal to K-factor

The simulator assumes that `k(ordinal)` is defined for all ordinals encountered.

---

### `entrant_initialiser: EntrantInitialiser`

```
Callable[[Chii], float]
```

Function used to initialise ratings for rikishi who are active in the current
basho but do not yet have a rating.

* input: `Chii` (rank information)
* output: initial rating

The simulator does not impose any structure on this function.

---

### `mode: SimulationMode`

```
class SimulationMode(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
```

Controls how departures are handled at basho boundaries.

* **OPEN**
  Departing rikishi are removed from the active population.

* **CLOSED**
  Departing rikishi are redistributed uniformly across survivors so that the
  active-population mean is preserved.

---

### `observer: SimulationObserver | None`

Optional callback interface for diagnostics and logging.

The observer may implement hooks including:

* `on_basho_start`
* `on_entry`
* `on_retirement`
* `on_day_start`
* `on_bout`
* `on_ignored_bout`
* `on_day_end`
* `on_basho_end`

The observer does not affect simulation state.

---

## Output

```
@dataclass(frozen=True)
class SimulationResult:
    basho_start_ratings: dict[Date, dict[RikId, float]]
    day_end_ratings: dict[Date, dict[Day, dict[RikId, float]]]
```

### `basho_start_ratings`

Snapshot taken for each basho:

* after departures are processed
* after entrants are initialised
* before the first scored bout

---

### `day_end_ratings`

Nested mapping of rating snapshots after each day's scored bouts.

---

### Excluded outputs

The result contains **ratings only**.

Diagnostics, logs, and CSV outputs are produced exclusively via the observer.

---

## Execution model

For each basho in chronological order:

1. Determine active rikishi from the banzuke
2. Apply departure rule relative to previous basho
3. Initialise any unseen rikishi
4. Record basho-start snapshot
5. For each day:

   * apply all scored bouts
   * record day-end snapshot
6. Advance to next basho

---

## Bout update rule

For each scored bout:

* ignore `fusen` and `blank`
* compute expected score:

```
E_A = 1 / (1 + 10 ** ((R_B - R_A) / q))
```

* compute:

```
delta = k * (actual - expected)
```

* update:

```
r1 += delta
r2 -= delta
```

---

## Conservation properties

### Within a bout

Rating mass is conserved (up to floating-point precision).

---

### Across basho boundaries

Depends on `mode`:

* **OPEN**
  Rating mass leaves with departing rikishi.

* **CLOSED**
  Departures are redistributed so that the active-population mean is preserved.

---

## Preconditions

The caller must ensure:

* `history` is internally consistent and fully prepared
* `params.k` is defined for all required ordinals
* `entrant_initialiser` returns valid ratings for all entrants
* every rikishi appearing in a scored bout has a rating at the time of the bout

---

## Determinism

The simulation is deterministic with respect to its inputs:

* no randomness is used
* no global mutable state is consulted
* results are fully determined by:

  * `history`
  * `params`
  * `entrant_initialiser`
  * `mode`

---

## Notes

* The simulator operates on the **active basho population**, not all historical
  participants in memory.
* Ratings are defined only up to an additive constant.
* The simulator is intended to be reused with different preprocessing and
  initialisation policies.
