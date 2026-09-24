# Elo89a: Absence-Penalised Illustrative Variant

**Status:** Parked idea, 24 September 2026. This document records the proposal
and the difficulties identified in discussion. It is not an agreed model,
implementation plan or publication decision.

## Why record the idea?

Elo89 deliberately treats a missing appearance as no new head-to-head evidence.
A rikishi who remains on the banzuke retains his rating, subject to the common
population shifts applied by Elo89. This is a defensible account of performance
conditional on fighting, but it does not reflect availability.

The recurring alternative is: why not treat a no-show as a loss?

An absence-sensitive variant could illustrate the difference between two
questions:

- **Elo89:** how has the rikishi performed in represented contested bouts?
- **Elo89a:** what would an availability-adjusted account look like if missed
  scheduled appearances attracted a rating charge?

Elo89 would remain the project's selected and primary rating model. Elo89a, if
ever produced, would be an explicitly illustrative counterfactual rather than
an equally validated replacement.

## The simplest proposed charge

An opponentless absence is not literally an Elo loss: there is no opponent and
therefore no opponent rating or matchup expectation. A simple convention is to
charge

\[
\frac{K}{2}
\]

for each absence. This is numerically equivalent to losing to a hypothetical
equally rated opponent. A rikishi with \(n\) such absences would receive the raw
adjustment

\[
-\frac{nK}{2}.
\]

This should be described as an **availability charge**, not as an observed bout
result. The equal-rating assumption is a transparent convention, not a fact
about the missing opponent.

Under Elo89's current divisional K schedule, a complete absence would have
different raw effects at different ranks:

| Position | K | Expected appearances | Raw complete-absence charge |
|---|---:|---:|---:|
| Sanyaku | 10 | 15 | -75 |
| Maegashira | 15 | 15 | -112.5 |
| Juryo | 25 | 15 | -187.5 |
| Below Juryo | 35 | 7 | -122.5 |

The idea of charging availability can be applied consistently while the
numerical charge remains rank-dependent because Elo89's K policy is
rank-dependent. Whether that is desirable would need explicit consideration.

## What the available results establish

Three cases should not be conflated.

### Recorded fusenpai

A recorded fusen has a known winner and loser. If Elo89a rated it, it could use
the two recorded participants and the ordinary expectation calculation. It
would not need the opponentless \(K/2\) convention. Care would be needed not to
charge the same missing appearance again as an absence.

### Sekitori absence

Makuuchi and Juryo rikishi are scheduled for one appearance on each of the 15
days. Given a complete results record, a day on which a banzuke rikishi has no
recorded appearance is a definite absence. Its chronological position is
known, so an availability charge could be inserted on that day.

This is the strongest available case for Elo89a. It would, for example, make
the ratings of repeatedly absent yokozuna fall and thereby illustrate a notion
of competitive effectiveness that includes availability.

### Sub-sekitori shortfall

Below Juryo a rikishi normally has seven scheduled bouts but is not scheduled
on a known set of seven calendar days. A daily non-appearance is therefore not
evidence of absence. At the end of a complete basho, fewer than seven recorded
appearances may support an aggregate absence count, provided that source-data
completeness has first been established.

The timing and opponent remain unknown. Applying the aggregate charge after
all recorded bouts is not equivalent to a chronological Elo replay: had the
charge occurred earlier, it could have changed expectations and updates in
later contested bouts. This is the principal objection to extending Elo89a
below Juryo. A sekitori-only variant is asymmetrical across the banzuke, but a
whole-banzuke variant would introduce timing assumptions unsupported by the
available data.

## Where do the lost points go?

An opponentless charge removes rating mass without awarding it to an opponent.
If total raw absence charges in a basho are \(P\) and the active population has
\(N\) members, Elo89's existing post-basho whole-population mean preservation
would add approximately

\[
\frac{P}{N}
\]

