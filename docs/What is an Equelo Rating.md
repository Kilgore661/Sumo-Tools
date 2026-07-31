# What Is an Equelo Rating?

## Status

Foundational project explanation and draft public-facing methodology.

This document explains what the Sumo-Tools project means by an Equelo rating,
why an Elo-like model is a reasonable thing to apply to professional sumo,
which modelling choices require explicit justification, and what evidence
should be used to assess whether the system works.

Implementation-specific documents remain authoritative for the exact policy
used by a particular Equelo version. A published rating should always identify
the model version that produced it.

## Short answer

An Equelo rating is a numerical estimate of a rikishi's demonstrated
head-to-head strength, calculated from recorded bout results using a system
derived from Elo ratings. A higher rating means that the model expects the
rikishi to perform better against the same opponent.

Equelo is not a banzuke rank and is not intended to reproduce or predict chii
exactly. Chii reflect recent results, previous rank, and the structure and
conventions of the banzuke. Equelo summarizes a longer history according to a
fixed numerical procedure. A rikishi can therefore have the higher chii but
the lower Equelo rating.

That difference is not, by itself, an error in either ordering. It is also not
something the project should dismiss without investigation.

## What the number means

The important quantity is normally the difference between two ratings, not
either absolute number.

If rikishi A has rating \(R_A\) and rikishi B has rating \(R_B\), the model
converts

\[
R_A-R_B
\]

into an expected score. The greater A's rating advantage, the greater the
probability assigned to A winning their bout.

Consequently:

- a rating is a model estimate, not an observed fact;
- the ordering and differences carry the principal meaning;
- the absolute origin of the scale is conventional;
- adding the same constant to every rating ordinarily leaves expectations
  unchanged;
- ratings change as further results are observed.

"Rikishi A has an Equelo rating of 2000" is therefore shorthand for A's
position relative to the other ratings produced by that model version.

## Why use Elo-like thinking?

An Elo-like system has several attractive properties:

- every rated bout changes the participants' ratings by an explicit,
  reproducible rule;
- the change depends on how surprising the result was;
- repeated performance accumulates into a continuously varying estimate;
- rating differences have a direct probabilistic interpretation;
- the model is simple enough to inspect and explain;
- its predictions can be tested against subsequent bouts.

This does not establish that Elo is uniquely correct. Equelo is one
transparent and testable way of converting historical results into comparative
ratings. Alternative models may be better; they can be compared using
published data and predictive tests.

FIDE provides useful precedent rather than proof. It adopted Elo's system in
1970, but practical FIDE ratings are governed by maintained regulations rather
than by an untouched mathematical ideal. FIDE uses different development
coefficients for different player categories and has changed initialization,
rating floors, and other rules. In 2024 it also applied a one-off adjustment to
lower ratings in response to rating compression and deflation concerns.

This history shows that a useful real-world "Elo system" can contain explicit
policy choices and later corrections. It does not show that any particular
sumo adaptation is valid merely because chess uses something related.

Official background:

