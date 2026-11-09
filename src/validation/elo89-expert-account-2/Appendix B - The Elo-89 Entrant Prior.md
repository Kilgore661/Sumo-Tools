# Preliminary Appendix B: The Elo-89 Entrant Prior

## Status

This is a preliminary technical appendix to the expert account. It records the
present construction and interpretation of the frozen Elo-89 entrant prior,
P89, denoted mathematically by \(P_{89}\). It is deliberately more detailed
than the main account, but it is not a claim that the construction is uniquely
correct or finally validated.

The persisted 484-row table used by Elo-89 is:

```text
src/analysis/equelo_prior_aggregation/results/priors.csv
```

Its SHA-256 is
`31ba2ea5430fb6a117b80290e78570cbbb160875febb6af14664a6c64ec93cdf`.
Ordinary Elo-89 replays load this table; they do not refit or reaggregate it.

## The first-rating problem

An Elo rating is a summary of results accumulated against rated opponents. At
the January 1989 epoch, however, Elo-89 has not yet processed any result. A
rikishi such as Chiyonofuji does not truly appear without a history: his Y1e
position reflects a long career before 1989. But that career cannot simply be
replayed backwards without eventually reaching periods in which the daily
bout record needed by the model is incomplete.

Earlier work began in January 1958, the first year from which six basho were
held annually. That supplied a longer run-in, but it did not supply a
convincing reason to regard the ratings reached in January 1989 as correct
relative to the results observed from 1989 onward. Moving the epoch backwards
relocates the initialisation problem; it does not remove it.

P89 therefore answers a limited question:

> What rating should Elo-89 assign before a rikishi has a stored rating, when
> the relevant information made available to the initialisation rule is his
> represented chii?

P89 is not a second banzuke, a claim that everyone at a chii has equal ability,
or a table of the present abilities of the rikishi occupying those positions.
It is a historically fitted initialisation rule. Once a rikishi is rated, his
results rather than his subsequent rank determine the evolution of his Elo-89
rating.

There is no observable true rating against which an initialisation error can
be measured. Rank is an outcome of a promotion system rather than a direct
measurement of ability; observations are unevenly distributed; some literal
positions are rare; and division boundaries can introduce real or apparent
discontinuities. Any initialisation rule therefore adds modelling judgement.

## Equal and random initialisation

Assigning every rikishi the same first rating is transparent. It can also be
described as an intellectually cautious representation of ignorance. But it
does not follow that equal numbers are the only honest representation of
ignorance. At the epoch it gives an established Yokozuna and a low-ranked
rikishi the same model state, despite the information already expressed by the
banzuke. It creates what we called the **initialisation gap**: the period in
which subsequent results must move a deliberately uninformative starting
rating toward a more useful part of the scale.

Random starting values were another conceivable response. Repeating the
history from many random initial states could produce a distribution of later
ratings or identify starts with favourable predictive scores. That proposal,
however, immediately requires a distribution, scale, correlation structure
and selection rule. It also does not define the unobservable initialisation
gap. Selecting freely among hundreds of starting values on the same history
used to assess them would introduce a substantial overfitting risk.

Neither objection makes random or modern optimisation methods illegitimate.
It means only that they are alternative modelling programmes, not neutral
solutions. They have not yet been carried out for Elo-89.

## Why P89 was adopted

The case for P89 should be separated into two questions. The first concerns
the configured model as a whole: does \(\operatorname{Elo}_{89}(P)\), using
some declared entrant prior \(P\), predict eligible bouts better than a
neutral 50--50 forecast? The second concerns the entrant prior specifically:
holding the rest of Elo-89 fixed, what changes when one \(P\) is substituted
for another? The 50--50 comparison principally tests whether the configured
rating system contains predictive information. Comparisons with flat or
alternative entrant priors test the contribution and selection of \(P\).

These are not independent hurdles which every candidate prior must pass
separately. If, on the same bouts and scoring rule, an informed-prior
configuration performs better than flat initialisation, and the
flat-initialisation configuration performs better than 50--50, the ordering
already implies that the informed configuration also performs better than
50--50. The comparisons nevertheless answer different interpretive questions
and should be reported separately.

