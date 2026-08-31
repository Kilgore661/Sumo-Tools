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

### Interim result: January start state and tenure cohorts

The first boundary analyses are implemented in
`src/analysis/equelo2_boundary_audit`. They compare two ratings for the same
event, immediately before any bout in January 1989:

- the full-history rating carried through November 1988 and the January
  population-normalisation step;
- the fresh Elo-89 rating assigned from the January chii.

Joiners and leavers are excluded, leaving 741 matched incumbents. The overall
comparison is:

| Measure | Result |
|---|---:|
| Mean historical minus Elo-89 | +0.031 points |
| Median difference | +1.766 points |
| Population SD of differences | 89.631 points |
| Mean absolute difference | 68.401 points |
| RMS difference | 89.631 points |
| Pearson correlation | 0.9340 |
| Spearman correlation | 0.8817 |

The common scale and broad ordering survive the join. The near-zero mean is
not, however, evidence of close individual agreement: both systems are
normalised to the same scale, and the mean conceals systematic division-level
offsets. Historical ratings average 101.703 points above the fresh priors in
Makuuchi and 68.434 points below them in Makushita. Jonokuchi has essentially
no within-division association: Pearson `0.0311`, Spearman `-0.0224`.

A complementary directional sanity check asks whether agreement improves when
the comparison is restricted to rikishi with longer represented careers.
Tenure begins at the first represented proper chii, Jk or above. Nested 0, 1,
2, 3, 5 and 10-year cohorts are retained; five years against the complete
cohort is the declared primary comparison. Both mean absolute and RMS
difference were required to fall.

| Minimum tenure | N | Median rated bouts | MAE | RMS | Pearson | Spearman |
|---:|---:|---:|---:|---:|---:|---:|
| 0 years | 741 | 42.0 | 68.401 | 89.631 | 0.9340 | 0.8817 |
| 1 year | 629 | 49.0 | 69.743 | 91.434 | 0.9336 | 0.8905 |
| 2 years | 518 | 56.0 | 72.246 | 94.244 | 0.9313 | 0.8838 |
| 3 years | 428 | 77.0 | 75.414 | 98.000 | 0.9275 | 0.8833 |
| 5 years | 300 | 90.5 | 75.505 | 99.332 | 0.9310 | 0.9048 |
| 10 years | 79 | 319.0 | 68.567 | 98.145 | 0.9533 | 0.9632 |

The five-year cohort therefore **does not pass the declared absolute-difference
check**. Its ordering agrees better by Spearman correlation, but its ratings
are farther from the chii priors by both MAE and RMS difference.

This aggregate result is partly compositional but cannot be dismissed wholly
as an aggregation artefact. Division-controlled five-year comparisons improve
by both MAE and RMS in Makuuchi, Juryo and Makushita. Sandanme is roughly flat
to worse, while Jonidan deteriorates materially. Longer tenure selects more
represented bouts, but also selects survivors and particular career
trajectories, including long-tenured rikishi at low current chii. It is not a
pure proxy for rating reliability.

The retained conclusion is deliberately mixed. The boundary comparison passes
as a basic wiring and scale sanity check and supports continuing the
investigation. The tenure result does not support the simple claim that
restricting the sample to longer-observed rikishi necessarily makes historical
ratings numerically closer to the fresh chii priors. Propagation must therefore
be examined without treating that claim as established.

Generated evidence is under
`files/output/analysis/equelo2_boundary_audit/1989_01/`, principally
`findings.md`, `matched_rikishi.csv`, `tenure_threshold_summary.csv` and
`tenure_division_summary.csv`.

### Interpretation: agreement, priors and propagation

The hypothesis that the two January 1989 rating sets are numerically the same
is rejected. Even in Makuuchi, where agreement is strongest, the conclusion is
only one of broad ordinal agreement. Pearson correlation is `0.8815` and
Spearman correlation `0.8276`, while the historical ratings average `101.703`
points above the fresh priors and their mean absolute difference is `106.363`
points. In the five-year Makuuchi cohort the correlations improve to `0.9165`
and `0.8800`, but mean absolute difference remains `100.245` points and the
mean historical-minus-prior difference remains `95.326` points.

This distinction matters because numerical equality was never a requirement
of the historical extension. A chii prior deliberately discards individual
history. A rating informed by a rikishi's bouts may be more useful precisely
because it moves away from the generic value for his present chii. The tenure
result therefore also rejects the simple argument that more evidence must make
an individual rating numerically closer to its chii prior. It may instead make
the disagreement better informed.

