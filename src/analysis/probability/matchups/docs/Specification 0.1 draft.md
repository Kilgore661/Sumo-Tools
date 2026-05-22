# Matchup Probability Distributions: Specification 0.1 Draft

This is an initial specification draft. It records the questions and decisions
that need to be settled before implementation.

Section 1 records the domain: what counts as a bout for this analysis. The
remaining sections record the other specification topics to work through.

---

# 1. Domain

The package analyses actual scheduled sumo bouts and asks how often the
stronger rikishi beats the weaker rikishi under two definitions:

* higher-ranked by chii
* higher-rated by model rating

The domain is the same cleaned bout domain used by Expt3c via
`make_oracle(...)`.

## 1.1 Date Range

Use everything in the available history after oracle cleaning.

The current oracle policy excludes pre-1958 data.

## 1.2 Basho and Bout Inclusion

The oracle policy is:

* before 1989, retain bouts where at least one participant is sekitori
* from 1989 onward, retain bouts where both participants are on the basho
  banzuke
* rebuild the banzuke according to the oracle's cleaned domain
* use the default `collapse_mode="annotation_only"` unless this specification
  later changes the rank-representation policy

In this context, sekitori means:

```text
Makuuchi ranks or Juryo
```

The empirical and model-based distributions must use the same oracle-cleaned
bout set. Differences between their outputs should not be caused by different
history inclusion rules.

## 1.3 Actual Bouts Only

The analysis is about actual scheduled bouts only.

It does not estimate probabilities for hypothetical pairings that never
happened. For example, the absence of a Yokozuna-vs-M17 pairing is itself part
of the observed torikumi structure, not a missing cell to be filled.

## 1.4 Probability-Eligible Outcomes

After oracle cleaning, probability rows should include only decisive fought or
rating-eligible outcomes.

Exclude non-rating/non-fought outcomes such as:

* fusen
* blank
* absences or other records that do not represent a fought/scored bout

The oracle is expected not to emit invalid chii for retained banzuke-domain
bouts. If an implementation nevertheless encounters missing chii or missing
model ratings, it should exclude the bout from the affected output and count the
exclusion in metadata.

## 1.5 Playoffs

Playoffs are not part of the domain. They are not represented in the original
raw source data used by this project.

## 1.6 Domain vs Ordering

Domain inclusion is separate from canonical stronger/weaker ordering.

A bout can be in-domain even if it later becomes an edge case for empirical or
model ordering, such as equal chii ordinal or equal pre-bout rating.

## 1.7 Metadata

The run should preserve inclusion/exclusion counts, including:

* raw candidate bouts, if available
* oracle-retained bouts
* excluded non-rating/non-fought bouts
* included probability bouts
* excluded missing-chii or missing-rating bouts, if any

---

# 2. Canonical Ordering

The analysis needs a canonical stronger/weaker ordering.

## Empirical

For empirical chii-based analysis:

```text
higher-ranked = lower/better chii ordinal
lower-ranked = higher/worse chii ordinal
```

`Chii.ordinal()` is the authoritative rank ordering in the core model.

Lower ordinal means higher-ranked.

`Chii.ordinal()` distinguishes east/west side and annotation. The oracle default
uses `collapse_mode="annotation_only"`, so annotations are not expected to drive
this analysis. East/west side remains part of the ordering.

No empirical tie policy is required: retained bouts are expected to have a
definite higher-ranked and lower-ranked rikishi under `Chii.ordinal()`.

## Model

For model-based analysis:

```text
higher-rated = larger pre-bout rating
lower-rated = smaller pre-bout rating
```

Use a deterministic total ordering:

```text
rikishi1 is higher-rated iff rating1_before >= rating2_before
otherwise rikishi2 is higher-rated
```

Exact equality is not analytically important, because ratings are continuous
floating-point values in practice. The `>=` rule exists only to make the
implementation total and deterministic.

---

# 3. Rank Representation

The empirical side depends on how chii is represented.

## 3.1 Base Representation

The base computation should use oracle-cleaned chii.

The oracle default removes annotations via `collapse_mode="annotation_only"`.
This is appropriate for this analysis. Annotated ranks are scarce, and the
public question does not depend on distinguishing them.

The rich CSV should preserve:

* full oracle-cleaned chii
* chii ordinal
* sideless chii
* division

The full chii/ordinal representation should be used for base ordering so that
nothing is lost in the analysis data.

## 3.2 Presentation Representation

The first observed-results presentation views should use sideless chii.

For example:

```text
M1e, M1w -> M1
J3e, J3w -> J3
```

This is a presentation/aggregation choice, not a loss of detail in the base
CSV.

## 3.3 Public Scopes

The first public per-sideless-chii views should be:

```text
Makuuchi only
Juryo only
```

Lower divisions may be present in the computed data, but they are not first-pick
public views because there are too many chii and the expected audience interest
is lower.

---

# 4. Empirical Aggregation

The observed-results side has three deliverables.

## 4.1 Rich Empirical Data

The package should write rich CSV artefacts before charting.

The bout-level empirical CSV should preserve enough detail to support later
views, including:

```text
date
day
rikishi1
rikishi2
chii1
chii2
sideless_chii1
sideless_chii2
division1
division2
ordinal1
ordinal2
higher_ranked_rikishi
higher_ranked_chii
higher_ranked_sideless_chii
lower_ranked_rikishi
lower_ranked_chii
lower_ranked_sideless_chii
ordinal_delta
winner
higher_ranked_won
```

