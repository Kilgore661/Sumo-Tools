# Donor Replacement and Rating Inflation

## Status and purpose

Recorded on 14 September 2026 following discussion with the author. This note
states the agreed argument that replacing rating-point donors produces
inflation at the upper ranks in a deliberately simplified Elo system. It
includes the extension from single replacements to simultaneous batches and
the induction over successive replacement stages.

The post-proof addendum below records the subsequent discussion of applicability
to real sumo, including the author's responses to the proposed weaknesses. Read
it before treating those weaknesses as new objections or planning experiments.

This is a conditional mathematical argument, not a report of a new simulation
or an empirical finding about historical sumo. The relaxation assumption below
is part of the proposition: this note does not supply a convergence theorem
for stochastic Elo or a numerical definition of a sufficiently large gap.

## The question and the meaning of inflation

The original concern was that wrestlers who leave sumo with fewer rating
points than they received on entry leave transferred points with the continuing
population. Replenishing their positions with newly initialised wrestlers
introduces further points. The question is whether this mechanism can raise
the ratings associated with upper chii without any improvement in true strength.

Here, inflation means an increase across successive relaxed stages in the
rating level associated with an unchanged true strength, including the true
strengths assigned to the upper chii. It does not require every realised rating
to increase monotonically, nor does it require an assertion of unbounded growth.

The selection criterion is a deficit relative to a wrestler's entry rating.
Neither low chii nor a rating below the population mean defines a donor. A
wrestler at any chii can be a donor.

## Stipulated system

1. There are 21 fixed positions: Y1e, O1e, S1e, K1e and M1e through M17e.
   The argument also applies to a general fixed population size N.
2. Position i has a fixed true strength s_i equal to its P1 rating. Initially,
   its occupant's estimated Elo rating is also s_i. P1 is held fixed throughout.
3. Each bout selects two distinct occupants uniformly at random. Outcomes are
   independently generated conditional on the selected pair from the Elo
   probability function applied to their true strengths.
4. The rating updates use that same probability function and a common positive
   K. No pre- or post-basho mean preservation or other rating adjustment is
   applied. This artificial experiment has bouts, not basho.
5. A replacement occupies the same position, has the same true strength as the
   departing occupant, and receives the position's P1 rating. Survivors retain
   their current estimates. Population size and the true-strength distribution
   therefore remain unchanged.
6. Each replacement stage removes one or more donors: every selected departing
   occupant has an estimated rating strictly below their P1 entry rating.
7. Replacement stages are separated by enough bouts for redistribution towards
   the common-offset balance to apply. We reason about these relaxed rating
   levels, allowing stochastic fluctuations around them, rather than claiming
   exact finite-time settling of a realised Elo trajectory.

Random pairing is an explicit simplification. Modelling actual torikumi is
deferred. The construction of P1 is also outside this argument: using it both
as the true-strength vector and as the entrant-rating vector fixes those
choices for this artificial system.

## 1. Bouts conserve rating mass

Write the Elo probability function as

\[
F(x)=\frac{1}{1+10^{-x/q}},\qquad q>0.
\]

For a bout between i and j, with W_i equal to one for a win and zero for a
loss, the updates are

\[
\Delta R_i=K\bigl(W_i-F(R_i-R_j)\bigr),
\qquad \Delta R_j=-\Delta R_i.
\]

Their sum is zero. Hence total rating mass is constant between replacement
stages, for every realised sequence of bouts, not merely in expectation.

## 2. A donor replacement adds its deficit to the mass

If occupant j leaves with estimated rating R_j below their entry rating s_j,
their positive deficit is

\[
d_j=s_j-R_j>0.
\]

Replacing them at s_j increases total rating mass by exactly d_j. No survivor
is directly awarded points at replacement. The departing wrestler transferred
points in earlier bouts; replacement replenishes the deficit without removing
those transferred points from the continuing population.

For a simultaneous batch B of m donors, the added mass is exactly

\[
D=\sum_{j\in B}d_j>0.
\]

The population mean consequently increases by D/N. The mean is just an
equivalent expression of the mass change in this fixed-size population; it is
neither the selection criterion nor an additional explanatory mechanism.

