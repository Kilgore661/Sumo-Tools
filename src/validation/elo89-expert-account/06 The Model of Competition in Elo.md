# 6. The Model of Competition in Elo

> **Draft status:** First continuous-prose draft. This chapter distinguishes
> what the Elo equations define from stronger interpretations which require
> additional assumptions. It describes the model before judging its adequacy
> for chess or sumo.

## From equations to a model

The equations in Chapter 5 are not model-free calculations. They impose a
particular structure on competition.

At time \(t\), ordinary Elo represents each competitor \(i\) by one real
number, \(R_i(t)\). When \(i\) faces \(j\), their current difference is passed
through one common probability function:

\[
P(i\text{ beats }j\mid R_i(t),R_j(t))
=F\bigl(R_i(t)-R_j(t)\bigr).
\]

After the result, the two coordinates are updated and become the state used
for later contests.

This can be displayed as a layered model:

```text
observed history: competitors, times and binary results
    -> one current scalar state for each competitor
    -> one universal difference-to-probability function
    -> a probability for the scheduled pair
    -> a result-dependent state transition
```

Each arrow is a substantive commitment. Elo does not merely collect the
evidence; it decides how that evidence is to be represented and carried
forward.

## The observational record does not contain strength

The directly observed objects are bouts: who competed, when, and who won. A
rating is added by the model. The record does not arrive with an independently
observed number called the rikishi's strength attached to it.

This distinction permits two levels of interpretation.

On the **operational interpretation**, a rating is exactly the state produced
by the recurrence. It summarises the selected past in the form required to
produce the next model probability. No further claim about an independently
existing quantity is necessary.

On a **latent-strength interpretation**, the rating is treated as an estimate
of an unobserved competitive property which helps generate bout outcomes. That
can be a useful scientific interpretation, but it is an additional hypothesis.
The Elo recurrence is not, by itself, proof that every rikishi possesses one
true scalar value or that the update has recovered it.

The safest exact statement is therefore:

> Ordinary Elo maintains a one-dimensional predictive state whose differences
> determine its conditional contest probabilities.

Calling that state *strength* requires an argument connecting the model state
to the intended real-world meaning of strength.

## A recurrence needs an initial state

The Elo equations describe how one rating state becomes the next. They do not
create the first state. Before the first represented contest can be processed,
the model must assign an initial rating to every competitor already present.

Write that initial state as

\[
R_i(t_0)=r_i^{(0)}.
\]

The values \(r_i^{(0)}\) are inputs to the recurrence. They may all be equal,
they may be informed by evidence preceding \(t_0\), or they may be supplied by
some separate model. None of these policies is derived from the probability
or update equation.

A simple ordinary-Elo calculation often begins with

\[
R_i(t_0)=b
\qquad\text{for every }i.
\tag{6.1}
\]

Two aspects of (6.1) must be separated.

First, the particular common number \(b\) is only the origin of the scale. By
translation invariance, starting everyone at 1,000 rather than 1,500 changes
no initial difference, probability or subsequent relative evolution, provided
the whole system is shifted consistently.

Second, giving everyone the **same** number is a substantive initial-state
choice. It makes every initial rating difference zero, so the model assigns
50–50 probabilities to the first contests. This need not mean that the
competitors are asserted to possess equal true ability. More cautiously, it
means that the initial rating state contains no information which distinguishes
them.

An unequal initial state can encode prior information, but that information
then becomes part of the model. If initial ratings use rank, earlier results or
expert judgement, the later ratings are no longer constructed from the
post-\(t_0\) contest sequence alone. The source, time boundary and intended
meaning of the initial information must be stated.

Initialisation also has lasting mathematical consequences. The first
probabilities depend on the initial differences; those probabilities determine
the first updates; and the resulting states enter every later update. New
results may progressively reduce sensitivity to the starting state, but the
ordinary recurrence contains no operation which instantly removes it after a
fixed number of contests.

Thus an Elo history requires both:

```text
an initial state
    + an ordered sequence of eligible results
    -> a sequence of later rating states
```

In a population whose membership changes, the same question reappears whenever
a competitor first becomes represented: what state should enter the recurrence
at that point? Section 7 examines the practical difficulty. The present point
is structural: initialisation is part of the rating model, not administrative
preparation performed outside it.

## One competitor, one scalar

At any instant the complete Elo representation of a competitor is one real
number. Differences in technique, health, experience, size, preferred style
and every other potentially relevant feature are either compressed into that
number or omitted.

