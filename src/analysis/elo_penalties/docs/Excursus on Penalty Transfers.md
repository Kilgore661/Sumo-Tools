# Excursus on Penalty Transfers

## Status

Deferred context for a possible future Elo-89 non-appearance model.

This document preserves a secondary modelling issue. It does not propose
changing production Elo-89 or treat the existence of recoverable absence
evidence as sufficient reason to use it in ratings. The separate
`Non-appearance Penalty Experiment Proposal.md` now specifies an isolated
experiment using deduction followed by normalisation.

## Terminology

This account uses **non-appearance** as the umbrella term for a rikishi not
competing when a result or expected opportunity would otherwise occur.

It reserves two narrower terms:

- **fusen-pai** (`FP`): the rikishi was named on the published torikumi but did
  not appear; the named opponent receives fusen-sho (`FS`); and
- **absence**: the rikishi was omitted from the torikumi because the withdrawal
  was known before it was prepared, so the final record contains an `A` rather
  than a loss.

Other project documents sometimes use *absence* for the wider concept. The
restricted meaning above governs this document.

## The motivating penalty

Ordinary Elo treats an unplayed game as supplying no new information. That is
a coherent interpretation when a rating estimates performance conditional on
the contest taking place.

A possible sumo-specific model could instead treat non-appearance as evidence
that the rikishi's current ability to compete is diminished, commonly through
injury. Such a model might deduct a quantity

\[
\lambda(R, C, t, \ldots)
\]

from the non-appearing rikishi, where the penalty may depend on rating, chii,
divisional `k`, time or other declared information. The simple example
`lambda = divisional_k / 2` has the interpretation of losing to a hypothetical
equally rated opponent, but it is only one candidate policy.

Making `lambda` a function of ratings is compatible with rejecting a special
reward for the fusen-sho recipient. Those are separate choices: the absent
rikishi's inferred loss of competitive effectiveness need not be evidence that
the named opponent demonstrated additional skill.

## Why direct transfer is attractive

If a penalty is deducted from one rating and credited in full to another, the
event conserves rating mass. No population-level compensation is required.
This is mathematically attractive because the update is self-contained and
does not move unrelated ratings.

An ordinary scored FP/FS pair could provide such a transfer: calculate the
loser's opponent-relative Elo deduction and give the corresponding amount to
the named opponent. This would treat the fusen-sho recipient as the beneficiary
of the update.

That interpretation is not presently supported. The named opponent displayed
no winning skill in an unperformed bout. Although availability could itself be
defined as part of skill, this project has not adopted that conception. The
existence of a convenient recipient is not sufficient justification for
crediting them.

## The opponentless-absence problem

An absence has no published opponent. Even if the model can determine that a
non-appearance occurred and calculate a rating-dependent deduction, the record
does not identify a particular rikishi to receive it.

Possible transfer rules would therefore add policy rather than recover an
observed fact. Examples include:

- crediting a hypothetical opponent and discarding that synthetic rating
  afterwards;
- crediting a division or population pool;
- distributing the deduction among rikishi who actually competed;
- distributing it among the complete active population; or
- selecting a representative opponent by an estimated scheduling model.

Each choice changes the meaning and dynamics of the rating system. None follows
from Elo or from the historical record merely because it preserves total rating
mass.

## What the SumoDB record does and does not prevent

The original practical reason for ignoring fusen and absences was the apparent
inadequacy of the daily record, especially below Juryo.

A sekitori normally has one bout opportunity per day. A missing daily result
can therefore ordinarily be interpreted as an absence. A sub-sekitori rikishi
normally fights only once in each of seven scheduling windows across the
15-day basho. Most daily `-` entries are ordinary unscheduled days, so an
individual dash cannot by itself distinguish availability from absence.

The research in `src.analysis.absences` changes the assessment of this block.
SumoDB supplies both:

- the final number of absences in the rikishi's `W-L-A` record; and
- the dated pattern of contested results, FS and FP outcomes.

Assuming the JSA's normal seven-window scheduling model applies, occupied and
empty windows can sometimes locate all recorded absences at window resolution.
For example, if a sub-sekitori rikishi has one recorded absence and exactly one
otherwise empty scheduling window, that window can be assigned as the absence.

