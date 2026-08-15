# Draft: A Standard Account of Elo

## Status and scope

This is a draft for the interested or STEM reader. It explains the mechanics
of Elo and the principal difficulties involved in applying a Basic Elo model
to historical sumo. It does not attempt to establish that Elo probabilities
are well calibrated or that Elo ratings measure a competitor's true strength.
Those are questions of validation and interpretation, to be considered
separately.

## Why use an opponent-sensitive rating?

In a complete and balanced competition, a table of wins and losses may provide
a reasonable summary of performance. Grand Sumo is not such a competition.
Rikishi do not all face the same opponents. Many pairs never meet, while other
pairs meet repeatedly. A win over a strong opponent is therefore not the same
kind of evidence as a win over a weak one.

Elo addresses this problem by maintaining a running rating for each
competitor. After every recorded result, it changes both ratings according to
how expected or surprising the result was. Beating a much lower-rated opponent
changes little; losing to that opponent changes much more.

This is the central idea of Elo. The formulae below make the idea precise.

The system is named after Árpád Élő, a Hungarian-American physicist and chess
player who developed it for the United States Chess Federation. The USCF first
implemented his system in 1960, and FIDE adopted it for international chess
ratings in 1970.

Adoption by FIDE establishes Elo's practical importance, but not that every
interpretation of its ratings is sound. Simplified theoretical accounts of Elo
often assume a fixed population of competitors with unchanging abilities.
Neither assumption holds in historical chess or Grand Sumo: competitors enter
and leave, while individuals improve, decline and experience interruptions.
The calculation can still be used, but claims that its ratings converge to
stable measures of underlying ability require much greater care.

## A Basic Elo model

There is no single set of numbers called *the Elo model*. An implementation
must specify its parameters, initial ratings, starting date, eligible results,
identity rules and update order. The following is a common Basic Elo form.

Let rikishi \(r\) and \(s\) have ratings \(E_r\) and \(E_s\) immediately before
a bout. The model assigns \(r\) the expected score

\[
p_{r,s} = \frac{1}{1 + 10^{(E_s-E_r)/q}},
\]

where \(q>0\) controls the scale on which rating differences are interpreted.
For a decisive win or loss, define

\[
w_r =
\begin{cases}
1 & \text{if } r \text{ wins},\\
0 & \text{if } r \text{ loses}.
\end{cases}
\]

The rating update is

\[
E'_r = E_r + k(w_r-p_{r,s}),
\]

where \(k>0\) controls the size of the response to a new result. In the
ordinary equal-\(k\) model, the opponent is updated in the same way:

\[
E'_s = E_s + k(w_s-p_{s,r}).
\]

For a decisive bout, \(w_s=1-w_r\) and \(p_{s,r}=1-p_{r,s}\). It follows that

\[
E'_s-E_s = -(E'_r-E_r).
\]

The bout is therefore zero-sum: one rikishi gains exactly the number of rating
points that the other loses. This property depends on using compatible
expected scores and the same \(k\) for both competitors. It should not be
assumed automatically for every Elo variant.

A specified Basic Elo model may ignore an absence or another event in which no
bout takes place. That is an eligibility rule: without an observed win or loss,
the result-update formula has nothing to process. Other systems could add an
explicit inactivity or injury policy, but that would be an additional model
choice rather than part of the calculation above.

## Rating differences and estimated probabilities

Only the difference between the two ratings appears in the expected-score
formula. If \(E_r=E_s\), then \(p_{r,s}=0.5\). If \(E_r>E_s\), the model favours
\(r\); if \(E_r<E_s\), it favours \(s\). No finite rating difference produces
an expected score of exactly zero or one.

The two expected scores are complementary:

\[
p_{r,s}+p_{s,r}=1.
\]

This makes them coherent as the model's probabilities for the two possible
winners. It does not establish that bouts assigned 70% are in fact won about
70% of the time. Whether the estimates are useful or well calibrated is an
empirical question.

The parameter \(q\) is essential to interpreting a numerical difference. If
\(r\) has a rating advantage \(D=E_r-E_s\), then

\[
p_{r,s} = \frac{1}{1+10^{-D/q}}.
\]

Thus the probability depends on the ratio \(D/q\), not on \(D\) alone. A
400-point difference has no universal meaning across all Elo implementations.
With \(q=900\), for example, it produces an expected score of about 0.74. With
\(q=400\), an advantage of about 177 points produces approximately the same
expected score.

