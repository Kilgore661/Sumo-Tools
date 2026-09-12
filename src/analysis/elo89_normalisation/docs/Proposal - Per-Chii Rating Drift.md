# Proposal: per-chii rating drift after mean preservation

Date: 12 September 2026.
Status: proposed; no analysis has been run under this proposal.

## Question and purpose

After Elo89's pre- and post-basho normalisation, do the ratings of the
occupants of a particular chii tend to rise or fall over historical time?

The active population mean is fixed by construction. That does not fix the
mean at each chii, the spread of ratings, or the gaps between groups of chii.
This study will describe those quantities in the saved production run and
identify sustained movements, reversals and exceptions. It supplies evidence
for the account's discussion of normalisation and historical comparability.
It is not a requirement to change or reject the accepted model.

Here, “drift” means an observed temporal trend in ratings at a chii. It does
not, by definition, mean an error or inflation caused by the algorithm. A
trend can reflect changing occupants, competitive relationships, population
composition, rank conventions, initialisation or model mechanics. Causal
attribution is a subsequent question.

## Relationship to existing work

The completed [normalisation investigation](Normalisation%20Investigation.md)
measures the contribution of common adjustments to individual rikishi's
rating changes. This proposal instead follows banzuke positions as their
occupants change, using the final ratings after those adjustments.

The prior producer's convergence concerns successive passes over the same
history. It does not demonstrate stability across historical dates. Likewise,
the divisional-averages experiments on the pre-1989 extension are not a
temporal drift test of the production Elo89 run.

## Scope and inputs

Implement a supplementary analysis within `src.analysis.elo89_normalisation`,
reusing the existing input validation where appropriate. Read the saved
production artifacts, normally under
`files/output/analysis/site89_bundle/sources/elo89`, and matching History
metadata. Do not regenerate ratings, fit priors, change population policies,
extend the date range, or regenerate the website.

The currently inspected run covers January 1989–July 2026, with 224 represented
basho. Read actual coverage from the manifest; do not infer it from the ZIP's
filename. Inputs comprise the manifest, basho-start and basho-end snapshots,
adjustment records, the saved prior table and the History banzuke records.
Reuse the bout ledger if needed for the existing validation.

Record source paths and hashes, actual dates, grouping rules and all analysis
settings in an output manifest. Keep output in a new subdirectory,
`files/output/analysis/elo89_normalisation/chii_drift`, so the completed
contribution study's outputs remain intact. A future command may be
`python -m src.analysis.elo89_normalisation.chii_drift`; it does not yet exist.

## Observations and chii definitions

The primary observation is one rikishi at one represented basho, with his
rating **after post-basho normalisation**, attached to his chii on that
basho's banzuke. Do not attach the rating to his next basho's chii.

Keep the corresponding rating after pre-basho normalisation as a parallel
series. It is a required sensitivity comparison, since the prior construction
aggregates basho-start ratings and the current basho's results affect the end
rating. Do not mix the two endpoints in a single average.

Preserve RikId, date, literal chii, division, both ratings and first-observed
or returning status. Retain the complete original chii label, including side
and any annotations, even when grouping it for a chart.

Use literal side-specific chii as the audit level. For the main overview,
also group the east and west sides of the same numbered rank. Keep numbered
yokozuna, ozeki, sekiwake and komusubi positions distinguishable in the source
data; provide separately labelled title-group summaries. Do not silently
inherit the broader collapsing used by the production prior consumer.

If several occupants map to the same group at a basho, average them within
that basho first. Then weight represented basho equally when summarising that
group over time. Report occupant counts as well as basho counts. Literal
duplicate positions must be retained and flagged, not silently overwritten.

Absence of a chii is missing support, not a zero rating. Do not interpolate
ratings for absent positions or join trend lines through long unsupported
periods without making the gap visible. Unclassified active rikishi belong
in population reconciliation but not an invented chii group.

## Primary descriptive analysis

1. Verify the fixed global mean at both snapshot endpoints for every basho.
   Show population size and the range of numerical residuals from the target.
2. For every chii/group, tabulate ratings by calendar period: 1989–1993,
   1994–1998, and successive five-year periods, ending with the partial
   2024–2026 period. Display actual coverage, number of represented basho,
   occupant observations and distinct rikishi. Do not present the final
   partial period as equally well supported as a full period.
3. Report the period mean, median, quartiles and range. Retain raw per-basho
   values, so summaries can be traced to occupants and dates.
