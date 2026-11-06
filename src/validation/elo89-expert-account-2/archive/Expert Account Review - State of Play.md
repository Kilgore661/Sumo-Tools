# Expert Account Review: State of Play

> **Archived:** This document records an intermediate review. Later edits and
> investigations resolved or superseded several of its conclusions. It is not
> the current assessment of the expert account.

**Review date:** 3 November 2026  
**Scope:** numbered chapters 1--13 in this folder  
**Purpose:** preserve the assessment made after the chapter-by-chapter review,
updated to include the subsequent investigation of Mae-zumo (`Mz`).

## Bottom line

Chapters 1--13 form a coherent account of Elo-89. They progress from the
purpose and interpretation of ratings, through ordinary Elo and its
application to sumo, to the exact Elo-89 contract, the reasons for its choices,
its limitations, the evidence for it and the alternatives.

The account also anticipates many of the questions an expert reader is likely
to ask: what a rating means, which evidence is admitted, how probabilities and
updates are calculated, how first ratings are assigned, how population changes
are handled, which conclusions are mathematical and which are empirical, and
what has not been established.

It is nevertheless not yet a complete expert account in one important sense.
Its specification and conceptual argument are substantially stronger than its
presentation of the supporting empirical work. In several places it says that
an audit, calibration study or controlled comparison found something without
giving enough of the design, denominator or result for an expert reader to
assess the claim. The remaining work is therefore principally to strengthen
the evidence layer, not to restructure the thirteen-chapter narrative.

## What is already strong

### The narrative has a clear progression

- Chapters 1--4 establish the purpose, interpretation and value of a mechanical
  numerical rating system without assuming that the banzuke is itself such a
  system.
- Chapters 5--8 explain ordinary Elo, expose its assumptions and show why a
  complete historical rating system requires choices beyond the familiar
  update equation.
- Chapter 9 states the Elo-89 recurrence and population operations precisely.
- Chapter 10 distinguishes empirical support, modelling judgement,
  reproducibility requirements and open questions.
- Chapters 11--13 criticise the model, delimit the evidence and describe
  alternatives without implying that every alternative has been tested.

### The exact model is mostly explicit

Chapter 9 gives the expectation equation, outcome rule, divisional \(K\)
schedule, P1-WL entry rule, active population, target mean, start and end
population shifts, chronology and observation stages. Its one-basho summary
is a useful compact contract.

The state model should be understood as one persistent partial mapping from
rikishi identity to rating, together with a basho-specific active set. Once a
rating has been assigned, its map entry is retained. Only members of the
current active set participate in forecasts, updates, common shifts and
published observations. There is no archive or restore operation.

### Qualifications are generally honest

The account does not present Elo-89 as a true latent-ability model or as the
winner of every possible comparison. It identifies the lack of a separate
uncertainty coordinate, the retrospective fitting of P1-WL, the coarseness of
division as a responsiveness proxy, the selective torikumi network, the
conditional nature of cross-era comparisons and the absence of prospective
validation.

These are disclosed properties and limitations. They are not, merely by
existing, defects in the account.

## Matters still requiring attention

### 1. P1-WL is not described in enough detail

Chapter 9 explains what the fixed P1-WL table does but describes its fitting
only as relating ratings to banzuke chii. It then says that the detailed
procedure and values are available in the repository.

For an expert account, this leaves a material input as a black box. The account
should either contain, or point precisely to a stable companion containing:

- the input history and eligibility rule;
- the quantity fitted at each chii;
- the support treatment and the role of epsilon;
- the iteration and convergence rule;
- east/west pairing and treatment of unnumbered upper ranks;
- the fixed table or an exact identified artifact; and
- the fitting boundary and artifact identity.

This does not require a history of superseded P1 variants. It requires a
self-contained account of the P1-WL input actually used by Elo-89.

### 2. The empirical comparisons are often reported only as verdicts

Chapter 10 says that divisional \(K\), informed initialisation and
whole-population preservation improved retrospective proper scores. Chapter 12
repeats those conclusions. The account often omits the compared policies,
evaluation interval, bout count, scores and effect sizes.

At minimum, an expert evidence summary should identify:

- the candidates compared;
- the common result domain and observation count;
- the primary and secondary scoring rules;
- the principal score differences;
- any block or uncertainty analysis used to judge those differences; and
- important metric or subgroup disagreements.