This explains the 400-point examples in the casual introduction: they are
illustrations on a scale with \(q=900\). Another Elo implementation may use a
different scale and assign different numerical gaps to the same estimated
probabilities.

## A worked example

Suppose that, immediately before a bout, one Elo model assigns Abi a rating of
2042 and Oho a rating of 1865. These values are illustrative; they are not
being presented here as verified ratings from a specified historical run. Let
the model use \(q=400\) and \(k=35\).

Abi's rating advantage is 177 points, so his expected score is

\[
\begin{aligned}
p_{\text{Abi},\text{Oho}}
&= \frac{1}{1+10^{(1865-2042)/400}} \\
&\approx 0.735.
\end{aligned}
\]

The model therefore gives Oho the complementary expected score

\[
p_{\text{Oho},\text{Abi}} \approx 0.265.
\]

If Abi wins, his change is

\[
35(1-0.735) \approx 9.3,
\]

so his rating rises to about 2051.3 and Oho's falls to about 1855.7. The
favourite has confirmed what the model already expected, so the adjustment is
comparatively small.

If Oho wins, Abi's change is

\[
35(0-0.735) \approx -25.7.
\]

Oho gains the same 25.7 points. The unexpected result produces the larger
adjustment.

Once a definitive Basic Elo implementation is used in the validation work,
this example can be replaced with ratings taken immediately before a specified
Abi--Oho bout. Any such values must still be described as ratings assigned by
that model, not as model-independent properties of the two rikishi.

## The roles of the parameters

### The initial level \(b\)

A simple Basic Elo implementation may assign every competitor the same initial
rating \(b\). The choice establishes the numerical origin of the scale, but it
does not affect probabilities if every rating is shifted by the same amount.
For any constant \(c\), replacing every \(E_r\) with \(E_r+c\) leaves every
rating difference, expected score and subsequent update unchanged apart from
the same common shift.

This property is called *translation invariance*. It is why an isolated rating
such as 2000 is not an amount of strength. Its meaning comes from its
difference from other ratings produced on the same scale.

Although the common value of \(b\) is arbitrary, assigning the same initial
rating to competitors who enter at very different levels is not harmless.
Their early ratings must move away from that common value as results arrive.
The period during which a rating remains materially affected by an
uninformative starting value is called *initialization lag*.

Equal initialization is a feature of this Basic Elo implementation, not a
requirement of every Elo-derived system. Different entrant ratings can be used
if the model supplies a principled way to choose them.

### The update rate \(k\)

The parameter \(k\) controls how strongly the newest result changes the
ratings. For a finite rating difference, the magnitude of a decisive-bout
update is less than \(k\), although it can approach \(k\) for an extremely
surprising result.

A small \(k\) makes ratings respond slowly. A large \(k\) makes them respond
quickly but also makes them more volatile. Choosing \(k\) is therefore a choice
about responsiveness, noise and the time scale over which past results retain
influence. Elo variants may also use different or changing update rates.

### The probability scale \(q\)

The parameter \(q\) controls how strongly a given numerical rating difference
changes the expected score. Increasing \(q\) makes the expected-score curve
flatter when differences are measured in the same rating points; decreasing
\(q\) makes it steeper.

The value of \(q\) must therefore accompany any probability interpretation of
a rating difference. It is not enough to say that one rikishi leads another by
400 points.

The parameters are also linked to the numerical units of the scale. If all
ratings, \(b\), \(q\) and \(k\) are multiplied by the same positive constant,
the expected probabilities and the underlying sequence of updates are the
same, expressed in larger or smaller rating units.

## A chronological calculation

An Elo history is normally calculated in chronological order. Immediately
before each eligible bout, the current ratings produce an expected score. Only
after that forecast has been recorded is the result used to update the
ratings. This forecast-before-update order is essential if the probabilities
are later evaluated as predictions.

The resulting ratings depend not only on \(b\), \(q\) and \(k\), but also on:

- the date at which the calculation starts;
- which historical bouts are available;
- which outcomes are eligible for updating;
- how rikishi identities are followed across names and careers;
- how entrants are initialized;
- whether ratings persist through absences;
- the order in which records are processed.

These choices belong to the definition of a particular implementation. The
formula alone does not determine a unique historical rating series.

## What the calculation records

Basic Elo is transparent in a limited but useful sense. Once the input history,
identity rules, parameters and update rules have been fixed, a rating changes
because of recorded results. A win is weighted by the model's prior estimate
of the opponent, so Elo contains information that a simple win total omits
when schedules differ.

