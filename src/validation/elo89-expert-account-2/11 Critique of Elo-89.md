# 11. Critique of Elo-89

## The standard of criticism

Elo-89 should be judged against the purpose stated in Chapter 3: a
reproducible, opponent-sensitive numerical account of changing bout-winning
strength from January 1989 onward. It is not a numerical banzuke, an injury
report, a measurement of physical ability in isolation or a complete
definition of greatness.

On that narrower standard, Elo-89 is credible. It led the declared
retrospective comparison, its rules are explicit, and its visible complexities
answer real problems of initialisation and open populations. Those successes
make critique more exacting, not less necessary. A useful model can still
misrepresent uncertainty, depend on historically fitted assumptions and work
unevenly across populations.

The criticisms below ask four different questions:

1. What does the model necessarily leave out?
2. Where has the omission or policy produced a measured weakness?
3. Is the appropriate response disclosure, further research or acceptance of
   a trade-off?
4. Which conclusions remain safe while the issue is unresolved?

## Criticism register

| Issue | Present evidence | Current disposition |
| --- | --- | --- |
| One scalar state | Structurally cannot express persistent non-transitive or context-specific effects; their size in sumo is unmeasured | Research question and interpretation limit |
| No individual uncertainty state | Ratings with very different support can have the same value; calibration work shows that rating maturity matters | Deliberately outside the point-rating model; open comparative question |
| Divisional \(K\) is a coarse proxy | Small aggregate improvement, but the exact schedule was not optimised and boundary evidence is thin | Accepted trade-off and research question |
| P89 is future-informed within its fitting period | Results through September 2026 helped construct the table used within that history | Disclosure; evidence was frozen on 30 October 2026 and the selected artifact was promoted on 8 November |
| Sparse and high-churn lower ranks | Fewer observations, irregular prior shapes and the largest normalisation contributions | Qualified interpretation and further research |
| Population normalisation affects displayed changes | Contribution audit found generally modest effects relative to ending ratings but potentially material effects on particular changes | Accepted with disclosure |
| Fixed global mean does not stabilise every chii | Measured rank-specific movement and reversals through time | Limits cross-era and rank-level interpretation |
| Inactivity leaves support less current | Elo-89 retains a point estimate but has no uncertainty state which can widen without new bouts | Interpretation limit and open comparative question |
| Selective schedule and connectivity | Sumo bouts are not random; subgroup and toy evidence show uneven support | Limit claims to the observed matchup network |
| Retrospective model selection | The model and first-rating table were selected using history through September 2026 | Major evidence qualification; genuinely later results provide prospective evidence |

## 1. One number may not be enough

Elo-89 represents each active rikishi by one scalar rating. The difference
between two ratings is sufficient for its forecast. This is powerful
compression, but it imposes a transitive ordering of favourites and treats
everything not represented by that ordering as residual variation.

If A has a persistent advantage over B, B over C and C over A because of style,
body type or another matchup interaction, no scalar can represent all three
tendencies. Injury, tactical change, stable-specific preparation and
tournament situation are likewise absent. The model cannot distinguish a
random upset from evidence of one of those omitted effects. Both appear as an
unexpected result and generate the same kind of update.

This is a structural criticism, but its practical size is unknown. No
systematic residual-interaction study with out-of-sample protection has been
conducted. Memorable head-to-head records and sumo narratives do not establish
a stable effect. The defensible conclusion is conditional:

> Elo-89 is a selected one-dimensional account of sumo performance. It has not
> established that one dimension captures every predictively useful feature.

A richer model would earn its complexity only if its contextual terms improve
later forecasts or another declared measurement objective.

## 2. A point rating conceals how well it is known

Two rikishi can have the same Elo-89 rating when one value rests on hundreds
of eligible bouts and the other is principally a P89 first rating. The
printed number contains no confidence interval, rating deviation, effective
sample size or age-of-evidence measure.

This is not the same as uncertainty about the next bout. A 60% matchup
probability already allows either result. The missing quantity is uncertainty
about whether the two point ratings support that 60% estimate securely.

Retrospective calibration work on closely related candidates found materially
weaker calibration when an immature rating faced a much more established one.
That is evidence that rating support matters, although it is not a direct
measurement of uncertainty in the final P89 model.

P89 reduces initial weakness but cannot solve it. It supplies a better point
before personal evidence accumulates; it does not say how uncertain that point
is. Nor does Elo-89 widen uncertainty during inactivity. Retaining a point
estimate without inventing a decline is defensible, but presenting it as
equally well supported would be stronger than the model justifies.

An uncertainty-aware Elo-family model is therefore a useful possible
comparator. Glicko-like systems belong among the open subjects for research,
alongside alternative responsiveness, matchup structure and population
anchoring.

## 3. Divisional \(K\) is useful but crude

The 10/15/25/35 schedule lets lower-division ratings move more quickly and
upper-division ratings move more slowly. Controlled comparison found a small
aggregate benefit, so this is not merely decorative complexity.