The starting reason for using an informed prior is that flat initialisation
discards information already expressed by the banzuke. At the January 1989
epoch, assigning an established Yokozuna and a low-ranked rikishi the same
rating is transparent, but it is not informationally neutral: it deliberately
gives the model states which are implausibly alike. Retained controlled
comparisons found that rank-informed first ratings improved retrospective log
and Brier loss relative to flat initialisation, particularly while ratings
contained little accumulated bout evidence. The final account should attach
the audited configurations, evaluation populations and scores to that claim.

That evidence supports informed initialisation in general; it does not
uniquely identify P89. The choice of the particular P89 table rests on three
further considerations.

First, P89 has a reproducible fitted construction. Its literal source uses
every represented binary W/L bout from January 1989 through September 2026,
including otherwise eligible bouts with missing kimarite. Literal cells are
combined into the paired consumer table by direct support weighting, so
represented banzuke appearances rather than arbitrary cell labels determine
their influence. This makes the construction explicit and auditable, although
it does not prove that support weighting is uniquely optimal.

Second, early stopping was selected using predictive evidence. Along the
retained fitting trajectory, performance improved rapidly from the flat
starting map, reached its best observed region around iterations 20--21, and
then deteriorated as numerical convergence continued. After applying the
production support-weighting rule consistently, iteration 20, selected by
epsilon 8.5, had the lowest mean log loss of the nearby candidates; iteration
21, selected by epsilon 8, had the lowest mean Brier loss. Because log loss is
the declared primary measure, iteration 20 was promoted. The differences were
small, and the same history was used for fitting and evaluation, so this is
retrospective model selection rather than prospective validation.

Third, the selected table passed operational and plausibility checks. It was
reproduced byte-for-byte from the retained iteration-20 result, passed strict
schema and hash validation, completed an Elo-89 replay, generated the
dependent site-data bundle and supported a complete website build. Its broad
numerical scale and rank curve remain intelligible, while known local
reversals and sparse lower-tail irregularities have been retained and
disclosed rather than silently smoothed. These checks establish
reproducibility, compatibility and face plausibility; they are not independent
proof of predictive superiority or true ability.

Replay consistency also supplies a limited acceptance check. Reapplying the
declared replay-and-aggregation procedure does not radically contradict the
selected source. A candidate which failed that test would be difficult to
defend. Passing it, however, establishes only approximate consistency with a
project-defined procedure. It does not show that
\(P_{89}=F(P_{89})\) is true exactly, that the operator \(F\) is uniquely
appropriate, or that its fixed point would be substantively correct.

P89 was therefore adopted as a reproducible, historically informed and
schedule-conditioned answer to Elo-89's first-rating problem. The evidence
supports informed initialisation and selects iteration 20 within the tested
fitting trajectory. It does not establish that P89 is the natural ability
associated with each chii, that all rikishi at one chii have equal ability, or
that the table minimises an unobservable gap between first rating and true
strength. The strongest defensible claim is narrower: P89 is the current
explicit entrant prior under which Elo-89 performs usefully, with known
retrospective, scheduling and support limitations.

## Mean preservation is a separate policy

Elo-89 was designed for an open population. With equal K, a played bout
transfers rating points between its two participants, but entry and departure
can change the coordinate occupied by the active population. A departing
rikishi takes his rating out of the active pool; an entrant brings an assigned
rating into it. Preserving the mean rating per active rikishi is Elo-89's
intuitive attempt to prevent those membership changes from producing rating
inflation or deflation and to keep the mapping from performance to displayed
points broadly stable through time.

This is an anchoring policy, not an empirically demonstrated cure. There is no
simple independently observable definition of rating inflation against which
the policy can be tested. Preserving the mean also does not conserve the
literal total of rating points when population size changes: the target total
is population size multiplied by the maintained mean.

Most importantly for this appendix, Elo-89 would use this population policy
whether its first-rating table came from iteration, random search, direct
optimisation or some other method. Mean preservation is not justified by the
mapping search, and the mapping search is not justified by mean preservation.

