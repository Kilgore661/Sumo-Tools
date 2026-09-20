# Ozeki runs and Ozeki32

Promotion to Ozeki is decided by the Japan Sumo Association. At the time of
writing (2026), there does not seem to be a published JSA rule under which a
numerical result automatically guarantees promotion. The JSA
[publicly describes 33 wins at sanyaku as a benchmark
(*meyasu*)](https://www.sumo.or.jp/Entertainment/quiz/236), and rikishi are
traditionally expected to demonstrate sustained success over three consecutive
basho.

For this analysis, the traditional benchmark is:

> At least 33 wins over three consecutive basho, with all three basho at
> komusubi or sekiwake.

For this site, we use a slightly different rule:

> At least 32 wins over three consecutive basho, with all three basho at
> komusubi or sekiwake.

We call this rule **Ozeki32**.

An Ozeki32 indicator means that the rikishi has reached, or is attempting to
reach, this benchmark. It is an indication that the rikishi is on an Ozeki
run—not a prediction, an official announcement or a guarantee of promotion.

## Why 32 rather than 33?

We tested several simple rules against recorded promotion decisions since
1958. For each rule, we asked two questions:

1. How often did a qualifying run result in promotion on the following
   banzuke?
2. How many actual promotions did the rule identify?

An F1 score combines these two measures. A perfect rule would score 100%; a
rule which gains accuracy in one direction by performing badly in the other
receives a lower score.

Across the complete history, Ozeki32 produced:

- 51 correctly identified promotions;
- 9 qualifying runs without promotion; and
- 20 promotions which it did not identify.

That gives Ozeki32:

- 85% precision;
- 72% recall; and
- an F1 score of **78%**.

The traditional benchmark produced:

- 42 correctly identified promotions;
- 4 qualifying runs without promotion; and
- 29 promotions which it did not identify.

That gives the traditional benchmark:

- 91% precision;
- 59% recall; and
- an F1 score of **72%**.

The traditional benchmark is more conservative: when it identifies a qualifying
run, promotion is somewhat more likely. Ozeki32 identifies nine additional
promotions at the cost of five additional non-promotion cases. Its much better
coverage produces the higher overall F1 score.

Among the simple rules tested, Ozeki32 gives the best balance. That is why we
use it for the indicator.

## Ozeki32 is not an official rule

Ozeki32 describes the historical decisions reasonably well, but it does not
describe every decision. It has been broken in three different ways.

### The benchmark was reached, but promotion did not follow

The most recent case was Takakeisho. His September 2018 to January 2019
results were:

- 9 wins at komusubi;
- 13 wins at komusubi; and
- 11 wins at sekiwake.

That was 33 wins, but he remained sekiwake on the March 2019 banzuke.

### Promotion followed fewer than 32 wins

The most recent case was Onokuni:

- 9 wins at sekiwake in March 1985;
- 10 wins at sekiwake in May; and
- 12 wins at sekiwake in July.

He was promoted for September 1985 with a total of 31 wins.

No rikishi has subsequently been promoted with fewer than 32 wins when all
three basho were at komusubi or sekiwake.

### The first basho was at maegashira

Ozeki32 requires all three basho to be at komusubi or sekiwake, but the JSA has
sometimes included a strong maegashira result.

Recent examples include:

- Aonishiki, promoted in January 2026 after `M 11, K 11, S 12`; and
- Kirishima, promoted in May 2026 after `M 11, S 11, S 12`.

Here `M`, `K` and `S` mean maegashira, komusubi and sekiwake.

Both accumulated 34 wins, but neither satisfied Ozeki32 because the first
basho was at maegashira.

These are genuine exceptions. We do not extend the indicator to
maegashira-based sequences because such promotions remain unusual, and a
general maegashira indicator would identify too many unconvincing runs.

## Has promotion practice changed?

The historically motivated dividing point is different for each rule. The
before-and-after figures therefore describe the history of each rule
separately; results from the two tables should not be compared row for row.

### Ozeki32 over time

March 1985 is the beginning of Onokuni's run—the most recent promotion with
fewer than 32 wins at komusubi or sekiwake.

| Period | Promotions | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Before March 1985 | 30 | 94% | 53% | **68%** |
| March 1985 onward | 41 | 81% | 85% | **83%** |
| Complete history | 71 | 85% | 72% | **78%** |

This suggests that Ozeki32 fits post-1985 promotion practice substantially
better than the earlier history.

### The traditional benchmark over time

September 2018 is the beginning of Takakeisho's 33-win run—the most recent run
satisfying the traditional benchmark without immediate promotion.

| Period | Promotions | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Before September 2018 | 60 | 92% | 58% | **71%** |
| September 2018 onward | 11 | 88% | 64% | **74%** |
| Complete history | 71 | 91% | 59% | **72%** |

The traditional benchmark is remarkably stable around its chosen cutoff. Its
principal weakness in both periods is recall: it misses a substantial
proportion of actual promotions.

There is nothing statistically privileged about either cutoff. Each was
chosen to examine a counterexample relevant to that rule. The results may
suggest that promotion practice changed, but they do not establish the date of
an official policy change.

## For the interested reader

Only the complete-history results use exactly the same period and can be
compared directly:

| Rule | Correct promotions | Non-promotions identified | Promotions missed | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Ozeki32 | 51 | 9 | 20 | 85% | 72% | **78%** |
| Traditional benchmark | 42 | 4 | 29 | 91% | 59% | **72%** |

Ozeki32 sacrifices some precision but identifies substantially more actual
promotions, giving it the higher F1 score. This does not prove that the JSA
uses—or has ever used—a 32-win rule. It explains why this site adopts Ozeki32
as a simple and reasonably accurate definition of an Ozeki run.

Readers are encouraged to explore the historical divisions further. Possible
questions include:

- What happens if a different cutoff date is used?
- Can the history be divided into several non-overlapping periods?
- Were there periods when Ozeki32 was unusually strict, permissive or
  accurate?
- Do the exceptional decisions cluster around particular years?
- Do any apparent changes correspond to documented changes in JSA practice?

For each period, useful figures include:

- the number of observed promotions;
- qualifying runs which did not result in promotion;
- promotions not identified by Ozeki32;
- precision, recall and F1; and
- the individual rikishi behind the exceptions.

Ozeki promotions are uncommon, so moving only one or two decisions between
periods can change the results appreciably. A cutoff selected after looking at
the scores is exploratory evidence, not independent confirmation of a
historical era.

If you find a persuasive pattern—particularly one corresponding to documented
changes in promotion practice—please tell us what you found.

## Scope of the analysis

All figures use three-basho windows beginning in January 1958 or later, with
promotion outcomes observed from the July 1958 banzuke. The same population is
used for Ozeki32, the traditional benchmark, the historical partitions and every
named exception above.

The analysis contains 71 ordinary qualification promotions. A promotion means
promotion on the immediately following banzuke; a later promotion does not
change the classification of an earlier decision.

Eight immediate ozekiwake reinstatements are excluded because they use a
different mechanism. The earlier Kotogahama boundary case, which depends on a
manually supplied November 1957 result, is also excluded from every figure in
this account.

Regular wins include fusensho and exclude playoff wins. Consecutive basho means
consecutive tournaments which were actually held.
