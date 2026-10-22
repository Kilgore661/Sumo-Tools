# 12. What Has and Has Not Been Established?

> **Draft status:** First continuous-prose draft. This chapter is a claim
> register for the account as a whole. Numerical findings remain attached to
> their declared model, input snapshot and observation stage.

## Why a claim register is necessary

The preceding chapters contain equations, implementation rules, experiments,
interpretations and judgements. All can be true without having the same
epistemic status.

Defining Elo-89 does not prove it is a good model. Deriving a property of its
equations does not show that sumo satisfies the corresponding assumptions. A
retrospective predictive improvement is empirical evidence, but not a
prospective validation. Accepting a measured effect as tolerable is a
judgement, not a finding that the effect is zero.

This chapter therefore separates six categories:

1. model definitions;
2. mathematical consequences;
3. empirical findings;
4. modelling judgements;
5. assumptions and interpretations; and
6. open questions or known defects.

“Established” below always means established within the declared scope. It
does not mean universal, timeless or beyond revision.

## 1. What is established by definition

The following statements identify Elo-89. They are true because they form its
contract, not because an experiment discovered them.

| Definition | Scope |
| --- | --- |
| Elo-89 begins with the represented January 1989 history | Model epoch |
| Its state is one carried point rating per active `RikId` | State and identity |
| A represented W/L result is rated; paired fusen and other non-W/L outcomes are excluded by the production selector | Evidence domain |
| Current rating differences map to probabilities with (q=400) | Expectation rule |
| K is 10 for Y/O/S/K, 15 for M, 25 for J and 35 below Juryo | Update policy |
| A rikishi without a carried rating is initialised from frozen paired P1 | Initialisation |
| The active population is banzuke membership plus participants in selected rated bouts | Population |
| Leaving that active population discards the rating; return invokes P1 again | Lifecycle |
| Common start- and end-of-basho shifts restore the first active population's mean | Population operator |
| Forecasts precede their result updates | Chronology |
| Basho-start, immediate post-bout, day-end and normalised basho-end states are distinct observations | Publication contract |

The off-banzuke clause reports the retained implementation. Chapter 9 records
that older prose states a different policy. That discrepancy must be resolved
before the triggering case occurs; it does not alter the ratings in the
current production artifact, which contains no rated participant with missing
chii.

## 2. What follows mathematically

These statements are consequences of the equations or accounting identities.
They do not depend on whether Elo-89 predicts sumo well.

| Consequence | Qualification |
| --- | --- |
| (p_A+p_B=1) for the binary logistic expectation | Assumes the same pre-bout rating difference and (q) |
| Increasing A's rating relative to B increases (p_A) monotonically | A property of the logistic link |
| Equal ratings imply 50--50; a 400-point gap implies decimal odds of 10:1 | Given (q=400) |
| Adding the same constant to every rating in a comparison changes no probability | Translation invariance |
| With common K, the two rating changes sum to zero | Bout-level conservation only |
| With unequal K, net bout mass is ((K_A-K_B)(s_A-p_A)) | Explains the need to account for dual-K movement |
| A common population shift preserves every current gap, order and probability within the shifted set | It can still affect later entrant comparisons |
| Entry or departure can change the population mean even when every bout is zero-sum | Open-population accounting identity |
| Disconnected comparison components have unidentified relative offsets | A path is required to place components on one empirically related scale |
| Sequential Elo is generally dependent on event order | Canonical ordering is therefore part of the contract |
| A recurrence requires initial state | A common numerical origin is arbitrary; equality of initial states is not |

None of these theorems establishes that one scalar is sufficient, that the
chosen K values are correct, that the active mean represents constant true
ability or that historical ratings are externally comparable.

## 3. What the empirical work has found

### Basic Elo contains predictive information

On the declared 1989/01--2026/07 model-selection snapshot, Basic Elo achieved
mean log loss 0.682753 and Brier loss 0.244687, compared with 0.693147 and 0.25
for a constant 50--50 probability. This establishes modest retrospective
predictive information for that exact Basic Elo model and bout domain.

It does not establish that Basic Elo is optimal, that all periods and
divisions benefit equally or that the same advantage will occur prospectively.

### Informed initialisation and divisional K improved the tested model

In the controlled four-cell comparison over 574,863 common bouts:

| Model | Mean log loss | Mean Brier loss |
| --- | ---: | ---: |
| Basic Elo (B) | 0.682753 | 0.244687 |
| Divisional-K (B_k) | 0.682015 | 0.244355 |
| Informed-prior (B_P) | 0.678055 | 0.242439 |
| Combined old (B_{kP}) | 0.676945 | 0.241968 |

Most of the improvement came from informed initialisation; divisional K added
a smaller favourable effect. The result concerns the tested policies, not all
possible priors or variable-K rules.

The prior was fitted from the broad history being scored. These are controlled
retrospective comparisons, not out-of-sample validation of informed
initialisation.

### P1 is useful but was not the best prior by itself

