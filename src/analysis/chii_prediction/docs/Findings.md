# Chii winner prediction and matched Elo89 validation

Initial chii baseline recorded 6 September 2026. Matched Elo89 comparison
recorded 24 November 2026.

The initial evaluation covered 1989/01–2026/07. The completed matched
comparison covers the frozen 1989/01–2026/11 record.

## Why we did this

Earlier work assessed Elo-like models against a model assigning each opponent
a 50% chance of winning. That establishes a useful reference, but overlooks
another obvious predictor: choose the rikishi with the stronger chii on the
current banzuke.

In retrospect, the natural evaluation sequence was:

1. Assume 50–50 outcomes.
2. Follow the existing chii ordering.
3. Use an Elo-like rating system.

The purpose of this probe was to fill that conceptual gap. It was not to
optimise a new model, resolve historical data discrepancies, or launch a
comprehensive comparison. The question was simply how often the winner follows
chii, overall and within each division.

The discussion also distinguished fitting known results from predicting unseen
results. A fitted model beating a baseline on its training data is a useful
sanity check, not proof of future predictive performance. This chii rule needs
no fitting: it uses the banzuke ordering for each basho and counts agreement
with that basho's recorded outcomes.

## What we did

We added the standalone `src.analysis.chii_prediction` module. For each eligible
bout it selects the stronger chii and records whether that rikishi won.
Stronger means a lower canonical `Chii.ordinal()`, including side and
annotations, rather than comparison of rank display strings.

The run used `files/output/Historys/1958_01 to 2026_11.zip`, restricted to
1989/01–2026/07: 224 represented basho. The default start is 1989 because
earlier lower-division records are incomplete. Both dates appear in every
output filename; the manifest records the source archive and its SHA-256 hash.

We reused the existing prediction bout selector, counting each W/L bout once
and accepting W/L results with blank kimarite. Defaults (FS/FP) are excluded.
Each division row requires both opponents to belong to that division.
Cross-division bouts are reported separately and included in the aggregate.
The aggregate weights bouts equally, rather than averaging division rates.

Of 582,448 recorded results, 3,022 were defaults. The remaining 579,426 W/L
bouts included 14 with equal recorded chii, despite the expectation that chii
would be unique. For example, a January 1996 bout records both opponents as
`Ms60eTD`. These 14 were excluded because the rule cannot select a stronger
chii. No bouts were excluded for missing chii or other outcomes in this run.
The resulting denominator was 579,412 bouts.

Focused checks covered participant orientation, chii ordering, population
counts, date selection, missing ranks and equal-rank exclusions. The full
historical run completed successfully.

## Results

| Population | Bouts | Stronger-chii wins | Win percentage | Above 50% (percentage points) |
|---|---:|---:|---:|---:|
| All | 579,412 | 304,984 | 52.637% | +2.637 |
| Makuuchi | 63,450 | 36,525 | 57.565% | +7.565 |
| Juryo | 41,061 | 20,963 | 51.053% | +1.053 |
| Makushita | 86,885 | 45,316 | 52.156% | +2.156 |
| Sandanme | 141,677 | 73,315 | 51.748% | +1.748 |
| Jonidan | 181,647 | 94,722 | 52.146% | +2.146 |
| Jonokuchi | 46,992 | 25,038 | 53.281% | +3.281 |
| Cross-division | 17,700 | 9,105 | 51.441% | +1.441 |

Following chii selected the winner more often than the 50% expected from random
choice, both overall and in every reported group. The aggregate advantage was
modest: 2.637 percentage points. Makuuchi had the largest observed advantage,
at 7.565 percentage points; Juryo had the smallest, at 1.053.

Here, "advantage" means win percentage minus 50%, not relative percentage
improvement, betting return, or a significance measure. No uncertainty
intervals or significance tests were calculated.

## How this relates to the earlier probability scores

Choosing the stronger chii is a winner-selection rule. If expressed literally
as a probability model, it assigns probability 1 to the stronger rikishi and
0 to the weaker. Its Brier loss is then zero for each correct selection and
one for each incorrect selection:

`mean Brier loss = 1 - win fraction`

The derived Brier score is approximately **0.473630**. For this deterministic
rule, Brier adds no information beyond the win fraction. Log loss becomes
infinite on any upset because the observed winner was assigned probability
zero. This is a consequence of asserting certainty, not of discreteness alone.

The earlier controlled Elo comparison reported:

| Probability model | Mean Brier loss (lower is better) |
|---|---:|
| Always 50–50 | 0.250000 |
| Basic Elo | 0.244687 |
| Elo with divisional update rates | 0.244355 |
| Elo with informed initial ratings | 0.242439 |
| Elo with both modifications | 0.241968 |

There is no contradiction between chii picking more winners than chance and
its literal 0/1 probabilities scoring worse than 50–50. Probability scores
penalise confidence as well as selecting the wrong side. These numbers do not
establish how often Elo's favourite wins relative to chii's favourite. A
probability function based on chii differences could be assessed with both
Brier and log loss, but no such function was fitted or evaluated here.