Nevertheless, division is a blunt proxy. A long-serving Makushita rikishi and
a rapidly rising rikishi receive the same \(K\); a newly promoted Juryo rikishi
changes \(K\) at a categorical boundary even though his evidential support did
not change discontinuously. The schedule does not respond directly to bout
count, recency, estimated volatility or uncertainty.

Cross-\(K\) bouts also cease to be zero-sum. The population correction handles
the resulting mean accounting, but it does not prove that both participants
had the right responsiveness. Cross-boundary bouts are a small and relatively
weakly supported subgroup, so their evidence does not determine a clearly
better alternative.

The appropriate verdict is not that divisional \(K\) failed. It improved the
declared aggregate scores. The inclusion of variable \(K\) has better evidence
than the exact boundaries and values through which it is implemented.

## 4. P89 imports the banzuke and future information

P89 addresses a real weakness in equal initialisation. It also changes the
epistemic character of the model.

First, P89 uses chii as evidence. Elo-89 is therefore not wholly independent
of the banzuke when a first rating is assigned. This does not make later
ratings numerical copies of rank: bout results subsequently move individuals
freely. It does mean that early agreement between rating and chii is partly
constructed and cannot validate the first-rating table independently.

Second, the table was fitted using history through September 2026, including
the broad period in which it is retrospectively evaluated. Later career
results within that period help determine values used for earlier first
ratings. The comparison can show internal usefulness and reject poor
constructions, but it is not an unseen-future test. The table was fixed on 30
October 2026, so results from November 2026 onward cannot alter it.

Third, P89 is a population average indexed by chii. Individuals at the same
chii can differ greatly, especially in high-churn lower divisions where a rank
can mix long-term lower-division rikishi, rapidly rising talent and careers
with very little bout evidence. A useful average can still be a poor
first estimate for a particular person.

P89 is therefore best understood as a historically fitted regulariser. It is
more useful than equal initialisation in the tested history, but it should not
be presented as the ability naturally belonging to a rank.

## 5. The lowest ranks remain the least secure

Elo-like ratings acquire meaning through a connected network of persistent
competitors. Jonokuchi and low Jonidan have high churn, short records, rapid
risers, weak long-stayers and historically changing banzuke depth. Many
careers supply few eligible bouts before their ratings can become mature.

The P89 rank curve is not strictly monotone. Most reversals, including the
largest, occur among sparsely supported lower chii, but reversals are not
confined to them. They may reflect real population mixtures, changing banzuke
structure, sparse support, model failure or several of these at once. Silently
smoothing the curve would hide the evidence; treating every reversal as a
discovery about sumo would overinterpret it.

The lowest-division normalisation results are also the least reassuring. In
the full-history 12-basho contribution study, all 219 observations outside the
author's ±5% practical band belonged to Jonidan or Jonokuchi.

Current inclusion is a pragmatic judgement. It allows broad career histories
to be included and makes model strain visible. Claims at the bottom of the
banzuke should nevertheless be weaker, and experiments on churn,
connectivity, alternative cut points and later sekitori performance remain
justified.

## 6. Normalisation is invisible in a gap but visible over time

At the instant a common shift is applied, every active rating gap, ordering
and Elo probability is unchanged. It is therefore tempting to call
normalisation cosmetic. That is incomplete for two reasons.

First, later first ratings come from fixed P89. A shifted incumbent
population has different gaps from those later ratings, so subsequent
forecasts and updates can differ.

Second, published individual rating changes include every common shift
received while active. A displayed increase is not necessarily the sum
of positive bout evidence. In May 1992, for example, Konishiki's recorded bout
contribution was about -26.1 points and his normalisation contribution about
+30.4, producing a displayed increase of about +4.2.

The contribution audit prevents exaggerating this criticism. Across all 51
recent sliding 12-basho windows, every eligible Makuuchi and Juryo observation
had a net normalisation contribution within ±1% of ending rating. Across the
full history, every Makuuchi and Juryo observation was within ±5%. Positive and
negative shifts substantially cancel.

Those percentages use the chosen rating origin and are practical benchmarks,
not probability-invariant measures. Nor does subtracting the recorded shifts
simulate a counterfactual model without normalisation, because later bout
updates would also change.

The accepted conclusion is proportionate: normalisation does not presently
undermine the usefulness of Elo-89, but rating-change products must not
describe their values as wholly bout-derived.

## 7. A fixed population mean does not fix historical meaning

Elo-89 holds one global active-population mean constant. That controls one
coordinate, not the composition, schedule or rating distribution within the
population.

The per-chii drift study makes the distinction concrete. Among 382 numbered
groups with at least 60 basho observations over ten years, full-history
post-basho slopes ranged from -104.5 to +92.3 points per decade. M1 period
means rose from about 2,293 in 1989--1993 to 2,512 in 2004--2008 and were about
2,452 in the partial 2024--2026 period. Y1 rose from about 2,515 to 2,939 and
then fell to about 2,633 across the corresponding periods.

