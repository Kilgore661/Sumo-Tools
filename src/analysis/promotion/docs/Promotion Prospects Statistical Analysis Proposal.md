# Promotion Prospects Statistical Analysis Proposal

## Status

Proposal arising from the September 2026 discussion of possible promotion
annotations on The Banzuke and Basho Results. This document authorizes and
defines an analysis, not a public-site implementation. No promotion annotation,
probability or new public page should be implemented merely because it appears
as a candidate output below.

Implementation status: the Ozeki pipeline is implemented under
[`src.analysis.promotion.prospects.ozeki`](../prospects/ozeki/README.md) and is
ready for a full operator-run analysis. Only synthetic smoke data has been run
during implementation. The Yokozuna analysis remains unimplemented in its
reserved sibling folder.

The earlier
[Promotion Annotations Proposal](../../../products/make_site89/docs/Promotion%20Annotations%20Proposal.md)
is an important record of the product context and the initial compact UI idea.
Its proposed `!` and required-wins annotations are now deferred pending this
analysis. In particular, two consecutive yusho and 33 wins at komusubi or
sekiwake are candidate historical descriptions, not rules enforced by the
data or promises about a future JSA decision.

## Product and temporal context

The site has two relevant views:

- **The Banzuke** shows the current official banzuke and how it changed from
  the preceding one. It is especially useful after a new banzuke is published
  and before the basho has results.
- **Basho Results** shows the selected basho's records. Once daily publication
  is implemented, it can show an attempt developing during the basho; Previous
  Basho supplies optional context.

The normal cycle is:

1. the new banzuke is published;
2. the 15 days of competition take place;
3. final results become known; and
4. any promotion decision may be reported, but this site currently learns the
   factual rank outcome only when the following banzuke is published.

This timing creates distinct questions which must not be conflated:

- At the start of a basho, what promotion-relevant context was knowable?
- Given each possible result in the current basho, what happened in comparable
  historical cases?
- Once the basho result is known, how often did the following banzuke contain
  the promotion?
- Once the following banzuke exists, what actually happened?

Any later UI must state which question it answers. It must not use later data
to label an earlier page state.

## Premise

Strictly, the operative promotion rule is the decision made by the Japan Sumo
Association. Familiar formulations such as two consecutive yusho at ozeki or
33 wins over three sanyaku basho are useful benchmarks, but the historical
record contains decisions outside them and non-promotions inside them.

The purpose of this work is therefore not to discover a hidden deterministic
rule. It is to determine whether historical decisions support any useful,
appropriately qualified digest of promotion prospects. The possible conclusion
that the evidence is too sparse, unstable or conditional for compact public
annotations is a valid and expected result.

## Questions

### Yokozuna

For an ozeki, investigate:

1. Promotion rates for ordered pairs of `Y`, `D`, `J` and `N`, where `Y` is
   yusho, `D` doten-yusho, `J` jun-yusho and `N` none of those markers.
2. The prospective question after the first result: for example, after a `J`,
   what historically happened following each possible second result?
3. Whether the number of wins materially separates cases within the same
   marker, such as an 11-4 and a 14-1 jun-yusho or doten-yusho.
4. Whether a third-basho context improves out-of-sample description rather
   than merely improving in-sample fit.
5. Whether relationships are stable through time or reflect different eras of
   institutional practice.

The analysis must distinguish a historical fraction such as “7 of 16 `JY`
opportunities led to promotion” from a claim that a present `JY` rikishi has a
particular true probability of promotion.

### Ozeki

For promotion to ozeki, investigate:

1. Three-basho totals across plausible rank patterns, including starts from
   maegashira followed by two komusubi/sekiwake basho.
2. Total wins and the distribution of those wins, including minimum wins in
   any component basho and the position of a weaker result.
3. Whether 28 through 34 wins describe materially different historical
   promotion rates.
4. Whether the apparent value of a threshold is stable through time.
5. Which maegashira starts, if any, form a defensible candidate population.
   The study must not begin by treating every maegashira as being on an ozeki
   run.
6. Immediate ozekiwake reinstatement as a separate mechanism, excluded from
   ordinary qualification analysis.

## Observation and outcome contracts

The unit is a **promotion opportunity at a banzuke boundary**, not a distinct
rikishi. The primary outcome is whether the rikishi is promoted on the next
published banzuke. “Eventually promoted” is a different outcome and must not
be substituted.