to every active rikishi. In the single-absentee case, the absentee therefore
receives \(-P + P/N\), while every other active rikishi receives \(P/N\).

Thus the existing policy already provides a post-basho answer: the removed
mass is redistributed across the whole active population by a common shift.
It is not distributed solely among the other rikishi, because the absentee
also receives the common shift. With several absentees, a lightly penalised
rikishi could receive more through the common shift than his own direct charge.

This interaction is not incidental. Elo89a would combine an individual
availability charge with a population-wide redistribution. If the model
charged sekitori only, some of the resulting mass would still be redistributed
to lower-division rikishi under the current whole-population policy.

Possible alternatives include redistribution only among other rikishi,
redistribution within the sekitori population, use of a separate rating-mass
reservoir, or no restoration of the removed mass. Each alternative changes the
meaning and dynamics of the model. Daily redistribution would also change
subsequent within-basho forecasts, whereas Elo89's existing post-basho
normalisation does not. Exploring all plausible opponent and redistribution
rules quickly becomes a large modelling programme.

## The tempting path towards an opponent model

It would be possible to estimate distributions of likely opponents for a
rikishi's first, second or \(d\)-th scheduled bout, perhaps conditional on chii,
division, basho stage or rating. An absence could then be charged against an
expected opponent rather than an equally rated hypothetical opponent.

This would require choices about cohorts, eras, schedules, promoted or
demoted wrestlers, cross-division bouts, and whether the opponent distribution
should itself depend on Elo89 or Elo89a. It would replace one transparent
convention with a substantial secondary model. No such model is proposed here.

The present judgement is that this path is disproportionate to the illustrative
purpose of Elo89a.

## A simpler end-of-basho snapshot

A materially simpler alternative is not to construct a persistent Elo89a
replay at all. Elo89 would run unchanged and remain the only state carried into
the next basho. At the end of each completed basho, the site could derive a
second, temporary set of values by subtracting the current basho's availability
charges from the canonical Elo89 end ratings.

For a rikishi with \(n\) absences, the displayed adjustment would be

\[
-\frac{nK}{2}.
\]

The interpretation would be conditional and local: assume that an absent
rikishi was injured, assume that he would have lost had he appeared, and assume
that the average such loss costs \(K/2\). The resulting value would answer
something like, "What would this basho-end snapshot look like if we applied an
illustrative charge for this basho's missed appearances?"

The adjusted values would not:

- feed into later bout expectations or updates;
- persist into the next basho;
- represent accumulated career-long absence penalties; or
- constitute a second Elo replay.

This avoids the unknown-opponent problem affecting subsequent Elo updates and
avoids choosing who receives the removed points. More precisely, let \(R_i\)
be rikishi \(i\)'s canonical, mean-preserved Elo89 end rating and let \(p_i\)
be his current-basho availability charge. Display

\[
A_i = R_i - p_i.
\]

This is algebraically equivalent to deducting the charges from the raw
post-results ratings and then applying the same common shift that the canonical
Elo89 run calculated without those charges. The shift must not be recalculated
from the adjusted values: doing so would redistribute the removed mass and turn
the display back into a population-policy experiment.

The adjusted snapshot consequently remains on the familiar Elo89 origin while
its mean is allowed to fall according to the amount of absence in that basho.
It should be presented beside the canonical Elo89 values as a within-basho
illustration, not as an independently anchored scale for comparisons between
different basho or eras. A less convenient alternative would be to show both
canonical and adjusted values before the ordinary post-basho shift; their
pairwise difference would be the same.

The data boundary still matters. A sekitori snapshot can use known missing
daily appearances. An extension below Juryo would still rely on an aggregate
shortfall from seven and on evidence that the result record is complete, but
the unknown timing would no longer affect later updates because the adjustment
is applied only after the replay is finished.

