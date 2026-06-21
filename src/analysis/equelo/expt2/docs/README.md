## `solve()` technical specification

This specification describes the **fixed-point solver** in `analysis/expt2/solve.py`, in the same style as the simulator spec: signature, formal parameters, output, execution semantics, invariants, postconditions, and a dedicated section on CLI/config-level parameters.

Primary source files: `solve.py`, `types.py`, `aggregate.py`, `normalise.py`, `runner.py`, `output.py`, `diagnostics.py`.       

---

## 1. Public solver API

### 1.1 Signature

```python
def solve(
    history: History,
    params: EloParams,
    base: float,
    epsilon: float,
    max_iter: int,
    mode: SimulationMode,
    probes: ProbeSet,
    output_csv_path: Path,
    diagnostics: IterationDiagnosticsSink | None = None,
    include_ci_stats: bool = False,
) -> SolveResult
```

Defined in `solve.py`. 

---

## 2. Purpose

`solve(...)` estimates a **self-consistent basho-start prior by `Chii`**.

Operationally, it searches for a map

[
\mu : \text{Chii} \to \mathbb{R}
]

such that, when Expt1 is run using `mu[chii]` as the entrant initial rating for that `Chii`, the resulting **mean basho-start ratings by `Chii`** reproduce the same profile after recentering to the chosen baseline. The implementation describes this explicitly as fixed-point iteration.

---

## 3. Formal parameters

### 3.1 `history: History`

A preprocessed history to solve over.

#### Meaning

This is the exact historical domain on which the fixed point is estimated. `solve(...)` does not load or cleanse history itself; it assumes the caller has already supplied the desired history slice.

#### Role in the solve

`history` determines:

* the `Chii` domain being solved
* the entrant events exposed to the inner simulation
* the basho-start observations used to re-estimate `mu`

---

### 3.2 `params: EloParams`

Resolved Elo parameter object used by the inner Expt1 simulator.

#### Meaning

This is passed through to `simulate(...)` inside each iteration.

#### Role in the solve

`params` determines the dynamics of the inner simulation:

* expectation curve via `q`
* bout update magnitude via `k`
* effective baseline convention when paired with the entry prior

In Expt2, `params` is treated as fixed while `mu` is iteratively updated. 

---

### 3.3 `base: float`

Scalar baseline used for:

* initial flat prior construction
* post-aggregation normalisation

#### Meaning

The initial iterate is:

```python
mu = {chii: float(base) for chii in chiis}
```

and after each iteration the aggregated means are uniformly shifted so that their **unweighted mean equals `base`**.

#### Role in the solve

`base` fixes the additive gauge of the solution. Without this recentering step, the solver would not explicitly anchor the absolute level of the `Chii` profile.

---

### 3.4 `epsilon: float`

Convergence tolerance.

#### Meaning

The solver stops when:

[
\max_{\text{chii}} |\mu_{next}(\text{chii}) - \mu(\text{chii})| < \epsilon
]

This is implemented by `max_abs_difference(...)`, i.e. a sup-norm convergence criterion. 

#### Role in the solve

Controls the stopping condition and therefore the precision of the fixed-point estimate.

---

### 3.5 `max_iter: int`

Maximum number of fixed-point iterations.

#### Meaning

Upper bound on solver iterations. If convergence is not reached within this bound, the solver returns `converged=False`.

#### Role in the solve

Caps runtime and guarantees termination.

---

### 3.6 `mode: SimulationMode`

Population mode passed through to the inner Expt1 simulator.

#### Meaning

This is the same Expt1 mode:

* `OPEN`
* `CLOSED`

#### Role in the solve

Determines how retirements/departures are handled during every inner simulation pass. Since the fixed point is defined relative to the simulation dynamics, changing `mode` changes the solved `mu`. 

---

### 3.7 `probes: ProbeSet`

Diagnostic probe ranks.

Type alias:

```python
ProbeSet = list[Chii]
```

Defined in `types.py`. 

#### Meaning

