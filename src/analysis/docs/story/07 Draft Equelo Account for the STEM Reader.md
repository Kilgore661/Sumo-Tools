# Draft: How Equelo Changes Elo

## Status and scope

This is a draft construction account for the interested or STEM reader. It
starts from the standard account of Elo and records the principal changes made
by Equelo. It does not attempt to justify those changes empirically or compare
the resulting model with Basic Elo. Those are separate tasks for evaluation.

The intended construction has three headline changes:

1. replace constant `k` with divisional `k`;
2. normalise the rating scale to control inflation and deflation;
3. replace constant initialisation with a chii-informed prior.

This draft covers the three headline changes at the conceptual construction
level. A later detailed-technical account will specify the exact algorithms,
support and completion policies, historical-data contract and worked examples.

## Divisional `k`

In the Elo update formula, `k` controls how strongly a new result changes the
rating. A larger `k` makes the rating respond more quickly, while a smaller `k`
makes it more stable.

The intended rationale for divisional `k` is that larger values in the lower
divisions allow newcomers and rapidly developing rikishi to find their rating
level quickly, while smaller values in the upper divisions prevent a brief
winning or losing streak from moving an established rating too far. This uses
division as a proxy for how established and stable the rating is.

This idea is adapted from the varying development coefficients used in chess
rating systems. Equelo does not independently estimate the uncertainty or
stability of an individual rikishi's rating. Whether division is an adequate
proxy, and whether divisional `k` improves the resulting ratings, are questions
for evaluation.

## Normalisation and an open population

Even when individual Elo bouts are zero-sum, a historical rating population is
not closed. New rikishi bring ratings into the system and retiring rikishi
remove them. There is no reason for the rating mass brought in by entrants to
equal the rating mass removed by departures. The mean and absolute location of
the active rating scale can therefore drift over time.

Such drift may be called inflation when the scale rises and deflation when it
falls. It need not mean that rikishi have collectively become stronger or
weaker. It can be produced by the accounting of entry, results and retirement.
This makes simple comparisons of absolute ratings from different eras less
secure.

Equelo applies a uniform adjustment when a rikishi leaves, intended to preserve
the mean of the active population across that departure. The difference
between the departing rating and the existing active mean is distributed
uniformly among the survivors. Because every survivor receives the same
additive adjustment, their pairwise rating differences and model-implied bout
probabilities are unchanged at that moment.

This is intended to control inflation and deflation caused by population
change. Whether the adjustment has important effects on later trajectories,
and whether it is the best way to stabilise the scale, are questions for
evaluation.

Production Equelo also uses divisional `k`. When opponents have different
values of `k`, a cross-division bout need not be exactly zero-sum. The scale
stability of the complete system therefore cannot be justified solely by the
zero-sum property of ordinary equal-`k` Elo. The size and significance of this
additional rating-mass flow belong in the evaluation account.

## Chii-informed initialisation

When a historical Elo calculation begins, it seems bizarre to give a yokozuna
and a jonokuchi rikishi the same initial rating. The banzuke already gives us
good reason to expect the yokozuna's eventual rating to be much higher.
Starting them equally forces the rating system to spend part of the early
history discovering something we already broadly know.

The obvious question is therefore: what initial rating should be associated
with a yokozuna, or with any other chii? But this creates an apparent
circularity. We want to use typical ratings by chii to initialise the
calculation, yet those ratings can be derived only by running the calculation
that requires them as inputs.

Equelo addresses this iteratively:

1. start with the same provisional initial rating for every chii;
2. run the historical simulation;
3. group the resulting basho-start ratings by chii and take their averages;
4. normalise the resulting chii-rating map;
5. use that map as the initial-rating map for the next simulation;
6. repeat the process.

The natural question is whether this process converges. In the implementations
tested so far, it does: successive initial-rating maps converge to a stable
fixed point.

This produces a self-consistent association between chii and entrant rating.
It does not claim to discover the uniquely true rating of a yokozuna or any
other chii. It finds a map that, when used to initialise the historical
simulation, approximately reproduces itself in the resulting basho-start
ratings.

## Normalisation in the initial-rating construction

A second normalisation operation appears within this iterative construction.
After candidate initial ratings have been derived, the same additive shift is
applied to every candidate chii value so that their unweighted mean equals the
chosen base. This fixes the origin of the initial-rating map without changing
differences within that map at that iteration.

This operation is distinct from preserving the active rikishi mean when a
rikishi leaves. Its interaction with weakly supported chii will be specified
alongside the support and completion policies in the detailed-technical
account, then assessed separately in evaluation.
