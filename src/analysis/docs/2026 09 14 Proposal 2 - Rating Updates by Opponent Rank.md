# Proposal 2: Rating updates by opponent rank

## Status and question

**Subsequent scope change:** the direct-opponent proposal below is retained as
the initial requirements record. Later discussion moved to inherited holdings
by individual rikishi, with proportional transfers, frozen departure rows and
post-run aggregation. The author selected retention of first stints and
exclusion of later returning appearances. The implemented experiment and its
live-store results are documented in
[Individual rating provenance](../inflation/expt2/README.md). The live-store
is the default source; no full ZIP replay was conducted. This supersedes this
proposal's direct-only accounting scope, not Experiment 1's settled proposal.

**15 September correction:** the author subsequently chose to ignore gaps:
preserve each individual's rating and provenance while absent and resume on
return, including Sokokurai. No returning bouts are excluded and no new P1
allocation is made on return. The current implementation uses this persistent
gap policy; the first-stint results are retained only as historical outputs.

Initial experiment proposal, 14 September 2026; no implementation or results.
Use the same post-1988, fixed-P1 replay without either basho-boundary
mean-preservation step specified in
[Proposal 1](2026%2009%2014%20Proposal%201%20-%20Unnormalised%20Turnover%20Accounting.md).
The shared replay contract, membership rules, provenance and production
separation in that proposal apply here unchanged.

For wrestlers occupying each rank or rank group, how many points do they gain
and lose against each opponent rank group? What proportion of their gross
gains and losses comes from each group? For a selected wrestler, how do those
contributions compose the change from their assigned entry rating?

This measures direct opponent contributions at the time of each bout. It does
not recursively trace the original owner of points an opponent acquired in
earlier bouts. That earlier provenance idea would require a separate allocation
convention and is not necessary for the requested Y1e-versus-M10w accounting.

## Exact bout accounting

Retain one canonical bout record with date, day, bout identity, both rikid,
both literal chii at that basho, outcome, pre-bout estimates, probability,
both K values and both actual signed updates. The current Elo-89 Forecast
already captures most of these fields. Derive two participant records from
each bout: subject, opponent, their respective chii/groups, subject's signed
update and subject's episode identifier.

For subject update delta define:

```text
gain = max(delta, 0)
loss = max(-delta, 0)
net  = gain - loss
```

A Y1e win over M10w contributes the actual Y1e gain to the Y1e/M10w cell and
the actual M10w loss to the M10w/Y1e cell. Do not assume they are equal, even
when an illustrative example uses five points on each side. With unequal K,
the winner gain G and loser loss L leave a bout mass residual G-L. Preserve
that residual and reconcile it with Proposal 1.

Initial P1 allocations, population entries, exits and resets are separate
ledger events, not invented bouts against an opponent rank. Their points
must never enter the opponent-gain/loss totals.

## Aggregation and denominators

Primary groups, in banzuke order:

1. Sanyaku: Yokozuna, Ozeki, Sekiwake and Komusubi (explicitly including all four).
2. Maegashira.
3. Juryo.
4. Makushita.
5. Sandanme.
6. Jonidan.
7. Jonokuchi.

Use an explicit Unknown category when chii cannot be classified; disclose its
counts and keep it in totals. Retain literal chii in the source data. Optional
drilldown uses the agreed levels: each sanyaku title, then numbered ranks M1,
M2, etc., combining east/west. No further ad hoc regrouping is needed initially.

For subject group g and opponent group h over the selected dates, calculate:

```text
G[g,h] = sum(subject gains)
L[g,h] = sum(subject loss magnitudes)
Net[g,h] = G[g,h] - L[g,h]
gain_share[g,h] = 100 * G[g,h] / sum_h G[g,h]
loss_share[g,h] = 100 * L[g,h] / sum_h L[g,h]
```

Gains and losses have separate denominators and separately sum to 100% per
subject group where nonzero. Do not divide by net gain: cancellation could
make that denominator zero or produce misleading percentages. Do not divide
by current rating to describe a share of bout-derived points, because current
rating includes P1 and has an arbitrary origin. Zero-denominator shares are
not applicable, not fabricated zero-percent distributions.