- [FIDE's history of Elo](https://www.fide.com/anniversary-of-arpad-elo-rating-system-that-changed-chess-world/)
- [FIDE rating regulations](https://handbook.fide.com/chapter/B022024)
- [FIDE's 2024 rating changes](https://www.fide.com/new-fide-rating-and-title-regulations-come-into-effect/)

## Fixed k and convergence

With a fixed \(k\), Elo ratings continue to move as results arrive. Even in an
artificial closed population whose abilities never change, a computed rating
does not normally settle permanently at one final value. It fluctuates within
a distribution determined by the abilities, schedule, model parameters, and
random results.

That is a limitation on claims that Elo eventually discovers a permanent
"true rating". It is not necessarily a defect for sumo. In the real sport:

- ability changes;
- injury and recovery matter;
- rikishi enter and retire;
- the opponent graph changes;
- recent evidence should affect the estimate.

The practical question is not whether a rating eventually stops moving. It is
whether the system produces useful, calibrated, and reasonably stable
estimates of comparative performance.

## Sumo-specific modelling choices

Plain Elo does not decide what a sumo rating should do with absence, missing
history, changing divisions, or banzuke structure. Those are model-definition
questions. They should be visible rather than hidden in implementation.

### What counts as a bout?

If Equelo estimates performance **when a contest occurs**, then ordinary bouts
count while fusen and opponentless absences need not. An absence supplies no
observed head-to-head result.

If Equelo instead measures broader **competitive effectiveness**, including
availability, an absence may attract a penalty.

Neither interpretation follows automatically from Elo. Treating an absence as
a loss, especially a loss to a hypothetical equally rated opponent, is a
sumo-specific policy rather than an observed contest. If both interpretations
are published, they should have unambiguous names and one should be designated
as the standard Equelo rating.

### Initialization

A new rikishi must enter the system somewhere. A constant initial rating is
transparent but initially imprecise. A rank-based initial rating uses more
information but makes chii part of the rating model.

The selected policy and its consequences should be published. The extent to
which mature ratings retain memory of initialization is an empirical
sensitivity question, not something to assume away.

### Persistence and missing observations

A persistent system keeps a rikishi's previous rating when the rikishi is not
represented in the available results and reuses it upon a later appearance.
This avoids repeatedly pretending that a previously observed rikishi is
completely unknown.

Long gaps make the retained estimate less credible. Plain Elo has no rating
deviation or time-decay mechanism with which to express that uncertainty. A
future Glicko-2 or dynamic Bayesian model could treat this more explicitly.

### Population change and inflation control

The absolute origin of an Elo scale is arbitrary, but entrants, departures,
unequal \(k\) values, missing records, and the choice of rated contests can
change the population mean.

An Equelo implementation may anchor or normalize the mean at defined
boundaries. A uniform shift within a population preserves all rating
differences in that population, but the complete policy can still have future
effects when previously absent rikishi return with persistent ratings.
Normalization is therefore both a scale convention and a modelling policy.
Its scope, timing, and target must be stated.

## Equelo and chii

Chii and Equelo are related but not interchangeable. Both are ordered and both
respond to performance, so broad agreement is expected. Chii also depend on
recent records, previous rank, promotion and demotion practice, available
positions, and banzuke structure. Equelo applies one numerical rule to a
longer sequence of recorded bouts.

A higher-chii rikishi having a lower Equelo rating is not by itself an error.
It means that the official ordering and Equelo's accumulated-performance
ordering differ in that case. The difference may be understandable from recent
results or banzuke constraints, but Equelo does not currently claim to explain
every such case.

The two natural conversion questions remain legitimate statistical questions:

\[
E[R\mid C=c]
\]

asks for the mean rating observed at chii \(c\), while

\[
P(C=c\mid R\text{ is near }r)
\]

asks which chii are empirically associated with a rating range. Neither
requires a deterministic one-to-one conversion. Each should be accompanied by
its distribution, support, and uncertainty.

Chii should not be dismissed as merely traditional cultural annotations. They
are official institutional rankings with considerable performance and
predictive information. Equally, exact agreement with chii is not an Equelo
objective.

The appropriate position is:

- one individual disagreement is not proof that Equelo failed;
- exact agreement is not required;
- persistent or systematic disagreement is still a valuable diagnostic;
- unexplained disagreement may reveal a modelling weakness, a structural
  banzuke effect, or a genuine difference between accumulated strength and
  official rank.

## The lower-maegashira problem

Across most of the banzuke, mean Equelo-like rating declines as chii worsens.
Literal lower-maegashira ranks are an exception in the clean 1989+ experiment:
the mean curve turns upwards after approximately M12.

Expressing ranks by their actual distance from the Makuuchi--Juryo boundary
removes the broad endpoint reversal, showing that historically variable
banzuke structure explains an important part of the effect. Smaller local
irregularities remain, and their precise cause has not yet been established.
Successively deleting lower-maegashira bouts without replacement also failed
to produce a monotonic retained literal-rank curve for any tested cutoff from
M18 through M12.

This finding should not be hidden behind a smoothed conversion table. It is an
open diagnostic question. The detailed research record is in
[`src/analysis/clean_elo/docs/Rating Probe Findings.md`](../src/analysis/clean_elo/docs/Rating%20Probe%20Findings.md).

## What would show that Equelo works?

"It works as well as FIDE" is not meaningful until "works" is defined. Equelo
should earn trust through published criteria:

- higher-rated rikishi win more often at approximately the probabilities
  predicted;
- predicted probabilities are calibrated;
- the system predicts held-out bouts better than simple alternatives;
- reasonable initialization and \(k\) policies do not radically change mature
  ratings;
- known data gaps have measured rather than concealed effects;
- implementation and model-version changes are reproducible.

Agreement with chii is a useful secondary sanity check, not the principal
validation target. A model should not be tuned merely until its ratings match
the institutional ordering that it is intended to complement.

## Project position

Equelo is not claimed to be the uniquely correct measurement of sumo ability.
It is a transparent, reproducible, and testable estimate of comparative
performance. Its modelling choices should be published, its disagreements
with the banzuke should not be concealed, and better-supported alternatives
are welcome.