This is a strong simplification, but not an incoherent one. A scalar gives a
common axis on which every represented competitor can be compared. It makes
the model economical, communicable and capable of connecting results through
a contest network.

It also means that the state contains no internal explanation. Two rikishi can
have the same rating after very different careers. Elo treats them identically
in a future contest against the same rated opponent unless some additional
feature is added outside the ordinary model.

The scalar assumption should not be confused with the weaker claim that a
one-number summary is sometimes useful. Elo asserts a particular use for the
summary: the difference of two such numbers is sufficient for the model's
probability of their contest.

## Rating difference is a sufficient matchup state

Once \(R_i(t)-R_j(t)\) is known, ordinary Elo's probability equation uses no
other information about the competitors or bout. Conditional on the current
states, the following do not enter separately:

- the competitors' identities;
- their previous head-to-head results;
- rank or division;
- age or career stage;
- injury or inactivity;
- style or technique;
- tournament score or bout importance;
- the route by which each rating was reached; or
- uncertainty about either rating.

This is a **sufficiency assumption inside the model**. It says that two
matchups with the same rating difference receive the same probability. It does
not establish empirically that the omitted information has no predictive
value.

The absolute rating level is also excluded from the matchup probability.
Competitors rated 2,300 and 2,100 receive the same probability as competitors
rated 1,800 and 1,600. Ordinary Elo consequently models relative location on a
common scale, not a separate effect of the level at which a given difference
occurs.

## One universal outcome curve

The parameter \(q\) fixes one function \(F\) for every represented contest.
The same numerical difference implies the same probability regardless of
competitor, date, division or region of the rating scale.

This gives the scale a stable internal interpretation. It also rules out, in
the ordinary model, such possibilities as:

- a 100-point difference being more decisive in one division than another;
- some competitors producing intrinsically more variable results than others;
- the probability curve changing between historical periods; or
- a particular pairing having an interaction not explained by the two
  individual states.

These are exclusions from the model, not findings about competition. A richer
model could include any of them, but its probability would no longer depend on
the ordinary Elo difference alone.

## The induced comparison is transitive

The scalar representation imposes a transitive ordering of model favourites.
If

\[
R_A>R_B
\quad\text{and}\quad
R_B>R_C,
\]

then

\[
R_A>R_C.
\]

Because \(F\) is strictly increasing, the model consequently favours A over B,
B over C, and A over C. Ordinary Elo cannot simultaneously represent a stable
rock–paper–scissors relationship in which A is favoured over B, B over C and C
over A.

The structure is stronger than ordinal transitivity. Define A's model odds
against B by

\[
O_{AB}
=\frac{P(A\text{ beats }B)}{P(B\text{ beats }A)}
=10^{(R_A-R_B)/q}.
\]

Rating differences add:

\[
R_A-R_C=(R_A-R_B)+(R_B-R_C).
\]

Therefore the model's log-odds add, and its odds multiply:

\[
O_{AC}=O_{AB}O_{BC}.
\]

Once two pairwise relationships have been placed on the common scale, the
third is constrained. The model cannot choose all pairwise probabilities
independently.

This is how Elo gains the ability to compare competitors who have not met: a
chain of common opponents can locate them on one scale. The same structure can
be a limitation if the real comparison relation contains persistent
non-transitive or pairing-specific effects.

## The scheduled pair is taken as given

Ordinary Elo supplies a probability after two competitors have been selected.
It does not model why that particular contest was scheduled.

Formally, it answers a conditional question:

\[
P(i\text{ wins}\mid i\text{ faces }j, R_i,R_j).
\]

It does not assign a probability that \(i\) will face \(j\), nor does it by
itself correct for the process which made the matchup observable. Schedule
strength enters indirectly because opponents have ratings, but the scheduling
mechanism remains outside the ordinary model.

This boundary is important. An opponent-sensitive model can use an unequal
schedule without thereby supplying a model of schedule formation.

## Time enters through events, not through a clock

Elo is time-indexed because its state changes as contests are processed in
order. But elapsed calendar time does no work in the ordinary equations.

If a competitor has no rated contest, his rating does not change. Ten contests
processed in a month create ten opportunities for change; the same ten
contests spread over a year create the same sequence of updates if their order
and all intervening states are otherwise identical.

The current rating is therefore a recursively compressed history, not a fixed
window. Earlier evidence persists through the state until later updates alter
its influence. There is no date at which an old result simply drops out, and
no universal number of months which the equations call “recent”.