Replacing additional donors adds strictly more mass than replacing any subset
of those same donors. Donor count alone does not order arbitrary different
batches: the relevant quantity is their total deficit.

## 3. Replacement creates upward pressure on survivors

A survivor i has actual winning probability F(s_i-s_j) against position j.
Replacement leaves this probability unchanged but raises the opponent's
estimated rating from R_j to R_j+d_j. The increase in i's expected Elo update
when facing that position is therefore

\[
K\left[F(R_i-R_j)-F(R_i-R_j-d_j)\right]>0.
\]

This applies to the strongest survivor as well as any other. With random
pairing, the effect can reach upper positions directly; it need not travel
through a succession of intermediate chii. The effects of several replaced
opponents add in a survivor's expected update over the possible pairings.

This is an increase relative to the update expected against the old opponent.
It need not make an already overrated survivor's expected update positive.
The conclusion about relaxed upper-rank levels uses the next step.

## 4. The balanced location of the added mass

The estimates

\[
R_i=s_i+c\quad\text{for every }i
\]

give exactly the true rating differences. Thus all matchup probabilities are
correct and every occupant has zero expected update.

Under uniform random pairing, a common offset is the only configuration in
which all occupants simultaneously have zero expected drift. To see this,
write the errors as e_i=R_i-s_i. If they are not all equal, an occupant with
maximal error has an estimated advantage at least as large as their true
advantage against every opponent, and strictly larger against at least one.
Because F is strictly increasing and every opponent has positive probability
of selection, that occupant's expected drift is strictly negative. Such a
configuration cannot be balanced.

If total rating mass is M, conservation determines the balanced offset:

\[
c=\frac{M-\sum_i s_i}{N}.
\]

Adding a batch deficit D therefore raises the balanced offset by D/N. Under
the stipulated relaxation assumption, this is the increase in the relaxed
rating level at every position, including the upper chii.

No uniform shift is being applied by the algorithm. The common offset
describes the balance towards which ordinary bout updates redistribute the
available mass. Identifying this balance is distinct from proving stochastic
convergence to it.

## 5. Induction over replacement stages

Initially the estimates equal P1, so the total mass is the sum of the true
strengths and the initial offset is c_0=0.

Suppose that after stage n-1 and its relaxation interval the balanced offset
is c_(n-1). At stage n, replace m_n donors whose total positive deficit is D_n.
Their replacement increases the mass by D_n, and bouts thereafter preserve
that mass. The next relaxed offset is therefore

\[
c_n=c_{n-1}+\frac{D_n}{N}>c_{n-1}.
\]

The same structural conditions hold for the next stage: identical fixed true
strengths, fixed P1 entry values, common K and a new accumulated offset. The
absolute starting ratings need not be identical from stage to stage.

By induction, after n admissible replacement stages,

\[
c_n=\frac{1}{N}\sum_{k=1}^{n}D_k,
\qquad
R^{\mathrm{balanced}}_{i,n}=s_i+c_n.
\]

The rating level associated with each upper position consequently increases
across these stages although its true strength is unchanged. Each batch has
the same qualitative effect as a single donor replacement, with its magnitude
determined by the sum of the donors' deficits.

**Under the stated assumptions, donor replacement causes inflation at the
upper chii. This holds for single replacements and for simultaneous batches
of m donors. QED.**

## Scope of the conclusion

The induction applies to any sequence of stages at which the stipulated
donors exist and sufficient relaxation occurs. It does not establish that
donors remain available indefinitely. At exact common-offset balance with
a non-negative offset, no occupant is below P1; donor opportunities must
arise from fluctuations away from that balance. A realised system is not
assumed to stop fluctuating during a large inter-replacement gap.

The proof does not say that stronger positions receive a larger share of the
extra mass than weaker positions. At balance they share a common offset.
Inflation at the top requires that the top's rating level rises, not that its
share of the increase is disproportionately large.

Historical applicability is a separate question. This argument does not
establish that real departures and entrants yield a net positive mass flow
after allowing for wrestlers who depart above their entry ratings, or quantify
the effect of actual schedules, variable population size and unequal K.
Nor does identifying this mechanism alone establish that preserving the mean
is the appropriate remedy.

