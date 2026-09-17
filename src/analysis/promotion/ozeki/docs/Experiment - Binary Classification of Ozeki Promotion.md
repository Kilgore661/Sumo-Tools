# Retrospective evaluation of rule-based classifiers for ozeki promotion

## Purpose

This experiment uses binary classification to develop a feeling for the
relationship between tournament results and ozeki promotion. Its purpose is
exploratory: it does not attempt to discover a hidden promotion rule or to
decide whether particular JSA decisions were correct.

The starting point is the conventional benchmark of 33 wins over three
consecutive basho at komusubi or sekiwake. We call this a benchmark rather
than an official, automatic qualification rule. We compare a small set of
simple variations with observed promotion decisions.

## The Xn classifiers

Each classifier has a letter **X** and a number **n**. The number is the
minimum total of wins across the three preceding consecutive held basho.
The letter specifies the other conditions:

| Family | Rank conditions | Additional win condition |
|---|---|---|
| A | All three basho at komusubi (K) or sekiwake (S) | None |
| B | First basho at maegashira (M), K or S; following two at K or S | None |
| C | All three basho at K or S | At least 10 wins in each basho |

Thus A33 represents the conventional benchmark. B32 permits a maegashira
start and requires at least 32 wins overall. C33 retains 33 wins overall
and rejects any run containing fewer than ten wins in a basho. None of these
classifiers requires a championship, a particular opponent, or a winning
record in each basho beyond the conditions explicitly stated above.

The seven candidates examined are A31, A32, A33, B31, B32, B33 and C33.
They were explored on the same historical sample; this was not a preregistered
test or an exhaustive search for the best possible classifier.

## Data, observation unit and exclusions

The source is the Sumo-Tools live History, covering 411 held basho from
January 1958 through September 2026 in the recorded run. The earliest
promotion banzuke included in scoring is **July 1958**, whose preceding
three basho are January, March and May 1958. The final observed outcome is
the September 2026 banzuke; results from that basho are not needed to determine
whether a promotion onto that banzuke occurred.

The observation unit is a **rikishi's promotion opportunity at a particular
banzuke boundary**, not a unique person. Overlapping three-basho runs count
separately. Promotion is inferred from entry into ozeki on the next banzuke,
not from the date of a JSA announcement. All qualifying promotion events
belong to one population, regardless of previous tenure at ozeki.

Immediate reinstatements under the ozekiwake provision are excluded. The
implementation identifies them as an O-to-S-to-O sequence across successive
held basho, with at least ten wins in the intervening sekiwake basho. Eight
such events are excluded in this source period. There are **71 retained
promotion events** in the scoring period.

Wins include fusensho. Championship playoff wins are excluded. Consecutive
means consecutive supplied held basho: cancelled March 2011 and May 2020
are not inserted, and May 2011 is included. The input is assumed to contain
every held basho between its endpoints. Core rank values, including annotated
ranks, determine rank eligibility.

An earlier exploratory promotion audit included Kotogahama's May 1958
promotion using the user's supplied November 1957 record (S, 10-5). That
case is **outside this experiment's July 1958 cutoff**. It accounts for the
earlier audit's 72 promotions and 43 A33 true positives, versus 71 and 42 here.
The two pre-1958 basho needed to assess the earliest 1958 opportunities have
not been reconstructed for this experiment.

## Classification and scoring

A classifier predicts promotion when its conditions are met. The observed
outcome is whether promotion occurred on the following banzuke.

| | Promoted | Not promoted |
|---|---|---|
| Meets classifier | True positive (TP) | False positive (FP) |
| Does not meet classifier | False negative (FN) | True negative (TN) |