The pre-review development narrative contains much of this material, including
the factorial \(K\)/initialisation comparison and the population-policy score
table. The useful evidence should be retained without restoring the full
development history to the numbered account.

### 3. The reason for retaining every assigned rating needs to be stated

Chapter 9 correctly specifies one persistent rating map, but Chapter 10 does
not explain this choice separately from the rule that no bout means no
individual update.

The relevant alternative was a map-pruning policy: delete an identity when it
is absent from the current ranked banzuke and assign P1-WL again if it later
appears. The retained comparison found no reason to discard the earlier bout
evidence and favoured the persistent map. That result can be explained without
the false language of archiving and restoring ratings and without presenting
ordinary lower-boundary banzuke cycles as retirement and return.

### 4. “Sufficiently complete from January 1989” needs an operational meaning

The phrase is central to the model name and scope, but the account supplies no
short quantitative definition of “sufficiently complete.” It should state
which ranked divisions and result fields are within the represented domain,
what the audit measured, and why the remaining omissions do not defeat the
chosen calculation.

The claim need not be that the source represents every event in professional
sumo. It should be a precise claim about the ranked-banzuke and result domain
to which Elo-89 is applied.

### 5. Several calibration and normalisation claims are too qualitative

Examples include statements that calibration was “substantially better” for
mature ratings, that divisional \(K\) improved scores “modestly,” and that
recent normalisation effects were “small” while lower-division exceptions were
“larger.”

Where these claims support a model choice or bound an important criticism, the
account should give the relevant definition, denominator and scale. Chapter 12
already improves the normalisation statement by giving 51 windows and the
±1% result; similar precision is needed for the other principal claims.

### 6. The model-selection protocol needs one compact, inspectable summary

The account says that mean log loss was declared primary before candidate
ordering was inspected and that Brier loss and calibration supplied checks.
It does not put the candidate set, common evaluation domain and principal
results together in one place.

An expert reader should be able to see why the declared rule selected Elo-89,
which alternatives were actually tested, and where another metric or subgroup
favoured a different candidate. This can be a compact table rather than a
return to a chronological development narrative.

### 7. Evidence provenance is collected but not yet easy to follow

`Working Sources.md` preserves the source list removed from individual
chapters. That avoids clutter, but a bare source list does not always show
which retained artifact supports a particular numerical or empirical claim.

The final account needs a lightweight mapping from its main empirical claims
to stable findings or artifacts. It should not require the reader to infer the
connection from filenames or reconstruct the project's development history.

## Conclusion of the Mz investigation

The Mz investigation does not create an outstanding correction to the
numbered account.

- Mae-zumo is outside the ranked-banzuke result domain represented by Elo-89.
- SumoDB daily pages do not provide a complete Mz--Mz bout record even after
  1989, so those bouts cannot be added consistently to the historical rating
  calculation.
- Excluding Mz from the active banzuke does not delete an existing rating. The
  single persistent rating map retains it unchanged while that identity is
  outside the basho-specific active set.
- Apparent `Jk -> unrepresented -> Jk` cycles therefore do not require an Mz
  chii, an Mz prior, or an archive-and-restore lifecycle.

The source comparison covered 220 post-1988 basho with a Mae-zumo roster and
1,604 rikishi with a non-zero published Mae-zumo record. Three basho omit all
of their implied Mz results from the daily pages (`1992-03`, `2020-07` and
`2026-09`), while `2016-01` contains a smaller internal inconsistency. This is
a source-domain limitation, not evidence that Elo-89 has lost a stored rating.

The source-domain investigation should be retained separately so that this
boundary is not rediscovered later, but the public expert account need not
introduce “leaving and returning” in order to explain Elo-89.

## Present assessment

The thirteen chapters are coherent and their structure should be retained.
There is no known Mz-driven model correction waiting to be made. The account's
remaining weakness is that it sometimes names evidence without presenting
enough of it.

The next review should therefore concentrate on chapters 9, 10 and 12:

1. make P1-WL reproducible or precisely traceable;
2. add a compact evidence table for the principal model choices;
3. explain the persistent-map choice accurately;
4. define the January 1989 completeness claim; and
5. replace important qualitative empirical descriptions with bounded
   quantitative statements.

After that work, the remaining open matters will predominantly be disclosed
limitations and future research questions rather than omissions in the expert
account itself.
