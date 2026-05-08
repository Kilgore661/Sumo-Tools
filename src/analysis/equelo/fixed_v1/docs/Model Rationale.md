# Equelo Fixed v1 Model Rationale

## Status

Initial rationale draft.

This document explains why `fixed_v1` uses its chosen Equelo model parameters.
It is deliberately practical.  The aim is not to prove that this is the only
valid rating system, but to define a stable, defensible rating series for the
project to use.

## The Problem

The project needs rating numbers that can be used by downstream tools without
rerunning the full Equelo experiment each time.

Those numbers should be:

- deterministic;
- reproducible;
- available for all represented rikishi through time;
- plausible when inspected next to the banzuke;
- grounded in the existing Equelo/probability experiments;
- honest about their experimental status.

The immediate pressure comes from the Banzuke Change Report, but the definition
is project-level.  `fixed_v1` is the first fixed meaning of "Equelo rating" for
the broader toolset.

## Why Not Pure Constant Entry?

The cleanest Expt3c baseline gives every new entrant the same initial rating.
That is attractive because it avoids building official rank information into
the rating scale.

However, it has a practical weakness: it takes time for ratings to settle.
At the start of the history slice, the system is asked to behave as though a
yokozuna and a juryo rikishi have the same prior strength.  That is
philosophically clean as an experiment, but poor as the basis for a usable
rating history.

The project already knows that chii carries information.  Refusing to use that
information at entry produces an avoidable warm-up problem.

## Why Use Fixed-Point Initialisation?

Expt2 was created to address the entry problem.  Instead of assigning every
entrant the same rating, it estimates a stable mapping:

```text
chii -> initial rating
```

The resulting fixed-point ratings are broadly monotone with chii and look
plausible as prior values.  They encode the common-sense fact that higher ranks
usually represent stronger rikishi.

The word "broadly" matters.  The Expt2 outcomes show stable local departures
from monotonicity:

- below roughly Jd100, the rating curve bends upward rather than continuing to
  fall smoothly;
- within Makuuchi, there is a small but persistent upward bump around the
  lower Maegashira ranks, with the M13--M16 region not following the otherwise
  smooth trajectory.

These features are not numerical noise.  They appear to be properties of the
fixed-point solution.  A plausible explanation is churn: lower-division ranks,
and possibly the lower Maegashira promotion/relegation boundary, may contain
systematically different mixes of entrants, short-career rikishi, and rikishi
moving through the rank system.  This explanation has not yet been tested.

This limits the claim that fixed-point ratings "follow chii".  They follow the
main chii ordering strikingly well over most of the populated range, but they
should not be treated as a clean monotone transformation of chii until the churn
hypothesis, or some alternative explanation for these bumps, has been
investigated.

This is not philosophically neutral.  It means rank information enters the
rating process.  For some research questions, especially questions about the
relationship between outcome-derived strength and institutional rank, that is a
real cost.

For `fixed_v1`, the practical benefit outweighs the cost.  The purpose is to
provide a serviceable rating series, not a perfectly rank-independent research
baseline.

## Why Scale The Fixed-Point Values?

Raw Expt2 fixed-point initialisation was found to be too dispersed.  In
probability experiments, using those values directly made predictions worse.

A scaled version keeps the ordering information while reducing the spread:

```text
r_scaled = mu + alpha * (r_fixed - mu)
```

where:

- `mu` is the mean fixed-point rating;
- `alpha` lies between `0` and `1`;
- `alpha = 0` collapses back to constant entry;
- `alpha = 1` uses raw fixed-point values.

The retained alpha sweep results show the expected trade-off:

- raw Brier score is best at `alpha = 0`;
- binned calibration MAE is best near `alpha = 0.55`;
- raw fixed-point initialisation (`alpha = 1`) is worse.

For `fixed_v1`, calibration is important because the ratings are intended to be
used as interpretable context, not only as a discriminative score.  We therefore
choose:

```text
alpha = 0.55
```

This should not be interpreted as a precise constant of nature.  It is a stable
rounded value near the observed calibration optimum.

## Why Base = 2000?

Equelo inherits an important property from Elo-style ratings: the absolute
rating level is not fixed by the model.  Rating differences are the meaningful
object.  They determine expectations, updates, and relative interpretation.
Adding the same constant to every rating leaves those semantics unchanged.

The project previously used a base near 1500.  A base-shift experiment reran
the Expt2 fixed-point pipeline with:

```text
INITIAL_ELO = 2000.0
```

The resulting Mark 3.1 combined fixed-point output was the previous `b = 1500`
output plus 500 within floating-point noise.  Applying the fixed-v1 alpha
scaling preserved the same additive shift.  Selected rating differences were
unchanged.