The literal-prior iteration also recentres each candidate chii map to a
declared base. That is a narrower identification step: rating differences do
not determine an absolute origin, so successive candidate maps must be placed
on a common coordinate. It should not be confused with the independent
production policy for maintaining the active-population mean.

## Evidence used

The retained literal-chii fit uses the represented History from January 1989
through September 2026, inclusive: 225 basho in the accepted run. A bout is
eligible when its paired outcomes are a binary win and loss. Kimarite is not
an input to an Elo update, so an otherwise valid W/L bout remains eligible
when kimarite is absent.

The accepted run contained 584,671 represented results. It rated 581,634 of
them, including 33,521 whose kimarite field was blank. It excluded 3,034
fusen results and three other non-binary results.

The construction is retrospective and future-informed. Later careers help to
determine values assigned to earlier entrants. It must therefore be understood
as a fitted regulariser for the historical Elo-89 account, not as a
rolling-origin estimate or unseen-data validation.

## Stage one: exploring literal-chii mappings

The first stage generates a sequence of candidate ratings for every literal
chii represented in the bounded History. At this stage east and west,
numbered sanyaku positions and annotations remain distinct.

Let \(C\) be the set of literal chii and let \(N_c\) be the number of
banzuke appearances at literal chii \(c\). The procedure begins from a flat
map:

\[
P^{(0)}(c)=1517 \qquad (c\in C).
\]

For iteration \(m\), the complete bounded History is replayed chronologically
using \(P^{(m)}\) to initialise unrated rikishi. The replay uses the ordinary
base-10 Elo expectation with \(q=400\), the declared divisional K schedule and
the fitting procedure's declared departure handling. This fitting lifecycle
is part of the prior construction; it is not silently substituted for the
lifecycle of the production Elo-89 replay.

For every occurrence of a rikishi at literal chii \(c\), record his rating at
the start of that basho. The raw next value is the mean of those basho-start
ratings:

\[
A^{(m)}(c)=
\frac{1}{N_c}
\sum_{(t,i):\,c_{t,i}=c} R^{(m)}_{t,i}.
\]

An Elo scale has an arbitrary location. After each replay, the construction
restores the unweighted mean of the literal map to 1517. If

\[
\Delta^{(m)}=1517|C|-\sum_{c\in C}A^{(m)}(c),
\]

the correction is allocated in proportion to literal-chii support:

\[
P^{(m+1)}(c)=A^{(m)}(c)+
\Delta^{(m)}\frac{N_c}{\sum_{d\in C}N_d}.
\]

The replay and aggregation together define an operator (F), so that
(P^{(m+1)}=F(P^{(m)})). The same algorithm could be continued to investigate
whether (F) has a numerical fixed point satisfying (P=F(P)). That is not
the reason for treating its limiting map as correct. The equation would
establish only self-consistency under an operator chosen by the project; it
would not establish true ability, optimal prediction, uniqueness or even that
the limiting map is a desirable entrant prior.

In practice, the iteration supplies a reproducible path through the large
space of chii-to-rating mappings. It begins with constant initialisation and
then produces increasingly differentiated candidates. The retained literal
source is an early map on that path, not a claim to have recovered a uniquely
correct fixed point.

## Stopping the iteration

The original production threshold of 10 rating points was a pragmatic
development choice: it made the procedure terminate in a reasonable time.
That literal source stopped after 18 iterations, when the largest change was
about 9.728 points. The current source uses epsilon 8.5 and stopped at
iteration 20, when the largest change was about 8.094 points. Neither number
is a statement that each cell is known to that precision.

A later epsilon sweep followed the same trajectory much further. It reached
epsilon 0.1 at iteration 1,171. Predictive performance improved rapidly from
the constant end of the trajectory to the region around iterations 18--21,
then deteriorated as the iteration continued. Among the tested candidates,
iteration 20, corresponding to epsilon 8.5, had the lowest log loss;
iteration 21, corresponding to epsilon 8, had the lowest Brier loss. Their
advantages over epsilon 10 were very small. By iteration 82 the scores were
already materially worse, and continued iteration increasingly produced
extreme values in sparsely supported cells.

This evidence argues against exact fixed-point consistency as the selection
principle. Greater numerical self-consistency did not produce a better prior
for probabilistic forecasting. Epsilon is therefore functioning as a
regularisation parameter, not merely as a numerical tolerance.