Recorded fusen would need an explicit display rule. One coherent choice would
count the fusenpai day among the missed appearances and apply the same \(K/2\)
availability charge, without treating it as a contested Elo bout. This would
keep the snapshot focused on availability rather than introduce a separate
opponent-sensitive fusen policy.

This snapshot appears more tractable and easier to explain than persistent
Elo89a. It is better regarded as a derived statistic or sensitivity view than
as a rating model. A label such as **Elo89 with current-basho availability
charge** would communicate more than the model-like name Elo89a.

The seductive extension is to carry each adjusted value into the next basho.
Once that is done, the charge changes later expectations and bout updates, its
missing rating mass interacts with normalisation, and the unknown timing and
opponent questions return. That persistent extension is the Elo89a problem
parked in the rest of this document, not a straightforward enhancement of the
snapshot.

## Possible publication shape

If the idea is resumed and survives investigation, the clearest presentation
may be two builds from one implementation:

1. the canonical Elo89 site; and
2. a clearly labelled Elo89a illustrative site.

The Elo89a site could reuse the layout and model-independent material while
substituting its own rating artifacts, explanations and persistent warning that
availability charges are applied only where the evidence and selected policy
permit them. The implementation should be shared; the source site should not be
forked and maintained twice.

A separate comparison component could consume both artifact sets and show
paired career trajectories, rating differences, peak and current-rank changes,
and examples grouped by absence history. It should distinguish:

- contested-bout movement;
- recorded-fusen movement;
- opponentless availability charges;
- pre-basho normalisation; and
- post-basho normalisation.

Without that accounting, an always-present rikishi's gain through population
redistribution could be mistaken for new individual performance evidence.

## Minimum work before publication

Illustrative status would reduce the burden of establishing Elo89a as a
replacement for Elo89, but it would not remove the need for basic assurance.
A resumed investigation should at least:

1. define exactly which appearances count as absences and audit source
   completeness;
2. decide whether recorded fusen are rated and prevent double charging;
3. choose sekitori-only or explicitly accept the non-chronological
   sub-sekitori convention;
4. specify the charge, its K dependence and its position in the daily replay;
5. retain a ledger separating direct charges from normalisation;
6. measure whole-population and divisional redistribution effects;
7. inspect extreme individual careers, returns and peak ratings;
8. test sensitivity to plausible alternative charges;
9. compare predictive performance on later contested bouts without pretending
   that opponentless charges are observed head-to-head forecasts; and
10. document incomplete and live-basho behaviour.

The cleanest first experiment would hold Elo89's P1 prior, q, K schedule and
population policy fixed and change only the treatment of absence. Rebuilding
P1 with absence charges would entangle the question with the prior
fixed-point construction and should not be the starting point.

## Current conclusion

The basic idea is intelligible and potentially illuminating, especially for
sekitori whose Elo89 ratings remain high during long absences. It is not a
straightforward extension of Elo. Opponentless charges, incomplete
sub-sekitori scheduling information, divisional K values and mean preservation
all introduce substantive policy choices.

For now the idea is parked. Elo89 remains the selected rating model. A future
investigation should begin from this note rather than from the apparently
simple question, "Why don't we penalise no-shows?"

## Existing relevant material

- [`docs/What is an Equelo Rating.md`](../../../docs/What%20is%20an%20Equelo%20Rating.md)
  distinguishes performance conditional on contests from broader competitive
  effectiveness including availability.
- [`src/analysis/clean_elo/simulate.py`](../clean_elo/simulate.py) contains an
  earlier experimental `count_absences` implementation. Its terminology and
  mechanics are prior work, not the specification of Elo89a.
- [`src/analysis/elo89/replay.py`](../elo89/replay.py) is the production Elo89
  replay whose policies would remain canonical.
- [`src/analysis/docs/story/22 Elo-89 Rating System Appraisal.md`](story/22%20Elo-89%20Rating%20System%20Appraisal.md)
  records the reasons for retaining Elo89's present no-new-evidence treatment
  of inactivity.