The inference remains conditional and sometimes ambiguous. It does not recover:

- the exact day within a two- or three-day window;
- the opponent the rikishi would have faced;
- the reason for the absence;
- a counterfactual torikumi; or
- certainty where more empty windows exist than recorded absences.

The important revised conclusion is therefore:

> SumoDB's daily dashes do not make sub-sekitori absences wholly unknowable.
> Under a declared scheduling assumption, the existing record can often
> identify their scheduling windows. The remaining obstacle to a direct
> penalty transfer is principally the absence of an observed or recoverable
> opponent, not a general inability to identify non-appearance.

The empirical authority for that conclusion remains the `absences` package,
especially `docs/On Absences.md` and the `jsa_check` experiment. A future
penalty model should consume an explicit inference result from that package,
not recreate an informal dash-counting rule.

## Deduction followed by Elo-89 normalisation

Elo-89 already restores the active-population mean after each basho. If total
non-appearance penalties of

\[
L = \sum_i \lambda_i
\]

are applied before that step to an active population of size `N`, the existing
normalisation adds `L/N` to every active rating. Rikishi `i` therefore receives
the net change

\[
-\lambda_i + \frac{L}{N},
\]

while an unpenalised rikishi receives `L/N`.

No additional compensation step is needed. Normalisation acts as an implicit
transfer of the deducted mass across the active population. Relative to every
unpenalised rikishi, a rikishi penalised by `lambda_i` loses exactly that amount
when no other distinction is introduced by the policy.

This avoids inventing a particular opponent and gives the FS rikishi no special
credit. It also exposes the cost: ratings of rikishi uninvolved in any
non-appearance move because of other people's penalties.

## The possible magnitude problem

Non-appearances may be frequent enough that their aggregate compensation is not
negligible. A common additive shift preserves pairwise differences among the
unpenalised population at that instant, but it still changes:

- reported individual rating changes;
- the coordinate carried by incumbents relative to fixed future entrant priors;
- day-end versus normalised basho-end presentation; and
- potentially later ratings when population membership changes.

The acceptability of this effect cannot be inferred from the existing Elo-89
normalisation investigation. That investigation measured corrections generated
by population turnover and unequal divisional `k`, not an additional systematic
non-appearance deduction.

Before adoption, a candidate model would need to report at least:

- FP and absence counts separately by basho and division;
- total deducted mass per basho;
- the resulting common compensation per active rikishi;
- the contribution of penalties and compensation to reported rating changes;
- maximum and distributional effects on unpenalised rikishi;
- effects on entrant and returning-rikishi comparisons; and
- predictive log loss, Brier loss and calibration against unpenalised Elo-89.

If compensation proves unacceptably large, that is a reason to revisit the
penalty magnitude, transfer population, or the decision to penalise. It is not
a reason to pretend that an opponent can be recovered from data which do not
identify one.

## Timing remains part of the model

The point at which a penalty is applied must be explicit. A day-level penalty
would affect any later forecast in the same basho and would appear in daily
rating records. A basho-end penalty could produce the same next-basho relative
state in simple cases but would not describe the same daily or peak-rating
history.

For sub-sekitori absences inferred only to a scheduling window, exact-day
application may be unsupported. A future experiment must decide whether window-
level evidence permits a conventional application point, requires interval
uncertainty, or restricts the first model to basho-end penalties.

## Relationship to the main account

This is an excursus because penalty transfer is not the first question. A main
proposal must first state:

1. what quantity the rating is intended to estimate;
2. why non-appearance supplies evidence about that quantity;
3. which events count as FP and absence under the restricted terminology;
4. how `lambda` is determined; and
5. when the penalty is applied.

Only then does the secondary accounting question arise: discard the deducted
mass, credit a particular recipient, distribute it through an explicit pool, or
allow Elo-89 normalisation to compensate the active population.

## Next

Treat this excursus as the record of the transfer problem and use the
`absences` package as the authority for what can be inferred from SumoDB. The
next active step is review of `Non-appearance Penalty Experiment Proposal.md`;
the experiment must remain isolated from production Elo-89.