## Why the first probe stopped short

The earlier Elo comparison scored 574,863 W/L bouts over the same dates. Its
manifest records an older snapshot of `1989_01 to 2026_11.zip`, with 577,861
raw results and 2,998 defaults excluded. The present archive supplies 4,563
more W/L bouts before the 14 equal-chii exclusions. The current version of
the 1989 archive also has a different checksum from that saved in the Elo
manifest. Most of the count difference therefore concerns source snapshots;
the chii rule adds a small, explicit exclusion of its own. We did not identify
the individual historical revisions responsible for the source difference.

A deeper investigation of those differences, or a matched comparison of
winner-selection accuracy across chii and Elo, was deliberately deferred at
that stage as a potential rabbit hole. The initial probe sufficiently filled
its original gap: the existing rank order is an obvious baseline and shows a
modest observed advantage over random choice.

"Random, follows chii, considered ratings" is a useful conceptual progression.
At that point, the interpretation that chii lay between random choice and Elo
was only a working picture. It had not been demonstrated on a common
winner-accuracy measure. The follow-up below closes that question.

## Matched production Elo89 comparison

### Question and status

The follow-up tested the complete proposed ordering:

```text
production Elo89 accuracy > higher-chii accuracy > random-choice accuracy
```

This is a deliberately narrow comparison among three declared winner-selection
rules. It is not a search over all possible rating systems, a betting test, or
a claim that Elo89 is the best possible sumo model.

The comparison is a necessary retrospective validation of production Elo89.
Had the completed model failed to outperform the simple higher-chii rule on
the record available when it was developed, there would have been little
reason to retain P89 or the wider Elo89 construction. Passing this test is
important positive model-selection evidence, but it is not by itself proof of
performance on genuinely future bouts.

### Frozen design

The run used:

- `files/output/Historys/1989_01 to 2026_11.zip`;
- the inclusive evaluation interval 1989/01–2026/11;
- the production P89 entrant prior, SHA-256
  `31ba2ea5430fb6a117b80290e78570cbbb160875febb6af14664a6c64ec93cdf`;
- the production divisional-K configuration;
- `q=400`;
- frozen rating persistence across absence;
- whole-population mean preservation; and
- forecasts emitted before the current result updated either rating.

One production Elo89 replay supplied the authoritative eligible bout stream.
For each forecast, Elo89 selected the side whose unrounded pre-bout probability
exceeded 0.5. The chii rule selected the side with the lower canonical
`Chii.ordinal()`. Exact Elo ties, missing chii and equal chii were left
unselected rather than broken by participant orientation or East/West.

The primary comparison retained only bouts on which both rules selected a
side. Thus both accuracies and their difference use exactly the same
denominator.

### Population flow

| Stage | Count |
|---|---:|
| Raw represented results | 586,914 |
| Production Elo89 eligible W/L forecasts | 583,860 |
| Elo89 exact-rating ties | 734 |
| Missing chii | 0 |
| Equal chii | 11 |
| Primary common-domain bouts | 583,115 |

The source contained 3,051 defaults and three other non-W/L outcomes, all
excluded by the production bout selector before either rule was compared.
The 734 exact Elo ties and 11 equal-chii rows account for the remaining gap
between eligible forecasts and the common domain.

### Primary result

| Rule or contrast | Estimate | Two-sided 95% bootstrap interval | One-sided 95% lower bound |
|---|---:|---:|---:|
| Production Elo89 accuracy | 57.774% | — | — |
| Higher-chii accuracy | 52.635% | — | — |
| Elo89 minus higher chii | +5.139 pp | +4.868 to +5.405 pp | +4.913 pp |
| Higher chii minus 50% | +2.635 pp | +2.485 to +2.788 pp | +2.509 pp |
| Elo89 minus 50% | +7.774 pp | +7.499 to +8.046 pp | +7.540 pp |

Uncertainty was estimated by 10,000 percentile-bootstrap replicates with seed
89, resampling complete basho rather than individual bouts. Both predeclared
one-sided lower bounds are above zero. The declared three-rule ordering is
therefore confirmed on the matched historical record.

Here, **confirmed** refers only to the predeclared ordering among production
Elo89, higher chii and random choice. It does not mean that Elo89 is the best
possible model.

### Where the difference came from

| Paired outcome | Count |
|---|---:|
| Both correct | 206,387 |
| Elo89 correct, chii wrong | 130,501 |
| Elo89 wrong, chii correct | 100,533 |
| Both wrong | 145,694 |

The two rules disagreed on 231,034 bouts. Elo89 won 29,968 more of those
discordant decisions than higher chii. The exact two-sided McNemar/binomial
probability is approximately `4.8e-849`; the standard floating-point routine
underflowed and recorded this as zero in the generated report. The basho-block
bootstrap remains the primary uncertainty method because bouts within a basho
should not be treated as independent.

Elo89 and higher chii selected the same side on 60.379% of common-domain
bouts. The result is therefore not simply two restatements of the banzuke
ordering: a substantial share of bouts distinguishes the rules.