4. Plot the per-basho series and a trailing 12-represented-basho mean. Require
   observations in at least six of those basho to display the rolling mean,
   and expose the actual count. Never fill missing chii with zero. This is a
   display convention, not a definition of stability.
5. Summarise each sufficiently supported series with an ordinary least-squares
   slope in points per calendar decade, using the per-basho group means and
   actual dates. Also report the first-versus-last period mean difference
   and the largest separation between period means. A near-zero full-run
   slope can conceal a rise followed by a fall.

Keep all groups in the coverage table. As a provisional reporting rule, rank
slopes only where a group has at least 60 represented basho spread over at
least ten calendar years. Display which periods provide that support. Show
lower-support groups separately rather than treating them as stable or
discarding them from the record. These thresholds control presentation, not
statistical significance or model acceptance.

The first pass is descriptive. Consecutive observations are dependent, often
belong to the same rikishi, and share population adjustments. Do not attach
ordinary independent-observation confidence intervals or p-values to these
slopes. Any later inferential study must specify a dependence-aware procedure
and address the many chii being examined.

## Reading a fixed mean alongside moving groups

Provide a compact population overview alongside the per-chii results:

- rating quantiles and spread over time;
- division means and membership counts, with the full population as the
  primary unit of normalisation;
- differences between selected group means where both are observed.

At each date, reconcile the count-weighted means of an exhaustive partition
of the population, including unclassified entries, to the preserved global
mean. Do not substitute an unweighted average of chii means. Changing
membership weights can accompany movement in group means, so a fixed global
mean does not imply that an observed rise in one group must be matched by an
equal fall in another group's mean.

Use a common additive shift of all ratings and the target as a verification:
slopes, period changes, spreads and between-group gaps must be unchanged.
Report temporal changes in points, not as percentages of absolute ratings.

## Required comparisons and interpretation checks

- Compare basho-start and basho-end findings. Distinguish agreement in the
  broad pattern from differences induced by the current basho's results.
- Repeat the trend summaries excluding the first 12 represented basho.
  Label this as sensitivity to the start of the simulation; do not claim
  that initialisation effects must have vanished by then.
- Compare full-history trends with the January 2000 onward period. Report
  disagreement rather than selecting whichever period looks more stable.
- For groups with conspicuous movement, inspect changes in occupants,
  distinct-rikishi counts, division depth and rank availability. Show the
  most frequent occupants and their shares of observations. This is context,
  not a causal explanation obtained automatically from a chart.
- Show all supported groups in a heatmap or sortable summary, as well as
  familiar top ranks and the largest positive and negative movements. Avoid
  relying only on selected attractive examples.

The fixed prior table can be shown as a clearly labelled reference line only
where its grouping matches the displayed data. A constant reference line is
not evidence of temporal stability. A gap from that prior is not by itself
an estimation error.

## Deliverables

- `observations.csv`: auditable rikishi/basho rows with literal and grouped
  chii, both endpoints, and membership flags.
- `chii_basho.csv` and `chii_periods.csv`: per-basho and period summaries with
  endpoint labels and support counts.
- `trend_summary.csv`: slopes, period contrasts, support eligibility and
  sensitivity comparisons for every group.
- `population_summary.csv`: global checks, quantiles, division means/counts
  and reconciliation residuals.
- `report.md`: main findings, exceptions, support limitations and the precise
  claims the production account can make.
- `charts.html` with supporting data: readable overview and selectable chii
  traces, clearly distinguishing missing support and the two endpoints.
- `manifest.json`: provenance, settings, schema versions and produced files.

Use the package's existing chart approach where practical. Numerical tables
should make positive and negative changes easy to compare. The report should
answer whether movements are predominantly directional, temporary, confined
to particular groups, or sensitive to the selected period. It must be able to
report mixed evidence rather than force a single stable/unstable verdict.

## Verification and completion

Check unique rikishi/date observations, snapshot membership, matching chii,
finite ratings, period boundaries and exact aggregation counts. Reconcile
both full-population snapshot means with the saved target. Verify missing
positions remain missing and equal-basho weighting differs correctly from
occupant weighting when group sizes change.

Small fixtures should include a constant global mean with diverging group
means, a trend reversal with little net slope, changing group membership,
missing positions and irregular dates. Spot-check reported examples against
the source snapshots and banzuke. Verify additive-shift invariance and that
inputs remain unchanged.

The study is complete when the summaries, charts, checks and an interpretable
account of the observed movements are available. It need not establish a
cause, prove absence of drift, or propose a replacement normalisation rule.
No counterfactual replay or new prior fitting is part of this proposal.
