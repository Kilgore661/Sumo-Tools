# Proposal: Matched Elo89 versus Chii Winner Accuracy

## Status

Implemented and run on the declared 1989/01–2026/11 record. The result and
its interpretation are recorded in [Findings](Findings.md): production Elo89
selected 57.774% of winners and higher chii selected 52.635% on the common
583,115-bout domain. Both predeclared one-sided lower bounds exceeded zero, so
the declared three-rule ordering was confirmed as a necessary retrospective
validation, not as a claim that Elo89 is the best possible model.

This work closes the question deliberately deferred in
[Findings](Findings.md): does production Elo89 select the winner more often
than the simple rule “choose the rikishi with the higher chii” when both rules
are scored on exactly the same bouts?

The overall objective is to test the complete proposed ordering:

```text
production Elo89 accuracy > higher-chii accuracy > random-choice accuracy
```

over a declared inclusive range of basho dates. The default range is the whole
represented Elo89 epoch, 1989/01 through 2026/11 inclusive. The comparison
must report whether the complete ordering is supported, contradicted or left
inconclusive; it must not treat confirmation of only one inequality as
confirmation of the whole ordering.

The work belongs in the existing `src.analysis.chii_prediction` package.
That package owns the higher-chii baseline, its eligibility rules and the
recorded 52.637% result. A new top-level analysis package would duplicate that
ownership. The implementation should extend this package with a matched
comparison while continuing to obtain Elo89 forecasts from the production
`src.analysis.elo89` replay.

## Motivation

The project has established three related facts, but not one complete
three-way comparison:

1. an always-50–50 forecast is a meaningful neutral baseline;
2. over 1989/01–2026/07, the higher-chii rule selected 52.637% of winners;
3. Basic Elo selected about 56% of winners, while later Elo-family models
   achieved better proper probability scores than Basic Elo.

Those results strongly suggest the ordering

```text
production Elo89 > higher chii > random choice
```

for categorical winner selection. They do not formally establish it. The
existing figures came from different runs and, in the chii case, a different
History snapshot and denominator. The final production Elo89 model also
postdates the older “about 56%” Basic Elo result.

The missing work is therefore not another broad model-selection exercise. It
is one controlled, matched retrospective comparison.

## Research question

On each eligible represented bout from 1989/01 through 2026/11, before the
result is used to update the ratings:

- does production Elo89 select the winner more often than chance?
- does the higher-chii rule select the winner more often than chance?
- does production Elo89 select the winner more often than the higher-chii
  rule on their common eligible bout population?

“Best” in this proposal means best categorical winner selector among these
three declared rules only. It does not mean best possible sumo model, best
probability model, or best betting strategy.

The compound primary hypothesis consists of two paired claims:

```text
H1: production Elo89 accuracy - higher-chii accuracy > 0
H2: higher-chii accuracy - 0.5 > 0
```

The proposed three-way ordering is confirmed only if both claims meet their
predeclared criteria on the same declared interval. If either point estimate
is at or below zero, the proposed ordering is contradicted on that record. If
both point estimates have the proposed sign but either uncertainty criterion
is unmet, the result is inconclusive rather than confirmed.

## Frozen evaluation

The declared primary evaluation shall use:

- a frozen History beginning at 1989/01 and ending at 2026/11;
- the exact archive path and SHA-256 recorded in the output manifest;
- the canonical accepted Elo89 entrant prior selected by
  `src.analysis.elo89.config.ACCEPTED_PRIOR_PATH`;
- the production divisional-K configuration;
- `q=400`;
- the production persistence and whole-population mean-preservation policies;
- the production W/L eligibility rule; and
- forecasts emitted before the current result updates either rating.

The intended source is:

```text
files/output/Historys/1989_01 to 2026_11.zip
```

The runner must reject a source whose represented interval differs from the
declared interval unless the caller explicitly supplies a different
`--evaluation-start` or `--evaluation-end`. Any such run is a separate
result and its filenames must contain its actual evaluation interval.

This is a retrospective evaluation. The accepted entrant prior was fitted
using historical information from the broad period being scored. The result
can establish descriptive historical superiority on the declared record; it
must not be described as a prospective or out-of-sample validation.

## Model identity and date-range semantics

Every comparison must use one and the same production Elo89 definition,
including its initial values. “Elo89” means the model loaded through the
production paths named above:

- the same accepted entrant-prior file and its exact values;
- the same divisional-K configuration;
- the same `q`;
- the same persistence rule;
- the same population-mean preservation; and
- the same W/L bout eligibility.

The runner must hash and record these inputs. It must not refit the prior,
substitute Basic Elo or `B_kP`, choose a different initial-value table for a
subgroup, or tune the model after seeing comparison results.