Overlapping opportunities may be retained because each boundary represented a
real decision, but repeated opportunities from the same rikishi are dependent.
Every report must state both opportunity counts and distinct-rikishi counts.

The existing repository conventions remain the starting point:

- scoring begins at the documented post-boundary cutoff in 1958;
- consecutive means consecutive held basho in History;
- regular wins include fusensho and exclude playoff wins;
- missing following banzuke/rank makes the outcome unresolved;
- missing historical results are reported rather than silently imputed; and
- user-supplied boundary supplements remain explicitly identified and are not
  written into History.

Before modelling, audit the observation builders against named positive,
negative, boundary, cancelled-basho and incomplete-data cases. Preserve
case-level evidence in generated artifacts.

## Definition of reliability

No single significance test will make an annotation reliable. Reliability for
this purpose has four components.

### 1. Adequate support

Every reported rate must include:

- promoted count;
- resolved opportunity count;
- distinct-rikishi count; and
- an uncertainty interval.

Wilson or Jeffreys binomial intervals may be used as an easily understood
first description. They must be labelled as approximate because overlapping
windows and repeated rikishi violate the independent-binomial assumption.
Cells with one or two cases must remain visibly sparse even if their observed
rate is 100%.

### 2. Robust uncertainty

Add sensitivity estimates that respect the structure of the data:

- cluster resampling by rikishi, so all of one rikishi's observations move
  together; and
- block resampling or temporal folds, so neighbouring decisions are not
  treated as freely exchangeable observations.

If the sample is too small for a stable interval, say so rather than replacing
the missing precision with a point estimate.

### 3. Temporal stability

Promotion practice may change. Use chronological evaluation rather than a
random train/test split:

1. select or fit the candidate using an earlier period;
2. freeze it;
3. evaluate it on a later period; and
4. repeat with expanding-window forward chaining where sample size permits.

Report performance by broad time block as a diagnostic. Any named era boundary
used for substantive conclusions should be justified by external institutional
history or an explicitly predeclared convention, not chosen because it improves
the score.

Poor transfer may mean overfitting, institutional change or both. The report
must not claim to distinguish those explanations without additional evidence.

### 4. Selection discipline and calibration

Candidate variables, thresholds and interactions should be declared before
examining their final-period performance. Searching many partitions and
reporting only the winner produces an optimistic estimate.

For binary annotations, report precision, recall and the complete confusion
counts. F1 may be retained for comparison but must not decide the product on
its own. For probabilistic models, report calibration tables and Brier score;
use log loss only where smoothing prevents unsupported zero/one predictions.
The practical target is calibrated uncertainty, not maximum classification
accuracy.

## Work plan

### Phase 1: freeze and audit the data

- Reproduce the existing 31-promotion Yokozuna pair sample, 30-promotion
  triple-eligible sample and 71-promotion Ozeki scoring sample.
- Record unresolved opportunities, missing results, boundary supplements and
  distinct rikishi.
- Check the outcome date and as-of date for every positive case and a sample of
  negative cases.
- Produce one versioned manifest describing the History snapshot and all
  inclusion and exclusion rules.

### Phase 2: descriptive tables

For Yokozuna, produce:

- the full pair table with counts, rates and intervals;
- prospective branch tables grouped by the first marker;
- score distributions within every non-empty marker pair;
- equivalent tables for predeclared score bands; and
- named positive and informative negative cases.

For Ozeki, produce:

- rates by total wins, rank pattern and component-win pattern;
- separate tables for all-K/S and maegashira-start populations;
- the conventional 33-win benchmark beside adjacent thresholds; and
- named promotions missed by each benchmark and qualifying runs not promoted.

### Phase 3: stability and validation

- Add broad-period descriptive tables without optimizing their boundaries.
- Run expanding-window forward validation for a small, frozen set of candidate
  rules or models.
- Compare pooled-history estimates with later-period estimates.
- Add rikishi-clustered and time-block sensitivity intervals.
- Record how often the selected category, threshold or model changes across
  folds.

The small Yokozuna sample may support only descriptive tables. Do not force a
predictive model merely to complete this phase.

### Phase 4: interpretation

Write a reader-facing account which separates:

- facts directly observed in the data;
- statistical summaries conditional on the stated sample;
- hypotheses about score quality or eras; and
- institutional explanations requiring contemporary sources.