Derived aggregate CSVs should include at least sideless-chii pair-level rows:

```text
selected_sideless_chii
opponent_sideless_chii
selected_division
opponent_division
n_obs
n_selected_wins
n_opponent_wins
p_selected_wins
ci95_lower
ci95_upper
```

and higher-vs-lower rows:

```text
higher_ranked_sideless_chii
lower_ranked_sideless_chii
higher_ranked_division
lower_ranked_division
n_obs
n_higher_ranked_wins
n_lower_ranked_wins
p_higher_ranked_wins
ci95_lower
ci95_upper
```

## 4.2 Per-Sideless-Chii Matchup View

For a selected sideless chii, show the observed probability of beating every
sideless opponent chii that it has actually faced.

The x-axis should contain every sideless opponent chii in the selected chii's
observed opponent set. The x-axis may therefore vary by selected chii.

The first public control set should be:

```text
division: Makuuchi | Juryo
sideless chii: ranks within the selected division
```

Expected visual form:

* column or point chart
* CI95 error bars
* hover text including `n_obs`

## 4.3 Aggregated Stronger-Ranked Distribution

The package should also produce an aggregate empirical view:

```text
P(higher-ranked sideless chii beats lower-ranked sideless chii)
```

This view should be support-weighted/bout-weighted. A matchup type with 1000
bouts should contribute 1000 times as much support as a matchup type with 1
bout.

Candidate scopes:

```text
Makuuchi
Juryo
all included divisions / broader domain
```

The exact chart form remains to be settled, but the data should support these
flavours.

---

# 5. Support and Uncertainty

Observed probabilities can be noisy when sample sizes are small.

The public observed charts should not initially hide rows behind an arbitrary
support threshold.

Instead:

* include all rows in CSV
* calculate CI95 for aggregate empirical probabilities
* show CI95 error bars in the per-sideless-chii view
* include `n_obs` in hover text

The interval method should be specified before implementation. Wilson 95%
intervals are the current likely choice because they are already used elsewhere
in the probability package.

---

# 6. Model Source

The model-based distribution requires pre-bout ratings and probabilities.

Questions to settle:

* Should the package run the Expt3 simulation directly?
* Should it consume bout-level forecasts written by `expt3c.py --bout-output`?
* Which model parameters define the default model distribution?
* Should alternate model settings be supported?

Current leaning:

* do not modify `expt3c.py`
* either reuse its simulation logic in a focused module or consume a rich
  bout-level model CSV
* record model parameters in metadata
* specify model-based presentation views after the observed-results views are
  settled

---

# 7. Comparison Shape

The empirical and model-based views are related but not identical.

Model-based per-bout quantity:

```text
p_higher_rated_wins = max(p_rikishi1_wins, 1 - p_rikishi1_wins)
```

Empirical aggregate quantity:

```text
p_higher_ranked_wins = n_higher_ranked_wins / n_obs
```

Questions to settle:

* What model-based views correspond to the empirical per-sideless-chii and
  aggregate views?
* Should the model aggregate use `[0.50, 1.00]` via `p_higher_rated_wins`?
* How should the labels avoid implying that empirical and model charts are the
  same statistic?

Observed-results comparison shape is settled for the first pass:

* per-sideless-chii matchup view
* support-weighted/bout-weighted aggregate stronger-ranked distribution

Model-based comparison shape is a placeholder for the next specification pass.

---

# 8. Outputs

The package should write durable analysis artefacts before publication charts.

Candidate outputs:

```text
files/output/probability/matchups/...
```

Candidate files:

* empirical bout-level CSV
* empirical chii-pair CSV
* empirical bucket CSV
* model bout-level CSV
* model distribution CSV
* comparable HTML chart or charts
* metadata JSON

Questions to settle:

* Exact output directory
* Exact filenames
* Which files are required for the first implementation
* Whether HTML is one combined page or separate chart pages

---

# 9. Time Range and CLI

Questions to settle:

* Default start year
* Default end year
* Whether `--zip` should be supported
* Whether empirical-only and model-only runs should be supported
* Whether chart generation can be run from existing CSVs

Current leaning:

* follow existing analysis defaults where possible
* support `--start`, `--end`, and `--zip`
* keep compute and chart generation separable if convenient

---

# 10. Output Semantics and Language

The public language needs to be careful.

Questions to settle:

* Should the empirical side say "higher-ranked" rather than "stronger"?
* Should the model side say "higher-rated" rather than "stronger"?
* Should "stronger" be used only as a generic internal label?

Current leaning:

* public labels should use:

  ```text
  higher-ranked
  higher-rated
  ```

* "stronger" can remain a shorthand in internal discussion only.

---

# 11. Reproducibility

The package should preserve enough information to reproduce the outputs.

Metadata should include:

* run timestamp
* date range
* history source policy
* oracle/cleaning policy
* chii representation policy
* model parameters
* included bout count
* excluded bout counts by reason
* output file names

---

# 12. Publication Boundary

This package may produce publication-ready CSV and HTML artefacts.

It should not own:

* SFTP deployment
* local web-root copying
* site navigation
* shared public shell/layout deployment

Those concerns belong to a future publication/deployment layer.

---

# 13. Initial Non-Goals

The first implementation should not:

* modify `expt3c.py`
* replace the existing calibration pipeline
* decide final website navigation
* claim that torikumi selection causally explains the results
* overfit the first public chart before the CSV artefacts exist