The evaluator combines the observed promotion events with all observed
qualifying windows. It does not enumerate the much larger true-negative
population; TN is not required for precision, recall or F1. Missing next
rank/banzuke is unresolved, not a negative outcome.

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2TP / (2TP + FP + FN)
```

Precision asks how often a predicted promotion happened. Recall asks how
many actual promotions the classifier captures. F1 is their harmonic mean.
For this experiment it provides a common summary of the tradeoff between
missed promotions and predictions that did not lead to promotion. It does
not establish which kind of error should matter more for another purpose.
The implementation reports 0.0 for a metric with a zero denominator; none
of the seven reported comparisons needs that convention.

## Results

| Classifier | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| **A32** | **51** | **9** | **20** | **85.00%** | **71.83%** | **77.86%** |
| B33 | 51 | 12 | 20 | 80.95% | 71.83% | 76.12% |
| B32 | 60 | 27 | 11 | 68.97% | 84.51% | 75.95% |
| A31 | 55 | 23 | 16 | 70.51% | 77.46% | 73.83% |
| A33 | 42 | 4 | 29 | 91.30% | 59.15% | 71.79% |
| B31 | 64 | 55 | 7 | 53.78% | 90.14% | 67.37% |
| C33 | 29 | 1 | 42 | 96.67% | 40.85% | 57.43% |

**A32 has the highest F1 of the seven candidates: 77.86%, compared with
71.79% for A33, a difference of 6.07 percentage points.** Lowering A's
threshold from 33 to 32 captures nine more actual promotions at the cost of
five additional false positives. Lowering it again to 31 captures four
more promotions but adds fourteen false positives, reducing F1.

Allowing a maegashira start at 33 wins captures nine additional promotions
but adds eight false positives. At 32 and 31 wins, the broader B condition
admits increasingly many runs that did not lead to promotion.

C33 has the highest precision but the lowest recall and F1. Requiring ten
wins in every basho removes three of A33's false positives, but also loses
thirteen of its true positives.

## Cases that help interpret the totals

A33's 29 false negatives separate into 20 promotions with fewer than 33
wins, all at K/S, and nine with at least 33 wins but a maegashira start.
There is no overlap between these groups. In every maegashira case, only
the first basho was outside K/S. The 20 lower totals consist of nine at
32 wins, four at 31, five at 30 and two at 28.

A33's four false positives involve three rikishi:

| Rikishi | Run ending | Wins by basho | Total |
|---|---|---|---:|
| Miyabiyama | July 2006 | 10, 14, 10 | 34 |
| Miyabiyama | September 2006 | 14, 10, 9 | 33 |
| Baruto | January 2010 | 12, 9, 12 | 33 |
| Takakeisho | January 2019 | 9, 13, 11 | 33 |

All remained sekiwake on the next banzuke. Miyabiyama's overlapping July
and September windows are separate opportunities. His July window is the
single false positive remaining under C33.

## Interpretation and limits

The simple classifiers do not completely describe the observed decisions.
That is consistent with promotion involving judgement beyond a three-basho
win total and rank sequence. Tradition, administrative concerns and changes
in practice over time are plausible influences. This experiment does not
measure those influences, demonstrate their causal effects, or prove that
no more elaborate rule could describe the decisions.

Practice might be more consistent in a recent period. We have not defined
or tested either a modern period or temporal stability, and make no claim
about them here. The same candidate conditions are applied retrospectively
throughout the sample.

The scores are **descriptive and in-sample**. Thresholds and families were
compared on the data used to score them. A32's higher F1 does not identify
the JSA's operative rule, establish a better promotion policy, or demonstrate
superior performance on unseen decisions. Overlapping windows and repeated
observations of the same rikishi also mean observations are not independent.
No significance test or confidence interval is claimed for the F1 difference.

Historical result coverage is a further limitation. Observed wins can prove
that a threshold has been reached, but missing results can conceal qualifying
windows or make an observed total too low. The figures describe the supplied
data; they are not a certification that every historical result is complete.

Conditional on F1 being a suitable descriptive measure for this exercise,
**A32 fits the observed promotion decisions better than the conventional
A33 benchmark by 6.07 percentage points**, achieving 77.86%.

## Reproduction and artifacts

From the repository root:

```powershell
python -m src.analysis.promotion.ozeki.evaluate_rule A 32
python -m src.analysis.promotion.ozeki.score_rules
```

The first command writes A32.json. The second evaluates all seven candidates
on one live History snapshot, saves Xn.json for each, and creates report.md
from the saved results. See the [package README](../README.md) for output
locations and options.

This write-up records the run `20260917T095710235912Z_rules` under
`files/output/analysis/promotion/ozeki/`. Its JSON files contain rule
definitions, coverage, confusion counts, metrics, qualifying windows and
false-negative events. Generated output lives outside version-controlled
source; the table above preserves the experiment's reported results.
Reruns against an updated live store may change them.

Eight focused checks passed during implementation, including threshold and
rank conditions, default wins, playoff exclusion, overlapping windows,
unresolved outcomes, reinstatement exclusion, JSON output, scoring and tied
winners. The seven saved results were checked for the common 71-promotion
denominator, and standalone A32 agreed with the orchestrated result.