The same point limits what should be expected at the other end of a propagated
run. Canonical \(P_1\) is an **entrant-initialisation policy**, not a target to
which mature ratings or a cross-sectional end-of-basho chii/rating map should
return. Mature ratings incorporate individual results; the active population
is selected by promotion, demotion, longevity and retirement; and the amount
of represented evidence differs across careers and divisions. There is no
sound requirement that ratings at the last represented basho reproduce the
priors used to initialise entrants.

That does not make propagation uninformative. It separates two different
questions:

1. **Prior consistency:** do mature individual ratings, or a map formed from
   them at the last basho, reproduce \(P_1\)? They are not expected to do so.
2. **Replay convergence:** does the world which inherits the pre-1989 state
   become more similar to the world freshly initialised in January 1989 when
   both process the same later bouts and use the same priors for later
   entrants? It is reasonable to expect increasing agreement because later
   evidence is shared and the January 1989 population is gradually replaced,
   but the speed and completeness of that convergence remain empirical
   questions.

The propagation experiment should therefore measure how much of the initial
historical difference survives, where it survives and for how long. It must
not be framed as a test of whether final ratings become equal to the entrant
prior map.

### Interim result: one-pass map implied by the complete history

The retained full-history ledger also permits the map-construction operation
used inside the P1 solver to be applied once, without another replay. This is
not a full-history fixed-point calculation. The operation is:

1. take every full-history basho-start rating observation at each
   annotation-free literal chii;
2. average all observations at that chii over the complete replay;
3. apply one canonical support-proportional recentering to make the unweighted
   literal-map mean `1517`;
4. apply the same unweighted east/west pairing used when canonical P1 is
   consumed;
5. compare the resulting map with P1 over their common domain, then stop.

The full-history map contains 1,125 literal chii and 558 canonical pairs. All
484 P1 pairs are present; the additional 74 pairs are historical-only and are
reported separately rather than included in common-domain comparison metrics.

| Measure over 484 common pairs | Result |
|---|---:|
| Mean full-history minus P1 | -16.359 points |
| Median full-history minus P1 | -34.239 points |
| Population SD of differences | 55.319 points |
| Mean absolute difference | 47.291 points |
| RMS difference | 57.687 points |
| 5th--95th percentile | -77.237 to +78.079 points |
| Minimum--maximum | -117.696 to +289.316 points |
| Pearson correlation | 0.979457 |
| Spearman correlation | 0.955111 |

The maps therefore have strongly similar overall shape but are not numerically
the same. As in the January boundary comparison, the overall result conceals
systematic division-level shifts:

| Division | Common pairs | Mean delta | MAE | Pearson | Spearman |
|---|---:|---:|---:|---:|---:|
| Makuuchi | 22 | +149.273 | 149.273 | 0.8670 | 0.9548 |
| Juryo | 14 | +39.552 | 40.915 | 0.7876 | 0.9736 |
| Makushita | 60 | -35.350 | 35.350 | 0.9964 | 0.9951 |
| Sandanme | 101 | -35.783 | 35.783 | 0.9939 | 0.9936 |
| Jonidan | 210 | -12.624 | 44.222 | 0.9113 | 0.9100 |
| Jonokuchi | 77 | -43.761 | 52.081 | 0.8332 | 0.5288 |

Makushita and Sandanme are particularly notable: their full-history maps are
about 35 points below P1 almost uniformly, while their within-division shape is
nearly unchanged. Makuuchi preserves its ordering strongly by Spearman
correlation but moves upward substantially in rating level. Jonokuchi again
has the weakest ordinal agreement.

The largest common-pair increases are `M17` at `+289.316`, `O1` at `+267.366`
and `Y1` at `+242.443`; the largest decreases are concentrated around
`Jk13`--`Jk22`, reaching `-117.696` at `Jk19`. These tails must be read with
their support counts: lower-end Makuuchi ranks have relatively few full-history
observations because division sizes changed, whereas the Jonokuchi differences
have hundreds.

The result supports further investigation because the post-1988 P1 structure
survives a full-history pass recognisably well. It does not support treating P1
and the implied full-history map as interchangeable, and it does not by itself
justify iterating the full-history map to a new fixed point.

### Provisional verdict: what is and is not broadly consistent

"Broadly consistent" is an umbrella conclusion drawn from several different
checks, not the result of a single statistic. It means that the provisional
Equelo2 has passed enough structural, predictive and historical-plausibility
checks to justify continuing. It does not mean that its ratings are numerically
interchangeable with Elo-89 or P1.

The reasonably clear cases are:

