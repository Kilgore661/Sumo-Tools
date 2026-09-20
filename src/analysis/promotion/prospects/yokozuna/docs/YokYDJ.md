# Yokozuna prospects and YokYDJ

Promotion to Yokozuna is decided by the Japan Sumo Association following a
recommendation from the Yokozuna Deliberation Council.

The JSA describes the conditions as outstanding dignity and ability, together
with [two consecutive championships at Ozeki or equivalent excellent
results](https://www.sumo.or.jp/Entertainment/quiz/1081).

There is naturally considerable speculation about what "equivalent" means. It
is not defined by a public numerical formula, and the historical decisions do
not reveal one results rule which applies neatly across every period.

For current promotion-prospect annotations, this site uses the following
interpretation:

> Across two consecutive basho at Ozeki, one result must be a yusho and the
> other must be a yusho, doten-yusho or jun-yusho.

We call this rule **YokYDJ**.

The letters mean:

- `Y`: yusho;
- `D`: doten-yusho—a tied leading score followed by defeat in the
  championship playoff; and
- `J`: jun-yusho—the second-highest distinct score without participating in a
  championship playoff.

YokYDJ accepts `YY`, the consecutive-yusho case. It treats `YD`, `YJ`, `DY`
and `JY` as equivalent-performance cases.

This is the site's limited interpretation of the results component of the JSA
wording. It does not attempt to evaluate dignity, ability or other
circumstances considered by the JSA, and it does not claim that the JSA itself
uses YokYDJ.

## What the annotation means

YokYDJ is used only to indicate a possible route to promotion on the current
banzuke.

After a yusho at Ozeki, the annotation indicates that a yusho, doten-yusho or
jun-yusho in the forthcoming basho would satisfy YokYDJ.

After a doten-yusho or jun-yusho at Ozeki, the annotation indicates that a
yusho in the forthcoming basho would satisfy YokYDJ.

The annotation does not mean that promotion is probable, guaranteed or
officially under consideration. It identifies a results sequence which has
described recent promotion decisions reasonably well.

The annotation records the position at the start of the basho. It is not a
live remaining-results calculation and is not applied retrospectively to
historical banzuke.

## Why use YokYDJ?

From 1990 through 2012, eight consecutive promotions—from Asahifuji through
Harumafuji—followed two consecutive yusho at Ozeki. The next promotion,
Kakuryu in 2014, began a different sequence of decisions.

For this analysis, the modern evidence begins with Kakuryu's January 2014
result and covers promotion decisions from May 2014 onward.

The observed qualifying sequences are:

| Promotion banzuke | Rikishi | Sequence | Decision |
|---|---|---:|---|
| May 2014 | Kakuryu | `DY` | Promoted |
| March 2017 | Kisenosato | `JY` | Promoted |
| January 2021 | Takakeisho | `JY` | Not promoted |
| September 2021 | Terunofuji | `YJ` | Promoted |
| March 2023 | Takakeisho | `DY` | Not promoted |
| March 2025 | Hoshoryu | `JY` | Promoted |
| July 2025 | Onosato | `YY` | Promoted |

YokYDJ identifies all five promotions in this period. It also identifies two
runs, both by Takakeisho, which did not result in promotion.

`YD` is included because YokYDJ treats doten-yusho and jun-yusho as the two
recorded forms of near-championship result. No `YD` case occurred in the
selected modern period, so this part of the rule is not independently tested
by a modern observation.

## YokYDJ is not an official rule

YokYDJ is a site-defined summary of a small number of recent decisions. It is
not published JSA policy.

It does not represent:

- the strength of the individual scores;
- the quality of the opposition;
- injuries or withdrawals;
- the wider competitive circumstances;
- the number, age or expected longevity of existing Yokozuna;
- the availability of other plausible candidates;
- the institutional assessment of a rikishi's ability or dignity; or
- the reasons given—or not given—for an individual decision.

Two rikishi with the same `Y`, `D` and `J` sequence may therefore receive
different decisions.

## For the interested reader

We evaluated YokYDJ as a classifier of recorded promotion decisions.

A qualifying sequence followed by promotion is a true positive. A qualifying
sequence without promotion is a false positive. A promotion not identified by
the rule is a false negative.

For promotion decisions from May 2014 through September 2026, YokYDJ
produced:

- 5 correctly identified promotions;
- 2 qualifying sequences without promotion; and
- no missed promotions.

That gives YokYDJ:

- 71% precision;
- 100% recall; and
- an F1 score of **83%**.

F1 combines precision and recall into a single classification score. It is not
the probability that an annotated rikishi will be promoted.

These figures are encouraging but fragile. They are based on only five
promotions and seven qualifying sequences. Both non-promotion cases belong to
the same rikishi. One or two future decisions could change the percentages
appreciably.

The start of the period also matters. January 2014 was selected because it
begins Kakuryu's run, which preceded the first non-`YY` promotion after eight
consecutive `YY` promotions from 1990 through 2012. It is a transparent
historical boundary, not proof that an official policy changed on that date.

Earlier history does not follow one simple pattern. It contains non-`YY`
promotions, a long period in which every promotion was `YY`, and individual
sequences which do not fit YokYDJ. That is why this site uses YokYDJ as a
current, modern prospect indicator rather than applying it retrospectively to
every historical banzuke.

No one knows whether recent practice will continue. If several strong
candidates compete for promotion, future decisions might adhere more closely
to consecutive yusho. If incumbent Yokozuna retire and no obvious successors
emerge, equivalent-performance decisions may remain important—or promotion
practice may change in some other way. These are possibilities, not adjustments
made by YokYDJ.

Interested readers may wish to explore:

- different starting dates;
- minimum win totals within each sequence;
- distinctions between doten-yusho and jun-yusho;
- longer three-basho histories;
- periods with different numbers of active Yokozuna;
- whether repeated observations from the same rikishi should be treated
  differently; and
- contemporary accounts of the reasons for particular decisions.

Any resulting percentage is meaningful only for the chosen population,
period and rule. A pattern selected after inspecting a small sample is
exploratory evidence, not a reliable forecast of future policy.

## Scope of the analysis

The modern results cover promotion decisions from May 2014 through September
2026, using evidence beginning with the January 2014 basho. The population
contains 183 resolved post-basho decisions for rikishi with results from two
consecutive basho at Ozeki.

Both results in a qualifying pair must have been recorded at Ozeki. Results
are classified using their recorded yusho, doten-yusho and jun-yusho markers.
Promotion means appearance at Yokozuna on the immediately following banzuke.

Regular wins include fusensho and exclude playoff wins. A later promotion does
not change the classification of an earlier non-promotion decision.
