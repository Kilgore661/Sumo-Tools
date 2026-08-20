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
level. It distinguishes the fixed-supported map used by current production
Equelo from the contextual entrant-prior policy adopted for the next
implementation. A later detailed-technical account will specify the exact
algorithms, historical-data contracts and worked examples.

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

## Informed entrant initialisation

When a historical Elo calculation begins, it seems bizarre to give a yokozuna
and a jonokuchi rikishi the same initial rating. The banzuke already gives us
good reason to expect the yokozuna's eventual rating to be much higher.
Starting them equally forces the rating system to spend part of the early
history discovering something we already broadly know.

The obvious question is therefore: what initial rating should be associated
with a yokozuna, or with any other position on the banzuke? This creates an
apparent circularity. We want to use typical ratings by banzuke position to
initialise the calculation, yet those ratings can be derived only by running
the calculation that requires them as inputs.

## Fixed-point experiments

Equelo's initial-rating experiments address this iteratively. They begin with
provisional initial values, run the historical simulation, average the
resulting basho-start ratings by the categories being studied, feed those
averages back as the next initial values, and repeat.

The natural question is whether this process converges. In the implementations
tested so far, it does: successive maps converge to stable fixed points. This
makes each experimental map self-consistent under its chosen history,
parameters and representation. It does not prove that the representation is
the right one or that the values are uniquely true.

Early experiments grouped observations by literal chii. They produced a
broadly sensible curve, but also produced unsupported extreme values at rare
low ranks and a rise through the lower maegashira ranks. Support filtering and
completion control the extreme low-support failure in current production
Equelo. Later work also showed that a literal chii such as M16 does not denote
one stable position relative to the Makuuchi--Juryo boundary: the size and
shape of the banzuke change over time.

The later experiments therefore used positions relative to contemporary
division boundaries. These substantially improved important local shapes, but
did not reveal one timeless representation that removed every reversal across
modern and historical banzuke. The fixed-point results are consequently treated
as evidence about plausible entrant values, not as a direct final answer.

## The adopted entrant-prior policy

For simulations beginning in 1989 or later, the adopted next policy reconciles
two contextual fixed-point results: one centred on the Makuuchi--Juryo boundary
and one using a continuous coordinate from Juryo down the lower banzuke. The
estimates are aligned and blended through Juryo, used only through the range in
which their shape remains credible, and combined into east/west rank pairs.

The resulting curve is already sensible for shortening the initialisation gap,
so the project chooses not to smooth it further merely to enforce exact
monotonicity. A small Makuuchi--Juryo reversal remains and is disclosed. Once
bouts are observed, an individual rating is free to disagree with chii.

These values are therefore *chosen, historically informed entrant priors*.
They are not the direct output of one fixed-point solve, a timeless table of
the ability belonging to each chii, or a claim that convergence discovers the
truth. Ranks that occur only before 1989 lie outside this policy and require a
separate historical-completion decision.

Current production Equelo still uses the earlier fixed-supported literal-chii
map. The contextual policy described here has been adopted for the next
implementation but has not yet replaced that production map.

## Normalisation and the origin of the priors

A second normalisation operation appears inside each source fixed-point
experiment. After candidate values have been derived, the same additive shift
is applied to every category in that solve so that their unweighted mean equals
the chosen base. This fixes the origin without changing differences within the
map at that iteration. It is distinct from preserving the active rikishi mean
when a rikishi leaves.

The adopted priors combine two such source maps, including one common alignment
shift, but are not centred again after contextual values are resolved onto
literal ranks, blended, completed and paired. Their final unweighted mean
depends on the enumerated domain and completion policy and is not treated as a
property recovered from the bouts.

This lack of final recentring is harmless when every entrant in a complete
simulation uses the same table, because Elo expectations depend on rating
differences. A future consumer that mixes these priors with previously
established ratings, a fixed fallback value or a separate pre-1989 table must
choose and test an explicit common anchoring shift.
