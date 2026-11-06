# 10. Why Elo-89 Makes Those Choices

## Different choices have different kinds of support

Chapter 9 specified the Elo-89 contract. Exact specification is necessary for
reproduction, but it does not show why each choice was made or how strongly
the available evidence supports it.

This chapter uses four descriptions:

- **empirical evidence**: declared alternatives were compared on relevant
  recorded outcomes;
- **modelling judgement**: a necessary interpretation or policy was chosen
  for stated reasons without a decisive comparative experiment;
- **reproducibility requirement**: the model or publication cannot be
  reconstructed unambiguously without fixing the choice; and
- **open question**: a plausible alternative has not been tested adequately.

A choice can have more than one status. Divisional \(K\), for example, has
empirical support as a general policy, while its exact numerical schedule
remains partly a modelling judgement.

## Decision register

| Component | Main status | Reason for the choice | Important qualification |
| --- | --- | --- | --- |
| January 1989 epoch | Data boundary and modelling judgement | Begins where SumoDB contains every banzuke and every bout between rikishi on the banzuke | Earlier lower-division records are incomplete; an earlier-history model would require a different evidence policy |
| Binary fought-result domain | Modelling judgement | Uses recorded W/L results while excluding fusen and other outcomes outside the binary fought-bout model | Alternative numerical treatments of fusen were not compared comprehensively |
| \(q=400\) | Convention with diagnostic support | Gives rating gaps their conventional Elo interpretation and is adequately calibrated for mature ratings | It was not selected by a comprehensive search |
| Divisional \(K\) | Empirical evidence and modelling judgement | Retrospective comparisons favoured faster adjustment in lower divisions | The exact values were not independently optimised; division is only a proxy for maturity and change |
| P1-WL first ratings | Empirical evidence and modelling judgement | Rank-informed initialisation reduces the weakness of ratings with little bout evidence | The table is future-informed within its fitting period, and sparse chii remain difficult |
| Fixed P1-WL table | Reproducibility requirement | Keeps later calculations comparable and allows subsequent results to test a genuinely fixed prior | Freezing does not make the table timeless or uniquely correct |
| Whole-population mean preservation | Empirical evidence and anchoring judgement | It performed better than the tested no-adjustment alternative and maintains a declared longitudinal coordinate | A fixed mean does not prove absolute equality of the scale across eras |
| Start and end common shifts | Modelling and accounting judgement | The start shift handles membership change; the end shift absorbs net mass from unequal-\(K\) bouts | Common shifts preserve current differences but can contribute to displayed rating changes |
| No bout update without an eligible result | Modelling judgement | No fought-bout evidence supplies no measured direction or magnitude of individual change | The point estimate can remain unchanged while confidence in it becomes less secure |
| Point rating only | Modelling judgement and open question | Keeps the system transparent and close to ordinary Elo | No uncertainty-aware sumo comparator has been tested |
| Multiple observation stages | Reproducibility requirement | Pre-bout, day-end and basho-boundary states answer different publication needs | Every published value must identify its stage |

## Why begin in January 1989?

January 1989 is a practical evidence boundary. From that point, SumoDB contains
every banzuke and every bout between rikishi on the banzuke, providing the
complete input required by Elo-89.

This is a data boundary, not a discovered discontinuity in sumo. The earlier
record contains useful evidence, but its lower-division bout coverage is
incomplete. A model beginning earlier would therefore require a different
evidence policy.

Elo-89 therefore says that January 1989 is its modern evidence boundary. It
does not say that relevant competition began then or that an earlier-history
rating system cannot be constructed.

## Why retain the binary fought-result domain?

Elo-89 is intended to learn from eligible competitive results. A W/L pair
contains the evidence required by its binary update.

Fusen identify a winner and loser administratively, but not the outcome of a
fought bout under the same competitive process. Excluding them avoids silently
treating non-contest events as ordinary performance evidence. Other non-binary
outcomes likewise fall outside the two-outcome model.

This is principally a semantic modelling choice. The available work has not
shown by controlled comparison that every possible numerical treatment of
fusen is worse.

## Why \(q=400\)?

The value \(q=400\) gives rating differences the familiar Elo interpretation:
a 400-point advantage corresponds to an expected score of about 0.91 under the
model's logistic equation. Retaining a fixed scale also makes rating gaps and
the \(K\) schedule interpretable in stable units.

Calibration analysis found no compelling reason for a global change.
Apparent aggregate overconfidence was concentrated mainly in contests where an
immature rating faced a mature one. When both ratings had more supporting
evidence, calibration on the \(q=400\) scale was substantially better. A
global change might improve a weakly supported group while damaging mature
comparisons.

That supports retention, not optimality. Elo-89 has not been compared across a
comprehensive declared grid of \(q\) values or expectation curves.

## Why divisional \(K\)?

Lower-division ratings often belong to newer or more rapidly developing
rikishi and therefore benefit from faster adjustment. Upper-division ratings
usually have more accumulated evidence and can reasonably be less volatile.
Division is an observable proxy for these differences, not an individual
measurement of uncertainty or development.

Controlled retrospective comparisons found that divisional \(K\) modestly
improved both log loss and Brier loss relative to constant \(K\). The benefit
was appreciably smaller than the benefit of informed initialisation, but it
was consistent with the intended mechanism.

The comparison supports a variable-\(K\) policy. It does not show that
10/15/25/35 is uniquely or locally optimal, or that division is better than
direct experience, age, estimated uncertainty or another responsiveness
model.

When opponents have different \(K\) values, their updates are not zero-sum.
The resulting rating mass is small relative to membership effects, and the
end-of-basho common shift accounts for it exactly at active-population level.
That makes the consequence controlled, not nonexistent.

