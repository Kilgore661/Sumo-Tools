# Elo89a Viability Experiment Proposal

## Status

Implemented proposal for an isolated fixed-point experiment assessing the
viability of a candidate rating model named **Elo89a**, where the suffix `a`
denotes absence.

This document specifies an experiment. It does not approve a production change
to Elo-89, alter the canonical P1 prior, or claim that Elo89a improves the
meaning or predictive quality of the rating.

## Purpose

Elo89a is Elo-89 with the non-appearance policy specified below. The experiment
asks one principal question about its viability:

> If each non-appearance costs the rikishi half of the applicable divisional
> `k`, and Elo-89's post-basho normalisation restores the population mean, does
> the chii-prior solver converge and, if so, what prior does it converge to?

Failure to converge is a hard stop for Elo89a. If the solver converges, the
resulting prior will be inspected by a human for weird or surprising values.
The code is not responsible for deciding whether a converged prior is
recognisable or acceptable.

The experiment includes an otherwise identical no-penalty control. This is one
experiment with two arms, not two independent experiments. The control is
necessary because feeding whole-population normalisation back through a
fixed-point solver may itself affect convergence or produce surprising priors.
The penalty arm is the Elo89a candidate. The canonical P1 prior is an external
reference, not a third experimental arm.

## Terminology

This proposal uses **non-appearance** as the umbrella term for two distinct
recorded events:

- **fusen-pai** (`FP`): the rikishi was named on the torikumi but did not
  appear; and
- **absence** (`A`): the rikishi was omitted from the torikumi and the final
  `W-L-A` record reports an absence.

The word *absence* has that restricted meaning in this document. Other project
documents sometimes use it for the wider category.

The `a` in the model name Elo89a is the mnemonic “absence” in the broader,
motivating sense. It does not collapse the formal distinction between FP and
absence used by this proposal.

The rikishi receiving fusen-sho (`FS`) is not treated as having demonstrated
winning skill and receives no rating credit.

## Candidate policy

For every non-appearance by rikishi `i`, deduct

\[
\lambda_i = \frac{k_i}{2},
\]

where `k_i` is the divisional `k` applicable to the rikishi's chii in that
basho. The experiment must use the same `k` configuration and the same missing-
chii `k` rule as the ordinary Elo replay. It must not introduce a separate
penalty scale.

Multiple non-appearances in one basho produce multiple deductions. If rikishi
`i` has `n_i` non-appearances, the total deduction before normalisation is

\[
D_i = -n_i\frac{k_i}{2}.
\]

No part of this deduction is credited directly to an FS rikishi or to a
synthetic opponent.

## Event evidence

The experiment consumes two kinds of evidence:

1. Explicit FP outcomes in `History` supply fusen-pai events.
2. Published final `W-L-A` records supply the number of absences.

An FP is counted once as a non-appearance. Although it contributes to `L` in a
published final record, it does not contribute to `A`, so the two sources do
not double-count it.

Only explicitly recorded events are penalised. The experiment must not infer
additional absences from an expected number of appearances, daily dashes,
short final records, retirement timing, or empty sub-sekitori scheduling
windows.

The final absence count is sufficient because every penalty is applied at
basho end. The experiment does not need to know the day or scheduling window
of an absence. The window inference developed in `src.analysis.absences` is
therefore relevant background evidence but is not an input to this experiment.

The selected interval must have complete `History` and published final-record
coverage. Missing or contradictory source evidence is a boundary failure. The
experiment must stop rather than guess, fill gaps, or silently omit an affected
rikishi-basho.

## Replay contract

Both experimental arms use the same replay except for the penalty deduction.
For each basho, replay performs these operations in order:

1. Establish the active population using the Elo-89 population rule.
2. Initialise entrants from the current chii-prior map.
3. Normalise the active population to the fixed target mean at basho start.
4. Replay every ordinarily rated contested bout in chronological order.
5. In the Elo89a arm only, deduct `k / 2` for each FP and each recorded
   absence.
6. Normalise the active population to the fixed target mean at basho end.
7. Retain the normalised basho-end ratings for the next basho.

Ordinary bout eligibility must be the production Elo-89 rule. In particular:

- a genuine W/L result remains rateable when its kimarite or decision text is
  blank;
- FS/FP is not rated as a contested bout;
- FP is handled only by the penalty deduction; and
- FS receives no update.

If the Elo89a arm deducts total mass `L` from an active population of size
`N`, the end normalisation includes compensation of `L/N` per active rikishi,
along with any correction already required by the ordinary replay. This is the
intended transfer mechanism; there is no additional compensation step.

## Fixed-point experiment

The control and Elo89a arms are solved independently.

Each arm begins with the same constant rating for every observed chii. One
solver iteration is:

```text
current chii-prior map
  -> replay the complete interval
  -> aggregate basho-start ratings by chii
  -> apply the canonical support-proportional map recentering
  -> next chii-prior map
```