The earlier [Strength, Purpose and Model Bias lab note](2026%2009%2011%20Strength,%20Purpose%20and%20Model%20Bias%20-%20Lab%20Note.md)
provides the broader interpretive context. The existing
[Elo-89 normalisation investigation](../elo89_normalisation/docs/Normalisation%20Investigation.md)
and [per-chii drift findings](../elo89_normalisation/docs/Per-Chii%20Drift%20Findings.md)
concern saved production ratings with mean preservation and answer different
questions from the artificial mechanism established here.

## Post-proof addendum: applicability to real sumo

### Agreed position and purpose of the discussion

The author accepts that, under the stated circumstances, inflation is a
meaningful concept and necessarily occurs. No experiment has been performed
for this argument. The next intellectual step is to challenge whether the
argument accurately captures real sumo, rather than repeatedly reopening the
conditional result.

This discussion explores potential weaknesses. It does not authorise or
specify a new implementation, simulation, historical replay or broad research
programme. The distinctions below should guide future work if it is requested.

The initial list of objections mixed three different things: empirical
premises that can be tested, interpretive assumptions already made explicitly,
and general limitations of Elo. They do not carry the same evidential weight.
A failure of applicability would show that this argument does not establish
inflation in historical sumo; it would not by itself establish its absence.

### 1. Actual net donation: the first empirical challenge

The artificial system deliberately replaces donors. Actual departures include
wrestlers leaving above their entry ratings, and actual arrivals and departures
need not pair up one for one. The author identified this as the first and most
readily checkable vulnerability: does historical turnover really provide the
asserted net surplus after the opposing effects are included?

The story about unsuccessful beginners is a proposed explanation, not evidence
that the balance is positive. The author's recollection is that earlier
experiments found rapid bottom-rank churn outweighed the effect of higher-rated
retirees; this addendum has not independently rechecked that recollection.

For a future historical accounting, changes in membership and the rating mass
assigned to arrivals or removed with departures must be distinguished from
individual entry-to-exit deficits, especially when population size varies.
Both can be informative, but they are not interchangeable quantities.

### 2. True ratings and the status of P1

The author's response to demanding accurate entrant ratings was: how do we
define a true rating in real sumo? Considerable earlier work attempted to
address this. Asking for independently known true ratings is not, on its own,
a constructive new objection.

In the artificial system, true strengths exist by stipulation: P1 defines the
outcome-generating probabilities. In real sumo, the closest interpretation is
a vector whose differences correctly describe matchup probabilities under
specified conditions. Neither the exact adequacy of a scalar representation
nor its values can simply be assumed independently observable.

P1 remains a pragmatic, informed initialisation policy, fixed once constructed.
Its fixed-point derivation is not a law of sumo and is not sacrosanct. That
limits claims of its truth, but does not require reopening its construction
before studying turnover. Distinguish the use of P1 as a declared convention
from a claim that P1 has independently measured real ability.

### 3. Changing ability: a general limitation of Elo

Actual wrestlers improve and decline; the artificial wrestlers do not. This
can affect the interpretation of entry-to-exit deficits. It is nevertheless
a general limitation of applying Elo to people, not a distinctive refutation
of the donor mechanism.

The author invoked Elo and FIDE as an informal analogy for proceeding with
useful ratings despite changing ability. The discussion did not verify a
historical quotation, a theorem attributed to Elo, or FIDE's institutional
reasoning. The position retained here is the pragmatic one: failure of the
idealised assumptions need not make the outputs useless, although it limits
what their usefulness establishes about the present explanation.

### 4. Fixed meaning of every chii: an explicit assumption

The author had explicitly stipulated that the meaning of every chii is fixed
over time. This is stronger than assuming only stable average quality across
sumo. An earlier assistant response weakened it to the latter and then raised
rank-specific change as though it were an unacknowledged omission.

Retain the stronger assumption. It is open to challenge as a representation of
real sumo, but it is not a newly discovered flaw in the conditional argument.
Historical interpretation of rank-associated rating growth is conditional on
this reference assumption; it has not been independently established as fact.