The model replay always begins at 1989/01, even when the requested evaluation
range begins later. A later `--evaluation-start` filters which already
chronological forecasts are scored; it does not reset ratings, reinitialise
the population, discard earlier updates or create a new model. Thus a
2000/01–2010/11 evaluation, for example, uses the state reached after replaying
all eligible bouts from 1989/01 through 1999/11 with the same frozen initial
values.

The default evaluation range is:

```text
1989/01 through 2026/11, inclusive
```

and therefore scores the complete frozen post-1988 record. Date-range
comparisons, division results, rolling windows and all other subgroups must be
derived from the single replay rather than produced by separate Elo-like
models.

## Shared bout population

The comparison shall start from one production Elo89 replay:

```python
run = replay_elo89(...)
```

Each `Forecast` already contains:

- basho and day;
- both rikishi IDs;
- both pre-bout ratings;
- both same-basho chii;
- the pre-bout Elo89 probability;
- the recorded winner; and
- the update parameters and post-bout values.

Using these forecasts makes the Elo chronology and bout eligibility
authoritative. The chii rule must be evaluated on those same forecast rows,
not by making an independent second bout selection.

The production replay already excludes fusen and draws. The comparison must
record those source exclusions from the Elo89 run manifest rather than infer
them again downstream.

## Winner-selection rules

### Elo89

For each forecast:

- select rikishi A if `probability_a_wins > 0.5`;
- select rikishi B if `probability_a_wins < 0.5`;
- declare no Elo89 selection if the probability is exactly 0.5.

The comparison must use the unrounded probability or pre-bout float ratings.
Displayed decimal odds and rounded ratings must never determine the selection.

### Higher chii

For the same forecast:

- select the rikishi with the lower canonical `Chii.ordinal()`;
- declare no chii selection if the ordinals are equal;
- declare no chii selection if either chii is unavailable.

No display-string comparison or East/West tie-break is permitted.

### Random choice

Random choice is represented analytically by expected accuracy 0.5. The
primary comparison does not need to simulate arbitrary coin flips. A
basho-block bootstrap may be used to estimate the uncertainty of an observed
rule’s difference from 0.5 while respecting the declared grouping.

## Primary matched domain

The primary Elo89-versus-chii comparison includes only rows on which both
rules select a side. This guarantees a common denominator.

The report must also give a population flow table:

| Stage | Count |
|---|---:|
| Raw represented results | |
| Production Elo89 eligible W/L forecasts | |
| Elo89 exact-rating ties | |
| Missing chii | |
| Equal chii | |
| Primary common-domain bouts | |

The excluded rows must remain available as diagnostics. They must not be
silently assigned to either rule.

## Primary estimand

For each common-domain bout (i), define:

```text
E_i = 1 if Elo89 selected the winner, otherwise 0
C_i = 1 if higher chii selected the winner, otherwise 0
D_i = E_i - C_i
```

The primary estimand is:

```text
mean(D) = Elo89 accuracy - higher-chii accuracy
```

reported as a percentage-point difference.

The report must include the paired two-by-two table:

| Outcome | Count |
|---|---:|
| Both correct | |
| Elo89 correct, chii wrong | |
| Elo89 wrong, chii correct | |
| Both wrong | |

This table shows where the difference comes from and prevents two marginal
percentages from being mistaken for a paired comparison.

## Uncertainty and decision rule

The primary uncertainty method shall resample complete basho blocks with
replacement. Individual bouts within a basho must remain together. Use a
fixed seed and at least 10,000 bootstrap replicates, recorded in the manifest.

Report:

- Elo89 accuracy;
- higher-chii accuracy;
- each rule’s difference from 50%;
- the paired Elo89-minus-chii accuracy difference;
- a two-sided 95% bootstrap interval for each difference; and
- the one-sided 95% lower bound for Elo89 minus chii.

The predeclared superiority conclusion is:

> Production Elo89 is historically more accurate than higher chii on the
> declared matched population if the one-sided 95% lower bound for
> `mean(D)` is greater than zero.

The higher-chii-over-random conclusion uses the analogous one-sided 95% lower
bound for `higher-chii accuracy - 0.5`. The complete proposed ordering is
confirmed only when both lower bounds are above zero.

Also report the exact McNemar/binomial result on the two discordant cells as a
secondary paired diagnostic. The bootstrap result remains primary because
bouts within a basho should not be treated as independent observations.

If the observed point estimate favours Elo89 but the lower bound is not above
zero, the conclusion must be “observed advantage not confirmed”, not
“Elo89 is best”.

## Secondary results

The following are descriptive and must not replace the primary all-bout
decision:

- Makuuchi, Juryo, Makushita, Sandanme, Jonidan and Jonokuchi;
- cross-division bouts;
- by-basho accuracy and paired difference;
- rolling 6-, 12- and 24-basho paired differences;
- rating-maturity bands based on the smaller prior rated-bout count;
- bouts where Elo89 and chii select different rikishi; and
- the frequency with which Elo89 agrees with chii.

