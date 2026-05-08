# Proposal: Mark 3.2 Base-Shift Experiment

## Status

Experiment completed.  The project should use `b = 2000` as the public-facing
Equelo base.

## Purpose

Test whether the current scaled fixed-point Equelo pipeline behaves as expected
under an additive change of rating base.

The immediate practical question is:

> If Mark 3.2 currently tops out around 2000 because it was built from a base
> near 1500, will rerunning the same construction with base `b + 500` produce
> the same system shifted upward, so that the top of the public scale is around
> 2500?

If yes, this gives us a cleaner way to produce a public-facing Equelo scale
with familiar-looking headline numbers, without pretending that the additive
level has independent Elo meaning.

## Background

### Mark 1: Basic Elo

The starting point is ordinary Elo-style rating.

All entrants begin at a common rating `b`.  Before this experiment the practical
project value was 1500.  Bout expectation
is computed from rating difference, and each bout updates the winner and loser
according to how surprising the result was.  The update size is controlled by
`k`, and the expectation curve by `q`.

This gives a simple and useful account:

* win and gain points;
* lose and lose points;
* an upset is worth more than an expected win;
* ratings are a running, path-dependent estimate produced by sequential bout
  updates.

However, Mark 1 has known sumo problems.

First, it takes time to settle.  A rikishi who appears in the observable data
already established in the real sumo world nevertheless starts at the same
baseline as everyone else.

Second, pool churn can cause drift or inflation/deflation.  Since rikishi enter
and leave the active pool, the level of the active rating population can move
over time.

Third, cross-era comparison becomes unsafe.  A rating from one era is not
automatically comparable with the same numerical rating in another era if the
scale has drifted.

Fourth, the 1989 observability cliff creates a large disturbance.  Many
already-active rikishi enter the observable model at once and are assigned flat
initial ratings, forcing another settling period.

The practical objection is the familiar chess-style problem: a great yokozuna
from an earlier era may receive a rating that looks merely sekiwake-level by
modern standards, not because he was weaker, but because the rating scale has
drifted.

### Mark 2: Mean-Preserving Elo

Mark 2 keeps the basic Elo update but preserves the active-pool mean.

When rikishi leave the active population, their rating deviation from the active
mean is redistributed across the remaining active population.  This is a
uniform additive operation, so it does not change rating differences and
therefore does not change bout expectations.

Mark 2 addresses rating drift/inflation by fixing the active reference level.

### Mark 3: Equelo

Mark 3 adds the major Equelo idea: fixed-point chii-based entry.

Instead of assigning every entrant the same rating, estimate a function:

```text
mu: Chii -> rating
```

The fixed-point condition is:

> The initial rating assigned to chii `c` should equal the mean basho-start
> rating observed for rikishi at chii `c` when the rating system is run using
> that same entry rule.

Thus Mark 3 is:

> mean-preserving Elo, with a self-consistent fixed-point entrant prior.

This is the main conceptual step away from basic Elo.  It addresses the flat
entry settling problem and the 1989 cliff, while Mark 2 addresses drift.

The name Equelo is therefore natural: the aim is equivalence over time, by
fixing the active scale and making entry conditions self-consistent.

## Current Version Names

Use the following working names for this discussion.

### Mark 3.1(b)

Raw fixed-point Equelo built with base `b`.

This is the unscaled Expt2 fixed-point map, currently represented by:

```text
files/output/Equelo/expt2_combined_final.csv
```

It has the strong representational story.  It is self-consistent with
basho-start ratings by chii.  With the pre-experiment base, it topped out
around 2500.

Problem: the Mark 3.1 chii-rating map is not monotone with respect to chii.

### Mark 3.2(b)

Scaled fixed-point Equelo built from Mark 3.1(b).

The scaling formula is:

```text
r_scaled = mean + alpha * (r_fixed - mean)
```

where current fixed_v1 uses:

```text
alpha = 0.55
```

This keeps some of the fixed-point rank signal but shrinks the curve toward the
global mean.  The rationale in the existing docs is that raw Expt2 fixed-point
entry was too dispersed for probability experiments; alpha near 0.55 improved
binned calibration MAE.