Explicitly document important ideas not yet modelled. These include finer
score quality, injuries or absences, the number and strength of other ozeki,
banzuke capacity, public announcements, deliberative criteria and historically
different expectations. Absence from the model is not evidence that a factor
did not matter.

### Phase 5: product decision

Only after the analysis is reviewed, choose among these outcomes:

1. **Compact annotations on both existing tables.** Appropriate only where a
   simple state is well supported, temporally stable and explainable without
   implying an official rule.
2. **Annotations linked to an advanced explanation.** Appropriate where a
   compact marker is useful but needs counts, qualifications and alternative
   outcomes to be understood.
3. **A separate Promotion Prospects analysis page only.** Appropriate where
   the history is interesting but too sparse or unstable for a table marker.
4. **No public feature.** Appropriate where the analysis cannot support a
   useful claim beyond anecdotes.

The product decision must separately consider Yokozuna and Ozeki promotion.
There is no requirement that both receive the same treatment.

## Preliminary baseline to reproduce

The existing artifacts provide checks, not final findings for the proposed
study.

### Yokozuna pair cells

| Pair | Promoted / resolved | Observed rate |
|---|---:|---:|
| `YY` | 12/12 | 100.0% |
| `YD` | 1/2 | 50.0% |
| `DY` | 1/3 | 33.3% |
| `DD` | 1/2 | 50.0% |
| `JY` | 7/16 | 43.8% |
| `YJ` | 2/7 | 28.6% |
| `JD` | 2/7 | 28.6% |
| `JJ` | 2/25 | 8.0% |
| `ND` | 2/16 | 12.5% |

The maximum-F1 pair partition was selected and scored in-sample. It predicted
32 promotions, of which 21 occurred, and missed 10 of the 31 observed
promotions. It is not a probability model or a validated public rule.

### Ozeki benchmarks

| Candidate | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| A32: 32+ wins, all K/S | 51 | 9 | 20 | 85.00% | 71.83% | 77.86% |
| A33: 33+ wins, all K/S | 42 | 4 | 29 | 91.30% | 59.15% | 71.79% |

A33's high precision does not make it a complete rule: it misses 29 of the 71
promotions in the scoring sample. A32 fits this sample better by F1, but its
selection and evaluation used the same history.

As a preliminary non-optimized time diagnostic, A32 recall rises from 52.2%
in 1958-1979 to 75.0% in 1980-1999 and 85.7% in 2000-2026, while precision is
92.3%, 83.3% and 82.8% respectively. These broad periods are not proposed as
institutional eras; the variation demonstrates why stability must be tested.

## Publication rules for any analysis page

If a public analysis page is ultimately approved:

- lead with counts, not percentages;
- use “historically promoted in x of n resolved opportunities,” not an
  unqualified `p(promotion)`;
- show uncertainty and sparse-cell warnings beside the relevant result;
- disclose the date range, outcome definition and exclusions;
- distinguish retrospective fit from later-period validation;
- name important counterexamples;
- do not describe inferred thresholds as JSA rules; and
- explain that unmodelled circumstances and discretion may affect decisions.

A total probability may be shown only if its conditioning information and
time point are explicit. For example, the historical rate after a preceding
`J`, before the next basho result is known, is a different quantity from the
rate after a completed `JY` sequence.

## Deliverables

1. Versioned machine-readable opportunity data or manifests for both promotion
   types, retaining case-level provenance.
2. Reproducible descriptive tables with counts and uncertainty intervals.
3. Chronological validation and clustered-sensitivity results where the sample
   supports them.
4. A written interpretation covering limitations, counterexamples and omitted
   factors.
5. A product recommendation for Yokozuna and Ozeki separately.
6. If warranted and separately approved, a specification for annotations or
   an advanced public page. UI and producer implementation are not deliverables
   of this proposal.

## Completion criteria

The analysis phase is complete when:

1. all observation and outcome definitions are explicit and tested;
2. reported percentages always retain their supporting counts;
3. simple and structure-aware uncertainty have both been considered;
4. model or rule selection is separated from later-period evaluation;
5. temporal stability is reported without data-mined era boundaries;
6. score and rank alternatives requested above have been evaluated or clearly
   recorded as unsupported by the available data;
7. historical description is not presented as an official or deterministic
   rule; and
8. the final recommendation may legitimately be that no annotation is useful.
