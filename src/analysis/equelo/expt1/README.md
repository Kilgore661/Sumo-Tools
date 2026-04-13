## Simulator technical specification

This specification covers the **simulation API** and the **effective run-time parameters exposed through the CLI and config layer**, with special emphasis on the latter.

Source files: `simulate.py`, `cli.py`, `params.py`, `initialisation.py`, `Oracle.py`, `diagnostics.py`.      

---

## 1. Public simulation API

### 1.1 Signature

```python
def simulate(
    history: History,
    params: EloParams,
    entrant_initialiser: EntrantInitialiser,
    mode: SimulationMode = SimulationMode.OPEN,
    observer: SimulationObserver | None = None,
) -> SimulationResult
```

Defined in `simulate.py`. 

---

## 2. Formal parameters

### 2.1 `history: History`

A preprocessed, already-selected historical dataset keyed by basho date.

#### Meaning

`history` is the full tournament stream to be simulated. The simulator assumes:

* data loading is already complete
* date-window selection is already complete
* historical cleansing/filtering is already complete

The simulator explicitly does **not** perform these steps itself. 

#### Required structure

For each `Date`, `history[date]` is a `BashoState` containing:

* `banzuke`: active rikishi and their `Chii`
* `summary`: day-indexed daily results / bouts

#### Role in the run

`history` determines:

* which basho are processed
* which rikishi are active in each basho
* which bouts are presented to the Elo update engine

---

### 2.2 `params: EloParams`

Resolved Elo parameter object.

Defined as:

```python
@dataclass(frozen=True)
class EloParams:
    b: float = INITIAL_ELO
    q: float = INITIAL_Q
    k: KFn | None = None
```

with `k` resolved to a callable if omitted. 

#### Fields

##### `b: float`

Baseline rating.

* Used as the conventional entrant baseline
* Also used as the diagnostics reference mean
* Not directly used in the per-bout Elo update formula itself

##### `q: float`

Logistic scale parameter in the expectation formula:

[
E_A = \frac{1}{1 + 10^{(R_B - R_A)/q}}
]

Implemented by `expect(ra, rb, q)`. 

##### `k: Callable[[int], float]`

K-factor function indexed by ordinal rank.
For a scored bout, the simulator computes:

* `ordinal_a = banzuke.rikchii[r1].ordinal()`
* `k = params.k(ordinal_a)` 

#### Role in the run

`params` determines:

* expectation sensitivity through `q`
* update magnitude through `k`
* entrant baseline convention through `b` when paired with the default entrant initialiser

---

### 2.3 `entrant_initialiser: EntrantInitialiser`

Type alias:

```python
EntrantInitialiser = Callable[Chii, float]
```

Defined in `initialisation.py`. 

#### Meaning

A function used when a rikishi appears in the current basho but does not yet have a rating in the working state.

#### Invocation contract

For each previously unseen active rikishi:

* input: the rikishi’s current `Chii`
* output: initial Elo rating as `float`

#### Role in the run

Determines the initial rating assigned to new entrants.

#### Default Expt1 policy

The CLI uses:

```python
constant_initialiser(params.b)
```

which ignores `Chii` and returns the baseline for every entrant.

---

### 2.4 `mode: SimulationMode = SimulationMode.OPEN`

Enum:

```python
class SimulationMode(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
```

Defined in `simulate.py`. 

#### Meaning

Controls basho-boundary handling of departures.

#### Semantics

##### `OPEN`

Departing rikishi are removed from the active universe with no redistribution. 

##### `CLOSED`

When a rikishi departs:

* compute the mean of the previously active set
* compute the retiree deviation from that mean
* redistribute uniformly over survivors
* remove retiree
  This preserves the active-universe mean across the basho boundary. 

#### Role in the run

Determines whether rating mass leaves with retirees or is reallocated among survivors.

---

### 2.5 `observer: SimulationObserver | None = None`

Optional observer protocol for diagnostics and logging. Methods include:

* `on_basho_start`
* `on_entry`
* `on_retirement`
* `on_day_start`
* `on_bout`
* `on_ignored_bout`
* `on_day_end`
* `on_basho_end` 

#### Meaning

Receives simulation events but does not define the rating state transition contract.

#### Role in the run

* optional diagnostics
* optional audit trail
* optional run logging

#### Expt1 default

CLI attaches `DiagnosticsCollector`.

---

## 3. Output

### 3.1 Return type

```python
@dataclass(frozen=True)
class SimulationResult:
    basho_start_ratings: BashoStartRatings = field(default_factory=dict)
    day_end_ratings: RatingsByDate = field(default_factory=dict)
```

Defined in `simulate.py`. 

---

### 3.2 `basho_start_ratings`

Type:

```python
dict[Date, dict[RikId, float]]
```

#### Meaning

For each basho date, this stores the snapshot taken:

* after departures are processed
* after entrants are initialised
* before the first scored bout of that basho 

---

### 3.3 `day_end_ratings`

Type:

```python
dict[Date, dict[Day, dict[RikId, float]]]
```

