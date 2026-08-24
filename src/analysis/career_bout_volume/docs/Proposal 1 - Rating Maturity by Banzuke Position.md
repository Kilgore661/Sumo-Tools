# Proposal 1: Rating Maturity, Initialisation Sensitivity and Banzuke Position

## Status

Implemented on 24 August 2026 in
`src/analysis/career_bout_volume/rating_maturity/`. The declared
`1989/01`--`2026/07` run is persisted beneath
`files/output/analysis/career_bout_volume/rating_maturity/`; its `findings.md`
records the staged answers. This document remains the experimental contract
suggested by the completed career-bout-volume probe and the fixed-skill
forgetting study.

The date ranges must not be conflated:

- the **existing career-bout-volume probe** was run over the available History
  from `1958/01` through `2026/07`; and
- the **investigation proposed here** must produce new declared results from a
  History truncated to begin at `1989/01`, when the represented bout record is
  complete across the banzuke.

No `1989/01`-onward cohort result is currently claimed as a persisted finding
of the existing package. Stage 1 below performs that complete-results-era
analysis.

## Objective

Test the proposed explanation of the irregular chii-rating relationship below
approximately `Jd100`:

> Deep lower-division chii are occupied disproportionately by rikishi with very
> little accumulated bout evidence. Many of those rikishi leave before their
> ratings can become predominantly result-informed. Ratings associated with
> those chii may therefore remain unusually sensitive to entrant
> initialisation.

The experiment must separate three progressively stronger questions:

1. **Exposure:** how many earlier eligible bouts does a rikishi actually have
   when observed at a given banzuke position?
2. **Initialisation sensitivity:** after the same evidence has been processed,
   how different are ratings and forecasts when the entrant initialisation is
   changed?
3. **Relationship to the lower-tail anomaly:** does controlling for rating
   maturity materially reduce the irregular chii-rating pattern below
   `Jd100`?

The first question is descriptive. The second is a coupled counterfactual. The
third connects the evidence to the observed Equelo problem. Answering only the
first question would make the explanation plausible but would not establish
it.

## Motivation

The existing career-bout-volume probe shows a strong association between mean
career position and the number of fought bouts represented in its
`1958/01`--`2026/07` History. It motivates the hypothesis that the lowest
positional tail has far less career exposure than the rest of the banzuke.
It does not provide the declared test proposed here. Before 1989,
lower-division results are incomplete, so full-history totals of represented
bouts can understate actual lower-division exposure. Stage 1 must test the
exposure hypothesis within the `1989/01`-onward complete-results era. Using
bouts rather than elapsed calendar time remains important because
lower-division rikishi normally fight fewer bouts per basho than sekitori.

The fixed-skill forgetting study supplies a separate conceptual result:
fixed-`k` ratings may continue to fluctuate while losing their sensitivity to
their initial ratings. It also shows, in its deliberately favourable toy
world, that initialisation can affect a substantial transient. Its numerical
event counts do not transfer to sumo: the toy population, schedule, `k`, latent
skills and entry policy are different.

The real historical question is therefore not whether a rikishi has crossed a
toy-derived universal bout threshold. It is whether low-banzuke observations
have systematically less prior result evidence and whether the ratings in
those observations are empirically more sensitive to the entrant prior.

## Claim boundary

This investigation can establish an association between banzuke position,
rating maturity and sensitivity to initialisation under the declared
historical models. It cannot establish that:

- a particular number of bouts makes a rating objectively meaningful;
- `Jd100` is a natural or causal boundary;
- chii is true ability;
- short careers cause the lower-tail anomaly;
- the fixed-skill toy forgetting times apply to historical sumo; or
- an informed prior is uniquely correct.

The language of *convergence* should be avoided for individual fixed-`k`
rating paths. The relevant quantities are accumulated evidence and remaining
counterfactual sensitivity to initialisation.

## Historical scope

### Primary history

Create a new declared run using a selected History whose first represented
basho is `1989/01`. Do not calculate the proposed primary results by silently
filtering presentation rows from the existing `1958/01`--`2026/07` report.
The replay, cumulative prior-bout counts, cohorts, summaries and manifest must
all share the `1989/01` boundary.

Pre-1989 lower-division results are incomplete, so a 1958-onward total of
recorded bouts would systematically understate lower-division exposure and
confound the question being tested. The earlier full-history probe remains
useful as motivation and as a source of methods, not as the primary evidence
for this investigation.