### 5. Transmission through the competitive population

The author regards it as clear that churn at the bottom of Jonokuchi can
eventually affect ratings above it, through to yokozuna. The discussion accepts
the transmission mechanism through the connected competitive population.
The substantive open questions are its magnitude and timescale under actual
torikumi, rather than repeatedly suggesting that an indirect connection cannot
transmit the effect.

Random pairing remains the deliberate first simplification for any artificial
experiment. The author has not found a satisfactory model of torikumi. There
is no present requirement to solve that problem before investigating the
simpler mechanism; schedule realism can be considered later if useful results
warrant a challenge.

The author suggested that a ratings-by-donor analysis might trace the origin,
by chii, of rating points reaching individual wrestlers. Most enter near the
bottom, while some enter at higher positions such as Makushita; those sources
could potentially be distinguished. This is an exploratory idea, not an
agreed implementation requirement.

The assistant noted that fractional provenance would require an explicit
accounting convention. Elo specifies how much a loser transfers but does not
uniquely specify which of several previously received sources fund that loss.
Source tracing under such a convention would also differ from a counterfactual
calculation of what ratings would have been without particular donors. These
are interpretation details for a possible analysis, not objections to the
existence of transfers.

### 6. Relaxation and initialisation memory: one technical uncertainty

Real churn is not separated by demonstrably sufficient relaxation intervals.
We do not have a justified historical timescale for forgetting initial values
or approaching the common-offset balance. The author recognises this as
difficult even in an artificial system perfectly compliant with the Elo
probability model.

Initialisation transients and the unresolved relaxation interval are related
parts of this same issue. Do not count them as two independent discoveries,
or treat a universal ten-basho forgetting period as established. Nor does
smoothing a series establish that initialisation effects have disappeared.

This limits the direct application of the relaxed-stage argument to a finite
historical trajectory. It does not undo the conditional proof, and the
discussion does not commission a wide-ranging convergence or forgetting study
as a prerequisite to further thought.

### 7. Unequal K and population size

The author is willing provisionally to treat the mass effect of variable K as
insignificant and recalls that an experiment probably measures it. The earlier
[Tranche 1 normalisation-policy record](story/15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md)
reports a controlled replay in which correcting unequal-divisional-K mass
required an average of about 0.0385 points per wrestler per basho, with a
maximum around 0.170. This is contextual support for treating the effect as
secondary, not a new verification run or a universal bound.

Unequal-K bout effects should remain conceptually separate from turnover.
Changing headcount likewise requires care in interpreting historical rating
mass. Neither is a reason to redefine donors as wrestlers below the population
mean: a donor's deficit is relative to their own entry allocation.

### Implications for future experiment design

The main empirical challenge is whether actual turnover supplies the proposed
surplus. The hardest dynamical uncertainty is how that surplus manifests over
the available timescale. Fixed chii meaning is an explicit interpretive
assumption. True-strength ambiguity and changing ability set wider limits on
Elo's interpretation, rather than independently refuting donor inflation.

The earlier historical experiment idea remains a starting point for later
discussion: hold P1 fixed, run the post-1988 Elo-89 calculation with both
pre- and post-basho mean preservation disabled, and inspect evidence of
inflation. This addendum does not finalise its metrics or authorise running it.
Pre-basho ratings were agreed as the initial sampling convention. Proposed
levels combine Yokozuna, Ozeki, Sekiwake and Komusubi by title, then numbered
ranks such as M1 and M2 with east/west pooled. No observation window, burn-in
period or growth criterion has yet been justified or selected.

Keep that historical question separate from the artificial system, where P1
is true by definition, pairs are sampled randomly, K is constant, headcount
is fixed and donors are deliberately selected. Also keep all of this separate
from normalisations used while deriving the fixed initial-rating map. The
mean-preservation policy is the policy under reconsideration.

Future discussion should preserve the agreed conditional QED and challenge
its historical applicability on the grounds above. Neither an upper bound on
inflation, non-monotonic realised ratings, multiple simultaneous donors, nor
the absence of disproportionately large gains at the top is a new objection
to the proposition actually stated.
