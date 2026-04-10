## `simulate`

Run a single forward Elo simulation over a prepared sumo history slice.

### Signature

```
def simulate(
    history: History,
    params: EloParams,
    entrant_initialiser: EntrantInitialiser,
    mode: SimulationMode = SimulationMode.OPEN,
    observer: SimulationObserver | None = None,
) -> SimulationResult:
```

Simulates ratings basho-by-basho and day-by-day over an already prepared `History`. The function does not load data, filter dates, or clean raw records; it assumes the caller has already supplied the exact history to process. 

---

## Purpose

`simulate` is the core Elo engine for the experiment. It:

* maintains a mutable map of current ratings
* removes departed rikishi at basho boundaries
* initialises previously unseen rikishi
* applies Elo updates for each scored bout
* records basho-start and day-end rating snapshots
* optionally emits diagnostics through an observer. 

---

## Parameters

### `history: History`

Chronologically indexed basho history to simulate.

Requirements:

* must already be the exact slice the caller wants to process
* each basho must contain a `banzuke` and a `summary`
* iteration is performed in sorted date order. 

### `params: EloParams`

Resolved Elo parameter bundle.

Contains:

* `b`: baseline rating
* `q`: logistic scale parameter used in the expectation formula
* `k`: callable returning the K-factor from rank ordinal. 

### `entrant_initialiser: EntrantInitialiser`

Callable used to assign an initial rating to any rikishi active in the current basho who does not already have a stored rating.

This is applied only at basho start, after departures have been handled and before the first scored bout of the basho. 

### `mode: SimulationMode = SimulationMode.OPEN`

Controls basho-boundary departure semantics.

Supported values:

* `SimulationMode.OPEN`
* `SimulationMode.CLOSED` 

Semantics:

* **OPEN**: departed rikishi are removed with no redistribution
* **CLOSED**: a departed rikishi’s rating offset from the prior active-set mean is redistributed uniformly across active survivors, preserving the active-universe mean at basho boundaries. 

### `observer: SimulationObserver | None = None`

Optional callback object for diagnostics/logging.

If provided, observer hooks are called at basho start/end, entry, retirement, day start/end, scored bout, and ignored bout events. The observer does not affect the simulation result contract. 

---

## Return value

Returns a `SimulationResult`:

```
@dataclass(frozen=True)
class SimulationResult:
    basho_start_ratings: BashoStartRatings
    day_end_ratings: RatingsByDate
```

### `basho_start_ratings`

Per-basho rating snapshot taken:

* after departures are processed
* after new entrants are initialised
* before the first scored bout of the basho. 

### `day_end_ratings`

Nested mapping of end-of-day rating snapshots after each day’s scored bouts. 

---

## Simulation algorithm

For each basho in ascending date order, `simulate` performs:

1. Read current basho state, banzuke, and results summary.
2. Determine the current active rikishi from the banzuke.
3. Notify `observer.on_basho_start(...)` if an observer is present.
4. Handle departures relative to the previous basho.
5. Initialise any active rikishi not already present in `current_ratings`.
6. Save the basho-start snapshot.
7. For each day in ascending day order:

   * copy current ratings
   * notify `observer.on_day_start(...)`
   * process each bout
   * notify `observer.on_day_end(...)`
   * save the day-end snapshot
8. Notify `observer.on_basho_end(...)`
9. Set the current active set as the previous active set for the next basho. 

---

## Bout update rule

For each scored bout:

* `fusen` and `blank` decisions are ignored for rating purposes
* expected score is computed by:

```python
1 / (1 + 10 ** ((rb - ra) / q))
```

* actual score for rikishi 1 is:

  * `1.0` if outcome is win
  * `0.0` otherwise
* `k` is selected from `params.k(chii.ordinal())`
* update is:

```python
delta = k * (actual_a - expected_a)
```

* rikishi 1 gains `delta`
* rikishi 2 loses `delta`. 

---

## Conservation properties

### Within a scored bout

Rating mass is conserved up to floating-point precision, because one rikishi gains exactly what the other loses. 

### Across basho boundaries

Depends on `mode`:

* **OPEN**: no cross-basho conservation; departures remove rating mass from the active universe
* **CLOSED**: departures are redistributed across survivors, preserving the active-universe mean at basho boundaries. 

---

## Scope and non-goals

`simulate` does **not**:

* load raw historical data
* filter the date range
* clean or validate raw records
* define preprocessing rules
* define the entrant initialisation policy itself
* persist diagnostics itself. 

Those concerns are expected to be handled by the caller or upstream pipeline.

---

## Preconditions

The caller should ensure that:

* `history` is already cleaned/prepared as intended
* `params` is fully resolved
* `entrant_initialiser` matches the simulator’s expected callable shape
* each rikishi appearing in scored bouts has a rating by the time the bout is processed
* the supplied history and banzuke structure are internally consistent enough for direct lookup during simulation. 

---

## Determinism

`simulate` is deterministic with respect to its inputs:

* no randomness is used
* no global mutable configuration is consulted inside the simulation logic
* results are fully determined by `history`, `params`, `entrant_initialiser`, `mode`, and any non-mutating observer behaviour. 

---

## Example

```
results = simulate(
    history=oracle.history,
    params=params,
    entrant_initialiser=constant_initialiser(params.b),
    mode=SimulationMode.OPEN,
    observer=diagnostics,
)
```

In the provided CLI path, the simulator is instantiated with a constant entrant initialiser, so any previously unseen rikishi receives the baseline rating `b` on entry.  