A selected ordered list of `Chii` values whose solved ratings and counts are logged at every iteration when diagnostics are enabled.

#### Role in the solve

Used only for iteration diagnostics; does not affect the numerical update rule. Probe extraction is done via `probe_values(...)`.

---

### 3.8 `output_csv_path: Path`

Path for the final rating table.

#### Meaning

If the solver converges, the final solved `mu` is written to this path as a CSV with columns:

* `chii`
* `ordinal`
* `rating`

A companion stats CSV is also written using a derived filename.

#### Role in the solve

Determines where persisted outputs are written on successful convergence.

---

### 3.9 `diagnostics: IterationDiagnosticsSink | None = None`

Optional iteration logger.

Protocol:

```python
class IterationDiagnosticsSink(Protocol):
    def record(self, row: IterationDiagnosticsRow) -> None: ...
    def finalise(self) -> Path | None: ...
```

Defined in `types.py`. 

#### Meaning

Receives one row per iteration containing:

* iteration index
* current delta
* current normalisation shift
* iteration wall time
* probe values
* probe counts

#### Role in the solve

Purely observational. It does not alter the fixed-point update.

---

### 3.10 `include_ci_stats: bool = False`

Flag controlling whether final confidence-interval-related columns are added to the stats output.

#### Meaning

If true, the solver performs one final analysis pass after convergence to collect basho-start ratings by `Chii`, then writes CI-style summary columns based on those observations.

#### Role in the solve

Affects post-convergence reporting only, not convergence behaviour.

---

## 4. Output

### 4.1 Return type

```python
@dataclass(frozen=True)
class SolveResult:
    mu: ChiiRatings
    converged: bool
    iterations: int
    final_delta: float
    output_csv_path: Path | None
    stats_csv_path: Path | None
    diagnostics_path: Path | None
    modern_output_csv_path: Path | None = None
    modern_stats_csv_path: Path | None = None
    modern_diagnostics_path: Path | None = None
```

Defined in `types.py`. 

---

### 4.2 `mu: ChiiRatings`

Type alias:

```python
ChiiRatings = dict[Chii, float]
```

#### Meaning

The current or converged `Chii -> rating` map.

* On success: the converged fixed-point estimate
* On failure to converge: the last iterate reached before termination

---

### 4.3 `converged: bool`

Whether the solver terminated by satisfying `final_delta < epsilon`. 

---

### 4.4 `iterations: int`

Number of iterations executed.

* equals the convergence iteration on success
* equals `max_iter` on non-convergence 

---

### 4.5 `final_delta: float`

The final sup-norm difference between consecutive iterates. 

---

### 4.6 `output_csv_path: Path | None`

Path to the final ratings CSV if convergence succeeded; otherwise `None`.

---

### 4.7 `stats_csv_path: Path | None`

Path to the stats companion CSV if convergence succeeded; otherwise `None`.

---

### 4.8 `diagnostics_path: Path | None`

Path returned by `diagnostics.finalise()` if diagnostics were enabled and wrote output; otherwise `None`.

---

### 4.9 Modern-prefixed fields

These are unused by plain `solve(...)` itself and are populated by the combined variant wrapper, not by the core solver.

---

## 5. Execution semantics

For a given `history`, `solve(...)` performs the following loop:

1. Build the `Chii` domain from the history

2. Initialise a flat prior `mu` at `base` over that domain

3. Repeat for `iteration = 1..max_iter`:
   
   1. Run Expt1 simulation with entrant prior induced by current `mu`
   2. Aggregate basho-start ratings into mean rating by `Chii`
   3. Uniformly normalise those means so the unweighted mean equals `base`
   4. Compute `final_delta = ||mu_next - mu||_\infty`
   5. Emit diagnostics row if configured
   6. If `final_delta < epsilon`, write outputs and return success
   7. Otherwise set `mu = mu_next` and continue

4. If the loop exhausts `max_iter`, finalise diagnostics and return failure

This is the complete fixed-point contract implemented in `solve.py`.

---

## 6. Internal update operators

