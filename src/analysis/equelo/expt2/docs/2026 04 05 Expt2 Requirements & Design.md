## Expt2 — requirements

### Purpose

Estimate a self-consistent basho-start prior by rank, to reduce artefacts caused by flat initialisation, especially at the 1989 observability cliff. The target object is a mapping from rank to typical basho-start rating, used only when a rikishi has no prior observable rating.  

### Inputs

The solver takes:

* a `HistorySlice`, where `History` is a `Date -> BashoState` mapping and the slice is inclusive on years `<start> ... <end>`; default years are 1989 and 2026
* a scalar `BASE`, used to initialise the very first prior
* a convergence tolerance `EPSILON`
* a maximum iteration count `MAX_ITER`
* the choice of aggregation function
* the choice of normalisation function
* the usual Elo parameters and any simulator config needed by Expt1’s engine.  

### Core data

Use:

* `ChiiRatings = dict[Chii, float]`
* `RatingsResults` for the simulator’s output

with the understanding that `Chii` is canonical and deterministic in this project. The current Expt1 engine already returns a `RatingsResults` object containing ratings plus diagnostics. 

### Required functions

The design requires three functions:

* `simulate : HistorySlice × ChiiRatings -> RatingsResults`
* `aggregate : RatingsResults -> ChiiRatings`
* `normalise : ChiiRatings -> ChiiRatings`

`simulate` is the Expt1 forward pass, refactored so that unseen rikishi are initialised from `ChiiRatings` instead of always from `params.b`; current Expt1 hard-wires new entries to `params.b`. `aggregate` must use basho-start observations only. `normalise` must be a uniform additive shift only.  

### Invariant

For the closed formulation, rating mass is conserved on the active basho universe.

More concretely:

* each scored bout is zero-sum
* with closed-system departure handling, the mean on the active basho population remains constant at the anchor level up to floating-point noise

This is already the invariant Expt1 is built to check.  

### Convergence

Convergence is defined by the maximum absolute pointwise change between successive **normalised** maps:

[
\delta_t = \max_c |\mu_{t+1}(c) - \mu_t(c)|
]

Terminate when `delta_t < EPSILON`, or when `MAX_ITER` is reached. This matches the old solver’s criterion.  

### Diagnostics

Expt2 needs only solver-level diagnostics:

* iteration number
* current `delta`
* current values for a fixed probe set of ranks such as `Y1e`, `O1e`, `S1e`, `K1e`, `M1e`, `M5e`, `M10e`, `J1e`, `J5e`, `Ms1e`
* optionally iteration runtime

These should be written to disk as a CSV or log. The old solver already printed representative ordinals, average Elo, max delta, and runtime per iteration; Expt1 already writes simulation diagnostics to CSV, though its exact return-vs-log boundary can be left undecided for now.  

### Scope / non-claims

Expt2 does not model promotion or banzuke formation. Rank is used only as a proxy for expected strength at basho start when prior rating history is unavailable. 

---

## Expt2 — design

### 1. High-level idea

Let `μ` be the basho-start prior by `Chii`. Expt2 seeks a fixed point of the operator

[
T = \text{normalise} \circ \text{aggregate} \circ \text{simulate}
]

so that

[
\mu^* = T(\mu^*)
]

up to the additive shift removed by `normalise`. This is the self-consistency condition described in the project notes. 

### 2. Simulation layer

Reuse Expt1’s historical Elo engine as the basis for `simulate`. The required refactor is only at the initialisation boundary:

* current Expt1: unseen rikishi at basho start get `params.b`
* required Expt2: unseen rikishi at basho start get `prior[banzuke.rikchii[rid]]`

Everything else in the forward pass can remain as it is in spirit: iterate basho in date order, handle departures, process bouts day by day, and preserve closed-system conservation on the active universe. 

### 3. Aggregation layer

`aggregate` takes the simulator output and forms a new `Chii -> float` map by:

* extracting start-of-basho snapshots only
* grouping observations by `Chii`
* taking the arithmetic mean in each group

This choice is not arbitrary: Expt2 is specifically estimating a basho-start initialisation rule, not an in-basho or daily descriptive profile. 

### 4. Normalisation layer

`normalise` applies one uniform shift to all values so that the unweighted mean of the map equals `BASE`. It must not rescale or otherwise deform the profile. This is an anchoring convention, not part of Elo dynamics. 

### 5. Solver loop

Initialise with a flat prior:

[
\mu_0(c) = BASE \quad \text{for all } c
]

Then iterate:

```text
mu := initialise(BASE)

for t in 1..MAX_ITER:
    results := simulate(history_slice, mu)
    raw := aggregate(results)
    mu_next := normalise(raw)
    delta := max_abs_difference(mu_next, mu)
    record_diagnostics(t, delta, probe_values(mu_next))
    if delta < EPSILON:
        return mu_next
    mu := mu_next

return mu
```

This is the cleaned top-down version of the old solver’s loop: simulate, aggregate, normalise, compare, update. 

### 6. Variants

Implement two entry points.

**Variant A: whole-history fixed point**
Use the full slice from the start.

**Variant B: post-1989 calibration, then full-history refinement**
First solve on the post-1989 slice, then use that solution as the starting prior for a full-history run, optionally with further iteration.  

### 7. Outputs

The solver should write:

* final converged `ChiiRatings`
* per-iteration diagnostics log
* optionally a CSV version of the final prior for inspection and plotting

The simulator may also write its own run diagnostics, but that is an implementation detail of the `simulate` boundary and need not be fixed in the Expt2 design now. 

### 8. Questions the design is intended to answer

This design is meant to determine:

* whether the fixed-point iteration converges
* whether the resulting prior is stable
* whether whole-history and post-1989-calibrated solutions agree up to shift
* whether the 1989 cliff is reduced
* how sensitive the result is to normalisation and aggregation choices
* whether downstream ratings change in plausible ways. 
