# 12. What Has and Has Not Been Established?

## Why a claim register is necessary

The preceding chapters contain equations, model rules, experiments,
interpretations and judgements. All can be true without having the same
epistemic status.

Defining Elo-89 does not prove that it is a good model. Deriving a property of
its equations does not show that sumo satisfies the corresponding assumptions.
A retrospective predictive improvement is empirical evidence, but not
prospective validation. Accepting a measured effect as tolerable is a
judgement, not a finding that the effect is zero.

This chapter separates six categories:

1. model definitions;
2. mathematical consequences;
3. empirical findings;
4. modelling judgements;
5. assumptions and interpretations; and
6. open questions and known limitations.

“Established” below always means established within the declared scope. It
does not mean universal, timeless or beyond revision.

## 1. What is established by definition

The following statements identify Elo-89. They are true because they form its
contract, not because an experiment discovered them.

| Definition | Scope |
| --- | --- |
| Elo-89 begins with represented history in January 1989 | Model epoch |
| Its state is one stored point rating for each previously rated rikishi, identified independently of shikona | State and identity |
| A represented W/L result is rated; paired fusen and other non-W/L outcomes are excluded | Evidence domain |
| Current rating differences map to probabilities with \(q=400\) | Expectation rule |
| \(K\) is 10 for Yokozuna/Ozeki/Sekiwake/Komusubi, 15 for Maegashira, 25 for Juryo and 35 below Juryo | Update policy |
| A rikishi without a stored rating receives the paired P1-WL value for his current chii | First rating |
| P1-WL was fixed on 30 October 2026 using history through the September 2026 basho | Fitted input |
| The active population consists of banzuke members | Population |
| An active rikishi without an eligible result receives no individual bout update; a stored rating outside the active population receives neither bout updates nor population shifts | Inactivity |
| Common start- and end-of-basho shifts restore the first active population's mean | Population operation |
| Forecasts precede the result updates to which they are compared | Chronology |
| Basho-start, pre-bout, immediate post-bout, day-end and normalised basho-end states are distinct observations | Publication contract |

## 2. What follows mathematically

These statements are consequences of the equations or accounting identities.
They do not depend on whether Elo-89 predicts sumo well.

| Consequence | Qualification |
| --- | --- |
| \(p_A+p_B=1\) for the binary logistic expectation | Assumes the same pre-bout rating difference and \(q\) |
| Increasing A's rating relative to B increases \(p_A\) monotonically | Property of the logistic link |
| Equal ratings imply 50--50; a 400-point gap implies decimal odds of 10:1 | Given \(q=400\) |
| Adding the same constant to every rating in a comparison changes no probability | Translation invariance |
| With common \(K\), the two rating changes sum to zero | Bout-level conservation only |
| With unequal \(K\), net bout mass is \((K_A-K_B)(s_A-p_A)\) | Explains the need to account for unequal-\(K\) movement |
| A common population shift preserves every current gap, order and probability within the shifted set | It can still affect comparisons with later first ratings |
| Adding or removing ratings can change the population mean even when every bout is zero-sum | Open-population accounting identity |
| Disconnected comparison components have unidentified relative offsets | A path is required to place components on one empirically related scale |
| Sequential Elo is generally dependent on event order | Chronology is therefore part of the contract |
| A recurrence requires an initial state | A common numerical origin is arbitrary; equality of initial states is not |

None of these consequences establishes that one scalar is sufficient, that the
chosen \(K\) values are correct, that the active mean represents constant
underlying ability or that historical ratings are externally comparable.

## 3. What the empirical work has found

### Elo-like ratings contain retrospective predictive information

Across the tested post-1988 histories, ordinary Elo-like ratings and the
selected Elo-89 policies produced lower log and Brier loss than a neutral
50--50 forecast. The current model therefore extracts predictive information
from prior represented results.

This does not establish that the advantage is uniform across periods,
divisions or levels of rating maturity, or that it will persist prospectively.

### Informed initialisation and divisional \(K\) improved tested forecasts

Controlled comparisons found that informed first ratings produced the larger
improvement in retrospective log and Brier loss. Divisional \(K\) supplied a
smaller favourable improvement over constant \(K\).

These findings support using rank information at first rating and a variable
responsiveness policy. They do not show that P1-WL is the uniquely best prior,
that division is the best responsiveness measure or that the exact
10/15/25/35 schedule is optimal.

### P1-WL provides useful first ratings

On matched represented history, P1-WL preserved the measured advantage of
informed initialisation over equal initialisation and behaved coherently when
propagated through Elo-89.

P1-WL was fitted from the broad history in which it was retrospectively
evaluated. The finding establishes usefulness within that history, not an
independent chii scale or unseen-data validation. Sparse chii remain less
securely supported than common ones.

### Whole-population preservation led the tested population policies

With the first-rating table held fixed, whole-population mean preservation
improved log and Brier loss relative to the tested no-adjustment policy.
Basho-block analysis supported the direction of the log-loss difference.

This supports the selected policy under the declared proper-score criterion.
It does not show that a fixed active mean is a fact about average sumo ability,
or that the policy wins every metric, subgroup or plausible alternative.

### Rating maturity matters

Calibration was materially weaker when a rating with very little prior bout
evidence faced a more established rating. Later maturity groups were more
closely calibrated, while two immature ratings could appear well calibrated
against one another without strongly discriminating between them.

This establishes heterogeneity hidden by an aggregate calibration curve. The
analysis was conducted on closely related retrospective candidates rather than
a model with an explicit uncertainty state, so it does not quantify an
uncertainty distribution for any individual Elo-89 rating.

### The banzuke contains outcome information

An independent chii-order probe found that choosing the stronger chii selected
the winner in 52.637% of 579,412 eligible unequal-chii bouts, with a rate above
50% in every reported division group.

