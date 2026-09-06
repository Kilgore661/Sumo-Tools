# Wins follow chii: a missing baseline

Recorded 6 September 2026. Evaluation period: 1989/01–2026/07.

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

## Data differences and the stopping point

The earlier Elo comparison scored 574,863 W/L bouts over the same dates. Its
manifest records an older snapshot of `1989_01 to 2026_11.zip`, with 577,861
raw results and 2,998 defaults excluded. The present archive supplies 4,563
more W/L bouts before the 14 equal-chii exclusions. The current version of
the 1989 archive also has a different checksum from that saved in the Elo
manifest. Most of the count difference therefore concerns source snapshots;
the chii rule adds a small, explicit exclusion of its own. We did not identify
the individual historical revisions responsible for the source difference.

A deeper investigation of those differences, or a matched comparison of
winner-selection accuracy across chii and Elo, was deliberately deferred as
a potential rabbit hole. This probe sufficiently fills the original gap:
the existing rank order is an obvious baseline and shows a modest observed
advantage over random choice.

"Random, follows chii, considered ratings" is a useful conceptual progression.
The interpretation that chii lies between random choice and Elo is a working
picture, not a demonstrated three-way ordering on a common winner-accuracy
measure. That distinction is sufficient for the present stopping point.

## Reproduction and evidence

```powershell
python -m src.analysis.chii_prediction --start 1989/01 --end 2026/07
```

- [Module usage and selection rules](../README.md)
- [Generated report](../../../../files/output/analysis/chii_prediction/report_1989_01_to_2026_07.md)
- [Counts CSV](../../../../files/output/analysis/chii_prediction/counts_1989_01_to_2026_07.csv)
- [Source and counts manifest](../../../../files/output/analysis/chii_prediction/manifest_1989_01_to_2026_07.json)
- [Earlier Elo comparison findings](../../elo_model_selection/docs/Results%201.md)
- [Earlier Elo run manifest](../../../../files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/manifest.json)