Subgroup intervals are diagnostic. No subgroup-specific superiority claim is
predeclared, and no multiple-testing correction is required unless later work
promotes a subgroup question to a confirmatory claim.

## Probability-score boundary

Categorical accuracy discards the magnitude and calibration of a forecast.
A 50.1% and a 90% forecast make the same winner selection. The matched report
must therefore retain, as context:

- mean Elo89 log loss;
- mean Elo89 Brier loss;
- the corresponding 50–50 values; and
- an explicit statement that chii has not been fitted as a probability model.

Do not represent the higher-chii rule as probabilities 1 and 0 merely to
compare proper scores. That would test unjustified certainty rather than the
winner-selection rule proposed here.

## Proposed implementation

Extend `src.analysis.chii_prediction` with:

```text
comparison.py
compare_elo89.py
comparison_output.py
```

Suggested command:

```powershell
python -m src.analysis.chii_prediction.compare_elo89 `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --evaluation-start 1989/01 `
  --evaluation-end 2026/11
```

The implementation should call the production replay and load the production
prior/configuration through their public paths. It must not copy Elo89 update
logic into the comparison package or consume the older `B_kP` forecast
ledger as a substitute for current production Elo89.

## Outputs

Write a retained directory whose name contains the actual interval:

```text
files/output/analysis/chii_prediction/
  elo89_vs_chii_1989_01_to_2026_11/
```

Required files:

- `manifest.json` — source hashes, model inputs, interval, exclusions,
  bootstrap settings and artifact names;
- `bout_comparison.csv` — one row per production Elo89 forecast, including
  both selections, correctness flags and exclusion reason;
- `summary.csv` — primary and population-level counts and accuracies;
- `discordance.csv` — the paired two-by-two counts;
- `by_basho.csv` — counts, accuracies and paired difference by basho;
- `rolling.csv` — declared rolling-window results;
- `report.md` — the human-readable result and qualified conclusion; and
- optionally, a compact chart of cumulative or rolling paired accuracy
  difference.

The bout file may be large, but it is the audit trail required to reproduce
every aggregate and inspect disagreements.

## Tests

Focused tests must cover:

1. Elo89 forecasts are evaluated before their result update.
2. The chii decision uses `ordinal()`, not display strings.
3. East/West and participant-A/B orientation do not change either result.
4. Exact Elo89 ties are excluded without a tie-break.
5. Equal and missing chii are excluded without a tie-break.
6. Fusen and draws remain excluded by the production selection.
7. The common domain uses one identical bout denominator.
8. All four discordance cells are counted correctly.
9. The paired difference equals the marginal accuracy difference.
10. Basho-block resampling keeps complete basho together and is deterministic
    for the fixed seed.
11. Division and cross-division populations partition the primary total.
12. Manifest hashes and the actual represented interval are preserved.
13. A synthetic case can make Elo89 superior, inferior or tied and produces
    the corresponding decision.
14. A later evaluation start does not change any pre-window rating or forecast
    state and does not reload different initial values.
15. The complete ordering is confirmed only when both
    `Elo89 > higher chii` and `higher chii > 50%` meet their predeclared
    criteria.

Run the existing chii tests as regression coverage:

```powershell
python -m pytest tests/test_chii_prediction.py
```

Add the matched-comparison coverage in:

```text
tests/test_elo89_chii_comparison.py
```

## Acceptance criteria

The work is complete when:

1. current production Elo89 and higher chii are evaluated on one frozen,
   identical bout population;
2. the exact interval, source and model hashes are recorded;
3. categorical accuracy, exclusions and the paired discordance table are
   reproducible from the bout artifact;
4. the predeclared basho-block superiority rule has been applied;
5. the outcome of the complete three-way ordering has been stated;
6. every range and subgroup uses the same production Elo89 definition,
   initial values and 1989/01 replay origin;
7. proper-score and retrospective-evidence qualifications are present;
8. focused and existing regression tests pass; and
9. [Findings](Findings.md) is updated with the result rather than leaving the
   comparison described as deferred.

## Interpretation limits

Even a confirmed result would establish only that production Elo89 selected
more winners than higher chii over the represented post-1988 historical
record. It would not establish:

- that Elo89 is the best possible rating or prediction model;
- that it is superior under every probability score or betting rule;
- that its fitted entrant prior generalises prospectively;
- that either rule is independent of the JSA’s adaptive matchmaking; or
- that the same ordering holds before 1989, where lower-division history is
  incomplete.

The intended conclusion is deliberately narrower and useful:

> Among random choice, higher chii and production Elo89, production Elo89 is
> the most accurate historical winner-selection rule on the declared matched
> post-1988 bouts, if and only if the predeclared paired superiority criterion
> is met.