| Check | Evidence | Provisional conclusion |
|---|---|---|
| Overall predictive usefulness | Over the complete history, proto-Equelo2 has mean log loss `0.679354` against `0.693147` for 50--50, and mean Brier loss `0.243025` against `0.250000`. | The complete system extracts information; the priors and updates are not producing arbitrary ratings. |
| Compatibility after 1988 | Post-1988 log loss is `0.675281`, against `0.675498` for a fresh Elo-89 start. | Carrying the pre-1989 state across January 1989 does not materially damage the established later account. The minute favourable difference is incidental. |
| January 1989 overall ordering | Across 741 common rikishi, Pearson correlation is `0.9340`, Spearman correlation `0.8817`, and the mean historical-minus-fresh difference is `+0.031`. | The historical replay and fresh P1 initialisation occupy broadly the same scale and agree strongly in overall ordering. |
| Complete-history chii-map shape | Across 484 common rank pairs, Pearson correlation is `0.979457` and Spearman correlation `0.955111`. | The broad P1 chii/rating structure survives the complete-history replay very clearly. |
| Makushita and Sandanme ordering | Both divisions have Pearson and Spearman correlations of about `0.995` between their complete-history and P1 maps. | Their internal rank order is almost unchanged even though their absolute levels move downward. |
| Elite historical face validity | The processed peak table contains the familiar post-1958 GOAT candidates, places Hakuho first and Taiho among the leaders, and places Kakuryu eleventh rather than in the top ten. | The result is recognisable to an informed sumo reader. Kakuryu's surprising fifth place belongs to legacy Equelo, not proto-Equelo2. |
| Hakuho against Taiho | Hakuho peaks at `3031.291`; Taiho at `2891.554`. Taiho had accumulated more rated bouts at his peak, and the active-population mean was restored throughout. | The model's Hakuho result cannot reasonably be dismissed as Taiho lacking time to stabilise or as simple uncorrected inflation. |

The qualifications and less convincing cases are equally important:

| Check | Less reassuring result | Retained interpretation |
|---|---|---|
| Numerical agreement at the boundary | Overall MAE is `68.401` points and RMS difference `89.631`; Makuuchi historical ratings average `101.703` points above fresh P1 ratings. | Strong correlation is not numerical equality. |
| Division-level boundary agreement | Agreement weakens down the banzuke. In Jonokuchi, Pearson correlation is `0.0311` and Spearman correlation `-0.0224`. | The overall correlation is partly supported by between-division differences; individual agreement at the bottom is absent. |
| Longer-career hypothesis | Requiring five years' tenure raises MAE from `68.401` to `75.505` and RMS difference from `89.631` to `99.332`. | The predeclared distance check fails. More evidence need not move an individual rating closer to the generic prior for his current chii. |
| Tenure within divisions | The five-year comparison improves in Makuuchi, Juryo and Makushita, is roughly flat to worse in Sandanme, and deteriorates materially in Jonidan. | The tenure result is mixed; it also selects survivors and particular career trajectories. |
| Pre-1989 prediction alone | Mean log loss is `0.000442` worse than 50--50, while mean Brier loss is `0.000481` better. | The fourth-decimal differences are contradictory and not treated as substantive, but both must be disclosed. |
| Absolute complete-history map levels | Relative to P1, Makuuchi averages `+149.273` and Juryo `+39.552`, while all four sub-sekitori divisions move downward. | This systematic sekitori--sub-sekitori displacement is the most important unresolved result. It may contain historical signal, a normalisation artefact caused by incomplete early evidence, or both. |
| Extreme pair differences | `M17` is about `+289`, `O1` `+267` and `Y1` `+242`; lower Jonokuchi reaches about `-118`. | High overall map correlation does not make the two maps numerically interchangeable. |
| Jonokuchi behaviour | Jonokuchi has weak within-division rank correlation, and even P1 assigns it a higher unweighted divisional mean than Jonidan. | Elo is already known not to behave sensibly at the bottom of the banzuke. This remains an explicit model weakness. |

The compact provisional judgement is therefore:

> The provisional Equelo2 passes the broad structural, predictive and
> historical-plausibility sanity checks needed to justify continuing.
> Agreement is strongest in overall ordering, within most divisions and in
> the elite historical results. It is much less convincing at the level of
> absolute ratings, lower-division individual ratings and especially the
> relative rating levels of sekitori and sub-sekitori.

The phrase "inflated sekitori ratings and deflated sub-sekitori ratings" is a
useful working hypothesis, not yet an established diagnosis. The defensible
observation is upward and downward **displacement relative to P1**. Establishing
whether the displacement is artificial requires a separate normalisation
experiment; the baseline described here must remain unchanged as its control.

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