Iteration continues until the canonical convergence condition is met or the
canonical maximum iteration count is reached. The experiment should initially
use the current P1 solver constants, including its base rating, convergence
tolerance and iteration limit. Any departure from those values is a new
experiment and must be recorded in the manifest.

There is no separate single-shot mode. Iteration 1 is an ordinary part of each
solver run. Its prior map and diagnostics must be retained so that they are
available if a run does not converge or its eventual prior is surprising.

The two arms are:

- **control**: the specified normalised replay with no non-appearance
  deductions; and
- **Elo89a**: the same replay with the basho-end deductions specified above.

The production canonical P1 prior must be copied into the comparison output as
a fixed reference. It is not regenerated and does not participate in either
solver.

## Required observations

The replay must record, for each basho and arm:

- active-population size;
- FP count and absence count, separately;
- penalised-rikishi count;
- total deducted rating mass;
- raw and normalised start means;
- raw end mean;
- end-normalisation adjustment per active rikishi; and
- normalised end mean.

The solver must record, for each iteration and arm:

- iteration number;
- maximum absolute prior change;
- the chii at which that change occurs;
- the observation support for that chii;
- the map-recentering adjustment; and
- the complete resulting chii-prior map.

The final comparison must present:

- whether each arm converged;
- iteration count and final maximum change;
- the control, Elo89a and canonical P1 rating for every chii;
- Elo89a-minus-control and Elo89a-minus-canonical differences;
- minimum and maximum prior values for each map; and
- a concise table of familiar chii landmarks across the three maps.

These are observations, not automated quality judgements. The output may make
large differences and extreme values easy to see, but it must not label a
prior acceptable, recognisable, weird or surprising.

## Interpretation

The experiment has three possible broad outcomes:

1. **Elo89a does not converge.** The candidate model fails this experiment.
   Iteration history, especially the first iteration, may then be inspected
   diagnostically.
2. **Elo89a converges to a weird or surprising prior.** The numerical fixed
   point exists, but the result raises a modelling issue for human
   investigation. The control distinguishes penalty effects from effects of
   the normalised solver itself.
3. **Elo89a converges to an unsurprising prior.** The experiment has succeeded.
   This establishes numerical viability only; it does not by itself justify
   adopting Elo89a.

No numerical definition of *weird* or *surprising* is required. Inspection by
the Mk 1 human eyeball is the assessment method.

## Reproducibility and outputs

One run must write a self-contained output directory containing at least:

- a manifest with the history interval, input paths and hashes, model
  constants, `k` configuration, convergence settings and code variant names;
- the per-basho replay ledger for both arms;
- per-iteration convergence diagnostics;
- per-iteration chii-prior maps;
- the final three-way prior comparison; and
- a short factual findings document reporting convergence and directing the
  reader to the comparison tables.

The command must return a non-zero exit status when either experimental arm
does not converge or an input contract fails. A surprising but converged map
is not a program failure and must not change the exit status.

## Ownership and implementation boundary

The experiment belongs in `src.analysis.elo_penalties`. It may reuse:

- production Elo-89 bout selection and population semantics;
- the final-record loader from `src.analysis.absences.jsa_check`;
- divisional `k` configuration from the maintained P1 path; and
- fixed-point aggregation, recentering and diagnostic ideas from the existing
  P1 and population-policy experiments.

It must not alter production Elo-89, overwrite canonical P1, or make the
experimental penalty available through a production switch. Shared behaviour
should be consumed from its owning module where practical; legacy replay bugs
must not be copied merely because an experimental runner already exists.

The intended transformation is:

```text
History + published final records
  -> explicit non-appearance ledger
  -> paired control and Elo89a fixed-point runs
  -> reproducible convergence and prior-comparison artefacts
```

## Tests required before execution

Focused tests must establish that:

- an ordinary W/L bout with blank decision text remains rated;
- FS receives no rating update;
- FP causes exactly one `-k/2` deduction and no opponent credit;
- each published `A` causes exactly one `-k/2` deduction;
- FP and `A` counts are not double-counted;
- multiple non-appearances accumulate linearly;
- penalties occur after all contested bouts and before end normalisation;
- end normalisation restores the target mean;
- control and Elo89a arms otherwise replay identical evidence;
- iteration 1 starts from the constant prior;
- both arms apply the same aggregation and map-recentering rule; and
- incomplete final-record coverage fails loudly.

## Out of scope

This experiment does not decide:

- whether availability should be part of the meaning of a sumo rating;
- whether `k/2` is predictively optimal;
- whether the resulting rating should replace Elo-89;
- how a penalty should be timed within a basho;
- how to credit a particular opponent or transfer pool;
- how the policy affects daily or peak-rating publications; or
- whether a converged prior is weird, surprising or acceptable.

Those questions may be investigated only after the fixed-point behaviour is
known.

## Next

The implementation is owned by `src.analysis.elo_penalties` and described in
`Elo89a Implementation Design.md`. Inspect the generated fixed-point maps; do
not change production Elo-89 or canonical P1 on the strength of numerical
convergence alone.
