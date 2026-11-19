# Proposal: Greedy and Constrained Torikumi Forecasting

## 1. Status

This document was written to specify two initial experiments before either was
implemented or run.  Experiment 1 has since been completed; its outcome is in
[Greedy Findings](Greedy%20Findings.md).  Experiment 2 has now been implemented
and smoke-tested; its full historical run remains to
be performed.  Both test the same simple account of late-basho makuuchi
torikumi and differ only in how they turn that account into a complete set of
pairs.

The purpose is reconnaissance.  The experiments ask whether the simple idea
is useful enough to justify further work.  They do not attempt to reconstruct
the JSA's unpublished decision process, fit a probabilistic model or achieve
perfect historical accuracy.

The package path retains the requested spelling
`src.analysis.torikumi_forcasting`.  The prose term is **torikumi
forecasting**, distinguishing this work from opponent-distribution analysis
and prediction of winners after a torikumi is known.

## 2. Research question

For a late basho day `d`, how much of the published makuuchi torikumi can be
recovered by:

1. ordering the represented makuuchi rikishi by wins through day `d - 2`,
   breaking ties by banzuke position; and
2. pairing rikishi as near the top of that order as the known restrictions
   permit?

The default late-basho range is Days 11 through 15 inclusive.  The first day
is a command-line parameter so that the same fixed analysis can be run over a
different suffix without changing code.  Day 15 is treated like the other
selected days in the initial experiment.

## 3. Two approaches

### 3.1 Experiment 1: greedy matching

The greedy algorithm takes the first remaining rikishi and pairs him with the
first eligible opponent in the remaining standings order.  It never revisits
an earlier choice.

If no eligible opponent remains, the rikishi is recorded as unpaired and the
algorithm continues.  It therefore completes as much of the torikumi as its
earlier choices permit.

### 3.2 Experiment 2: constrained matching

The constrained algorithm considers the complete card at once.  Among all
legal complete solutions, it minimizes the sum of the standings-order distance
between paired rikishi.

This approach tests whether poor greedy performance comes from the underlying
standings idea or merely from irrevocable local choices.  It is deterministic
optimization, not a fitted or probabilistic model.

The implementation will use OR-Tools CP-SAT.  Only a solution whose status is
`OPTIMAL` is accepted.  `INFEASIBLE` is a substantive result requiring
diagnostics.  `FEASIBLE`, `UNKNOWN`, a timeout or a solver error is an
experiment failure and is not scored as a constrained forecast.

Where several optimal solutions have the same cost, the experiment reports
one of them.  It assigns no substantive preference among equal optima and does
not enumerate or count them.

## 4. Source and historical cases

The source of completed results, scheduled pairs, banzuke positions and
stable rikishi identity is canonical `History`.  Historical heya observations
are extracted separately from the archived SumoDB daily-results HTML.

Only completed basho with all required selected days are eligible.  Start and
end basho may be supplied on the command line.  In the absence of an explicit
range, the analysis uses the complete eligible range represented by its input
sources and reports that resolved range.

Every `(basho, day)` is one forecast case.  The two approaches must receive
the identical case data.

The current or an incomplete basho is not mixed into retrospective scoring.
A live forecast may later use the same algorithms, but it is not part of these
experiments.

## 5. Information cutoff

For a target Day `d`:

* standings contain results only through Day `d - 2`;
* wins include `W` and `FS`;
* the Day `d - 1` torikumi is treated as already known;
* the Day `d - 1` result is not used; and
* prior-opponent restrictions use every scheduled pair from Days 1 through
  `d - 1`, including fusen pairs.

This reconstructs the ordinary situation in which the next makuuchi torikumi
is available before the current day's makuuchi results.  The experiment does
not use any Day `d - 1` outcome when ordering rikishi.

## 6. Target-day population

The experiment is conditional on the makuuchi population represented in the
published target-day torikumi.  It does not forecast whether a banzuke rikishi
will be omitted as kyujo.

The population is the set of target-day torikumi participants whose same-basho
chii belongs to makuuchi.  The target pairs themselves are not supplied to
either forecasting algorithm.

This treatment follows the recorded publication semantics:

* a rikishi whose kyujo status was known before preparation is omitted from
  the published torikumi and therefore from the case population; and
* a rikishi who withdrew after publication remains in the scheduled pair,
  producing `FP` and `FS`, and therefore remains in the population.