These are pooled shares of rating-point activity, not averages of individual
wrestlers' percentages. Retain bout-participation counts, distinct subject
counts, gains per win, losses per loss and net per participation to distinguish
activity volume from update size. Within-group bouts give two subject records;
label participation counts accordingly rather than calling their sum unique
bouts. Count wins and losses from outcomes, including a possible zero update.

## Two different meanings of a subject's rank

The primary matrix classifies both wrestlers by their chii at the bout. It
answers, for example, what Makuuchi occupants gained while occupying Makuuchi.
Earlier lower-division gains of a later yokozuna must not be relabelled as
Yokozuna-versus-lower-division bouts.

Provide a second, explicitly labelled endpoint-cohort view for the question
"where did the ratings of wrestlers now at this chii come from?" Choose a
pre-basho endpoint and group the wrestlers represented there by their chii at
that endpoint. Sum their actual bout updates before that endpoint, within
their current represented episode, by opponents' ranks at the original bouts.
Include their earlier subject ranks in drilldown. The endpoint is exclusive
of its own basho's bouts, consistent with pre-basho sampling.

For each selected wrestler and each pooled endpoint cohort, reconcile:

```text
pre_basho_rating = current_episode_P1_allocation
                  + gains_since_episode_entry - losses_since_episode_entry
```

Older episodes remain inspectable but are not added into a reinitialised
current rating. Label initial-cohort episodes as left-censored. A selected
date range within an episode instead reconciles its actual start estimate
plus the updates in that range. Do not imply full-career coverage from a
partial range. Use actual loaded pre-basho endpoints, not synthetic dates.

## Interactive HTML charts

Use the same versioned Plotly CDN, embedded-data, reactive filtering and
responsive HTML requirements as Proposal 1. The initial deliverable should
contain a small set of linked views:

1. **Opponent matrix:** subject groups as rows and opponent groups as columns.
   Switch between gains, losses, net, gain share and loss share. Use sequential
   colours for nonnegative values and a zero-centred diverging scale for net.
   Hover shows raw points, percentages, participation counts and denominators.
   Offer totals and per-participation views with clearly different units.
2. **Selected-group profile:** two 100% stacked bars showing the source of gains
   and destination of losses across opponent groups; accompanying absolute
   bars retain the scale hidden by percentages. Drill down to levels or an
   individual wrestler. Do not subtract one percentage distribution from the
   other to call it a net flow.
3. **History of contributions:** for a selected subject group, show per-basho
   signed net updates by opponent group, with separate gain/loss modes and an
   optional cumulative view. No smoothing or burn-in by default.
4. **Endpoint cohort/individual composition:** show P1 allocation, positive
   opponent-group contributions, negative contributions and resulting pre-basho
   rating as a waterfall or equivalent signed accounting chart. Provide the
   separate gain/loss percentage profiles alongside it. Explain that the
   endpoint cohort's earlier bouts occurred at its historical ranks.

Controls include date range, aggregation level, subject group or rikishi,
metric and the explicit at-bout/endpoint-cohort view. Changing controls must
update titles, units, totals and denominators together. Default to the seven
groups and full history in the at-bout view. Display no-data states explicitly.
Filtering never reruns or reinitialises the rating model.

## Outputs and checks

Reuse the shared canonical replay and manifest; do not create an independently
configured second history. Retain participant ledger, grouped per-basho
aggregates, selected-endpoint episode/cohort summaries, CSV exports, HTML,
and a findings note defining every percentage and cohort. Precompute the
seven-group aggregates; load or embed compact drilldown data so interaction
does not require rebuilding the entire raw bout ledger on every control change.

Reconcile both participant updates against every canonical bout. Across all
groups, sum(gains)-sum(losses) must equal the total bout mass residual from
Proposal 1. Verify individual episode and endpoint identities; percentage row
sums; same-group bouts; unequal-K cross-group bouts; promotions/demotions;
returns/resets; zero denominators; Unknown chii; and selected-date boundaries.
Check chart values independently against CSV aggregates and exercise the
interactive controls and resizing in a browser.

This experiment will show direct numerical exchanges by opponent rank and
their history. It will not by itself prove that points earned against a
lower-ranked opponent originally entered through Jonokuchi churn, or measure
the counterfactual effect of removing that churn. Such a claim must not be
inferred from a matrix of direct bout contributions.