### Descriptive division results

| Population | Bouts | Elo89 accuracy | Higher-chii accuracy | Elo89 advantage |
|---|---:|---:|---:|---:|
| Makuuchi | 64,030 | 59.268% | 57.586% | +1.682 pp |
| Juryo | 41,438 | 52.662% | 51.062% | +1.600 pp |
| Makushita | 87,605 | 55.000% | 52.131% | +2.870 pp |
| Sandanme | 142,676 | 58.147% | 51.739% | +6.408 pp |
| Jonidan | 182,852 | 59.414% | 52.152% | +7.262 pp |
| Jonokuchi | 46,653 | 57.979% | 53.266% | +4.714 pp |
| Cross-division | 17,861 | 57.578% | 51.453% | +6.125 pp |

The observed Elo89 advantage is positive in every division and for
cross-division bouts. These rows are descriptive diagnostics, not separately
predeclared superiority tests. The smallest advantages occur in Makuuchi and
Juryo, where the banzuke ordering is itself most competitive as a categorical
selector.

### Rating maturity

| Smaller prior rated-bout count | Bouts | Elo89 accuracy | Higher-chii accuracy | Elo89 advantage |
|---|---:|---:|---:|---:|
| 0 | 1,799 | 55.031% | 56.198% | -1.167 pp |
| 1–9 | 25,048 | 58.053% | 52.000% | +6.052 pp |
| 10–49 | 108,861 | 54.542% | 52.524% | +2.018 pp |
| 50–99 | 102,130 | 59.154% | 51.810% | +7.344 pp |
| 100+ | 345,277 | 58.379% | 52.941% | +5.438 pp |

The only observed reversal is the small zero-history group. This includes the
artificial January 1989 boundary population as well as genuine first rated
bouts. It is an expected weak point for a rating model and does not overturn
the all-bout primary result. No subgroup superiority claim was predeclared.

### Probability-score context

Production Elo89's mean log loss was `0.674674`, compared with `0.693147` for
an always-50–50 forecast. Its mean Brier loss was `0.240874`, compared with
`0.250000` for 50–50. Thus the model's probabilities also improve upon the
neutral reference on this record.

Higher chii remains a categorical rule rather than a fitted probability
model. Assigning probabilities one and zero would assert unjustified certainty
and make every upset infinitely bad under log loss, so no proper probability
score is assigned to it in this comparison.

### Interpretation

The matched result supports the following statement:

> Production Elo89 passed a necessary retrospective validation: it selected
> winners substantially more often than either higher chii or random choice
> on the matched post-1988 historical record.

That result is stronger than the earlier working picture. It establishes the
declared historical ordering on one common bout population and supplies a
clear reason to retain the production model.

The qualification concerns generalisation, not whether the recorded
historical comparison happened. P89 was estimated using results from much of
the period being scored, and its epsilon-8.5 fitted source was selected using
retrospective log loss. The bootstrap treats the resulting production model as
fixed; it measures variation across basho blocks, not uncertainty from fitting
or selecting the prior. Consequently, this is not an unbiased prospective or
out-of-sample estimate.

The conclusion is intentionally asymmetric. Failure on this retrospective
test would have been strong evidence against P89 and the wider model. Success
is important evidence that the model is adequate and useful, but it cannot
establish that Elo89 is the best possible rating system or that the same
advantage will persist unchanged on future bouts. A rolling-origin prior fit
or scoring the now-frozen model on genuinely later basho would address that
separate question.

## Reproduction and evidence

Initial chii-only probe:

```powershell
python -m src.analysis.chii_prediction --start 1989/01 --end 2026/07
```

Matched production comparison:

```powershell
python -m src.analysis.chii_prediction.compare_elo89 `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --evaluation-start 1989/01 `
  --evaluation-end 2026/11
```

- [Module usage and selection rules](../README.md)
- [Generated report](../../../../files/output/analysis/chii_prediction/report_1989_01_to_2026_07.md)
- [Counts CSV](../../../../files/output/analysis/chii_prediction/counts_1989_01_to_2026_07.csv)
- [Source and counts manifest](../../../../files/output/analysis/chii_prediction/manifest_1989_01_to_2026_07.json)
- [Earlier Elo comparison findings](../../elo_model_selection/docs/Results%201.md)
- [Earlier Elo run manifest](../../../../files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/manifest.json)
- [Matched-comparison proposal](Proposal%20-%20Matched%20Elo89%20vs%20Chii%20Accuracy.md)
- [Matched report](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/report.md)
- [Matched manifest](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/manifest.json)
- [Bout-level audit ledger](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/bout_comparison.csv)
- [Summary and subgroup results](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/summary.csv)
- [Paired discordance table](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/discordance.csv)
- [By-basho results](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/by_basho.csv)
- [Rolling 6-, 12- and 24-basho results](../../../../files/output/analysis/chii_prediction/elo89_vs_chii_1989_01_to_2026_11/rolling.csv)
