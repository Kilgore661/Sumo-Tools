# Stage 1 Proposal: Checking the JSA Scheduling Guideline

## Purpose

Measure how consistently historical sub-sekitori schedules recorded by
SumoDB follow the Japan Sumo Association's stated normal pattern of one
bout-related outcome in each of seven tournament windows.

Stage 1 establishes what the records say about the guideline.  It does not
infer the windows or calendar days on which a rikishi was kyujo.

## Scope

The experiment covers ranked rikishi in:

- makushita;
- sandanme;
- jonidan; and
- jonokuchi.

The period begins with the January 1989 basho and ends with the latest complete
basho selected for the experiment.

The unit of analysis is one rikishi in one basho.  Mae-zumo is outside the
scope.  Playoffs require no adjustment because SumoDB does not record them as
part of the regular daily result sequence.

## Scheduling guideline

The fifteen basho days are divided into seven scheduling windows:

| Window | Days |
| --- | --- |
| 1 | 1-2 |
| 2 | 3-4 |
| 3 | 5-6 |
| 4 | 7-8 |
| 5 | 9-10 |
| 6 | 11-12 |
| 7 | 13-15 |

The documents may refer to these collectively as two-day windows, with the
explicit qualification that the final window contains three days.

The normal JSA pattern predicts no more than one bout-related outcome for a
rikishi in each window.

## Recorded facts

For each rikishi-basho, the experiment requires:

- the final number of wins, `W`;
- the final number of losses, `L`;
- the final number of non-fusen-pai absences, `A`; and
- the calendar day and result type of every recorded bout-related outcome.

The bout-related result types are:

- ordinary win;
- ordinary loss;
- fusen-sho (`FS`); and
- fusen-pai (`FP`).

All four types establish that the rikishi was on that day's torikumi.  An
ordinary win or `FS` contributes to `W`; an ordinary loss or `FP` contributes
to `L`.  `A` records absences that did not produce a dated fusen-pai result.

The final `W-L-A` record must be treated as recorded evidence rather than
reconstructed as seven minus the number of dated outcomes.  Reconstructing
`A` that way would make the experiment circular.

## Source sanitation

The experiment first checks whether the source facts are internally
consistent.

### Daily uniqueness

A rikishi should not have more than one regular bout-related outcome on the
same calendar day.

### Win reconciliation

The number of dated ordinary wins and fusen-sho results should equal `W`.

### Loss reconciliation

The number of dated ordinary losses and fusen-pai results should equal `L`.

### Appearance reconciliation

If `N` is the number of dated bout-related outcomes, then:

```text
N = W + L
```

### Seven-slot reconciliation

An ordinary sub-sekitori record should satisfy:

```text
W + L + A = 7
```

Records that do not satisfy these checks are preserved as findings and kept
separate from ordinary scheduling departures.  They are not silently repaired
or discarded.  Eight-bout records are exceptional records, not ordinary
seven-slot records.

## Window occupancy

For each rikishi-basho, define `c_i` as the number of bout-related outcomes in
window `i`.  This gives a seven-element occupancy vector:

```text
(c_1, c_2, c_3, c_4, c_5, c_6, c_7)
```

Examples include:

```text
(1, 1, 1, 1, 1, 1, 1)  seven outcomes and no absences
(0, 1, 1, 1, 1, 1, 1)  one empty window and six outcomes
(0, 2, 1, 1, 1, 1, 1)  one empty window and one double-occupied window
(0, 0, 0, 0, 2, 2, 3)  the extreme pattern ........XXXXXXX
```

The normal guideline admits occupancies of zero or one.  Zero may be explained
by a recorded absence.  An occupancy greater than one is a departure from the
normal guideline, not necessarily a source error.

## Measures

Let `E` be the number of empty windows:

```text
E = number of windows for which c_i = 0
```

Let `D` be the number of excess outcomes in already occupied windows:

```text
D = sum(max(0, c_i - 1)) over the seven windows
```

For an internally consistent seven-slot record:

```text
E = A + D
```

`A` accounts for empty windows required by the final absence total.  Each
excess outcome counted by `D` creates one further empty window elsewhere.

## Classification

Each rikishi-basho is assigned to one of these categories.

### Guideline-conforming

Every window contains at most one outcome, so `D = 0`.  For an internally
consistent seven-slot record, `E = A` also holds.

### Single departure

Exactly one excess outcome is present, so `D = 1`.

### Multiple departure

Two or more excess outcomes are present, so `D >= 2`.

### Exceptional total

The record does not have the ordinary seven-slot total.  This includes
eight-bout records.

### Internally inconsistent

The dated outcomes cannot be reconciled with the recorded final `W-L-A`
totals.

Exceptional totals and internal inconsistencies are not combined with
ordinary scheduling departures.

## Principal results

The primary result is the proportion of internally consistent seven-slot
rikishi-basho records for which every window contains at most one
bout-related outcome.

Secondary results are:

- the distribution of `D`;
- the frequency of windows containing two or more outcomes;
- the frequency of each observed occupancy vector;
- the windows most often involved in departures;
- the calendar-day combinations within double-occupied windows;
- the number and form of exceptional-total records; and
- the number and form of internally inconsistent records.

Results should also be broken down by division, year, basho, window, final
absence count and the presence of fusen-sho or fusen-pai.

## Duplicate observations

A bout appears in the records of both participants.  One unusually scheduled
bout may therefore produce two related rikishi-level observations.

Results should be reported at both levels:

1. rikishi-basho records affected; and
2. distinct bouts affected, deduplicated by basho, day and participant pair.

The first measures how many individual records depart from the guideline.  The
second measures how many distinct scheduling decisions are represented.

## Interpretation

The JSA statement is treated as a testable description of normal practice, not
as an inviolable rule.  A double-occupied window is therefore a departure from
the guideline, not automatically an error.  It may reflect withdrawals, an odd
number of available rikishi or another legitimate scheduling requirement.

Stage 1 reports the prevalence, location and severity of such departures.  It
does not determine which empty windows are absences or why any individual
schedule departed from the guideline.

## Non-goals

Stage 1 does not:

- infer a particular kyujo day or window;
- diagnose injury or any other reason for absence;
- change or validate another analysis or product;
- define a downstream integration contract;
- recommend how another model should treat absences; or
- assume any future use for its findings.

Possible applications are outside scope until the experiment has concluded
and its results have been considered independently.
