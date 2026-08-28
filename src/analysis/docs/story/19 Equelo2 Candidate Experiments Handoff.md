# Equelo2 Candidate Experiments Handoff

## Purpose and status

This is the restart point for the two experiments still required before asking
whether the present proto-Equelo2 has become a defensible Equelo2 candidate.
They are:

1. audit the November 1988 endpoint, the January 1989 handover and the
   historical chii-to-rating maps;
2. test realised-outcome forecasting against 50--50 in a fixed rikishi pool.

The experiments address different questions. The first tests the actual join
between the historical extension and Elo-89. The second tests the predictive
content of ordinary Elo updates in the simplest closed setting. Neither is a
request to tune proto-Equelo2 until it produces a preferred result.

## Position inherited by this handoff

The present baseline applies Elo-89's canonical \(P_1\) priors, `q=400`,
divisional `k` and whole-population mean preservation to the represented
history from January 1958. Chii outside the Elo-89 prior map inherit the rating
of the nearest supported chii above them. A rikishi's most recently informed
rating persists through gaps in the available results and through absence
from the represented banzuke. Published ratings are observed after the named
basho's eligible bouts and all post-basho processing.

Several surrounding questions have already been settled sufficiently for the
present purpose:

- pre-1989 results are included so that historical and modern rikishi can be
  compared in one account, not to improve post-1988 forecasts;
- post-1988 scoring is principally a compatibility check on that historical
  extension;
- rating persistence is the adopted working policy under incomplete
  information; the unusual cases in which a ranked rikishi leaves and later
  returns to the banzuke are recorded, but do not currently justify a separate
  reset policy;
- the pre-1989 comparison with 50--50 is mixed by measure and differs only in
  the fourth decimal place; it is disclosed but is not a candidate blocker;
- a broad Hakuho--Taiho sensitivity exercise is not a candidate gate. The
  model's conclusion is conditional on its stated cross-era assumptions and
  on peak rating being the chosen meaning of “better”.

The current full-history baseline contains 745,206 rated bouts. Its mean log
loss is 0.679354 and its mean Brier loss is 0.243025. Over the post-1988 domain
its log loss is 0.675281, compared with 0.675498 for Elo-89 started afresh.
That small favourable difference is incidental: the important observation is
that adding the historical state has not materially damaged the established
post-1988 account.

The existing baseline artifacts are under:

`files/output/analysis/equelo2_baseline/full_history_1958_01_to_2026_07/`

They include `1988_11_ratings.csv`, `1989_01_handover.csv` and
`chii_rating_summary.csv`. These are useful inputs to the first experiment,
but their existence is not itself the requested analysis.

## Experiment 1: audit the historical/modern join

### Question

What state has the 1958--1988 replay produced by the processed end of November
1988, how is that state carried into January 1989, and what relationship
between chii and rating does the historical evidence actually support?

The audit should answer at least these questions:

1. Which January 1989 rikishi receive a persisted rating, and which receive an
   entrant prior?
2. For the incumbents, how different is the persisted proto-Equelo2 rating
   from the rating with which a fresh Elo-89 run would start them?
3. Are any differences caused by identity, eligibility, population or
   handover errors rather than by genuine historical state?
4. What chii-to-rating relationships appear before 1989, with what support,
   and how do they compare with canonical \(P_1\)?
5. Is the transition intelligible at the level of divisions, chii and
   individual rikishi rather than merely acceptable in an aggregate score?

### Why this experiment suggests itself

Equelo2 exists to join the pre-1989 record to Elo-89. November 1988 and January
1989 are therefore the exact seam at which its defining claim can be inspected.
The aggregate post-1988 score tells us that the carried historical state does
not materially spoil Elo-89, but it can conceal compensating errors, anomalous
individual ratings or a discontinuity in the chii/rating relationship.

The construction also began with a deliberately simple assumption: chii have
stable enough ordinal meaning across the represented history for Elo-89 priors
to initialise earlier rikishi. Examining the historical chii-to-rating map is
the direct descriptive check suggested by that assumption. It cannot prove
that the meaning of chii is invariant, but it can reveal where the data agree,
where they differ and where support is too weak to say much.

This is a bounded next step because the replay already emits the principal
boundary artifacts. The missing work is to turn them into an auditable account
of the join before considering a more elaborate historical prior procedure.

### Proposed analysis

The implementation should produce a reproducible source and model manifest,
then:

1. inventory the processed November 1988 ratings and the January 1989
   represented population;
2. classify the January 1989 population into carried incumbents, genuine
   entrants or re-entrants, and other explicitly explained cases;
3. compare each incumbent's carried rating with its fresh Elo-89 initial
   rating, reporting counts, mean and median differences, quantiles, RMS
   difference, rank correlation and the largest absolute differences;
4. inspect the largest discrepancies as named rikishi rather than leaving
   them as distribution tails;
5. calculate pre-1989 chii-to-rating summaries with support counts, by division
   and by useful time bands, using the processed basho-end observation
   convention;
6. compare those summaries with \(P_1\), preserving literal annotated chii and
   making unsupported or weakly supported cells visible;
7. report post-1988 scoring over short boundary horizons as well as over the
   complete later interval, so that a temporary handover disturbance cannot
   disappear inside four decades of results.