With the pre-experiment base, Mark 3.2 topped out around 2000.  This is conceptually
fine, because Elo levels are arbitrary up to an additive constant, but it is
awkward for public presentation next to familiar Elo-ish expectations.

Problem: Mark 3.2 also needs monotonicity before it can serve as a public
rank-rating ruler.

### Mark 3.2.1(b)

Smoothed or curated monotone Mark 3.2(b).

This is the role currently played by the v5 landmark curve: it keeps the
scaled fixed-point curve but deletes, masks, and interpolates selected points
to produce a monotone chii-to-rating scale.

### Mark 3.2.2(b)

Shifted Mark 3.2.1(b), for public scale presentation.

The proposed shift is:

```text
Mark 3.2.2(b) = Mark 3.2.1(b) + 500
```

This would make headline ranks such as yokozuna appear around 2500 rather than
around 2000, without changing rating differences.

However, manually adding 500 is less satisfying than proving and exercising
the underlying gauge property by rerunning the pipeline with `b + 500`.

After the experiment, this is better understood as `Mark 3.2.1(2000)`, not as
a separate model with an extra post-processing shift.

## Hypothesis

The Mark 3 fixed-point construction should be equivariant under additive shifts
of the base.

That is:

```text
Mark 3.1(b + k) = Mark 3.1(b) + k
```

If this holds, then scaling also commutes with the base shift:

```text
Mark 3.2(b + k) = Mark 3.2(b) + k
```

Proof sketch for scaling:

```text
Mark 3.2(b) = mean_b + alpha * (Mark 3.1(b) - mean_b)
```

If:

```text
Mark 3.1(b + k) = Mark 3.1(b) + k
mean_(b+k) = mean_b + k
```

then:

```text
Mark 3.2(b + k)
  = (mean_b + k)
    + alpha * ((Mark 3.1(b) + k) - (mean_b + k))
  = Mark 3.2(b) + k
```

The same should remain true of smoothing/curation if the smoothing operation
uses only chii positions, masks, ordering, and fitted rating values, and does
not contain absolute rating thresholds.

## Experiment

### 1. Reproduce Current Mark 3.2(b)

Confirm the current pipeline:

* raw fixed point: `expt2_combined_final.csv`;
* scaled entrant map: fixed_v1 `entrant_initial_ratings.json`;
* alpha: `0.55`;
* base: pre-experiment configured value, practically 1500;
* v5-style smoothing/curation.

Record headline values for:

```text
Y1e, Y1w, O1e, S1e, K1e, M1e, M6e, J1e, Jd100w
```

Record curve maximum, minimum, and selected differences:

```text
Y1e - O1e
Y1e - M1e
M1e - M6e
J1e - Ms1e
Jd1e - Jd100w
```

### 2. Rerun Mark 3.1 With Base b + 500

Add an experiment path that changes the base from `b` to `b + 500` and reruns
the fixed-point production.

This should not be patched by post-processing the CSV.  The point is to test
the pipeline, not merely the algebra.

The output should be separate from production fixed_v1 outputs, for example:

```text
files/output/Equelo/base_shift_experiment/
```

or another explicitly experimental path.

### 3. Build Mark 3.2(b + 500)

Apply the same alpha scaling to the shifted Mark 3.1 output:

```text
alpha = 0.55
```

Compare each shifted value with:

```text
Mark 3.2(b) + 500
```

Expected result:

```text
max_abs_error ~= 0
```

allowing only for ordinary floating-point and CSV round-trip noise.

### 4. Build Smoothed Mark 3.2.1(b + 500)

Run the same v5-style smoothing/curation process on Mark 3.2(b + 500).

Compare with:

```text
Mark 3.2.1(b) + 500
```

Expected result:

```text
same support
same masks/deletions
same monotonicity
same rating differences
all ratings shifted by 500
```

### 5. Inspect Headline Scale

Confirm that the shifted, smoothed public curve tops out around 2500 rather
than around 2000.

If successful, this supports the public-scale idea:

> Mark 3.2.2 is not a different predictive system from Mark 3.2.1.  It is the
> same rating-difference system on a more familiar additive gauge.

## Outcome

The experiment succeeded.

The practical experiment was deliberately simple:

1. Preserve the existing `b = 1500` output as:

   ```text
   files/output/Equelo (b=1500)
   ```