The solver is easiest to understand as an iteration on a composite operator:

[
\mu_{t+1} = N(A(S(\mu_t)))
]

where:

### 6.1 `S`: simulate with current prior

`simulate_with_prior(...)` runs Expt1 using:

```python
entrant_initialiser = make_entrant_initialiser(mu)
```

so each entrant with rank `chii` receives initial rating `mu[chii]`. 

### 6.2 `A`: aggregate basho-start outcomes

`aggregate(...)` computes the arithmetic mean basho-start rating by `Chii` over the cleaned banzuke domain. It uses:

* basho-start snapshots only
* canonical `Chii` from the cleaned history
* arithmetic mean by group 

### 6.3 `N`: normalise to baseline

`normalise(...)` applies a constant additive shift to all `Chii` ratings so the unweighted mean is exactly `base`. 

---

## 7. Intermediate data products

### 7.1 Initial prior

Constructed by:

```python
initialise(base, chiis)
```

which returns a flat map over all `Chii` seen in the supplied history. 

### 7.2 Aggregated means

Produced as:

```python
AggregateResult(
    mean_by_chii=...,
    count_by_chii=...
)
```

where `count_by_chii` counts basho-start observations per `Chii`.

### 7.3 Diagnostics rows

If diagnostics are enabled, each iteration records:

```python
IterationDiagnosticsRow(
    iteration,
    delta,
    shift,
    iter_seconds,
    probe_values,
    probe_counts,
)
```

Defined in `types.py`.

---

## 8. Preconditions

### 8.1 Prepared history

`history` must already be:

* loaded
* date-windowed as intended
* oracle-cleaned as intended

The solver does not call `connect(...)` or `make_oracle(...)` itself.

### 8.2 Compatible `Chii` domain

Every entrant `Chii` encountered during the inner simulation must be present in the current `mu` domain. In plain `solve(...)`, this is satisfied because the domain is built from the supplied history before iteration begins. 

### 8.3 Resolved simulation parameters

`params` must be valid for all ranks encountered during the run. 

### 8.4 Writable outputs

If convergence succeeds, `output_csv_path` and its sibling stats path must be writable. `write_final_ratings_csv(...)` and `write_final_ratings_stats_csv(...)` create parent directories as needed.

---

## 9. Invariants

### 9.1 Fixed `Chii` domain within one solve

The solved domain is:

```python
{chii for basho in history.values() for chii in basho.banzuke.rikchii.values()}
```

and the iterate `mu` remains defined on that domain throughout the run. 

### 9.2 Baseline-normalised iterates

After each application of `normalise(...)`, the unweighted mean of `mu_next.values()` equals `base` whenever the map is non-empty. 

### 9.3 Convergence metric

The stopping rule is always the sup norm between successive iterates. No other convergence criterion is used. 

### 9.4 Solver numerics are independent of diagnostics

Diagnostics observe the iteration state but do not modify `mu_next`, stopping logic, or output-writing decisions.

---

## 10. Postconditions

### 10.1 On convergence

If `final_delta < epsilon` at iteration `t`, then:

* `SolveResult.converged == True`
* `SolveResult.iterations == t`
* `SolveResult.mu == mu_next`
* final ratings CSV is written
* final stats CSV is written
* diagnostics are finalised if enabled
* optional CI columns are included if requested

### 10.2 On non-convergence

If no iterate satisfies the tolerance within `max_iter`, then:

* `SolveResult.converged == False`
* `SolveResult.iterations == max_iter`
* `SolveResult.mu` is the last iterate
* `output_csv_path == None`
* `stats_csv_path == None`
* diagnostics may still be finalised and returned 

---

## 11. Persisted outputs

### 11.1 Final ratings CSV

Written by `write_final_ratings_csv(...)` with columns:

* `chii`
* `ordinal`
* `rating`

Sorted by ordinal then string form. 

### 11.2 Stats CSV

Written by `write_final_ratings_stats_csv(...)` with at least:

* `chii`
* `ordinal`
* `rating`
* `observations`
* `distinct_rikishi`
* `strictly_less_than_preceding`
* `violation`

If CI stats are enabled, it also includes:

* `n_basho_start`
* `mean_basho_start`
* `stdev_basho_start`
* `se_basho_start`
* `ci95_lower`
* `ci95_upper` 

### 11.3 Diagnostics CSV/log

Produced by the concrete sink, typically `IterationDiagnosticsWriter`, which writes per-iteration rows and may also echo aligned text to console. 

---

# 12. CLI/config-level parameters

This is the most important operational layer for Expt2, because in practice `solve(...)` is almost never called in isolation. It is driven by the Expt2 CLI and runner, which determine the history slice, solver tolerance, iteration cap, mode, K-policy, collapse mode, and output locations. 

## 12.1 Effective CLI pipeline

A single Expt2 run follows this structure:

1. Parse CLI arguments
2. Validate and resolve K-policy arguments
3. Load raw history with `connect(...)`
4. Load bios JSON
5. Build oracle-cleaned history via `make_oracle(...)`
6. Build `EloParams`
7. Choose mode
8. Dispatch to one solver variant (`naive`, `modern`, or `combined`) 

For the naive and modern variants, this eventually reaches `solve(...)` directly. For the combined variant, it reaches `_solve_from_initial_mu(...)`, which has the same iterative contract but starts from a supplied initial iterate rather than a flat one.

---

## 12.2 Direct CLI parameters affecting `solve(...)`

### `--start`

Type: `int`
Default: `EPOCH`

Controls the lower bound passed to `connect(...)`, affecting the raw history that is later oracle-cleaned and then solved. 

### `--end`

Type: `int`
Default: current year at runtime

Controls the upper bound passed to `connect(...)`. 

### `--zip`

Type: boolean flag
Default: `False`

Passed as `use_zip=args.zip` to `connect(...)`. A data-loading parameter that affects the source representation of the history. 

### `--epsilon`

Type: `float`
Default: `1`

Mapped directly to `solve(..., epsilon=...)`. This is the fixed-point convergence tolerance.

### `--max-iter`

Type: `int`
Default: `10000000`

Mapped directly to `solve(..., max_iter=...)`. This is the solver iteration cap.

### `--open`

Type: boolean flag
Default: `False`

If present, selects `SimulationMode.OPEN`; otherwise Expt2 defaults to `CLOSED`. This is notable because Expt1’s CLI default was open, while Expt2 flips the default by using `--open` as an opt-in. 

### `--k-policy`

Type: enum
Choices: `constant`, `divisional`
Default: `constant`

Determines how `EloParams.k` is built before entering the solver. 

### `--k-value`

Type: `float | None`

Used only when `--k-policy constant`. If omitted, the runner resolves it to `CONSTANT_K`. 

### `--k-config`

Type: `Path | None`

Used only when `--k-policy divisional`. If omitted, the runner resolves it to `DEFAULT_K_CONFIG_PATH`. 

### `--collapse` / `--collapse-mode`

Type: enum
Choices:

* `annotation-only`
* `chii-bucket`

Default: `annotation-only`

Determines the `collapse_mode` passed into `make_oracle(...)`, which changes the canonicalised `Chii` domain seen by the solver. This is one of the most important Expt2 run parameters, because the object being solved is precisely the `Chii -> rating` map.

### `--variant`

Type: enum
Choices:

* `naive`
* `modern`
* `combined`

Default: `naive`

Controls which wrapper invokes `solve(...)` or its refinement analogue.

### `--modern-start-year`

Type: `int`
Default: `1989`

Used by the modern and combined variants to slice history before solving the modern stage.

### `--modern-end-year`

Type: `int`
Default: `2026`

Used by the modern and combined variants similarly.

---

## 12.3 Config/default parameters with solver effect

### `INITIAL_ELO`

Used as the default `base` for all variant wrappers:

* `solve_variant_naive`
* `solve_variant_modern`
* `solve_variant_combined` 