The experiment forecasts intra-makuuchi pairs only.  When the population is
odd, exactly one makuuchi rikishi may be unmatched.  That rikishi represents
the makuuchi participant in the cross-division bout.  The juryo opponent is
not forecast.

An eligible target card must contain:

* no cross-division makuuchi participant when the population is even; and
* exactly one when the population is odd.

A target card with more cross-division makuuchi participants than this parity
minimum is outside the deliberately simplified experiment.  It is excluded
and reported with its basho, day, population size, actual cross-division count
and parity minimum.  The experiment does not attempt to explain or forecast
the additional cross-division selections.

## 7. Standings order

The case population is sorted by:

1. wins through Day `d - 2`, descending; then
2. structured same-basho chii, from higher to lower banzuke position.

Losses do not enter the order.  Display strings are not parsed to establish
rank.  Identical chii do not occur and no fallback order is specified for
them.

The resulting zero-based list position is used by the constrained objective.
For clarity in reports, the displayed standings position may be one-based.

## 8. Eligibility

Two rikishi are eligible to be paired exactly when:

* they have not appeared together in a scheduled torikumi on any Day 1 through
  `d - 1`; and
* their historical heya values for the basho differ.

Fusen does not remove a scheduled meeting from prior-opponent history.
Playoffs are not regular torikumi and are excluded.

Familial relationships are not represented.  The first experiments maintain
no family registry and infer no relationships from names, birth data or
shusshin.  No additional pairing restrictions are specified.

## 9. Historical heya

Historical heya is read from the second field of the rikishi-link `title`
metadata in archived SumoDB daily-results HTML.  Extraction must be audited
for within-basho consistency.  A source title is parsed structurally; it is
not split indiscriminately because later fields such as shusshin may contain
commas.

For the exploratory analysis, a separate forecasting-owned compiler reads:

```text
files/output/HTML results/<YYYY MM>/<DD>.html
```

and writes:

```text
files/output/analysis/torikumi_forcasting/heya_index.json
files/output/analysis/torikumi_forcasting/heya_diagnostics.csv
```

The versioned JSON contains one consensus record per `(basho, rikid)`, with
the heya, observed source days and raw observation count.  The diagnostics CSV
records malformed titles, blank heya and conflicting within-basho values.  A
within-basho conflict prevents the compiler from writing the index.

The forecaster reads only the compiled index; it does not parse source HTML.
The index records its source root, compilation time, represented range and
source, observation, record and diagnostic counts.  It is regenerated
explicitly when the HTML archive changes.  Incremental refresh, automatic
freshness enforcement and integration into canonical `History` are deferred
unless the forecasting experiments justify that work.

If no heya can be established for a rikishi at the basho, assign the unique
synthetic value:

```text
heya<rikid>
```

This permits the algorithms to proceed without falsely treating two unknown
rikishi as stablemates.  It can fail to prohibit a real same-heya pairing and
is therefore disclosed, not treated as equivalent to observed heya.

For every synthetic assignment the outputs report:

* basho;
* rikishi ID and displayed shikona;
* the assigned value;
* forecast cases in which it was used; and
* predicted pairs containing the assignment.

## 10. Pair representation and presentation

Pairs are unordered for constraint checks and evaluation.  Official source
East/West orientation and bout order are not forecast.

For presentation only, the member with the higher chii is placed in the East
slot and the lower-chii member in the West slot.  There is no equal-chii case.

The forecast solution consists of:

```text
intra-makuuchi pairs
unmatched makuuchi rikishi, if the population is odd
```

The unmatched rikishi is part of the solution and is displayed and evaluated.

## 11. Experiment 1 algorithm

Given the ordered population:

```text
pairs = []
unpaired = []
remaining = ordered population

while remaining is not empty:
    rikishi = remove the first member of remaining
    opponent = first eligible member of remaining

    if opponent exists:
        remove opponent from remaining
        append (rikishi, opponent) to pairs
    else:
        append rikishi to unpaired
```

There is no maximum permitted standings distance, backtracking, repair or
second pass.

Let `expected_unpaired = population_size mod 2`.  The greedy forecast succeeds
when the number left unpaired equals `expected_unpaired`.  Otherwise it retains
the partial card and reports:

```text
failure: unpaired rikishi are ...
```

For each unpaired rikishi, diagnostics include standings position, wins,
chii, heya, previous opponents and the reason every candidate considered at
that step was ineligible.

