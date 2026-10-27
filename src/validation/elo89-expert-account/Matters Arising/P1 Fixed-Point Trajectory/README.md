# Proposal: P1 Fixed-Point Trajectory Recorder

## Status

Implemented under `src.validation.p1_trajectory` and smoke-tested on synthetic
History only. No full-history trajectory has yet been started and no
checkpoint has been selected for predictive evaluation.

This matter arose while testing a lower fixed-point stopping tolerance for
P1-WL. Reducing epsilon from 10 to 3 did not improve the resulting prior. It
allowed the iteration to continue from 18 passes to roughly 300, during which
sparse literal-chii cells acquired extreme values and retrospective predictive
performance deteriorated.

That result exposed a question which is independent of missing-kimarite bout
eligibility:

> What sequence of complete chii-rating maps does the P1 fixed-point procedure
> produce as the number of iterations increases?

The proposed program records that sequence at regular checkpoints. It does
not choose an epsilon, declare convergence, or decide which checkpoint should
be used in production.

## Why this is a separate Matter Arising

The existing canonical producer answers a bounded operational question: run
until the maximum change is below a supplied epsilon, or stop at a supplied
maximum iteration count. The proposed program answers a diagnostic question:
hold the inputs and update rule fixed, make iteration count the independent
variable, and inspect the maps produced along the path.

Kimarite work prompted the question because it produced parallel P1 and P1-WL
fits. The question is nevertheless intrinsic to the P1 solver. It exists
whether the bout selector includes or excludes represented W/L results whose
kimarite is missing. The recorder must therefore accept bout eligibility as
an explicit input rather than belong to `src.validation.kimarite`.

## Proposed code boundary

The implementation should be divided as follows:

```text
src/analysis/equelo_bkp1/solve.py
    canonical shared fixed-point iteration mechanics

src/validation/p1_trajectory/
    __init__.py
    __main__.py
    runner.py
```

The validation runner must reuse the canonical solver's replay, aggregation
and support-proportional recentering operations. It must not maintain a copied
or approximately equivalent version of the algorithm. If necessary,
`equelo_bkp1.solve` should expose a pure one-iteration function and a small
state/result type which both the bounded solver and trajectory recorder use.

The existing bounded `solve(...)` API and canonical production command must
retain their current behaviour. Adding the recorder must not silently alter a
production P1 fit.

## Required behaviour

### Open-ended iteration

The runner has no epsilon stopping rule and no maximum iteration count. It
continues until the Python process is terminated, normally by the user
pressing Ctrl-C. The program does not need to read or handle key presses.

Iteration count is the independent variable. After every completed pass the
runner has:

- the complete current literal-chii prior map;
- support for every chii;
- the maximum absolute change from the preceding map;
- the chii at which that maximum occurred;
- the support of that chii;
- recentering diagnostics; and
- cumulative elapsed time.

The current maximum change is the effective epsilon reached at that iteration.
The program must report it as a measurement, not interpret it as proof of
convergence or model quality.

### One eligibility policy per run

Each process records one trajectory selected explicitly as either:

- `p1`: the historical decision-field eligibility rule; or
- `p1-wl`: positive represented binary W/L eligibility.

Running one policy at a time keeps iteration number, runtime and checkpoint
identity unambiguous. A comparison may run the command twice against the same
frozen inputs. The eligibility choice must appear in every manifest and
console heading.

### Checkpoints

At every 100th completed iteration, the runner writes a durable checkpoint as
if that map had been selected as the final fitted artifact, without claiming
that it converged:

```text
output/<run-id>/
    manifest.json
    iterations.csv
    checkpoints/
        iteration-000100/
            manifest.json
            prior.csv
        iteration-000200/
            manifest.json
            prior.csv
        ...
```

Every checkpoint `prior.csv` must contain at least:

```text
chii,ordinal,support,rating
```

where `ordinal` is the integer returned by `Chii.ordinal()`. Rows should be
ordered by that ordinal, not by the display string.

The checkpoint manifest must record:

- iteration number;
- current maximum prior change;
- maximum-change chii and its support;
- the ten-iteration gradient when available;
- elapsed time;
- eligibility rule;
- complete source and parameter provenance; and
- the SHA-256 of the checkpoint prior.

The root `iterations.csv` is the append-only trajectory ledger. It must record
and flush every completed iteration immediately so that ordinary process
termination does not lose completed results and later analysis is not limited
to the 100-iteration checkpoint interval. Opening, appending and closing the
file for each row is acceptable; keeping it open requires an explicit flush
after every row. A checkpoint manifest may refer to that ledger rather than
duplicate it.

Checkpoint publication must be atomic at directory level: an interruption
must not leave a directory which appears to be a complete checkpoint. A
temporary checkpoint may be completed and then renamed into place.

The checkpoint interval should default to 100. It may be exposed as a
diagnostic command option for focused tests, but every production evidence run
must record the selected value and should use 100 unless a separate purpose is
declared.

### Console output

The console should print one compact tabular heading followed by progress
rows. A progress row should be printed after iteration 1 and then every 10
iterations by default. Checkpoint rows should be visibly marked.

The minimum columns are:

```text
iteration  max-change  chii  support  gradient-10  elapsed  checkpoint
```

For example:

```text
iteration  max-change  chii   support  gradient-10  elapsed   checkpoint
        1    711.5806  Y1e        221            -  00:00:02
       10     18.4217  Jk72e        3      -69.3159  00:00:21
      100      6.8421  Jk65e        9       -0.0513  00:03:31  saved
      200      4.2376  Jk65e        9       -0.0218  00:07:05  saved
```