The calculation does not directly know why a result occurred. It does not know
about injury, form, style match-ups, motivation, the importance of a bout or an
administrative absence unless such information is explicitly added to the
model. Transparency of calculation should therefore not be confused with a
complete explanation of performance.

Nor does transparency remove judgement from the construction. The data,
parameters, initialization policy and eligibility rules are all choices that
must be stated and defended.

## Incomplete comparisons

Elo learns relative ratings through the network of recorded bouts. If two
groups of rikishi never compete across the boundary between them, results can
identify differences within each group but cannot determine the rating offset
between the groups. Adding a constant to every rating in one disconnected
group would leave all of its internal expected scores unchanged.

Sparse bouts between groups can connect their scales, but the result may depend
heavily on a small amount of bridge evidence. This matters in sumo because
bouts are predominantly local: rikishi usually face opponents near them in the
banzuke, and cross-division comparisons are relatively rare.

Unequal schedules are one reason to use an opponent-sensitive rating, but they
also limit what the resulting rating system can identify.

## Changing competitors and incomplete history

The cleanest mathematical picture imagines a fixed population whose underlying
performance levels do not change. Historical sumo violates both assumptions.
Rikishi improve, decline, become injured, return from absence and retire. New
rikishi enter continually, often with very short lower-division careers.

The historical record is also incomplete. Full lower-division bout results are
available only for the later part of the history used by this project. A
rikishi appearing in the recorded sekitori results may already have accumulated
substantial unobserved lower-division experience. Basic Elo cannot recover
information from bouts that are not present in its input.

These circumstances make initialization particularly important. They also
make it unsafe to describe a rating as though it were a settled measurement of
a permanent underlying quantity.

## Entry, retirement and scale drift

Each ordinary equal-\(k\) bout is zero-sum, but a historical rating population
is open. An entrant brings an assigned initial rating into the active pool. A
retiring rikishi removes his final rating from it. If the ratings entering and
leaving the population do not balance, the location of the active rating scale
can move over time.

This movement may be called rating inflation when the scale rises and rating
deflation when it falls. It need not mean that rikishi have collectively become
stronger or weaker. It can be a consequence of the accounting produced by
entry, retirement and initialization.

Scale drift does not affect a bout prediction made from two contemporaneous
ratings if their difference remains appropriate. It does undermine a simple
comparison of absolute ratings taken from widely separated eras.

## Fixed-\(k\) fluctuation is not permanent convergence

It is tempting to imagine that repeated results cause Elo ratings to settle
permanently at their correct values. That is not the ordinary behaviour of a
model with a fixed nonzero \(k\). Every new win or loss produces another
nonzero update. Even in an ideal stationary world, ratings continue to
fluctuate around the underlying structure rather than becoming fixed forever.

This does not make the ratings useless. It means that a running fixed-\(k\)
rating should be understood as a responsive estimate, not as a calculation
that eventually completes. Claims about convergence must specify what kind of
convergence is meant and under what assumptions it holds.

In real sumo, where both the population and individual performance change,
some responsiveness is necessary. The same responsiveness guarantees that
individual ratings will continue to move.

## Construction is not validation

The expected-score formula defines what a rating difference means inside the
model. It makes Elo capable of producing forecasts, but it does not prove that
those forecasts describe sumo accurately.

Validation asks separate questions. Do higher probabilities discriminate
between winners and losers? Do bouts assigned a given probability occur at the
corresponding frequency? Does the model improve materially on a 50--50
forecast? Does it behave differently among sekitori and sub-sekitori? How does
it compare with an alternative model under the same chronological protocol?

Those questions require historical experiments. As with the 74% estimates in
the casual introduction and the worked example above, how well any particular
Elo model predicts actual results is a separate matter, to which the account
will return later.

## Why this leads to Equelo

Basic Elo provides a transparent, opponent-sensitive and difference-based way
to turn a sequence of results into running ratings. Its application to
historical sumo nevertheless exposes two immediate construction problems:

- an arbitrary common entrant rating can create initialization lag;
- entry and retirement can allow the historical rating scale to drift.

Equelo is based on Elo and is designed to address those problems through
chii-informed initialization and normalization. That motivation does not imply
that Equelo solves every difficulty described above, nor does it establish
Equelo's predictive validity. Its construction and its validation require
their own accounts.