Canonical (q=400) P1 with divisional K and no population adjustment achieved
mean log loss 0.677319. It retained roughly 94% of the old combined model's
incremental log-loss improvement over Basic Elo. The remaining disadvantage
was concentrated mainly before 30 prior rated bouts.

This establishes P1 as a credible initialisation artifact in the tested
family. It does not establish that P1 is a timeless chii scale or that its
support-proportional construction was selected solely by predictive evidence.

### Whole-population preservation led the tested final candidates

Holding P1 fixed on the same 574,863-bout domain produced:

| Population policy | Mean log loss | Mean Brier loss | Aggregate ECE |
| --- | ---: | ---: | ---: |
| No population adjustment | 0.677319 | 0.242086 | 0.014453 |
| Expt2 departure redistribution | 0.684196 | 0.245148 | 0.017651 |
| Elo-89 whole-population preservation | **0.675629** | **0.241362** | 0.014537 |

Elo-89 improved log loss over no adjustment by 0.001690 and over the old
combined model by 0.001316; the recorded basho-block bootstrap intervals
excluded zero. Brier loss agreed. The old combined model retained slightly
better aggregate ECE.

This supports selecting Elo-89 under the declared primary criterion. It does
not show that the model wins every metric, every maturity band or every
plausible alternative.

### Rating maturity matters

Calibration was materially weaker when a rating with fewer than 30 prior
bouts faced a more established rating. Later maturity groups were much more
closely calibrated, and two immature ratings could be well calibrated against
one another while remaining weakly discriminating.

This establishes heterogeneity hidden by an aggregate calibration curve. It
does not quantify an uncertainty distribution for any individual rating.

### The banzuke contains outcome information

On a later History snapshot over the same nominal dates, simply choosing the
stronger chii selected the winner in 52.637% of 579,412 eligible unequal-chii
bouts. The rate exceeded 50% in every reported division group.

This establishes that chii order is informative. It does not establish a
matched winner-selection ordering between chii and Elo: the probe used a
different source snapshot, and it did not compare their favourites bout by
bout. Treating the chii selection as a literal probability of one also gives
poor proper scores and infinite log loss on an upset.

### Normalisation effects have been measured and accepted

The accounting reconstruction reconciled Elo-89 rating changes into bout,
start-shift, end-shift and reinitialisation contributions. Normalisation can
determine the sign of a particular displayed change. Across 51 recent sliding
12-basho windows, however, every eligible Makuuchi and Juryo observation had a
net signed contribution within ±1% of end rating. Full-history low-division
exceptions were larger.

The reconstruction and distributions are findings. The one- and five-percent
benchmarks, and the conclusion that the observed effect is acceptable, are
modelling judgements on the published scale.

### A fixed mean does not make chii stationary

The per-chii drift study found substantial historical movement and reversals
among rank-group means despite exact reconciliation of the global population
mean. It verified those movements against a saved January 1989--July 2026
production run.

This establishes temporal movement in model outputs by chii. It does not
identify whether the cause is changing occupants, sumo strength, schedule,
banzuke structure, model behaviour or a mixture. It is not by itself evidence
of algorithmic inflation.

### Toy results remain conditional toy results

Under a correctly specified stationary toy process, the implementation
recovered the hidden skill-gap structure according to predefined stability
criteria. In the tested two-division worlds, particular sparse boundary
bridges were sufficient to make the scales commensurate.

These findings validate machinery and demonstrate possibility under declared
conditions. They do not show that historical sumo is generated by the Elo
model or that every real division and era is adequately connected.

## Evidence snapshots must not be merged silently

Several valid results use different source histories or cut-offs.

| Investigation | Declared scope |
| --- | --- |
| Final model-selection and population-policy gate | 574,863 common W/L bouts, 1989/01--2026/07, frozen comparison snapshot |
| Chii-order probe | 579,412 unequal-chii W/L bouts, same nominal dates but a later History snapshot |
| Per-chii drift study | Saved Elo-89 run through 2026/07, 224 basho and 160,185 rikishi/basho observations |
| Current inspected production artifact | Through 2026/09, 581,634 rated bouts |

Different counts do not automatically contradict one another. They prevent
unqualified numerical combination. A claim must cite its own snapshot rather
than borrowing a newer denominator or presenting an older score as though it
were calculated on current production data.

## 4. What has been accepted as judgement

The project has made the following defensible choices without claiming that
the data uniquely demanded them:

- January 1989 is the modern operational boundary.
- Competitive strength is represented by one opponent-sensitive point state.
- (q=400) is retained rather than selected through a comprehensive search.
- The exact 10/15/25/35 schedule is used as the variable-K policy.
- P1's unsmoothed and sometimes non-monotone values are preferable to imposing
  the curve expected in advance.
