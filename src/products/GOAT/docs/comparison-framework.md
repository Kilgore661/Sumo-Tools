# GOAT comparison framework

## Status

This is a prototype framework for asking measurable questions about possible
GOAT candidates. It does not define a GOAT score, prescribe how inconsistent
evidence should be resolved, or claim that any factor measures true ability.

The discussion began with Taiho and Hakuho because they are commonly treated
as the leading pair, but the framework applies to any pair of represented
Yokozuna.

## Pairwise comparison

For candidates `X` and `Y`, present the same factual and descriptive values
side by side. The comparison may include:

- achievement;
- opportunities and achievement rates;
- the banzuke levels of opponents actually faced;
- the proportion of actual opponents at Yokozuna or Ozeki; and
- opponents' form entering the basho.

Differences between `X` and `Y` are derived views of the rikishi values, not
new metrics. The canonical producer output remains one row per rikishi. There
is no need to materialize every possible pair merely to duplicate those rows;
a spreadsheet or website prototype can select any two candidates.

Candidate identity must use rikishi ID as well as shikona because names can be
reused. Comparisons must expose metric-specific coverage limitations,
particularly for careers truncated by the January 1958 data epoch.

## Neutral factor identifiers

Avoid interpretive names such as `quality of opposition`. Factors receive
stable neutral identifiers and exact definitions. The first proposed set is:

| ID | Definition |
|---|---|
| `F1` | Number of Makuuchi `Y` markers. |
| `F2` | `F1` divided by Makuuchi-banzuke basho. |
| `F3` | Arithmetic mean of opponents' banzuke-level indices in contested Makuuchi bouts. |
| `F4` | Proportion of contested Makuuchi bouts against Yokozuna or Ozeki. |
| `F5` | Arithmetic mean of opponents' pre-basho trailing three-basho `W` rates. |
| `F6` | `F5` restricted to Yokozuna-or-Ozeki opponents. |

These identifiers are provisional until adopted, but once published they must
remain stable. A rejected factor is retired rather than removed and followed
by renumbering.

Every factor definition must state:

- its formula, unit, numerator and denominator;
- included divisions, basho and bouts;
- date and completeness requirements;
- fusen and absence treatment;
- missing-value behaviour;
- the direction of the numerical ordering, without claiming that this settles
  GOATness; and
- important limitations.

The product may therefore state that `X` has a larger or smaller `F6` than
`Y`. It must not silently rename `F6` as true opposition strength.

## Current calculations

The current CSV producer supplies the components needed for `F1` through `F6`.
The relevant Taiho and Hakuho values are:

| Observation | Taiho | Hakuho |
|---|---:|---:|
| Makuuchi yusho (`F1`) | 32 | 45 |
| Makuuchi-banzuke basho | 69 | 103 |
| Makuuchi yusho rate (`F2`) | 46.38% | 43.69% |
| Mean opponent banzuke-level index (`F3`) | 3.6617 | 3.7688 |
| Contested Makuuchi bouts | 878 | 1,276 |
| Bouts against Yokozuna or Ozeki | 224 | 319 |
| Proportion against Yokozuna or Ozeki (`F4`) | 25.51% | 25.00% |
| Mean opponent trailing three-basho `W` rate (`F5`) | 54.72% | 54.36% |
| Mean Y/O-opponent trailing three-basho `W` rate (`F6`) | 63.03% | 59.07% |

There were no unavailable trailing-form observations in these Taiho or Hakuho
aggregates.

## What the present evidence says

The number of Yokozuna and Ozeki on a banzuke is not a rikishi's actual
schedule. Stable structure, heya restrictions and normal torikumi decisions
mean that a Yokozuna does not necessarily face every available Ozeki or other
Yokozuna. Actual contested bouts are therefore used.

Taiho and Hakuho faced Yokozuna-or-Ozeki opponents in essentially the same
proportion of their contested Makuuchi bouts: 25.51% and 25.00%. The elite-rank
opponents whom Taiho actually faced had the higher mean pre-basho trailing
three-basho `W` rate: 63.03% against 59.07%.

This supports the narrow descriptive statement that Taiho's actual Y/O
opponents entered with stronger recent records. It does not establish that
Taiho's entire era possessed greater absolute ability.

## Interpretation limits

The banzuke gives an ordinal statement: a better chii denotes a formally
better-ranked rikishi. The consecutive level index is the simplest transparent
encoding, but its arithmetic mean conventionally treats adjacent levels as
equal steps. A different monotonic numerical encoding could change a mean.

Trailing form is calculated before the current basho:

```text
W in the preceding three non-cancelled banzuke
------------------------------------------------
scheduled opportunities in those three banzuke
```

Absences consume opportunities and `FS` does not count as `W`. The measure has
no Yokozuna/Ozeki expectation adjustment.

Sumo results are largely zero-sum. Recent win rates can show which candidates
faced the in-form rikishi of their own eras, but cannot identify the absolute
ability of one era relative to another. The measure is also endogenous: a
dominant rikishi lowers his opponents' recent rates by defeating them. A lower
opponent-form value can therefore reflect the candidate's own dominance as
well as the form of his opposition.

These caveats are part of each comparison, not reasons to combine the factors
into a compensating score.

## Prototype role

The framework is intended to reveal useful questions. Spreadsheet inspection
comes first. If a pairwise comparison exposes a question that the retained
facts cannot answer, the factual or descriptive producer can be extended. A
factor should enter a later GOAT-o-Matic prototype only after its definition
and output have proved informative in these comparisons.
