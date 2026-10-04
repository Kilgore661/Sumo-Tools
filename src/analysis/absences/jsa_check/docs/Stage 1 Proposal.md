# Stage 1 Proposal: Testing the JSA Scheduling Model

## Status and context

This proposal turns the problem introduced in
[`On Absences`](../../docs/On%20Absences.md) into a test against the historical
record.  That document provides the tutorial account; this proposal defines
the exact result model, qualifications and tests.

The experiment is considered in isolation.  No use of its findings elsewhere
in the project is assumed, and possible applications will not be considered
until the experiment has concluded.

## Question

JSA guidance says that a sub-sekitori rikishi normally has one bout opportunity
in each of seven scheduling windows.  If that description can be relied upon,
a window with no bout result can be interpreted as an absence rather than a
collection of ordinary rest days.

The experiment asks:

1. how often do historical sub-sekitori records fit the seven-window scheduling
   model; and
2. for how many of those records can the recorded absences be assigned to
   particular windows?

The inference is about a window, not an exact day within that window.

## Scope

The population consists of ranked rikishi in:

- makushita;
- sandanme;
- jonidan; and
- jonokuchi.

The period begins with the January 1989 basho and ends with the latest complete
basho selected for the experiment.  The unit of analysis is one rikishi in one
basho.

Mae-zumo is outside the scope.  Playoffs require no adjustment because SumoDB
does not include them in the regular daily result sequence.

## Sources

The dated bout results come from the canonical `History` artefact.  The final
result is read independently from the cached SumoDB banzuke page; it must not
be reconstructed from the dated results, because that would make the
reconciliation tests circular.

The post-parsing rank-at-retirement rikishi artefact is joined by rikishi ID.
It identifies whether a rikishi-basho is the rikishi's final observed banzuke
appearance.  That classification helps explain the shape of short records, but
it does not alter the absence inference.

## Exact result model

For dated results, the bout-related outcomes are:

- ordinary win (`W`);
- ordinary loss (`L`);
- fusen-sho (`FS`);
- fusen-pai (`FP`); and
- draw (`d`).

Each of these occupies a calendar day and a scheduling window.  A missing
daily result does not itself establish an absence.

Let the independently published final result contain:

```text
nw  wins
nl  losses
na  absences
nd  draws
```

The familiar forms are `W-L` and `W-L-A`.  The corresponding forms containing
a draw are much less familiar: `W-L-Dd` and `W-L-A-Dd`, where the numeric
suffix before `d` is the draw count.  Thus `3-3-1d` means three wins, three
losses and one draw, whereas `1-1-3-1d` means one win, one loss, three absences
and one draw.

At first sight, a complete sub-sekitori result might be expected to satisfy:

```text
nw + nl + na = 7
```

This is not quite correct.  Although they are rare, drawn bouts are possible.
A draw occupies one of the seven bout opportunities but is neither a win, a
loss nor an absence.  The complete seven-opportunity model is therefore:

```text
nw + nl + na + nd = 7
```

For example, `3-3-1d` accounts for seven opportunities.  `1-1-3-1d` accounts
for only six.

Eight-opportunity records are known to occur.  They are departures from the
ordinary seven-opportunity pattern, but they do not have to be excluded from
the inference.  In particular, a rikishi who actually fought eight times has
no absences to locate.  Records with fewer than seven opportunities may include
rikishi whose records end because they retired during the basho.

The opportunity total is therefore a diagnostic description of the data, not
an eligibility condition for absence inference.

## Scheduling windows

The 15 basho days are divided into seven windows:

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

For each rikishi-basho, let `c_i` be the number of dated bout outcomes in
window `i`.  The seven values form an occupancy vector:

```text
(c_1, c_2, c_3, c_4, c_5, c_6, c_7)
```

Examples include:

```text
(1, 1, 1, 1, 1, 1, 1)  seven occupied windows
(0, 1, 1, 1, 1, 1, 1)  one empty window
(0, 2, 1, 1, 1, 1, 1)  one empty and one double-occupied window
(0, 0, 0, 0, 2, 2, 3)  the extreme pattern ........XXXXXXX
```

The normal JSA pattern produces an occupancy of zero or one.  An occupancy
greater than one is a departure from that pattern, but it is not automatically
a source error and does not by itself prevent absence inference.  It may
reflect a legitimate exceptional scheduling decision.

## Analysis

The experiment separates absence inference from diagnostics about the quality
and shape of the data.  A diagnostic failure is reported, but it is not
automatically used to suppress the inference.  This allows the experiment to
show both what the recorded facts imply and how much confidence should be
placed in those facts.

### Source sanitation diagnostic

A rikishi should not have more than one regular bout outcome on the same
calendar day.  Multiple daily outcomes, if found, remain visible as source
anomalies and are not silently collapsed.

### Opportunity-total diagnostic

For each record, calculate:

```text
T = nw + nl + na + nd
```

Report the distribution of `T`, including totals below seven, equal to seven,
equal to eight and above eight.  Also report how many short records coincide
with the rikishi's final observed basho according to the rank-at-retirement
artefact.

Seven is the normal total, but `T = 7` is not a prerequisite for asking whether
the record contains identifiable absence windows.

### Dated-result reconciliation diagnostic

Compare the independently published final result with the dated outcomes:

```text
nw = count(W) + count(FS)
nl = count(L) + count(FP)
nd = count(d)
```