This means the baseline anchoring constant is config-backed unless explicitly changed in code.

### `CONSTANT_K`

Resolved as the default constant K when `--k-policy constant` and no explicit `--k-value` is supplied. 

### `DEFAULT_K_CONFIG_PATH`

Resolved as the default K-config path when `--k-policy divisional` and no explicit `--k-config` is supplied. 

### `OUTPUT_ROOT`

Used as the base directory for default final CSVs and diagnostics outputs.

---

## 12.4 Fixed run-time wiring choices

These are not CLI flags, but they strongly define the effective Expt2 solve.

### Oracle preprocessing is always applied before solving

The runner always does:

```python
oracle = make_oracle(
    raw_history,
    collapse_mode=oracle_collapse_mode_from_args(args),
)
```

So the solver never operates on raw history. It always operates on oracle-cleaned history, with collapse mode chosen from the CLI. 

### Base is fixed by wrapper defaults unless code changes it

The public wrappers all default `base=INITIAL_ELO`; the CLI does not expose a `--base` or `--b` argument for Expt2. So the baseline anchoring constant is a config/code choice, not a CLI knob in this package. 

### CI stats are enabled in public variant wrappers

Both `solve_variant_naive(...)` and `solve_variant_modern(...)` call `solve(..., include_ci_stats=True)`. The combined refinement path also enables CI stats for the full-history refinement stage. 

### Diagnostics are usually attached by the runner

The runner creates `IterationDiagnosticsWriter(...)` instances and passes them into the solve wrappers, making iteration-level traces part of the standard CLI run contract.

---

## 12.5 Variant-level meaning

### Naive variant

Calls `solve(...)` directly on the full oracle-cleaned history.

### Modern variant

Slices the history to `modern_start_year..modern_end_year`, then calls `solve(...)` on that restricted history. 

### Combined variant

1. Solve the modern slice first
2. Extend the resulting `mu` to the full history domain using `base` for missing `Chii`
3. Refine on the full history starting from that modern-informed initial iterate via `_solve_from_initial_mu(...)` 

This makes the combined variant a two-stage estimator rather than a direct call to plain `solve(...)`.

---

## 12.6 Effective parameter set for a reproducible Expt2 run

A reproducible Expt2 solve is determined by:

### Explicit CLI surface

* start year
* end year
* zip/data-loading mode
* epsilon
* max iterations
* open vs closed mode
* K-policy
* K-value or K-config
* collapse mode
* variant
* modern slice bounds for modern/combined runs 

### Config/default surface

* `INITIAL_ELO`
* `CONSTANT_K`
* `DEFAULT_K_CONFIG_PATH`
* `OUTPUT_ROOT`

### Fixed wiring

* oracle preprocessing always precedes solving
* public wrappers enable CI stats
* diagnostics writers are normally attached
* combined variant performs a staged modern-then-full refinement

---

## 13. Recommended interpretation

For documentation purposes, `solve(...)` should be described at two levels:

### Core solver layer

A fixed-point routine:

[
\mu_{t+1} = \text{normalise}(\text{aggregate}(\text{simulate_with_prior}(\mu_t)), \text{base})
]

with sup-norm stopping rule.

### Effective experiment/run layer

The actual Expt2 run is parameterised by:

[
(\text{history slice}, \text{oracle collapse mode}, \text{mode}, \text{K-policy}, \epsilon, \text{max_iter}, \text{variant}, \text{modern bounds}, \text{base})
]

In practice, that second layer is what governs reproducible results.

---

## 14. Concise run contract

`solve(...)` computes a `Chii -> rating` prior that is self-consistent with the basho-start ratings induced by running Expt1 under that same prior. It iterates:

* simulate,
* aggregate by `Chii`,
* renormalise to baseline,
* test convergence,

and on success writes final rating tables and stats. The most important practical parameters come from the Expt2 CLI/config layer, because they determine the cleaned history, collapse regime, population mode, K-policy, stopping rule, and variant strategy that define the solved fixed point.
