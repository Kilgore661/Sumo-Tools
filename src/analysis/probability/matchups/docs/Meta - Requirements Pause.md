# Requirements Pause: Observed Matchup Experiment

This note records why requirements/specification refinement for
`probability.matchups` is temporarily on hold, and what must happen next.

The pause is deliberate. It is not because the requirements are unclear in a
general sense. It is because the most important public-facing claim has not yet
been established from observed data.

---

# 1. The Claim We Care About

The motivating claim is roughly:

> In actual scheduled sumo bouts, the higher-ranked rikishi often does not have
> a large observed advantage over the lower-ranked rikishi.

In a compressed form:

```text
P(higher-ranked beats lower-ranked) ~= 0.5
```

The `~=` is doing a lot of work. It will need to be unpacked carefully:

* which ranks?
* which divisions?
* which matchup types?
* how much support?
* how wide are the confidence intervals?
* is the statement true generally, or only in specific regions of the banzuke?

Even with those caveats, the claim is likely to be surprising. People tend to
trust chii as a meaningful ordering, and chii does make a kind of institutional
sense. If actual scheduled bouts are close to coin flips across much of the
observed matchup space, that is a significant fact about torikumi and about what
chii means in context.

---

# 2. What We Have Not Yet Shown

We have not yet shown this from observed chii-based bout outcomes.

The existing model-side HTML:

```text
files/output/Equelo/expt3_predicted_distribution.html
```

does not establish the observed claim.

That chart shows that, according to the Expt3/Equelo model, actual scheduled
bouts are usually assigned probabilities near 0.5. In other words:

> Given model ratings, actual torikumi mostly looks competitive.

That is interesting and suggestive, but it is not the same as:

> Given observed chii positions, the higher-ranked side actually wins only
> about half the time in scheduled bouts.

The model result may later become confirmation or comparison. It cannot be the
primary empirical fact.

---

# 3. Why This Blocks Further Specification

Several specification choices depend on what the observed data actually says.

Examples:

* whether the public-facing story should emphasise a broad banzuke-wide
  near-coin-flip distribution
* whether the key result is confined to Makuuchi and Juryo
* whether per-sideless-chii charts are mainly exploratory or central
* whether confidence intervals make the surprising claim robust or fragile
* whether aggregation should lead the public page or sit behind per-rank views
* how strongly the model-based view should be positioned as confirmation

Without the observed experiment, further refinement risks designing a page for a
claim that may be false, local, noisy, or more nuanced than expected.

So the correct next step is experimental:

> compute the observed matchup distributions first, then refine the publication
> spec in light of what they show.

---

# 4. What Is Settled Enough To Proceed

Although the larger publication story is paused, the observed experiment itself
is now defined well enough to implement.

## Domain

Use the same cleaned bout domain as Expt3c via `make_oracle(...)`.

This means:

* use the available history after oracle cleaning
* exclude pre-1958 data through the oracle policy
* before 1989, retain bouts where at least one participant is sekitori
* from 1989 onward, retain bouts where both participants are on the basho
  banzuke
* exclude non-rating/non-fought outcomes such as fusen and blank
* ignore playoffs because they are not present in the raw source data

The empirical and model-based work should use the same domain where possible,
but the immediate experiment is empirical only.

## Ordering

For empirical/chii analysis:

```text
higher-ranked = lower Chii.ordinal()
lower-ranked = higher Chii.ordinal()
```

`Chii.ordinal()` is authoritative and distinguishes east/west side. The oracle
default collapses annotations, which is suitable here.

## Base Data

The experiment should write rich CSV artefacts first.

The base data should preserve:

* date
* day
* rikishi ids
* full oracle-cleaned chii
* sideless chii
* divisions
* ordinals
* winner
* higher-ranked side
* whether the higher-ranked side won

This prevents the first chart from becoming the only available interpretation.

## Observed Views

Three observed-results deliverables are currently defined:

1. rich empirical data
2. per-sideless-chii matchup view
3. aggregated stronger-ranked-vs-weaker-ranked view

The per-sideless-chii view should initially focus on:

```text
Makuuchi
Juryo
```

It should show a selected sideless chii against every sideless opponent chii it
has actually faced, with CI95 error bars and `n_obs` available.

The aggregate view should be support-weighted/bout-weighted. Common matchup
types should count more than one-off matchup types.

---

# 5. What The Experiment Should Answer First

The first experiment should answer practical questions, not build the final
publication page.

Questions:

* What does the per-sideless-chii view look like for Makuuchi?
* What does it look like for Juryo?
* Are observed probabilities often close to 0.5?
* Where are they not close to 0.5?
* How wide are the confidence intervals?
* Are low-support extreme results visually obvious as low-support results?
* Does the support-weighted aggregate view support the near-coin-flip claim?
* Does the answer change by division?

The output should make it easy to decide whether the surprising claim is:

* broadly true
* true only in selected regions
* too noisy to present directly
* false, in which case the model-side result means something different

---

# 6. Model-Based Work Is Next, Not Now

The model-based side remains important, but it should follow the observed
experiment.

There are at least two legitimate narrative directions:

## Chii First

Start with observed chii-space results, then ask whether those results make
sense when translated into Equelo/fixed-v1 rating space.

This asks:

> Does the rating-space interpretation explain the observed chii-space pattern?

## Ratings First

Start with Equelo ratings as first-class data, compute equivalent
rating-space matchup views, then ask whether the canonical chii-to-rating
mapping reproduces similar structure.

This asks:

> Does chii, mapped through fixed-v1 ratings, behave like the rating model's own
> matchup structure?

Neither direction is inherently the "right" one. They are different narrative
routes around the same conceptual diagram.

For now, the important point is simply to keep the distinction visible. The
observed experiment must come first because it establishes the empirical fact
that the model-based work may later explain, confirm, or complicate.

---

# 7. Consequence For Requirements And Specification

The current requirements and specification drafts should be treated as paused
after the observed-results path.

Do not over-refine:

* model-based chart requirements
* final public page copy
* final aggregation choices
* final publication layout

until the observed experiment has produced data.

The next concrete task is therefore:

> implement the observed matchup experiment in a way that is consistent with
> the defined domain, ordering, CSV-first approach, and observed view
> requirements.

After that, revisit the requirements and specification with the actual results
in hand.