- A common fixed mean is the chosen longitudinal anchor.
- Normalisation's measured contribution is acceptable with disclosure.
- A rikishi who remains represented receives no invented inactivity penalty.
- A rikishi who leaves the active population and returns is reinitialised.
- Lower divisions remain included despite weaker support.
- Log loss is the primary selection measure; Brier and calibration provide
  corroboration and qualification.

These are not arbitrary merely because judgement is involved. Each has a
purpose and some supporting argument. They remain contestable because other
reasonable purposes or assumptions could support different choices.

## 5. What is assumed or interpreted

Using an Elo-89 rating as an account of “strength” requires additional
interpretation beyond the algorithm:

- that capacity to win represented pairwise bouts is the relevant aspect of
  strength;
- that one scalar is a useful approximation across the observed schedule;
- that older results should persist through the fixed-K recurrence until
  displaced by later evidence;
- that the banzuke supplies appropriate prior information at entry;
- that division is an adequate proxy for responsiveness;
- that the selected active population and anchor support the desired
  longitudinal comparisons; and
- that the observed torikumi network supports the comparisons actually made.

The retrospective scores test consequences of the whole fitted system. They
do not separately prove every assumption. Nor does a plausible ranking prove
the interpretation: tuning until favoured rikishi or expected chii appear in
the desired order would reintroduce the model bias this project seeks to
avoid.

## 6. What has not been established

The project has not established that:

- Elo-89 measures a unique, observer-independent quantity called true
  strength;
- one-dimensional strength is sufficient for all important sumo matchups;
- style or other non-transitive effects are negligible;
- the exact q, K schedule, prior, epoch or anchor is uniquely optimal;
- a point rating reports how precisely an individual's strength is known;
- inactivity leaves either ability or uncertainty unchanged;
- reinitialisation after departure predicts better than restoration or
  partial shrinkage;
- a fixed population mean makes equal ratings fully comparable across eras;
- the lowest ranks are as reliably represented as mature upper-division
  populations;
- Elo-89 beats a fitted probabilistic chii model, an uncertainty-aware model,
  a dynamic paired-comparison model or every other reasonable family;
- retrospective superiority will persist prospectively; or
- the current canonical P1 would remain preferred after its missing-kimarite
  eligibility defect is corrected.

These are not all prerequisites for publishing a useful model. They define
the boundary around the claims which publication may safely make.

## Known defects are not open philosophical questions

Three concrete matters require resolution or corrective work:

1. canonical P1 excluded known W/L results whose kimarite field was blank;
2. the off-banzuke W/L policy differs between retained code and named-model
   prose; and
3. production manifests do not yet bind every input and code identity with
   stable hashes.

The first can change fitted values and therefore needs regeneration and
evaluation. The second currently has no triggering case in the production
ledger but must be made prospective policy. The third weakens provenance but
does not change the mathematical output already copied into a bundle.

## What would count against Elo-89?

A model which cannot in principle lose is not being tested. Evidence against
Elo-89 could include:

- prospective proper scores no better than simpler declared baselines;
- persistent, material miscalibration after conditioning on rating maturity;
- a reproducible uncertainty-aware or non-Elo alternative with meaningfully
  better later-bout forecasts and no concealed subgroup regression;
- stable matchup residuals demonstrating that the scalar representation
  systematically fails;
- severe sensitivity to reasonable prior, K, epoch or population choices;
- disconnected or weakly bridged populations being used for claims the data
  cannot support;
- corrected P1 evidence materially degrading the selected system; or
- model outputs whose documented interpretation no longer serves the site's
  stated purpose.

Surprising rankings alone are not decisive evidence. They should prompt a
check of data, support, assumptions and residual outcomes, not automatic
adjustment toward expectation.

## Bottom line

Elo-89 has established a bounded claim:

> On the declared modern represented history, this specified Elo-like system
> extracts modest predictive information from prior outcomes, improves on the
> tested simpler Elo variants under the declared retrospective proper-score
> criterion, and provides a reproducible opponent-sensitive rating history.

It has not established a definitive measure of sumo strength. Its results are
conditional on a scalar model, a future-informed and presently defective P1
artifact, a chosen responsiveness policy, an open-population anchor, the
observed schedule and a retrospective evidence base.

That combination is enough to justify use with explicit qualifications. It is
also enough to make alternative choices meaningful and testable. The final
chapter explains how.

## Working sources

- `../../../../analysis/elo_model_selection/docs/Results 1.md`
- `../../../../analysis/equelo_population_policy/README.md`
- `../../../../analysis/docs/story/15 Tranche 1 - Population Normalisation Policy.md`
- `../../../../analysis/docs/story/22 Elo-89 Rating System Appraisal.md`
- `../../../../analysis/chii_prediction/docs/Findings.md`
- `../../../../analysis/elo89_normalisation/docs/Normalisation Investigation.md`
- `../../../../analysis/elo89_normalisation/docs/Per-Chii Drift Findings.md`
- `../../../../analysis/toy_elo/README.md`
- `../../../../../docs/Elo-89 P1 Missing Kimarite Repair.md`