The initial sweep converted literal cells by unweighted pairing, whereas P89
uses support weighting. Before promotion, the epsilon-10, epsilon-8.5 and
epsilon-8 candidates were therefore replayed again after applying the final
support-weighting rule. Their mean log losses were respectively 0.677094,
0.677089 and 0.677090; their mean Brier losses were 0.241965, 0.241955 and
0.241953. Iteration 20 retained the best log loss, while iteration 21 retained
the adjacent Brier minimum. Because log loss is the declared primary measure,
iteration 20 was promoted on 8 November 2026.

The selected literal table was reproduced independently as immutable
`2026-09/run-002`; it was byte-for-byte identical to the retained sweep table
and has SHA-256
`8e798ca6ee1d5aa5fe42d5787d9d9887c200b4bb15546f0bb79669858420610f`.
The score differences remain very small and use the fitting history, so the
promotion is retrospective model selection rather than prospective
validation.

## What “looked about right” meant

The retained early map was not selected by a pre-registered optimisation
criterion. It was accepted because, on inspection, its broad structure looked
plausible for the intended role. In retrospect, that informal judgement seems
to have included:

- broad ordering by rank and division;
- plausible separation among the commonly represented upper ranks;
- no immediately obvious extreme values in the well-supported part of the
  map;
- tolerable local discontinuities rather than enforced smoothness; and
- a numerical scale compatible with the rest of Elo-89.

This was a face-validity screen, not evidence that the map was true or
optimal. The later discovery of a paired Komusubi value below M1 demonstrates
its limitations: a table can look broadly plausible while containing a local
relationship produced by an indefensible aggregation rule. The phrase
“looked about right” should therefore be retained as an honest description of
the modelling judgement, not rewritten after the event as a formal test.

## Stage two: constructing the consumer table

The literal fit is more detailed than the table consumed by Elo-89. The
consumer table removes annotations and pools east and west. For Y, O, S and K,
every numbered position present is also mapped to the single family key. Thus
the rule is generic: it applies in exactly the same way whether a family has
one represented slot or seventeen. For other ranks, the rank number is
retained while side and annotation are removed.

Suppose the literal cells mapped to consumer key \(g\) have fitted ratings
\(r_i\) and support \(n_i\). P89 uses direct support weighting:

\[
P_{89}(g)=
\frac{\sum_{i\in g} n_i r_i}
     {\sum_{i\in g} n_i}.
\]

Here support means the number of represented banzuke appearances contributing
to the literal cell. The formula therefore gives each represented appearance,
rather than each arbitrary cell label, equal influence within its consumer
pool.

Three aggregation policies were examined:

1. give every mapped literal cell equal weight;
2. weight every mapped cell by its support; and
3. for Y, O, S and K, retain only the canonical first slot.

The second was selected. Equal-cell averaging lets a rare cell exert the same
influence as a heavily represented cell. Retaining only the first slot avoids
that problem by discarding supported observations. Direct support weighting
uses all represented cells and states exactly how their unequal evidence is
combined.

## The Komusubi diagnostic

The practical anomaly that exposed the aggregation question was a Komusubi
value below M1. In the retained literal source, K2 supplied only 35 of 485
Komusubi appearances. Equal-cell averaging nevertheless gave K2 the same vote
as K1. That was not a defensible consequence of the evidence; it was a
consequence of treating cell labels rather than their support as the units of
aggregation.

Support weighting was applied to the whole table, including east/west and all
represented Y, O, S and K slots. It was not a one-off adjustment to Komusubi.
The resulting values include:

| Chii | P89 rating |
| --- | ---: |
| Y1 | 2526.63 |
| O1 | 2402.10 |
| S1 | 2360.96 |
| K1 | 2324.54 |
| M1 | 2303.09 |
| J1 | 2143.43 |
| Ms1 | 2017.45 |
| Sd1 | 1701.36 |
| Jd1 | 1479.00 |

The upper-rank sequence is now narratively coherent, but monotonicity was not
imposed as a constraint. Local reversals and division-boundary discontinuities
remain visible where the fitted construction produces them.