#### Meaning

For each basho and day, this stores the snapshot after all scored bouts for that day have been applied. 

---

### 3.4 Output exclusion boundary

`SimulationResult` contains **rating observations only**. It does not include:

* CSV diagnostics
* run logs
* retirement tables
* summary metrics

Those are produced only through the observer path.

---

## 4. Execution semantics

For each basho date in chronological order, `simulate(...)` does the following:

1. Load `basho_state = history[date]`
2. Extract current active rikishi from `banzuke`
3. Apply departure rule from previous basho to current basho
4. Initialise any active rikishi not yet in the rating map
5. Save basho-start snapshot
6. For each day in sorted order:

   * apply each scored bout
   * save day-end snapshot
7. Save basho-level day map
8. Advance `previous_active_rikishi` for the next basho 

---

## 5. Rating update rule

For each bout:

* `fusen` and `blank` are ignored and do not update ratings 
* otherwise:

  * compute expected score from `q`
  * compute `k` from ordinal rank
  * compute:
    [
    \Delta = K \cdot (A - E_A)
    ]
  * update:

    * `r1 += Δ`
    * `r2 -= Δ` 

This is zero-sum per scored bout, so rating mass is conserved up to floating-point precision.

---

## 6. Preconditions

The caller is responsible for satisfying these conditions before invoking `simulate(...)`:

### 6.1 History preparation

`history` must already be:

* loaded
* date-sliced
* cleansed to the desired observability policy

The simulator will not repair or filter raw history.

### 6.2 Parameter resolution

`params.k` must be valid for all ordinals encountered during the run. `EloParams` handles default resolution automatically if `k` is omitted. 

### 6.3 Entrant initialiser compatibility

`entrant_initialiser(chii)` must return a valid numeric rating for every active entrant rank that appears in the supplied history.

---

## 7. Invariants

### 7.1 Bout-level conservation

Each scored bout adds `Δ` to one competitor and subtracts `Δ` from the other. 

### 7.2 Active-universe semantics

Conservation and redistribution are defined over the active basho universe, not over all ratings ever seen in memory. 

### 7.3 Snapshot timing

* basho-start snapshots are pre-bout
* day-end snapshots are post-bout 

---

## 8. Postconditions

On successful completion:

* every processed basho has a `basho_start_ratings[date]`
* every processed basho has a `day_end_ratings[date]`
* rating state reflects all processed scored bouts in chronological order
* ignored bouts have left no rating effect 

If the supplied history is empty or yields no processable basho, the returned mappings may be empty. This is consistent with CLI behaviour, which prints “No ratings produced.” when appropriate. 

---

# 9. CLI/config-level parameters

This is the most important operational parameter surface, because in practice it determines the effective model run.

The CLI in `cli.py` is the orchestration layer that:

* loads raw data
* loads bios
* constructs the oracle
* resolves Elo parameters
* selects mode
* attaches diagnostics
* invokes `simulate(...)` 

## 9.1 Effective run pipeline

The run performed by the CLI is:

```python
raw_history = connect(args.start, args.end, use_zip=args.zip)
bios = load(BIOS_PATH)
oracle = make_oracle(raw_history, bios)
params = build_elo_params(...)
mode = SimulationMode.CLOSED if args.closed else SimulationMode.OPEN
diagnostics = DiagnosticsCollector(...)
results = simulate(
    history=oracle.history,
    params=params,
    entrant_initialiser=constant_initialiser(params.b),
    mode=mode,
    observer=diagnostics,
)
```

This means the **effective simulator configuration is not just the `simulate(...)` signature**. It is the combination of CLI arguments, config defaults, oracle behaviour, and fixed wiring choices.

---

## 9.2 Direct CLI parameters

### `--start`

Type: `int`
Default: `EPOCH`

Controls the lower year bound passed into `connect(...)`. This changes which raw historical basho enter the run. 

### `--end`

Type: `int`
Default: `datetime.datetime.now().year`

Controls the upper year bound passed into `connect(...)`. This changes which raw historical basho enter the run. 

### `--zip`

Type: boolean flag
Default: `False`

Forwarded as `use_zip=args.zip` to `connect(...)`. This is a data-source/loading parameter. It may affect the exact source representation used for the run. 

### `--closed`

Type: boolean flag
Default: `False`

If present, selects `SimulationMode.CLOSED`; otherwise the run uses `SimulationMode.OPEN`. This is the CLI control for basho-boundary population dynamics. 

### `--k-policy`

Type: enum
Choices: `constant`, `divisional`
Default: `constant`

Selects how the `k` function is constructed inside `build_elo_params(...)`.

### `--k-value`

Type: `float | None`
Default: `None`

Valid only with `--k-policy constant`. If omitted, the code falls back to `CONSTANT_K`. The CLI explicitly rejects using `--k-value` with divisional mode.

### `--k-config`

Type: `Path | None`
Default: `None`

Valid only with `--k-policy divisional`. Supplies the JSON config used by `load_divisional_k_fn(...)`. The CLI explicitly rejects using `--k-config` with constant mode.