## 12. Experiment 2 formulation

For every permitted unordered pair `{i, j}`, create a Boolean variable
`x[i,j]`.  For every rikishi `i`, create a Boolean `unpaired[i]`, representing
the zero-cost conceptual self-pair.

Every rikishi has exactly one disposition:

```text
sum(x[i,j] for permitted opponents j) + unpaired[i] == 1
```

The number unmatched is fixed by population parity:

```text
sum(unpaired[i]) == population_size mod 2
```

For standings positions `p[i]` and `p[j]`, pair cost is:

```text
cost(i, j) = abs(p[i] - p[j])
```

The unmatched variable has cost zero.  The objective is:

```text
minimize sum(cost(i, j) * x[i,j])
```

Because the unmatched count is fixed, zero unmatched cost cannot be exploited
by omitting additional rikishi.

An `OPTIMAL` result is independently checked for complete coverage, legal
pairs, correct unmatched parity and recomputed objective value before it is
accepted.

## 13. Infeasibility and solver diagnostics

For an `INFEASIBLE` case, retain at least:

* basho, day and ordered population;
* allowed-opponent count for every rikishi;
* every prohibited edge and its reason or reasons;
* the actual target-day reduced card used as the feasibility witness;
* all historical-heya observations and synthetic assignments used; and
* solver status and elapsed time.

An accepted historical case normally has an immediate feasibility witness:
the actual published card reduced to its intra-makuuchi pairs plus its one
cross-division participant as unmatched, if present.  Before either experiment
is scored, this actual reduced card must pass the same eligibility and parity
checks.  Failure indicates an input, historical-heya, restriction or domain
assumption problem.

If the actual card passes but CP-SAT reports `INFEASIBLE`, the implementation
has contradicted a known witness and the run fails.

For a non-accepted solver status, also record the best solution and bound when
the API supplies them, but do not publish or score that solution as the
constrained forecast.

## 14. Evaluation

For each approach and case, report:

* population size;
* actual and forecast intra-makuuchi pair counts;
* recovered-pair count;
* pair recovery rate against the actual intra-makuuchi pairs;
* actual and forecast unmatched rikishi, where applicable;
* whether the unmatched rikishi is correct;
* whether pairs plus unmatched rikishi reproduce the complete reduced card;
* success, greedy failure, `OPTIMAL`, `INFEASIBLE`, or experiment-failure
  status; and
* constrained objective cost where applicable.

Separately report every extra-cross-division exclusion and aggregate its count
overall and by target day.  Excluded cases are not included in forecasting
accuracy denominators.

Aggregate results report counts and rates overall, by target day and by basho.
Greedy failures remain in the denominator and are not repaired.  Their partial
pairs may be described but must not be confused with successful complete-card
forecasts.

The paired comparison between experiments reports at least:

* cases where both return the same complete solution;
* cases where greedy fails and constrained matching is optimal;
* cases where both complete but return different solutions;
* pair-recovery difference on their shared cases; and
* constrained infeasibility or other solver failures.

No accuracy threshold is declared as success.  The purpose is to see how bad
or promising the two simple approaches are.

## 15. Protection against later overfitting

These experiments contain no fitted parameters, and their rules are fixed in
this proposal before results are inspected.  Nevertheless, later refinements
could be tailored to their mistakes.

The latest twelve eligible completed basho form a reserved holdout.  Earlier
eligible basho form the initial evaluation/development period.  The
implementation and validation suite are frozen before the holdout is run.
Results from the holdout are reported separately and are not used to repair
either baseline.

Historical note: the 2026 pilot used to validate source and population
assumptions exposed the need for the predeclared extra-cross-division
exclusion, so part of the eventual recent split had been inspected before the
full greedy run.  The greedy pairing rule was not changed.  The recent split
is reported for comparison but is not described in the findings as wholly
unseen evidence.

If an explicitly selected historical range contains fewer than thirteen
eligible basho, the run reports that no meaningful twelve-basho holdout can be
formed and does not relabel part of the range arbitrarily.

Any future model inspired by the results must define a new evaluation policy;
the present holdout will no longer be untouched after these experiments.

## 16. Predeclared validation cases

Synthetic labels `A`, `B`, and so on are in standings order.  Costs use their
one-based positions, which gives the same differences as zero-based positions.