## Open matters before this appendix is final

### Why epsilon 8.5 replaced epsilon 10

Iteration 20 was selected because log loss is the declared primary measure
and it remained the lowest-loss candidate after the production
support-weighting rule was applied consistently. Iteration 21's slightly lower
Brier loss is corroborating evidence that the useful region is narrow, not a
reason to imply that both scores have the same exact optimum. The rebuilt map
changed the 484 paired values by a mean absolute 1.47 points relative to the
epsilon-10 release; the largest absolute change was 14.91 points in a sparse
lower-tail cell. Inspection found no new upper-rank or boundary pathology.

The promotion was explicit: it created a new immutable literal run, a new
paired-table hash, updated configuration and pinned tests, and passed strict
loading, full Elo-89 replay, site-data production and a build-only website
assembly. It did not move the fitting boundary or impose smoothing.

### How else should mapping space be explored?

The retained iteration is only one structured path through mapping space.
Modern alternatives include regularised direct optimisation, partial pooling,
hierarchical and Bayesian models, uncertainty-aware estimates, and random or
quasi-random search. A serious comparison would need to state the objective
function and regularisation in advance and use held-out or rolling-origin
evidence. Optimising hundreds of values and evaluating them on the same
history would reward overfitting rather than discover a better prior.

This is not a peripheral implementation possibility. It is the principal
unexplored alternative to the way P89's literal source was constructed. It is
recorded as a separate
[Entrant Prior Mapping Optimisation](Matters%20Arising/Entrant%20Prior%20Mapping%20Optimisation/README.md)
matter arising.

### Can the plausibility judgement be audited?

The historical judgement that the selected map looked about right should be
documented more precisely without pretending that its criteria were fixed in
advance. A retrospective audit could report ordering, discontinuities,
support, extreme values, stability across nearby iterations and sensitivity
to aggregation. Such an audit would make the judgement inspectable; it would
not convert it into independent validation.

## What has and has not been established

The retained P89 artifact has passed strict schema and hash checks, a complete
Elo-89 replay and the dependent site build. Those checks establish that the
table is reproducible, loadable and compatible with the production pipeline.
They do not establish that support count is the uniquely correct weight, that
P89 is timeless, or that every local value is substantively meaningful.

Earlier work established that informed initialisation is useful relative to a
flat starting value, especially for new and immature ratings. The
complete-W/L fitted source underlying P89 also passed the retained predictive
evaluation before aggregation. P89 is the support-weighted aggregation of
that tested source.

The support-weighted aggregation itself was audited against alternative
pooling rules and accepted because it represents the underlying observations
more defensibly. A separate predictive comparison did not isolate the
incremental effect of replacing the fitted source's legacy aggregation with
support weighting. The later epsilon comparison held support weighting fixed;
it establishes the ordering of the nearby stopping points under the production
aggregation, but it still does not establish that support weighting improves
prediction.

The fixed-point equation is not part of what has been established. The
iteration appears empirically capable of reaching much smaller update sizes,
but closer numerical self-consistency worsened the tested predictions. The
retained justification is therefore for an early candidate on this particular
trajectory, not for the operator's limit.

Reasonable successors could include regularised optimisation, partial
pooling, explicit uncertainty, rolling-origin fitting, monotonic constraints,
or a richer entrant model using information beyond chii. Each would answer a
somewhat different question and would need its own declared evidence domain
and evaluation. P89 is the present Elo-89 answer: explicit, reproducible and
frozen, but not beyond criticism.

## Reproduction and audit trail

The literal-prior producer is documented in:

```text
src/analysis/elo89/prior/README.md
```

The accepted literal source is:

```text
files/output/analysis/elo89/prior/2026-09/run-002/prior.csv
```

The aggregation experiment and exact promotion decision are documented in:

```text
src/analysis/equelo_prior_aggregation/README.md
src/validation/elo89-expert-account/Matters Arising/Prior Aggregation/README.md
```

The source-controlled result under `results/priors.csv` changes only through
an explicit promotion decision. Routine Elo-89 and website builds consume the
persisted file and preserve its identity in their manifests; they do not
silently refit it.