### `--b`

Type: `float`
Default: `INITIAL_ELO`

Sets the baseline rating passed into `build_elo_params(...)`. In Expt1, this also determines the constant entrant initialisation level because the CLI uses `constant_initialiser(params.b)`.

### `--q`

Type: `float`
Default: `INITIAL_Q`

Sets the Elo logistic scale parameter passed into `build_elo_params(...)`.

---

## 9.3 Config-backed defaults with model effect

These are not necessarily passed on the command line, but they still determine run behaviour when CLI overrides are absent.

### `EPOCH`

Default lower year bound for `--start`. 

### `INITIAL_ELO`

Default baseline rating used for:

* `--b`
* `EloParams.b` default

### `INITIAL_Q`

Default logistic scale used for:

* `--q`
* `EloParams.q` default

### `CONSTANT_K`

Default scalar K in constant-K mode when no explicit `--k-value` is supplied.

### `DEFAULT_K_CONFIG_PATH`

Default JSON source for divisional-K mode when no explicit `--k-config` is supplied. 

### `BIOS_PATH`

Path to the bios JSON loaded before oracle construction. This affects the oracle input state assembled by the CLI. 

### `OUTPUT_ROOT`

Used by diagnostics to write:

* basho summary CSV
* retirements CSV
* run log 

This does not change `SimulationResult`, but it changes output artefact locations for a CLI run.

---

## 9.4 Fixed CLI-wired modelling choices

These are especially important because they are **effective run parameters even though they are not exposed as flags**.

### Oracle construction is mandatory and fixed

The CLI always calls:

```python
oracle = make_oracle(raw_history, bios)
```

with no explicit `collapse_mode`, so the default applies.

#### Consequences

The effective run always uses these preprocessing rules:

* skip pre-1958 data
* before 1989, keep only bouts with at least one sekitori
* from 1989 onward, keep only bouts whose participants are both on the banzuke
* collapse mode defaults to `"annotation_only"` 

This is a major model choice, not merely a data-cleaning implementation detail, because it determines what observations reach the simulator.

---

### Entrant initialisation is fixed to flat baseline in Expt1

The CLI always passes:

```python
entrant_initialiser=constant_initialiser(params.b)
```

So the effective entry model is:

* all unseen entrants start at exactly `b`
* rank-aware entrant modelling is not exposed in this CLI path

This is one of the most important implicit run parameters.

---

### Diagnostics observer is always attached

The CLI always constructs a `DiagnosticsCollector(...)` and passes it as the observer.

This does not affect the numerical rating path, but it does affect:

* produced artefacts
* logging side outputs
* audit summaries

---

## 9.5 K-policy configuration semantics

### Constant K mode

If `--k-policy constant`:

* `k` is `constant_k_fn(k_value)`
* if `k_value` is omitted, `CONSTANT_K` is used 

This means every scored bout uses the same K regardless of rank ordinal.

### Divisional K mode

If `--k-policy divisional`:

* JSON is loaded from `--k-config` or `DEFAULT_K_CONFIG_PATH`
* config format includes:

  * `"max"`
  * `"lims"` mapping bucket limits to K values
* ordinal is mapped to division bucket by:

  * `division_index = ordinal // 100000` 

This means K is rank-bucket dependent.

---

## 9.6 Effective parameter set for a CLI run

A CLI invocation effectively determines the simulator through the following parameter set:

### Explicit CLI surface

* start year
* end year
* data loading mode (`--zip`)
* basho-boundary population mode (`--closed` / open)
* K-policy
* K-value or K-config
* baseline `b`
* logistic scale `q`

### Config/default surface

* `EPOCH`
* `INITIAL_ELO`
* `INITIAL_Q`
* `CONSTANT_K`
* `DEFAULT_K_CONFIG_PATH`
* `BIOS_PATH`
* `OUTPUT_ROOT`

### Fixed but model-defining wiring

* oracle preprocessing is always applied
* oracle collapse mode defaults to `"annotation_only"`
* entrant initialisation is always `constant_initialiser(b)`
* diagnostics observer is always attached

---

## 9.7 Recommended interpretation

For documentation purposes, the simulator should be described at two layers:

### Core API layer

`simulate(history, params, entrant_initialiser, mode, observer)`

### Effective experiment/run layer

The actual Expt1 run is parameterised by:

[
(\text{start}, \text{end}, \text{zip}, \text{mode}, \text{K-policy}, \text{K-value/config}, b, q, \text{oracle rules}, \text{entrant rule})
]

That second layer is the one that really governs reproducible CLI runs.

---

## 10. Concise run contract

A complete Expt1 simulator run is defined by:

* the raw history interval selected by CLI
* the preprocessing/oracle transformation applied to that history
* the Elo parameterisation (`b`, `q`, `k`)
* the entrant initialisation rule
* the basho-boundary population mode
* optional diagnostic observation

The most important practical parameters are the CLI/config-level ones, because they determine the exact `history`, `params`, and `entrant_initialiser` that are ultimately passed into `simulate(...)`.