For `fixed_v1`, we therefore choose:

```text
base = 2000
```

This choice is arguably cosmetic.  The project could choose `b = 0`,
`b = 1500`, or `b = 2000` without changing the semantics of rating
differences.  The reason to prefer `b = 2000` is public presentation: after
alpha scaling and monotone landmark smoothing, the yokozuna landmark sits near
2500, a round Elo-like number reminiscent of a chess grandmaster rating.  This
should not be read as a claim that 2500 has independent sumo meaning.

## Why q = 900?

The logistic scale `q` controls how rating differences map to win
probabilities.

The retained q sweep indicates:

- raw Brier score is best around `q = 800`;
- binned calibration MAE is best around `q = 1000`;
- behaviour is smooth across the neighbourhood.

A link-only sweep also supports `q = 900` as internally consistent for the
rating differences produced by a `q = 900` run.

For `fixed_v1`, we choose:

```text
q = 900
```

This is a compromise value rather than a sharp optimum.  It balances predictive
accuracy and calibration and is already used as the project-level working
choice in later Expt3c documentation.

## Why Divisional K?

The K-factor controls how quickly ratings respond to bout results.

The current Expt3c default uses a divisional K policy loaded from:

```text
files/input/elo_fide.json
```

This lets update size vary by rank region.  That is not perfectly neutral:
official rank affects the dynamics through K.  However, it is the maintained
practical configuration used by the later Expt3c experiments and is consistent
with the general idea that different parts of the banzuke may have different
expected volatility.

For `fixed_v1`, we choose the maintained practical default:

```text
K policy = divisional
K config = files/input/elo_fide.json
```

This is a candidate for later sensitivity work, but not a blocker for v1.

## Why Closed Mode?

Closed mode redistributes departing rating mass across the active survivors at
basho boundaries.  This helps maintain a stable active-universe scale.

Open mode is a conventional Elo interpretation, but in this project it allows
the active rating population to drift as rikishi enter and leave.  Since
`fixed_v1` is intended to provide a long historical rating series, stability of
the active scale is valuable.

For `fixed_v1`, we choose:

```text
mode = closed
```

## Why Annotation-Only Collapse?

The cleaned Equelo history can collapse chii in more than one way.  The current
default removes annotations while preserving the main rank structure, side, and
number.

For `fixed_v1`, we choose:

```text
collapse mode = annotation-only
```

This preserves the banzuke structure that users expect while avoiding
over-interpreting exceptional annotations.

## Fixed v1 Definition

`fixed_v1` shall use:

```text
source history: January 1958 onward
history cleaning: Expt1 Oracle
simulator: Expt1 simulate()
interpretation: Expt3c-style sequential rating process
mode: closed
entrant policy: scaled fixed-point
fixed-point source: files/output/Equelo/expt2_combined_final.csv
base: 2000
alpha: 0.55
q: 900
K policy: divisional
K config: files/input/elo_fide.json
collapse mode: annotation-only
```

## What This Claims

`fixed_v1` claims to be a useful, reproducible, project-level rating series.

It is based on:

- a coherent Elo-like update process;
- plausible rank-aware initial values;
- retained experiments showing calibrated probabilities;
- parameter sweeps indicating reasonable robustness;
- a practical compromise between purity and usefulness.

It is reasonable to use these ratings as contextual numbers in project tools.
It is not yet reasonable to use them where a strictly chii-monotone scale is a
hard requirement.

## What This Does Not Claim

`fixed_v1` does not claim:

- to be the final or optimal Equelo model;
- to be a causal model of rikishi ability;
- to replace the banzuke;
- to be independent of rank information;
- to be strictly monotone in chii;
- to explain the observed Jd100 and lower-Maegashira non-monotonicities;
- to settle the philosophical question of what ratings "really mean".

The ratings should be read as model-derived context: meaningful, useful, and
tested enough to be worth publishing, but still derived from an explicit model
choice.

## Provenance Notes

The relevant retained output files include:

```text
files/output/Equelo/expt2_combined_final.csv
files/output/Equelo(850 or 900)/expt3_q_sweep.csv
files/output/Equelo(850 or 900)/expt3_alpha_sweep.csv
files/output/Equelo(850 or 900)/expt3_link_sweep.csv
```

During the base-shift experiment, the old `b = 1500` output was retained as:

```text
files/output/Equelo (b=1500)
```

and the regenerated `b = 2000` output occupied:

```text
files/output/Equelo
```

The parenthesised output directory names are historical artefacts.  A future
cleanup should move fixed-v1 generation outputs into a dedicated location with
clean provenance metadata.
