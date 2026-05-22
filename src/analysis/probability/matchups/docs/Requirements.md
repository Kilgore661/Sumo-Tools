# Matchup Probability Distributions: Requirements

This package will analyse the distribution of stronger-vs-weaker bout
probabilities in actual scheduled sumo bouts.

The immediate motivation is public-facing: produce clear, comparable charts
that show how competitive historical matchups are under two definitions of
"stronger".

The implementation should follow the existing analysis pattern:

* compute rich CSV artefacts first
* include fields that may be useful later, not only fields needed by the first
  chart
* derive publication views from those CSVs
* leave publication/deployment mechanics to a separate layer

---

# 1. Core Question

For actual scheduled bouts, how often does the stronger rikishi beat the weaker
rikishi?

There are two definitions of "stronger":

1. empirical/institutional strength: better chii
2. model-based strength: higher pre-bout rating

The public comparison should make these two views legible side by side.

---

# 2. Empirical Distribution

## Definition

For each observed scored bout:

* obtain both rikishi's chii from that basho's banzuke
* define the stronger rikishi as the rikishi with the lower/better chii ordinal
* record whether the lower-ordinal chii won

The empirical probability of interest is:

```text
P(lower-ordinal chii beats higher-ordinal chii)
```

This is an observed-outcome quantity. It does not use Equelo ratings or model
probabilities.

## Intended Interpretation

This view tests the idea that torikumi selection makes actual scheduled bouts
competitive.

Even when nominal chii distance is large, those bouts may occur only in
particular tournament contexts, such as when the higher-ranked rikishi is doing
poorly or the lower-ranked rikishi is doing well. If so, the observed
probability may remain close to a coin flip for many scheduled matchup types.

This result should be interpreted alongside finish-by-chii:

* finish-by-chii shows that basho outcomes vary by starting chii
* matchup probabilities may show that individual scheduled bouts are still
  often close contests

The tension between those facts is part of the point.

## Empirical Deliverables

The observed-results side has three intended deliverables.

### 2.1 Rich Empirical Data

The package should write CSV data that preserves enough detail for later
analysis and alternative public views.

The base data should keep full oracle-cleaned chii, ordinal, sideless chii,
division, bout outcome, and whether the higher-ranked side won.

### 2.2 Per-Sideless-Chii Matchup View

For a selected sideless chii, show the observed probability of beating every
sideless opponent chii that it has actually faced.

The first public scopes are:

```text
Makuuchi only
Juryo only
```

Lower divisions should be computed if convenient, but they are not first-pick
public views because the number of chii is large and likely less useful to
readers.

This view should use confidence intervals rather than hide low-support points
behind an arbitrary cutoff.

### 2.3 Aggregated Stronger-Ranked Distribution

The package should also produce an aggregated empirical view:

```text
P(higher-ranked sideless chii beats lower-ranked sideless chii)
```

This aggregate should be support-weighted/bout-weighted. Common matchup types
should count more than one-off matchup types.

Possible public flavours:

```text
Makuuchi
Juryo
broader/all included domain
```

The exact presentation can be settled later, but the computation should support
these scopes.

---

# 3. Model-Based Distribution

## Definition

For each model-scored bout:

* obtain both rikishi's pre-bout ratings
* define the stronger rikishi as the rikishi with the higher pre-bout rating
* compute the model probability that the stronger-rated rikishi wins

If the model has recorded:

```text
p_rikishi1_wins
```

then the model probability of interest is:

```text
p_stronger_wins = max(p_rikishi1_wins, 1 - p_rikishi1_wins)
```

This transforms the existing arbitrary/stored bout order into a canonical
stronger-vs-weaker view.

## Relationship to Existing Expt3c Chart

`src/analysis/probability/expt3c.py` currently writes:

```text
files/output/Equelo/expt3_predicted_distribution.html
```

That chart bins:

```text
P(stored rikishi1 beats stored rikishi2)
```

The stored rikishi order is not the conceptual variable, so the current chart is
a useful diagnostic but not the preferred public view.

The preferred model-based distribution should instead bin:

```text
P(higher-rated rikishi beats lower-rated rikishi)
```

over the range:

```text
0.50 to 1.00
```

## Model-Based Placeholders

The model-based side should eventually have comparable views to the empirical
side, but its details are not yet specified.

Topics still to settle:

* whether to build a per-sideless-chii model view
* how to make the model aggregate comparable with the empirical aggregate
* whether the model output is computed directly here or consumed from a
  bout-level model forecast CSV
* which model parameters define the public/default model view

---

# 4. Output Requirements

The package should write rich CSV artefacts before writing publication charts.

## Empirical CSV

The empirical output should preserve enough detail to support later views.

Candidate fields:

```text
date
day
rikishi1
rikishi2
chii1
chii2
ordinal1
ordinal2
higher_chii
lower_chii
ordinal_delta
winner
higher_chii_won
```

A derived pair-level or bucket-level CSV may also be useful:

```text
higher_chii
lower_chii
higher_ordinal
lower_ordinal
ordinal_delta
n_obs
n_higher_wins
n_lower_wins
p_higher_wins
ci95_lower
ci95_upper
```

## Model CSV

The model output should likewise preserve bout-level detail.

Candidate fields:

```text
date
day
rikishi1
rikishi2
chii1
chii2
rating1_before
rating2_before
rating_delta_abs
p_rikishi1_wins
p_stronger_wins
stronger_rikishi
stronger_chii
winner
stronger_won
```

---

# 5. Publication Requirements

The first public-facing goal is a pair of comparable charts:

1. empirical distribution:

   ```text
   P(lower-ordinal chii beats higher-ordinal chii)
   ```

2. model-based distribution:

   ```text
   P(higher-rated rikishi beats lower-rated rikishi)
   ```

The charts should be comparable in range and presentation where possible. The
model-based chart naturally lives on `[0.50, 1.00]`. The empirical chart should
be shaped so that the same "stronger beats weaker" interpretation is clear.

The charts are intended as public-facing facts for the broader presentation
layer, but deployment and site navigation should not be implemented inside this
package.

---

# 6. Non-Goals

This package should not initially:

* modify `expt3c.py`
* replace the existing calibration pipeline
* implement SFTP or web-root deployment
* decide the final site navigation
* claim causality for torikumi design

Its job is to compute and expose the distributions cleanly.