This establishes that chii order is informative. It does not provide a matched
winner-selection comparison between chii and Elo-89, and it does not justify
treating the stronger chii as certain to win.

### Normalisation effects have been measured

The accounting reconstruction separated Elo-89 rating changes into bout,
start-shift, end-shift and first-rating contributions. Normalisation can
determine the sign of a particular displayed change.

Across 51 recent sliding 12-basho windows, every eligible Makuuchi and Juryo
observation had a net signed normalisation contribution within ±1% of ending
rating. Full-history lower-division exceptions were larger.

The reconstruction and distributions are empirical findings. The percentage
benchmarks and the conclusion that the observed effects are acceptable are
modelling judgements on the published scale.

### A fixed mean does not make chii stationary

The per-chii drift study found substantial historical movement and reversals
among rank-group means despite exact reconciliation of the global population
mean.

This establishes temporal movement in model outputs by chii. It does not
identify whether the cause is changing occupants, competitive ability,
schedule, banzuke structure, model behaviour or a mixture. It is not by itself
evidence of algorithmic inflation.

### Toy results remain conditional toy results

Under a correctly specified stationary toy process, the rating calculation
recovered the hidden skill-gap structure according to predefined stability
criteria. In tested two-division worlds, particular sparse boundary bridges
were sufficient to make the scales commensurate.

These findings validate the calculation and demonstrate possibility under
declared conditions. They do not show that historical sumo is generated by
the Elo model or that every real division and era is adequately connected.

### Evidence snapshots must remain attached to their findings

The investigations above used declared histories and cut-offs appropriate to
their questions. Different bout counts do not automatically contradict one
another, but results from different snapshots must not be combined as though
they came from one calculation. Each numerical claim retains the scope of its
own evidence.

## 4. What has been accepted as judgement

The following choices are defensible without being uniquely demanded by the
data:

- January 1989 is the modern operational boundary.
- Competitive strength is represented by one opponent-sensitive point state.
- \(q=400\) is retained without a comprehensive scale search.
- The 10/15/25/35 schedule implements variable \(K\).
- P1-WL's unsmoothed and sometimes non-monotone values are retained rather
  than forcing the expected curve in advance.
- The P1-WL fitting period ends with the September 2026 basho; the table is
  fixed from 30 October 2026 and later calculations do not refit it.
- A common fixed mean is the longitudinal anchor.
- Normalisation's measured contribution is acceptable with disclosure.
- No individual bout update is invented when no eligible result occurs.
- A stored rating outside the active population receives no population shift.
- Lower divisions remain included despite weaker support.
- Log loss is the primary selection measure; Brier loss and calibration
  provide corroboration and qualification.

These choices are not arbitrary merely because judgement is involved. Each
has a purpose and supporting argument. They remain contestable because other
reasonable purposes or assumptions could support different choices.

## 5. What is assumed or interpreted

Using an Elo-89 rating as an account of “strength” requires interpretation
beyond the algorithm:

- capacity to win represented pairwise bouts is the relevant aspect of
  strength;
- one scalar is a useful approximation across the observed schedule;
- older results should persist through the recurrence until displaced by
  later evidence;
- the banzuke supplies appropriate information when a first rating is needed;
- division is an adequate proxy for responsiveness;
- the selected active population and anchor support the intended longitudinal
  comparisons; and
- the observed torikumi network supports the comparisons actually made.

Retrospective scores test consequences of the fitted system as a whole. They
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
- the exact \(q\), \(K\) schedule, first-rating table, epoch or anchor is
  uniquely optimal;
- a point rating reports how precisely an individual's strength is known;
- inactivity leaves either ability or uncertainty unchanged;
- the current treatment of inactivity is superior to every uncertainty-aware,
  shrinkage or evidence-based time model;
- a fixed population mean makes equal ratings fully comparable across eras;
- the lowest ranks are as reliably represented as mature upper-division
  populations;
- Elo-89 beats a fitted probabilistic chii model, an uncertainty-aware model,
  a dynamic paired-comparison model or every other reasonable family; or
- retrospective superiority will persist prospectively.

These are not all prerequisites for publishing a useful model. They define
the boundary around the claims publication may safely make.

## What would count against Elo-89?

A model which cannot in principle lose is not being tested. Evidence against
Elo-89 could include:

- prospective proper scores no better than simpler declared baselines;
- persistent, material miscalibration after conditioning on rating maturity;
- a reproducible uncertainty-aware or non-Elo alternative with meaningfully
  better later-bout forecasts and no concealed subgroup regression;
- stable matchup residuals demonstrating that the scalar representation
  systematically fails;
- severe sensitivity to reasonable first-rating, \(K\), epoch or population
  choices;
- disconnected or weakly bridged populations being used for claims the data
  cannot support; or
- model outputs whose documented interpretation no longer serves the site's
  stated purpose.

Surprising rankings alone are not decisive evidence. They should prompt a
check of data, support, assumptions and residual outcomes, not automatic
adjustment toward expectation.

## Bottom line

Elo-89 has established a bounded claim:

> On the declared modern represented history, this specified Elo-like system
> extracts modest predictive information from prior outcomes, improves on the
> tested declared alternatives under the retrospective proper-score criterion,
> and provides a reproducible opponent-sensitive rating history.

It has not established a definitive measure of sumo strength. Its results are
conditional on a scalar model, a P1-WL table which is future-informed within
its fitting history, a chosen responsiveness policy, the treatment of
inactivity, an open-population anchor, the observed schedule and a
retrospective evidence base.

That is enough to justify use with explicit qualifications. It is also enough
to make alternative choices meaningful and testable. The final chapter
explains how.