2. Set:

   ```text
   INITIAL_ELO = 2000.0
   ```

3. Rerun the Expt2 fixed-point production, producing the new:

   ```text
   files/output/Equelo
   ```

The new Mark 3.1 combined fixed-point output was the old output plus 500 within
floating-point noise.  The maximum absolute shift error in
`expt2_combined_final.csv` was about:

```text
8.19e-12
```

Applying the fixed-v1 alpha scaling also produced the old Mark 3.2 values plus
500 within floating-point noise.  The maximum absolute scaled shift error was
about:

```text
4.55e-12
```

Selected Mark 3.2 combined headline values moved as follows:

| Chii | b=1500 | b=2000 |
| --- | ---: | ---: |
| Y1e | 2054.713363 | 2554.713363 |
| Y1w | 2017.490514 | 2517.490514 |
| O1e | 1903.262165 | 2403.262165 |
| S1e | 1818.270677 | 2318.270677 |
| K1e | 1782.707248 | 2282.707248 |
| M1e | 1761.795229 | 2261.795229 |
| M6e | 1720.950355 | 2220.950355 |
| J1e | 1688.656224 | 2188.656224 |
| Ms1e | 1648.866030 | 2148.866030 |
| Jd1e | 1398.802642 | 1898.802642 |
| Jd100w | 1349.763811 | 1849.763811 |

Selected rating differences were unchanged to floating-point noise.  For
example:

| Difference | Value |
| --- | ---: |
| Y1e - O1e | 275.365814 |
| Y1e - M1e | 532.578425 |
| M1e - M6e | 74.263407 |
| J1e - Ms1e | 72.345809 |
| Jd1e - Jd100w | 89.161511 |

This confirms the expected additive-gauge behaviour for the parts of the
pipeline inspected here.

The project choice is therefore:

```text
base: b = 2000
```

This choice is arguably cosmetic.  Like Elo ratings, Equelo ratings do not have
a fixed absolute zero point.  Rating differences are the meaningful object:
they determine expectations, updates, and relative interpretation.  The project
could choose `b = 0`, `b = 1500`, or `b = 2000` without changing those rating
differences.

The reason to choose `b = 2000` is presentational.  After alpha scaling and
monotone landmark smoothing, it places the yokozuna headline value near 2500, a
round Elo-like number reminiscent of a chess grandmaster rating.  This should
not be read as a claim that 2500 has independent sumo meaning.

## Success Criteria

The experiment succeeds if:

1. Mark 3.1(b + 500) equals Mark 3.1(b) + 500 within numerical tolerance.
2. Mark 3.2(b + 500) equals Mark 3.2(b) + 500 within numerical tolerance.
3. The smoothed curve produced from Mark 3.2(b + 500) equals the old smoothed
   curve plus 500 within numerical tolerance.
4. Rating differences are unchanged.
5. The shifted public curve has headline values in the desired range, with
   yokozuna around 2500.

## Failure Modes

If the experiment fails, likely causes include:

* a hidden absolute-rating threshold in the pipeline;
* a default base value not being passed through all stages;
* rounding or serialisation being applied too early;
* smoothing code depending on absolute y-values rather than only differences
  and chii positions;
* a K policy or other rule depending on absolute rating level.

Any such failure is important, because it would mean the pipeline is not a
pure additive-gauge system in practice.

## Product Implication

Because the experiment succeeded, the public site can honestly present
`Mark 3.2.1(2000)` as the public Equelo rank landmark scale.

The explanation can be:

> Elo-style ratings are meaningful through differences.  The public Equelo
> scale uses the calibrated, monotone Equelo curve on a conventional additive
> scale, so that familiar headline ranks sit in a familiar numerical range.

This avoids saying that the higher absolute level carries new information.  It
does not.  It is a display-scale convention.

The substantive choices remain:

* alpha shrinkage, which changes the gradient;
* monotone smoothing, which changes the raw fixed-point curve;
* the selected lower bound and masked points.

Those choices must still be documented and defended.

Downstream code and documentation must also make sure they read and describe
the `b = 2000` artefacts once that choice is promoted.  Mixing `b = 1500` and
`b = 2000` outputs would not change rating differences, but it would produce
confusing public numbers and make provenance hard to follow.