The report must distinguish a descriptive historical map from an entrant
prior map. It must also call out Jonokuchi explicitly: the fitted map there is
not merely noisy but directionally implausible, with ratings rising as formal
chii falls. It must not present that relationship as a meaningful skill scale.

### Completion criterion

This experiment is complete when another reader can reconstruct who carried
which rating across the boundary, understand the largest differences from a
fresh Elo-89 start, and see the amount of evidence behind every reported
historical chii/rating summary. Any unexplained identity or population
discontinuity is a defect to resolve, not a modelling result.

The experiment should not silently replace \(P_1\). If the historical maps
suggest that a pre-1989 fixed-point prior might be useful, that becomes a
separate, explicit proposal evaluated against the unchanged baseline.

## Experiment 2: fixed-pool realised-outcome control

### Question

In a constant pool of rikishi with fixed, unequal latent abilities, do Elo's
chronological pre-bout forecasts score better against realised outcomes than a
50--50 forecast?

### Why this experiment suggests itself

The project uses prediction against 50--50 as a basic sanity check: a rating
system which has learned useful differences between rikishi ought to do better
than knowing nothing. The historical tests support that proposition for the
complete system, but they also contain entry, retirement, incomplete early
records, chii-informed priors and a population whose composition changes over
time. Those features make it easy to confuse the basic claim about Elo's
updates with claims about the quality of every Equelo2 policy.

Existing fixed-pool toy experiments remove those historical complications,
but measure recovery of latent gaps, convergence, forecast error against the
latent probabilities and forgetting of initial conditions. They do not make
the most direct realised-outcome comparison: score the forecasts Elo actually
made against the same wins and losses scored by a neutral predictor.

The missing experiment therefore suggests itself as the cleanest bridge
between the mathematical update rule and the project's public, deliberately
modest claim that the ratings contain more information than 50--50. It also
supplies a negative control: when all latent abilities are equal, Elo should
not manufacture a systematic advantage over neutral prediction.

### Proposed design

Use a fixed set of simulated rikishi, a connected reproducible schedule and
fixed latent abilities. Generate every result from the declared logistic win
probability, have Elo forecast the bout before updating either rating, and
score both that forecast and 0.5 against the realised result.

The primary unequal-ability condition should:

- use `q=400` and a declared, untuned `k`;
- start from an explicitly stated common rating or prior state;
- keep identities, abilities and pool membership fixed;
- use multiple recorded random seeds;
- report paired Elo-minus-neutral differences in mean log loss and Brier loss;
- show the variation across runs and across time, including the initial
  learning period rather than deleting it without explanation.

An equal-ability condition should repeat the design with every true bout
probability equal to 0.5. Optional signal-strength or schedule variants may be
reported as secondary results, but should not replace a predeclared primary
condition.

Because the population is fixed, this control needs no chii, entrant prior,
departure policy or population normalisation. Adding those features would
defeat its purpose. It tests the information extracted by the Elo update
dynamics, not the complete historical Equelo2 contract.

### Completion criterion

The experiment is complete when its seeds, schedule, latent abilities,
outcomes and pre-bout forecasts are reproducible; the paired log-loss and
Brier comparisons with 50--50 are reported; and the equal-ability negative
control is included. The conclusion must state the size and variability of
any advantage, not merely whether the average has the desired sign.

Success would establish the intended narrow proposition in a clean setting.
It would not prove that proto-Equelo2 is the best historical model, validate
future-informed priors prospectively, or resolve the weakness of its
Jonokuchi chii/rating relationship.

## Order and implementation convention

The experiments are logically independent. The boundary audit should normally
come first because it tests Equelo2's defining historical join and can reuse
artifacts already produced by the full-history run. The fixed-pool control can
then close the separate explanatory gap about prediction in a constant pool.

Following current analysis-package conventions, implementation code should
live under `src/analysis` and generated artifacts under the matching
`files/output/analysis/<package>` directory. The exact package names should be
chosen after checking the neighbouring boundary and toy-Elo packages, rather
than creating a second home for an existing analysis family.

The baseline must remain frozen while these diagnostics are run. A result
which motivates a model change should lead to a separately named candidate
and a controlled comparison with the baseline.

## Explicit non-goals

This handoff does not propose:

- a persistence-versus-reset experiment;
- a broad Hakuho--Taiho robustness sweep;
- extension before January 1958;
- adoption of a pre-1989 fixed-point prior before the boundary evidence is
  examined;
- tuning on the fixed-pool outcomes;
- production or website migration.

## Decision after the experiments

When both reports exist, the Equelo2 candidate review should ask:

1. Is the 1988/89 handover correct, intelligible and free of unexplained
   discontinuities?
2. Do the historical chii/rating summaries expose a candidate-blocking problem
   or merely documented limits on what the data support?
3. Does Elo beat 50--50 on realised outcomes in the fixed unequal-ability
   control, while behaving appropriately in the equal-ability control?
4. If either experiment motivated a model change, was that change evaluated
   as a new candidate rather than folded silently into the baseline?

Only then should the project return to the question: **have we got a candidate
for Equelo2 nailed down?**
