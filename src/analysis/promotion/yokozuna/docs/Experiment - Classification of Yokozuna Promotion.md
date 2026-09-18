# Retrospective classification of yokozuna promotion

## Purpose

This experiment develops a feeling for the competitive-results component of
yokozuna promotion. It begins with the conventional benchmark of two
consecutive Makuuchi championships while ranked at ozeki, then asks how well
progressively broader championship-result categories describe observed
promotion decisions.

The Japan Sumo Association describes the Yokozuna Deliberation Council's
internal criteria as outstanding dignity and ability, together with two
consecutive championships as an ozeki or equivalent strong results. See the
[JSA explanation](https://www.sumo.or.jp/Entertainment/quiz/1081). The present
experiment can examine results, rank and chronology. It cannot measure dignity
or reconstruct the deliberative reasons for a decision.

This is therefore exploratory retrospective classification. It is not an
attempt to discover a hidden automatic rule, determine whether individual
decisions were correct, or recommend a promotion policy.

## Symbols and observation unit

Each Makuuchi result is placed in one mutually exclusive championship category:

| Symbol | Meaning |
|---|---|
| `Y` | Yusho |
| `D` | Doten-yusho: a losing participant in a playoff for the leading score |
| `J` | Non-playoff jun-yusho at the second-highest distinct score |
| `N` | No `Y`, `D` or `J` marker |

The source markers are used as recorded. `N` means a known result without one
of the three markers; it does not mean missing evidence. Detailed playoff bouts
are not required because `Y` and `D` identify the relevant participants.

The observation unit is a rikishi at a particular post-basho promotion
boundary, not a distinct person. Opportunities can overlap. The outcome is
whether the rikishi appears at yokozuna on the next supplied banzuke. Entry at
yokozuna is inferred from adjacent banzuke rather than announcement dates.

For the pair experiment, both evidence basho must be at ozeki. For the triple
experiment, the final two evidence basho must be at ozeki and the earliest is
Makuuchi context at any rank. Requiring ozeki rank in all three would remove
rapid promotions and answer a different question. Every one of the 31 fully
observed pair-sample promotions was at ozeki in both immediately preceding
basho.

Consecutive means consecutive held basho in History. Cancelled tournaments are
not inserted, and May 2011 remains a supplied held basho. An absent next rank
or banzuke is unresolved rather than a negative result. Championship playoff
wins do not add to the scheduled-basho record.

## Boundary evidence and samples

History begins in January 1958. Wakanohana's March 1958 promotion would
otherwise lack its first evidence basho. The pair experiment includes the
following evidence supplied by the user:

| Basho | Rank | Record | Marker | Source |
|---|---|---:|---|---|
| November 1957 | Ozeki | 12-3 | `J` | User supplied |
| January 1958 | Ozeki | 13-2 | `Y` | History |

The supplement is attributed in every artifact and does not modify History.
It makes March 1958 the first scoreable pair-sample promotion banzuke and gives
the pair experiment 31 observed promotions. The generated pair run contains
1,255 resolved opportunities and 19 unresolved opportunities through September
2026.

A triple for Wakanohana would also require September 1957, which has not been
supplied. The triple experiment therefore starts with the July 1958 promotion
banzuke and has 30 observed promotions. Its recorded run contains 1,252
resolved opportunities and 19 unresolved opportunities. The same-sample pair
comparison in the triple artifact uses exactly these boundaries, so it differs
slightly from the full 31-promotion pair experiment.

## Classification and metrics

A selected sequence predicts promotion. A selected sequence followed by
promotion is a true positive (TP); a selected sequence without promotion is a
false positive (FP). An actual promotion whose sequence is not selected is a
false negative (FN). The much larger true-negative population is not required
for the reported metrics.

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2TP / (2TP + FP + FN)
```

F1 weights false positives and false negatives symmetrically. That is useful
for a common descriptive comparison, but it does not assert that the two errors
have equal institutional cost. Yokozuna promotion is permanent, which may make
precision particularly important in another analysis.

## The initial rule ladder

The first classifiers retain the literal `YY` benchmark and add specified
two-basho sequences. Results below use the complete 31-promotion pair sample.

| Classifier | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| `YY` | 12 | 0 | 19 | 100.00% | 38.71% | 55.81% |
| `YY ∪ DY` | 13 | 2 | 18 | 86.67% | 41.94% | 56.52% |
| `YY ∪ YD` | 13 | 1 | 18 | 92.86% | 41.94% | 57.78% |
| `YY ∪ DD` | 13 | 1 | 18 | 92.86% | 41.94% | 57.78% |
| `{Y,D}²` | 15 | 4 | 16 | 78.95% | 48.39% | 60.00% |
| `{Y,D,J}²` | 28 | 50 | 3 | 35.90% | 90.32% | 51.38% |

The literal rule is perfectly precise in this sample but captures only 12 of
31 promotions. A doten-yusho is not a uniform substitute for a championship:
the three additional `DY` opportunities are Wakanohana's 11-4 D followed by
14-1 Y, Kakuryu's 14-1 D followed by 14-1 Y, and Takakeisho's 12-3 D followed
by 12-3 Y. Only Kakuryu was promoted.

Admitting every jun-yusho combination raises recall to 90.32% but creates 50
false positives. `JJ` is especially weak: two promotions and 23
non-promotions. The three promotions still missed by `{Y,D,J}²` are Kashiwado
(`ND`), Tochinoumi (`YN`) and Tamanoumi (`ND`).

## Exhaustive pair partitions

The four symbols form 16 ordered pairs. A pair classifier is any subset of
those cells, so there are `2^16 = 65,536` possible classifiers. The pair
program evaluates all of them and retains every tied maximum.

The complete cell table is shown as `TP/FP`, with the first result on the rows
and the second result on the columns:

| First \ second | `Y` | `D` | `J` | `N` |
|---|---:|---:|---:|---:|
| `Y` | 12/0 | 1/1 | 2/5 | 1/52 |
| `D` | 1/2 | 1/1 | 0/4 | 0/13 |
| `J` | 7/9 | 2/5 | 2/23 | 0/80 |
| `N` | 0/57 | 2/14 | 0/85 | 0/873 |

Two partitions tie at the maximum F1 of **66.67%**:

| Included cells | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| `YY, YD, DD, JY` | 21 | 11 | 10 | 65.63% | 67.74% | 66.67% |
| `YY, YD, DY, DD, JY` | 22 | 13 | 9 | 62.86% | 70.97% | 66.67% |

`DY` is exactly neutral at the optimum: it contributes one promotion and two
non-promotions. Adding it trades one FN for two FP without changing F1.

The `N` cells confirm the broad expectation but preserve important exceptions.
`NN` contains no promotions among 873 resolved opportunities. Across every
cell containing `N`, there are only three promotions against 1,174
non-promotions. Consequently, no `N` cell belongs to a maximum-F1 pair
partition. This does not mean that an unmarked basho historically precluded
promotion; the optimizer sacrifices rare exceptions to avoid their very large
cells.

## Exact triple optimization

The four symbols form 64 ordered triples and therefore `2^64` possible cell
subsets. The program does not enumerate those 18.4 quintillion subsets.
Instead, it uses an exact property of F1.

Suppose a selected partition has `T` true positives and `F` false positives,
and the sample contains `P` actual promotions:

```text
F1 = 2T / (P + T + F)
```

Adding a cell with `t` promotions and `f` non-promotions improves F1 exactly
when:

```text
t / (t + f) > F1 / 2
```

At an optimum, cells above that promotion-rate threshold must be included,
cells below it must be excluded, and cells exactly on it are optional. Sorting
the non-empty cells by promotion rate and evaluating the finite thresholds
therefore finds the same exact optimum as considering every subset separately.
Empty cells have no effect on the observed score and remain unidentified.

## Triple results

The best observed triple partition contains nine cells, ordered from oldest to
newest:

| Triple | TP | FP | Promotion rate |
|---|---:|---:|---:|
| `YYJ` | 1 | 0 | 100.00% |
| `YJJ` | 2 | 1 | 66.67% |
| `JYY` | 2 | 0 | 100.00% |
| `JDD` | 1 | 0 | 100.00% |
| `JJY` | 4 | 3 | 57.14% |
| `NYY` | 10 | 0 | 100.00% |
| `NYD` | 1 | 0 | 100.00% |
| `NDY` | 1 | 1 | 50.00% |
| `NJD` | 2 | 3 | 40.00% |

There are no optional non-empty cells at the optimum. Seventeen triple cells
are empty, so their treatment cannot be learned from this sample. Ignoring
empty-cell toggles, the optimum is observationally unique.

For a fair comparison, the triple artifact re-optimizes the pairs on the same
30-promotion, three-basho-eligible sample:

| Model | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Best pair partition | 21 | 13 | 9 | 61.76% | 70.00% | 65.62% |
| Best triple partition | 24 | 8 | 6 | 75.00% | 80.00% | **77.42%** |

The triple representation improves in-sample F1 by **11.80 percentage points**,
captures three additional promotions and produces five fewer false positives.
The six missed promotions are Kashiwado (`NND`), Tochinoumi (`NYN`), Tamanoumi
(`YND`), Hokutoumi (`NYJ`), Kisenosato (`NJY`) and Hoshoryu (`NJY`).

The improvement is descriptive, not necessarily substantive. Several selected
cells contain only one or two observations. The optimizer accepts `JJY` but
rejects `NJY`, thereby missing the recent promotions of Kisenosato and Hoshoryu.
This may reflect sparse cells and era-specific practice rather than a stable
meaning of "equivalent".

## Historically false "obvious" constraints

The cases are at least as informative as the maximum scores. Several
conditions that may sound indispensable to a modern observer are not
historically necessary in this sample:

- An actual yusho in the final two basho was not required.
- A `Y`, `D` or `J` marker in both immediately preceding basho was not required.
- At least 12 wins in each basho was not required.
- At least 11 wins in each basho was not required.
- A yusho in the final basho was not required.

Three promotions contain 11 wins or fewer in one of the two immediately
preceding basho:

| Rikishi | Results | Promotion banzuke |
|---|---|---|
| Asashio | 11-4 J, 13-2 J | May 1959 |
| Kashiwado | 11-4 N, 12-3 D | November 1961 |
| Tamanoumi | 10-5 N, 13-2 D | March 1970 |

Tamanoumi is the only observed promotion with fewer than 11 wins in either
basho. Tochinoumi supplies another unmarked example: 14-1 Y followed by 13-2 N
before promotion in March 1964.

These facts should not be converted into a claim that almost any result could
qualify. They show that simple categorical preclusions do not describe the
whole historical record.

## Interpretation, era and scores

The pair and triple results point to two missing axes.

First, marker categories suppress score quality. A 14-1 doten-yusho and an
11-4 doten-yusho receive the same `D`, although the cases suggest that they may
not have carried the same promotion significance. Adding record thresholds is
a natural subsequent experiment, provided that thresholds are declared and
reported transparently rather than searched without limit.

Second, one rule across 1958-2026 may average together changing practice. The
early unmarked promotions, the notably strict sequence of literal consecutive-
yusho promotions, and later equivalent-performance promotions all make era a
plausible explanatory axis. Era boundaries should be justified by documented
institutional history or policy rather than chosen solely to improve F1.

There is also a possible institutional interpretation, which must remain
properly caveated. From the perspective of a non-Japanese observer without
specialist expertise in the JSA's institutional history, it is tempting to
wonder whether earlier promotion practice reflected different expectations of
transparency and public accountability. The results establish neither that
interpretation nor the motives behind individual decisions; they show only
that historical outcomes do not consistently satisfy several conditions that
modern observers might assume were indispensable. Stronger claims require
contemporary historical sources.

## In-sample fit and held-out performance

Every maximum reported here is selected and scored on the same history. The
pair search examines all 65,536 pair partitions, while the triple search has
greater flexibility and many sparse cells. Their maximum F1 values are
therefore optimistic descriptions of this sample.

Held-out performance would require selecting a partition on one period,
freezing it, and applying it to observations that played no part in selection.
A chronological split or forward-chaining design would be more appropriate
than a random split because promotion practice may change with time. With only
30 or 31 promotions, any held-out estimate would be noisy; poor transfer could
represent either statistical overfitting or genuine institutional change.

The threshold method is unrelated to held-out testing. It is an exact
computational shortcut for finding the in-sample F1 optimum over all triple
partitions; it is not a sampling method or a generalization estimate.

## Implementation and reproduction

The implementation is divided into three modules:

- `evaluate_rule.py` evaluates the named initial pair classifiers and retains
  case-level evidence.
- `score_partitions.py` builds all resolved pair opportunities and exhaustively
  scores the 65,536 pair partitions.
- `score_triples.py` builds triple contexts, performs exact threshold
  optimization and compares triples with pairs on the identical sample.

Run the pair and triple searches from the repository root:

```powershell
python -m src.analysis.promotion.yokozuna.score_partitions
python -m src.analysis.promotion.yokozuna.score_triples
```

Both commands show progress, print a human-readable summary and write a UTC
timestamped JSON artifact beneath
`files/output/analysis/promotion/yokozuna/`. Output paths are fixed and cannot
be changed through the CLI.

This write-up records pair run `20260917T183135372620Z_partitions.json` and
triple run `20260917T203049743016Z_triples.json`. Generated output is outside
version-controlled source; the tables above preserve the reported results.
Rerunning against a changed History snapshot may change them.

Focused synthetic checks cover rank eligibility, marker direction, all pair
combinations, the Wakanohana supplement, exhaustive pair maximization, exact
triple threshold optimization and neutral boundary cells.

The archived official JSA banzuke supplement that motivated part of this work
is available at
[`docs/JSA/betsuhyo201607en.pdf`](../../../../../docs/JSA/betsuhyo201607en.pdf).