These movements are not estimates of causal inflation. Occupants, banzuke
depth, division sizes, schedules and support change over time; Hakuho alone
accounted for 22.1% of the Y1 observations. A single linear slope can also
conceal rises and reversals.

The finding is nevertheless important: identical chii and identical printed
ratings do not acquire timeless meaning merely because the global mean is
fixed. Cross-era comparisons are model-conditional comparisons within an
anchored changing population, not direct measurements against an external
constant standard.

## 8. Inactivity leaves uncertainty unmodelled

A rikishi who remains in the active population but records no eligible bout
receives the common population shifts but no individual bout update. A stored
rating outside the active population receives neither kind of change. Calendar
time by itself does not alter the point estimate.

This embodies the principle that absence of competition supplies no new
directional bout evidence. Inactivity may accompany injury, recovery,
deterioration or no material change, but it does not quantify the direction or
size of an ability change. Automatic decay would insert a numerical claim not
supplied by the eligible bouts.

The unresolved issue is evidential support. An old point estimate need not be
as securely informative as a recent one, and physical change may occur without
being observed by the result stream. Elo-89 has no uncertainty coordinate
which can widen during such a period. Uncertainty-aware state evolution,
partial shrinkage and evidence-based time models remain possible alternatives,
but none has yet been shown to improve sumo forecasts.

## 9. The observed schedule limits what has been learned

Elo-89 adjusts for the strength of opponents actually faced. It does not turn
sumo into a random round robin.

Torikumi are strongly structured by division and rank and can react to results
within a basho. Unscheduled matchups provide no direct evidence. A connected
path through the bout graph can identify a relative coordinate in principle,
but sparse bridge bouts may leave that relationship weakly supported.

This matters most when extending claims across divisions, distant ranks or
eras. One audit found only 2,533 sekitori--sub-sekitori cross-boundary bouts in
a 574,863-bout comparison domain. Toy experiments show that realistically
shaped bridges can identify a divisional offset in controlled worlds; they do
not establish that every historical comparison in the real network is equally
secure.

The rating is consequently opponent-sensitive, not schedule-free. It
describes performance through the matchups sumo supplied and relies on the
scalar model when extrapolating beyond densely observed regions.

## 10. Validation remains retrospective

Across the history from January 1989 onward, retrospective evaluations
consistently gave Elo-89 lower log and Brier loss than a neutral 50--50
forecast. The current contract also led the declared proper-score comparisons
used to select its main policies. The model therefore contains genuine
predictive information about the eligible results.

That evidence is retrospective. P89 was fitted using the broad period being
scored, and the population policy and diagnostics were developed after
extensive inspection of the same historical system. Bootstrap intervals
quantify sampling variation conditional on that process. They do not undo
information reuse or account for every researcher choice.

The evidence boundary for the model and P89 table was fixed on 30 October
2026; the selected epsilon-8.5 artifact was promoted on 8 November without
using later results. The strongest next validation is therefore to score
genuinely later basho without changing them.
Rolling-origin experiments could supply additional historical evidence if the
first-rating table and every model choice were reconstructed using only
information available at each origin.

The absence of prospective evidence does not erase the retrospective result
or prohibit publication. It limits the strength of claims such as “validated
probability” and leaves open how well the measured advantage will persist.

## What needs disclosure or further research?

### Disclose

- P89 is future-informed within the retrospective fitting period through
  September 2026 and fixed thereafter.
- A rating is a point estimate whose support varies by rikishi and date.
- Rating changes include population adjustments.
- Cross-era comparisons depend on the fixed anchor and changing population.
- Lower-rank and cross-boundary interpretations have weaker support.
- Inactivity produces no individual bout update, and uncertainty does not
  widen explicitly.

### Further research

- uncertainty-aware or support-dependent updates;
- matchup and contextual residuals;
- responsiveness policies more individual than division;
- lower-rank churn, connectivity and cut-point sensitivity;
- uncertainty evolution during inactivity;
- prospective or rolling-origin evaluation; and
- population anchors with clearer historical interpretation.

Normalisation is not presented as a defect requiring correction. Its effects
have been investigated and accepted with disclosure. Nor is the absence of an
injury penalty such a defect: adding one without evidence would replace one
limitation with an unsupported story.

## Overall assessment

Elo-89 is a disciplined exploration of an Elo-like point-rating model, not a
definitive theory of sumo strength. It succeeds at the central tasks for which
it was built: turning unequal pairwise results into a changing
opponent-sensitive scale, making probabilistic forecasts and exposing a
reproducible modern history.

One deliberate limitation is that one point cannot express both strength and
uncertainty. Whether a Glicko-like system improves on that limitation is an
open question, as are the other possible extensions considered here. Its most
important evidential limitation is retrospective selection with a first-rating
table which is future-informed within its fitting period. Its most important
interpretive limitation is that a fixed global mean does not create an
external timeless standard.

Those conclusions justify qualified use and continued investigation, not the
claim that the model has failed. Chapter 12 now separates more formally what
has been established from what remains assumption, judgement or open question.