The recurrence also has a Markov form at the level of the model: the next
probability and update require the current ratings, not the complete history
which produced them. The history matters because it produced the state; once
compressed into that state, its separate details are unavailable to ordinary
Elo.

## What fixed non-zero K means

With a fixed \(K>0\), the same prediction error always has the same numerical
effect on a rating. A result does not receive a smaller update merely because
the competitor has already completed many contests.

This makes ordinary Elo an adaptive process. New evidence continues to move
the state indefinitely. As Chapter 5 showed, if results are generated from the
model's current probability, the next update has zero conditional mean but
positive conditional variance. A correctly centred rating can therefore move
after an ordinary random result.

Fixed K consequently combines two effects which should be distinguished:

1. **learning or correction:** the current state may be a poor estimate, and a
   result supplies evidence for moving it; and
2. **tracking:** the competitive property represented by the state may itself
   change, so old evidence should not dominate forever.

The bare update equation does not tell us which effect caused a particular
residual. Nor does it specify a stochastic law by which an underlying true
ability changes. K determines how the algorithm responds; interpreting that
response as optimal learning about a latent process requires further theory.

This is why two apparently contrary descriptions of Elo can both contain part
of the truth. It can be studied as an estimator of stable latent strengths,
while a fixed-K implementation can also be used as a running tracker of
changing competitors. These are not the same statistical model, and the
recurrence alone does not settle between them.

## Does ordinary Elo assume stationarity?

The answer depends on what is claimed to be stationary.

Ordinary Elo with fixed parameters assumes a stable *form* for its model: the
same difference-to-probability function and the same update rule are applied
throughout the replay. In that sense, its response mechanism is stationary.

It does not require individual ratings to remain constant. They change after
results. Nor does fixed K force us to assert that a rikishi's underlying
competitive capacity is constant; continued responsiveness is compatible with
the intention to track change.

But ordinary Elo contains no explicit time-evolution model for latent ability.
It does not say how quickly a rikishi ought to improve with experience, decline
with age, recover from injury or lose precision during inactivity. If ratings
are interpreted as estimates of a changing real quantity, those dynamics are
being handled only implicitly through the stream of observed residuals.

We should therefore avoid both overstatements:

- ordinary Elo does not simply assume that competitors never change; and
- ordinary Elo does not provide a fully specified model of how they change.

## Probability, uncertainty and information

The number \(p_A\) is uncertainty about the outcome under the model. It is not
an uncertainty interval around \(R_A\), and it does not report how much
evidence supports either rating.

Two competitors with equal ratings receive a 50–50 matchup probability whether
both states are supported by hundreds of results or each was assigned moments
ago. Ordinary Elo's state contains no separate coordinate for estimation
uncertainty. Similarly, a long absence does not widen an interval or lower a
confidence measure because no such quantity exists in the model.

Outcome uncertainty and rating uncertainty are different. The first is
represented by \(F(R_A-R_B)\); the second is absent from bare point-rating Elo.
Adding it would create a richer model rather than reveal a quantity already
encoded in the rating.

## What ordinary Elo claims—and omits

The operational model makes a compact set of commitments:

- every represented competitor enters the recurrence with an assigned initial
  state;
- every competitor is represented at an instant by one scalar state;
- the difference of two states is sufficient for the matchup probability;
- one common logistic curve maps every difference to probability;
- the scheduled matchup is treated as given;
- results update the states sequentially through one common fixed K;
- history affects the future only through the current states; and
- elapsed time without an observed contest does not alter the state.

It omits explicit representations of style, injury, physical attributes,
career stage, motivation, bout importance, schedule formation and uncertainty
about the ratings. It also leaves the interpretation of the scalar open beyond
the exact role assigned to it by the equations.

These omissions are not automatically defects. A model is useful partly
because it is selective. The relevant questions are whether the retained
structure is adequate for the purpose, whether the omitted structure causes
material failures, and whether added complexity earns its place.

Those are empirical and applied questions. We now turn from the model implied
by ordinary Elo to the difficulties encountered when that model is used in
chess and, especially, professional sumo.

## Working sources

- `../../analysis/docs/2026 09 11 Strength, Purpose and Model Bias - Lab Note.md`
- `../../analysis/docs/2026 09 26 Chii and the Measurement of Strength.md`
- `../../../docs/What It Means to Test a Sumo Model.md`
- `../../../docs/Foundations/01-what-is-this-about.md`
- `../../../docs/Foundations/02-base-model.md`
- `../../../docs/Foundations/05-mathematical-context.md`