These comparisons are sanity tests on the source data.  They do not define
whether an absence is inferable, although a disagreement may reduce confidence
in the inference and must remain visible beside it.

### Scheduling-shape diagnostic

Report whether every window has at most one outcome and, separately, the number
of excess outcomes in already occupied windows:

```text
X = sum(max(0, c_i - 1))
```

Let `E` be the number of empty windows.  The following accounting identity is
expected when the final opportunity total and all dated outcomes reconcile:

```text
E = na + X - (T - 7)
```

This is a useful check on the relationship between the final result and the
window shape.  It is not the absence-inference test.  In particular, a normal
eight-bout record has `T = 8`, `X = 1`, `E = 0` and `na = 0`.

### Absence inference

The final record supplies the number of absences, `na`, while the dated results
identify the empty windows.  Under the JSA scheduling assumption, classify each
rikishi-basho as follows:

| Condition | Interpretation |
| --- | --- |
| `na = 0` | There are no absences to locate. |
| `na > 0` and `E = na` | Every empty window can be identified as an absence window. |
| `na > 0` and `E > na` | There are more candidate windows than absences, so their locations are ambiguous. |
| `E < na` | The recorded absence count is inconsistent with the observed empty windows. |

When `na > 0` and `E = na`, the number of absences assigned to windows is
`na`; otherwise no particular absence window is identified from these facts
alone.  A non-empty window contains `W`, `L`, `FS`, `FP` or `d`, so it is not
an absence window.

This classification states what the records imply if the JSA scheduling
guidance is accepted.  It does not prove that an empty window was created by
the precise administrative process described in the introductory account.

## Outputs

The atomic output contains one row per rikishi-basho, including:

- identifiers and basho;
- the 15 dated result positions;
- the seven window occupancies;
- the final win, loss, absence and draw components;
- the opportunity total and each reconciliation diagnostic;
- whether this is the rikishi's final observed basho;
- whether any window is double-occupied;
- the number of empty windows; and
- the absence-inference classification and number of absences assigned to
  windows.

The summary reports the population count and the counts and percentages for
each diagnostic, including:

- opportunity-total categories;
- dated win, loss and draw reconciliation;
- records with double-occupied windows; and
- final-basho classifications for short records.

The summary also records a timezone-aware generation timestamp and the exact
History, final-record and retirement sources selected for the run.

For the central inference question it reports:

- records with no absences;
- records whose positive absences can all be assigned to windows;
- records whose positive absences are ambiguous;
- records whose absence count is inconsistent with their empty windows;
- the total number of absences; and
- the number and percentage of those absences assignable to scheduling windows.

Patterns among double-occupied records are a possible later analysis, justified
only if their number is large enough to make such an analysis useful.

### Unit of counting

The principal unit remains the rikishi-basho record.  Because a bout appears in
the records of both participants, one unusual scheduling decision may create
two related rikishi-basho observations.  The main percentages measure the
prevalence of each absence-inference classification among rikishi-basho
records, which is the question posed by this experiment.

If double-occupied records are examined later, that analysis should report both
the number of affected rikishi-basho records and the number of distinct bouts,
deduplicated by basho, day and participant pair.

## Draw-source requirement

The omission of dated draws is historical.  The original model was created on
the assumption that draws were impossible.  When that assumption was corrected,
draws were rare enough to record as exceptional final-result components without
changing the daily-result pipeline.  That is no longer sufficient for this
experiment because the date of a draw determines which window is occupied.

Canonical `History` artefacts built before the draw translation was corrected
omit three drawn bouts, affecting six rikishi-basho records.  SumoDB records
their daily outcomes as `D`/`D`; the parser now translates those tokens to the
core model's `Outcome.DRAW`.  The affected bouts are:

- 1994/03 day 5: Asanishiharu versus Tasai;
- 1999/01 day 3: Ueda versus Sakaguchi; and
- 1999/01 day 14: Hidenishiki versus Fusanonami.

A draw is an occupied window.  The final absence inference must therefore use
a rebuilt `History` that preserves these draws.  The implementation treats
draw reconciliation as a source precondition and stops with an error if a
final draw count has no corresponding dated draw.  Merely observing the draw
component in the final result is not a substitute for retaining its date.

Win and loss reconciliation remain diagnostics: discrepancies are reported
but do not suppress absence inference.  Draw reconciliation is stricter only
because omitting a dated draw directly changes which scheduling window appears
empty.

## Conditional conclusion

The experiment is designed to support a conclusion of the following form:

> Given the final number of absences and the occupied scheduling windows, and
> assuming the JSA scheduling model applies, a record with no absences requires
> no location inference.  Where there are absences and their number equals the
> number of empty windows, every empty window can be identified as an absence
> window.  Where there are more empty windows than absences, their locations
> cannot be determined from these records alone.

The conclusion does not identify the exact day on which the rikishi would have
fought or the reason for the absence.  Opportunity totals, result
reconciliation and departures from the normal one-outcome-per-window pattern
are reported as diagnostics rather than used automatically to suppress the
inference.

## Non-goals

The experiment does not:

- diagnose injury or any other reason for absence;
- treat fusen-pai as absence;
- explain why an individual schedule departed from the JSA model;
- change or validate another analysis or product;
- define a downstream integration contract;
- recommend how another model should treat absences; or
- assume any future use for the findings.

Possible applications remain outside scope until the experiment has concluded
and its results have been considered independently.