The declared run must record:

- the first and last basho;
- the exact History source and hash;
- the number of represented basho, rikishi, rikishi-basho observations and
  eligible bouts;
- the Git commit and dirty state; and
- all exceptional records and exclusions.

### Cohorts

Report at least three cohorts separately:

1. **Boundary incumbents:** rikishi present in `1989/01`. Their earlier bout
   support is unknown within the selected History, and they represent the
   special system-start problem.
2. **Observed entrants:** rikishi first appearing after `1989/01`. Their prior
   eligible-bout count is observable from zero.
3. **All observations:** useful for describing the rating system actually
   replayed, but never a substitute for the two cohort-specific views.

Active careers may be included. Unlike completed-career volume, prior support
at a historical observation is known at that time and is not right-censored by
the rikishi's future career. No analysis should condition on eventual career
length unless it is explicitly labelled retrospective.

Avoid the potentially ambiguous label *post-1988 cohort*. Use **1989/01
boundary incumbents**, **entrants first observed after 1989/01**, or **all
observations in the 1989/01-onward replay**, as appropriate.

## Model contracts

### Evidence count

For the primary analysis, *prior rated bouts* means the number of earlier bouts
for that rikishi that are eligible for a `B'` rating update:

```text
represented W or L result
forecast and update in chronological order
FS, FP and draw excluded
```

Also retain the package's broader prior fought-bout count, if different, as an
audit field. Do not count the current basho's results in a start-of-basho
measurement.

### Coupled models

Use the selected divisional-`k` model twice on the same ordered history:

| Model | `k` policy | Entrant initialisation |
|---|---|---|
| `B_k` | declared divisional policy | one common value |
| `B_kP` | same declared divisional policy | adopted prior `P` |

Both processes must consume exactly the same eligible bouts and realised
results. They differ only in entrant initialisation. Record the divisional-`k`
configuration and adopted-prior artifact paths and hashes.

`B_kP` is the selected `B'`; `B_k` is the coupled counterfactual needed to
isolate the continuing effect of `P`. This comparison does not ask which model
predicts better—that is already covered by the controlled model-selection
package. It asks where and for how long changing initialisation still changes
the rating state or forecast.

Stage 1 retains every ranked rikishi-basho observation. For Stages 2 and 3,
model state is created at the first eligible rated bout, preserving the
`elo_model_selection` contract. A start-of-basho rating is available for
rikishi initialized earlier and for rikishi who will contest an eligible bout
in the current basho; the latter are initialized from that basho's chii before
its first eligible bout. Ranked observations with no eligible bout yet retain
null model ratings, remain in the audit ledger, and are counted explicitly as
model-state exclusions.

## Stable banzuke coordinates

Every rikishi-basho observation must retain:

- raw chii and chii ordinal;
- division;
- position from the top and bottom of the actual banzuke;
- actual banzuke size; and
- normalized position

\[
\frac{\text{number of ranked rikishi above}}
     {\text{number of ranked rikishi}-1}.
\]

Use two complementary descriptions of the lower tail:

1. a literal `Jd100` classification, preserving east/west and the actual
   contemporary banzuke; and
2. the inherited normalized cut at `0.8395` plus uniform normalized-position
   bins.

The inherited cut is an evidence-motivated comparison point, not a discovered
change point. Uniform bins must also be shown so that a gradual exposure
gradient is not turned rhetorically into a sharp `Jd100` discontinuity.

## Stage 1: The maturity landscape

Construct one row per rikishi at the start of every represented basho. Required
fields include:

```text
RikId
shikona
basho
cohort
chii and division
banzuke coordinates
first observed basho
elapsed represented basho
prior rated bouts
prior fought bouts
```

For each positional bin and cohort, report:

- observation and distinct-rikishi counts;
- median, quartiles and selected upper quantiles of prior rated bouts;
- proportions below `15`, `30`, `60`, `120`, `180`, `200` and `240` prior
  bouts; and
- the empirical curve

\[
P(\text{prior rated bouts}\geq x\mid\text{current position}).
\]

The thresholds are descriptive landmarks. In particular, `180` and `200`
provide continuity with the discussion prompted by the toy work; they must not
be labelled universal maturity thresholds.