| Case | Order | Forbidden pairs | Expected greedy result | Expected constrained result |
|---|---|---|---|---|
| Ordinary even | `A B C D` | none | `A-B, C-D`; success | `OPTIMAL`, cost 2 |
| First pair forbidden | `A B C D` | `A-B` | `A-C, B-D`; success | `OPTIMAL`, cost 4; any optimum |
| Greedy trap | `A B C D` | `C-D` | `A-B`; C and D unpaired; failure | `OPTIMAL`, cost 4 |
| Ordinary odd | `A B C D E` | none | `A-B, C-D`; E unmatched; success | `OPTIMAL`, cost 2; exactly one unmatched |
| Odd greedy trap | `A B C D E` | `C-D, C-E, D-E` | `A-B`; C, D and E unpaired; failure | `OPTIMAL`, cost 4 |
| Even infeasible | `A B C D` | every pair except `A-B` | `A-B`; C and D unpaired; failure | `INFEASIBLE` |
| Odd infeasible | `A B C` | every pair | A, B and C unpaired; failure | `INFEASIBLE` |

The constrained tests check legality and optimal cost, not exact pair identity
where equal optima exist.

Additional fixed tests establish that:

* a previous scheduled meeting prohibits an edge;
* same-heya membership prohibits an edge;
* different heya remain eligible;
* two missing heya observations produce distinct `heya<rikid>` values and do
  not prohibit an edge;
* the target-day cross-division makuuchi participant is represented as the
  actual unmatched rikishi;
* a scheduled fusen pair remains a pair;
* playoffs do not enter prior-opponent history or the target card; and
* presentation puts the higher-chii member in the East slot.

## 17. Exhaustive-oracle validation

An implementation independent of OR-Tools enumerates every legal complete
solution for small populations.  It recursively pairs the first remaining
rikishi with every permitted opponent and, for odd populations, tries exactly
one unmatched assignment.  It returns infeasibility or the minimum cost.

CP-SAT and the exhaustive oracle must agree on feasibility and optimum cost.
The returned pair identities may differ only when they have the same optimum
cost.

In addition to the named cases above, use random seed `20261119` to generate
20 constraint graphs at each permitted-edge probability `0.25`, `0.50` and
`0.75` for every population size from 2 through 9.  All 480 cases are checked
against exhaustive enumeration.  Generated cases are test inputs, not
forecasting data and not evidence about JSA practice.

## 18. Historical input validation

Before forecasting, every case verifies:

* all population members have structured makuuchi chii;
* all chii are distinct;
* wins were accumulated only through `d - 2`;
* prior opponents were accumulated from scheduled Days 1 through `d - 1`;
* the heya source is observed or explicitly synthetic;
* target population parity identifies the minimum cross-division count;
* cases exceeding that minimum are recorded as declared exclusions; and
* the reduced actual card is a legal complete solution.

The run fails clearly rather than excluding a case merely because it is
awkward.  A source-coverage exclusion defined independently of the observed
forecast may be reported, but its rule and count must appear in the manifest.

## 19. Proposed command and outputs

The exact argument names may follow established package conventions, but the
intended interface is:

```powershell
python -m src.analysis.torikumi_forcasting `
  --history-zip PATH `
  --start YYYY/MM `
  --end YYYY/MM `
  --first-day 11 `
  --output-root files/output/analysis/torikumi_forcasting
```

The output bundle should contain at least:

```text
manifest.json
cases.csv
excluded_cases.csv
forecast_pairs.csv
heya_diagnostics.csv
failure_diagnostics.csv
report.md
```

The manifest records source paths and hashes, resolved basho range, day range,
holdout boundary, population and restriction policies, solver version and
configuration, case counts and output hashes.  Outputs must distinguish
development and holdout results and the two experiment approaches.

## 20. Interpretation limits

These experiments can show how closely two explicit algorithms reproduce
historical torikumi.  They cannot establish:

* the JSA's actual decision rule;
* that standings caused a pairing;
* that omitted family restrictions had no effect;
* that synthetic heya assignments are harmless;
* that a reported optimum was the only optimum; or
* that remaining discrepancies can or should be eliminated.

A poor result may justify stopping.  A better constrained result than greedy
would show that local greedy choices matter, not that the constrained objective
is the JSA's policy.  High but imperfect recovery may indicate that standings
and known restrictions narrow the possible card while leaving genuine or
unobserved discretion at the edges.