`max-change` is the current effective epsilon: if the bounded producer had
used this iteration as its ceiling, this is the final maximum update it would
have reported.

The ten-iteration gradient at iteration (t) is:

\[
g_{10}(t)=\frac{\Delta_t-\Delta_{t-10}}{10},
\]

where (\Delta_t) is the maximum absolute prior change at iteration (t). It is
measured in rating points per iteration. A negative value means the maximum
update has declined over that interval; zero means it has stalled; a positive
value means it has increased. The value is unavailable before iteration 11.

This is a descriptive local slope. The program must not extrapolate it into a
claimed number of iterations remaining, because the convergence path need not
continue linearly.

### Process termination

Ctrl-C relies on Python's ordinary process-interruption behaviour. The runner
must not implement a keyboard listener, catch Ctrl-C in order to write a final
summary, create an interruption record, or promote the current map. It has no
special shutdown protocol.

Durability instead comes from writing output as soon as it becomes available:

- every fully completed iteration has already been appended and flushed to
  `iterations.csv`;
- every fully completed 100-iteration checkpoint has already been published
  atomically; and
- a map which has not reached its checkpoint boundary has not been promised as
  a durable rating artifact.

If termination occurs while an iteration is being calculated, that incomplete
iteration is simply absent from the ledger. If it occurs while a checkpoint is
being assembled, only the temporary checkpoint may be incomplete; because
publication uses an atomic rename, it cannot appear to be a completed
checkpoint. A later run or ordinary housekeeping may remove an abandoned
temporary directory.

### Possible later resume support

Resume is not part of the initial recorder. A later extension may accept a
`--resume` path identifying an existing trajectory root. Before continuing,
it would need to verify the checkpoint prior hash and exact agreement of all
model inputs and parameters, refusing to resume if the History, K
configuration, eligibility rule, base, q, preprocessing contract or
checkpoint interval differs.

Such an extension should begin with a selected checkpoint map and its
iteration number. The root ledger would need to make the session boundary
visible while preserving one continuous iteration sequence. These are design
requirements for a future extension, not behaviour claimed by the current
module.

## Proposed command

The intended interface is:

```powershell
py -m src.validation.p1_trajectory `
  --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip" `
  --start 1989-01 `
  --end 2026-09 `
  --eligibility p1-wl `
  --output ".\src\validation\elo89-expert-account\Matters Arising\P1 Fixed-Point Trajectory\output\p1-wl-trajectory-<date-time>"
```

There is deliberately no `--epsilon` and no `--max-iterations` option.
Diagnostic `--report-every` and `--checkpoint-every` options are provided,
with defaults of 10 and 100 respectively.

The exact CLI may be refined during implementation, but it must preserve the
absence of an iteration ceiling and convergence-triggered exit.

## Provenance

The root manifest must bind the trajectory to:

- History source path and SHA-256;
- selected-History deterministic fingerprint;
- selected start and end basho;
- Oracle preprocessing mode;
- eligibility rule and exact eligibility counts;
- K configuration path and SHA-256;
- q and base;
- support-proportional recentering rule;
- initial-map rule;
- report and checkpoint intervals;
- implementation/schema version;
- start time, resume-session boundaries and elapsed time recorded so far.

This Matter Arising belongs to the Elo-89 epoch. The default evidence interval
begins at `1989-01` even if its source archive contains earlier history.

## Explicit non-goals

The trajectory recorder does not:

- select an epsilon or recommended iteration count;
- stop because the maximum change crosses any threshold;
- claim mathematical convergence or uniqueness;
- assess monotonicity, plausibility or predictive value;
- smooth, clip, pair or otherwise repair checkpoint ratings;
- run Elo-89 from a checkpoint;
- compare P1 with P1-WL in the same process;
- promote a checkpoint to canonical P1; or
- modify the ordinary bounded P1 production contract.

Predictive evaluation of P1-WL at epsilon 0.03, iteration 500, or any other
selected checkpoint is a separate experiment. It should consume the frozen
checkpoint artifact without causing the trajectory runner to acquire model-
selection responsibilities.

## Tests required before a full run

Focused tests should establish that:

1. the shared single-iteration operation gives exactly the same successive
   maps and diagnostics as the current bounded solver;
2. a checkpoint at synthetic iteration (n) equals the bounded solver's map
   after exactly (n) iterations when early stopping is disabled for the test;
3. `prior.csv` ordinals are exact `Chii.ordinal()` values and rows are in
   ordinal order;
4. the ten-iteration gradient uses the declared formula;
5. console reporting does not affect iteration state;
6. checkpoint creation is atomic and refuses overwrite;
7. every completed ledger row is flushed before the next iteration begins;
8. neither eligibility mode silently changes the other's selected bout
    domain.

Only synthetic and short-history smoke tests should be run during
implementation. An open-ended full-history trajectory begins only when the
user explicitly starts the command and remains under the user's Ctrl-C
control.

## Expected evidence and later questions

The first full run should establish a reproducible relationship between
iteration number and the complete rating map. Later analysis may then ask:

- whether maximum change decreases monotonically or enters plateaus;
- which chii controls the maximum at different stages;
- whether sparse cells drift while well-supported landmarks stabilise;
- how map range, chii-order reversals and division-boundary discontinuities
  evolve;
- whether P1 and P1-WL trajectories differ mainly in level, shape or rate;
  and
- which checkpoints, if any, merit separate predictive evaluation.

Those are consumers of the recorded trajectory. They must not be allowed to
change what the recorder measures.