### Primary displays

Produce:

1. an interactive heatmap with current normalized position on one axis, prior
   rated-bout bands on the other and observation count or proportion as the
   value;
2. prior-support survival curves by current-position band;
3. a focused table comparing observations above and below literal `Jd100`;
4. cohort-specific versions separating boundary incumbents from observed
   entrants; and
5. CSVs containing every plotted aggregate.

The principal presentation should use current position, not mean position over
the completed career. This avoids using future career development to classify
an earlier rating observation.

Stage 1 is the first declared test of the hypothesis in the complete-results
era. Its findings must be derived from the new `1989/01`-onward run and
persisted with that run's manifest. They must not be described as confirmation
of an already-established `1989/01`-onward package result.

## Stage 2: Historical initialisation sensitivity

At every start-of-basho observation, save the rating supplied by `B_k` and
`B_kP`. Because a common rating translation has no forecasting meaning, compare
centred rating states or rating differences rather than unadjusted absolute
levels.

Required measures are:

- absolute centred rating disagreement for the observed rikishi;
- median, quartiles and upper quantiles of that disagreement by current
  position and prior support;
- scheduled-bout forecast disagreement between the coupled models;
- mean and upper-quantile absolute probability disagreement by the same
  position-support cells; and
- proportions exceeding declared practical probability tolerances such as
  `0.005`, `0.01`, `0.02` and `0.05`.

Participant-level forecast rows must be used consistently with the calibration
work: each eligible bout contributes one forecast for each participant. The
two probabilities within a model are complementary, but the coupled absolute
disagreement should be the same for both orientations; this duplication must
be recorded rather than mistaken for independent support.

### Primary displays

Produce paired heatmaps for:

1. median absolute rating disagreement; and
2. mean absolute forecast-probability disagreement,

with current banzuke position and prior rated-bout band as the axes. Add curves
of disagreement against prior support for broad position bands, including the
literal `Jd100` comparison.

These views answer whether low-position ratings merely belong to short-career
rikishi or actually retain more counterfactual memory of the entrant policy.

## Stage 3: Relationship to the chii-rating anomaly

Recalculate the mean start-of-basho `B'` rating by chii for:

1. all observations;
2. observations with at least 30 prior rated bouts;
3. observations with at least 60;
4. observations with at least 120; and
5. observations with at least 180.

For each threshold, retain support counts and do not draw a curve through cells
whose support is below a declared minimum. Compare:

- the overall shape through Jonidan and Jonokuchi;
- the location and magnitude of monotonicity reversals;
- literal and normalized-position views; and
- the amount of the lower tail left after each maturity restriction.

This stage is diagnostic rather than a proposal to publish only mature
rikishi. If the anomalous tail disappears merely because almost no observations
remain, that is evidence of inadequate support, not evidence that the mature
curve proves the intended ordering.

As a sensitivity check, repeat the shape comparison with observation weights
that increase smoothly with prior support. This must remain secondary to the
unweighted threshold views so that a convenient weighting rule is not mistaken
for an empirical discovery.

## Dependence and uncertainty

Rikishi-basho rows are repeated observations, and successive ratings for one
rikishi are strongly dependent. Ordinary row-wise confidence intervals would
therefore exaggerate precision.

Descriptive counts and quantiles are primary. Where uncertainty intervals are
used, resample whole rikishi careers, not individual observations. A secondary
block bootstrap by basho may be useful for sensitivity to historical eras.
Report both the number of observations and the number of distinct rikishi in
every aggregate.

## Interpretation matrix

| Observation | Interpretation |
|---|---|
| Prior support falls sharply near or below Jd100 | Supports the exposure component of the explanation |
| Coupled disagreement also rises there | Supports continuing sensitivity to entrant initialisation |
| Disagreement is explained by support rather than position once both are shown | Suggests maturity, not chii itself, is the operative variable |
| Mature-only chii means become materially more regular | Supports maturity composition as a contributor to the anomaly |
| Mature-only cells vanish below Jd100 | Shows that the tail is not empirically identified at that maturity level |
| Low support but negligible coupled disagreement | Weakens the claim that entrant initialisation drives the anomaly |
| High support with persistent disagreement or irregularity | Points to other mechanisms such as schedule connectivity, changing ability, normalisation or fixed-point feedback |
| No material support gradient | Contradicts the proposed exposure explanation |