## Why use P1-WL?

Equal initialisation is simple only in notation. At the January 1989 boundary
it would assign an established Yokozuna and a low-ranked rikishi the same
state; later, it would ignore information already present in the banzuke when
a first rating is required.

P1-WL uses chii as limited starting evidence. It aims to place a first rating
nearer a useful part of the scale, reducing initialisation lag without forcing
subsequent ratings to remain aligned with the banzuke. Retrospective
comparisons show that informed initialisation materially improves proper
scores, especially for ratings with little bout evidence.

The qualification is important. P1-WL was estimated from the same historical
period in which many of its first ratings are evaluated. Later career evidence
therefore helped determine values used earlier in that period. These results
show retrospective usefulness and internal coherence, not unseen-data
validation. Low-support chii also remain less securely estimated than common
ones.

## Why hold P1-WL fixed?

P1-WL was fitted using eligible results through the September 2026 basho
and then fixed. Extending Elo-89 through later basho does not re-estimate it.

This boundary serves two purposes. It makes a release reproducible: the same
first-rating input is used whenever the same model version is named. It also
allows results from November 2026 onward to provide genuinely prospective
evidence about a prior which they did not help construct.

A later refit may eventually be justified, but it would create a new fitted
artifact and should be identified explicitly rather than treated as an
ordinary extension of the existing calculation.

## Why preserve the whole-population mean?

Equal-\(K\) Elo conserves rating mass within a bout. It does not prevent the
active mean moving when ratings are added to or removed from an open
population. Elo-89 therefore needs an explicit anchor if numbers printed at
different dates are to occupy one administered coordinate.

Retrospective comparisons found that whole-population mean preservation
improved both log loss and Brier loss relative to leaving the population
unadjusted. Basho-block analysis supported the direction of the log-loss
difference. The gain was concentrated among younger ratings, which is
consistent with the mechanism.

A common shift cannot change probabilities among the rikishi active when it is
applied. It does, however, change the coordinate they carry relative to fixed
P1-WL values used for later first ratings. This explains how an operation
which preserves current differences can affect later forecasts.

The policy is an administered anchor, not a theorem that average sumo ability
is constant. It makes longitudinal ratings interpretable conditional on the
declared population model; it does not independently prove absolute
cross-era equivalence.

## Why shift both before and after a basho?

The start shift corrects the active mean after membership changes. The end
shift removes the much smaller net mass created by unequal-\(K\) bout updates.
Both add one common value to every active rating, preserving current order,
rating gaps and matchup probabilities at the moment of application.

In the controlled analysis, the mean absolute adjustment was about 3.975
points per active rikishi at basho start and 0.040 points at basho end. The end
shift contributed almost no measured predictive improvement, but it closes
the accounting contract: every published basho-end active population has
exactly the target mean.

Common shifts are not irrelevant to reported individual changes. Positive and
negative contributions substantially cancel over time, and recent Makuuchi
and Juryo effects were small relative to ending ratings, but larger
low-division cases occur in the full history. The appropriate conclusion is
acceptance with disclosure, not that normalisation has no effect.

## Why does inactivity produce no bout update?

A rikishi on the banzuke remains in the active population even when he records
no eligible bout. His point rating receives the common population shifts but
no individual bout update. A stored rating outside the active population
receives neither kind of change.

This follows the principle that a rating changes in response to eligible bout
evidence. Inactivity may accompany injury, recovery, deterioration or no
material change, but inactivity alone does not quantify the direction or size
of any ability change. Automatic decay would insert a numerical claim not
supplied by the bout record.

An unchanged point estimate must not be mistaken for unchanged certainty.
Elo-89 has no separate uncertainty coordinate which can widen while the
estimate receives no new contest support. Whether such a state would improve
sumo forecasts remains an open empirical question.

## Why select by log loss?

Elo-89 attaches probabilities to binary outcomes, so candidate comparisons
used mean log loss calculated from forecasts made before the corresponding
results were processed. Log loss is a proper scoring rule and penalises
confident errors. Brier loss supplied a second proper-score check, while
calibration analysis examined whether nominal probabilities matched observed
frequencies in important subgroups.

Log loss was declared as the primary criterion before the candidate ordering
was inspected. That matters because no single summary dominates every
interpretive question. The selected model performed best on the declared
aggregate log-loss criterion and was supported by Brier loss, while calibration
and subgroup results supplied qualifications rather than universal victory.

The resulting claim is deliberately bounded:

> Elo-89 is the selected model among the tested candidates under the declared
> retrospective primary criterion, with supporting Brier evidence and recorded
> calibration qualifications.

It is not the true model of sumo or the winner of every possible evaluation.

## What evidence could change these decisions?

The most informative new evidence would include:

- prospective or rolling-origin results for the fixed P1-WL model;
- a declared \(q\) or expectation-curve comparison which protects the
  calibration of mature ratings;
- a responsiveness policy based directly on rating support or uncertainty,
  compared with divisional \(K\);
- an uncertainty-aware model which improves forecasts and communicates
  immature or inactive estimates more fully;
- an evidence-based model of how uncertainty, rather than assumed ability,
  changes during inactivity;
- a population anchor with clearer historical interpretation and equal or
  better predictive behaviour; or
- evidence that subgroup regressions are large enough to outweigh aggregate
  gains.

Until such evidence exists, the present choices are defensible rather than
final. Their status should remain attached to them: empirical selection where
comparison was performed, modelling judgement where it was not,
reproducibility requirement where the model must choose, and open question
where the evidence remains thin.

Chapter 11 critiques Elo-89 on those terms rather than requiring it to prove
claims it does not make.