No single row is decisive. The intended explanation is best supported by the
joint pattern: low exposure, persistent coupled disagreement and attenuation of
the anomalous chii curve after conditioning on maturity.

## Success criteria

The investigation is successful as research if it produces an auditable answer,
including a negative one. Implementation success requires:

- a declared History truncated to begin at `1989/01` and a reproducible
  manifest;
- exact reuse of the adopted `P` and divisional-`k` contracts;
- correct chronological prior-bout counts;
- separate boundary-incumbent and observed-entrant results;
- both literal `Jd100` and normalized-position views;
- coupled `B_k`/`B_kP` rating and forecast ledgers;
- support-aware chii curves;
- standalone responsive Plotly/CDN HTML and ordinary CSV outputs beneath
  `files/output/analysis/career_bout_volume/`; and
- focused automated tests for chronology, eligibility, centring, cohort
  assignment, position normalization and coupled replay identity.

Substantive support for the proposed explanation requires more than reproducing
the career-volume association. At minimum:

1. deep lower-banzuke observations must have materially less prior rated-bout
   support;
2. remaining sensitivity to initialisation must decrease as that support
   accumulates; and
3. the `Jd100`-related rating irregularity must either attenuate among mature
   observations or be shown to occur where mature observations are too scarce
   to identify a stable relationship.

If only the first condition holds, the result is useful context but the
initialisation explanation remains untested.

## Outputs and package layout

Implement the new work in a clearly named subpackage, for example:

```text
src/analysis/career_bout_volume/rating_maturity/
```

Write each declared run beneath:

```text
files/output/analysis/career_bout_volume/rating_maturity/<run-id>/
```

At minimum persist:

```text
manifest.json
rikishi_basho_maturity.csv
position_support_summary.csv
position_support.html
coupled_rating_disagreement.csv
coupled_forecast_disagreement.csv
initialisation_sensitivity.html
chii_means_by_maturity.csv
chii_means_by_maturity.html
findings.md
```

The findings document must lead with the answer to the three staged questions
and preserve the distinction between established findings, interpretations and
limitations.

## Relationship to the wider story

If supported, the result would connect three parts of the Elo/Equelo account:

1. changing populations make entrant initialisation consequential;
2. fixed-`k` systems can forget initialisation, but only after accumulating
   evidence; and
3. the rapid-turnover lower tail may contain too little evidence for that
   forgetting to make chii-associated ratings independently meaningful.

This would justify treating informed priors as more than a cosmetic correction
at the start of the historical chart. It would also support an explicit domain
qualification: ratings may be interpretable over the well-supported banzuke
without requiring every deep lower-division chii to define a stable empirical
rating.

The lower tail cannot simply be ignored, however. Future sekitori enter through
it, and entrant policies affect rating mass in an open population. A later
Equelo experiment must therefore ask whether alternative treatments below the
supported boundary materially change ratings higher in the banzuke.

## References

- [Career Bout Volume and Relative Banzuke Position](../README.md) defines the
  existing career-level association and normalized banzuke coordinate. Its
  declared full run covers `1958/01`--`2026/07`; it motivates but does not
  constitute the proposed `1989/01`-onward test.
- [Forgetting package README](../../forgetting/README.md) defines
  initialisation forgetting as a coupled-process property.
- [Completed Investigation: Forgetting in a Fixed-Skill Toy World](../../forgetting/docs/Completed%20Investigation%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md)
  supplies the controlled conceptual evidence and its limits.
- [Initial Rating Policy](../../docs/story/10%20Initial%20Rating%20Policy.md)
  defines the adopted prior `P`.
- [Elo Model Selection README](../../elo_model_selection/README.md) defines
  `B_k`, `B_kP` and the controlled `1989/01`-onward replay.
- [Controlled Retrospective Results](../../elo_model_selection/docs/Results%201.md)
  records the predictive and calibration evidence for selecting provisional
  `B'=B_kP`.
- [Initial Rating Audit](../../equelo/docs/2026-06-27%20Initial%20Rating%20Audit.md)
  records the Jd100-related anomaly and the existing support/churn hypothesis.
- [Rating Probe Findings](../../clean_elo/docs/Rating%20Probe%20Findings.md)
  records the observed chii-rating shape and the limitations of naive support
  measures.
