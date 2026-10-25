# 7. Problems Applying Elo to Chess and Sumo

> **Draft status:** First continuous-prose draft. The chapter distinguishes
> mathematical consequences, observed data conditions, empirical findings and
> unresolved modelling risks. It is not an audit of current FIDE regulations
> or a claim that every possible defect has been demonstrated in sumo.

## The equations are not a complete rating institution

Ordinary Elo provides a probability equation, an update equation and a
recursive state. Applying those ideas to an enduring human competition
requires more.

Chess and professional sumo both have competitors who enter, improve, become
inactive, return and leave. Their contest records form incomplete networks
rather than permanent full round robins. The evidence available at the start
of a calculation may not include the beginning of every career, and the
meaning of a rating may be expected to persist across many years.

An administered chess system supplies policies around the Elo core. A sumo
system must do the same. Those policies should not be mistaken for deductions
from the two ordinary equations.

The manifestations differ. Chess permits draws and is played across many
tournaments and rating pools. Sumo's represented outcomes are predominantly
binary, its schedule is strongly structured by banzuke and division, and its
careers proceed through a changing hierarchical population. The common lesson
is that “use Elo” does not identify one complete model.

## 1. Initialisation is unavoidable

Chapter 6 showed that a recurrence needs an initial state. There are two
distinct initialisation problems.

The **epoch problem** concerns competitors already present when the historical
calculation begins. They have careers and relative levels which predate the
chosen start, but the Elo state does not yet exist. Giving them all the same
rating means that the model initially has no information which distinguishes
them.

The **entrant problem** recurs whenever a new competitor appears after the
epoch. A rating must be assigned before his first represented contest can be
forecast or updated. The ordinary equations do not supply it.

A common initial value has an arbitrary *level* but a substantive *equality*.
Changing 1,500 to 2,000 everywhere is merely translation. Giving a Yokozuna
and a new Jonokuchi entrant equal states gives their hypothetical first contest
a 50–50 probability. That is a strong information policy even if it is
described as neutral.

An informed initial state can reduce that implausibility, but it imports a new
source of evidence and assumptions. Rank, division, results from another
system or expert judgement might be used. The model must then say when that
information was available, how it became numerical and whether it will later
be used to validate the same ratings.

### Initialisation lag

Once an initial state has been chosen, its influence is not removed at a fixed
date. It affects the first probabilities and updates, which affect the next
ones. A poorly initialised rating requires enough informative contests to move
to a useful region of the scale. This transition is **initialisation lag**.

The lag is not one universal number of bouts. It depends on K, the size and
direction of the initial error, the opponents encountered, their own states
and the realised results.

The project's Basic Elo experiments supply direct evidence that this matters
in sumo, while also warning against a simple diagnosis. Equal-initialisation
Elo showed a long early aggregate penalty after January 1989, located mainly
in the lower divisions. A future-informed exact-chii prior improved the
sub-sekitori result only slightly; a division-level prior performed materially
better in the retrospective experiment. Thus uniform initialisation explains
part, but not all, of the early behaviour. Those priors used later history and
were diagnostics, not prospectively validated solutions.

## 2. A zero-sum update does not close an open population

Equal-K bouts conserve the sum of the two ratings. Careers do not.

Suppose a population of \(N\) competitors has mean rating \(\mu\). Adding an
entrant with rating \(r\) changes the mean to

\[
\mu_{\mathrm{add}}
=\frac{N\mu+r}{N+1}
=\mu+\frac{r-\mu}{N+1}.
\tag{7.1}
\]

Removing a departing competitor rated \(r\) changes it to

\[
\mu_{\mathrm{remove}}
=\frac{N\mu-r}{N-1}
=\mu+\frac{\mu-r}{N-1}.
\tag{7.2}
\]

These are accounting identities. Entry below the current mean lowers the
mean; departure below it raises the mean, and the converse holds above the
mean. If the ratings brought in and taken out do not balance over time, the
location of the surviving scale moves even though every intervening equal-K
bout was zero-sum.

This movement is commonly described as rating inflation or deflation. The
name does not identify its cause and should not be allowed to imply that the
competitors themselves became stronger or weaker. It may arise from population
turnover and the chosen entry policy.

Contemporaneous probabilities depend on differences and may remain useful
while the common level moves. Historical comparisons of absolute ratings do
not enjoy that protection: a rikishi labelled 2,200 in one period and another
labelled 2,200 decades later need not occupy equivalent positions on a stable
scale.

The problem exists in principle wherever a rating population is open. It is
especially visible in sumo because entry, progression and retirement are
continuous parts of the system rather than exceptional events.

## 3. Competitors change, while the update rule does not explain how

Human competitive capacity is not fixed. Competitors learn, age, become
injured, recover and decline. Ordinary fixed-K Elo remains responsive, but
responsiveness is not a model of the causes or rate of change.

An unexpected result can arise because:

- the current rating was a poor estimate of a stable level;
- the competitor's level has changed;
- the opponent's level was misestimated;
- relevant matchup or contextual information was omitted; or
- an unsurprising random upset occurred.

The same residual drives the update in every case. Ordinary Elo does not
identify the explanation.

K controls the compromise. A small K protects the state from ordinary result
noise but responds slowly to genuine change. A large K follows change more
quickly but also chases more noise. There is no reason to expect one fixed K to
be optimal for every career stage, evidence level and rate of change merely
because it is simple.

Nor does fixed-K Elo converge to an unchanging individual rating in the
everyday sense. Even in a stationary toy world generated from the same
probability family, realised wins and losses continue to produce non-zero
updates. Ensemble averages may recover the latent structure while individual
rating paths continue to fluctuate. This is a mathematical and experimental
feature of the process, not evidence that the implementation has failed to
finish calculating.

## 4. Inactivity is not the same as evidence of decline

Calendar time without a rated contest leaves an ordinary Elo rating unchanged.
That policy has a defensible evidential reading: no new contest result has
arrived, so the result-based estimate is retained.

But two different claims can be hidden inside “the rating remains the same”:

1. the best point estimate remains where it was; and
2. the estimate remains equally well supported.

The first does not entail the second. During inactivity the competitor may
recover, deteriorate or remain unchanged, while our information becomes less
current. Bare Elo has no separate uncertainty state which can widen during the
gap.

This is particularly important in sumo, where absence is often associated
with injury but does not reveal its severity, recovery path or effect on later
performance. Automatically lowering a rating would add a claim about decline
which the absence alone does not quantify. Leaving it untouched avoids that
unsupported penalty but should not be described as certainty that ability has
remained fixed.

A return creates a related choice: retain the last state, adjust it, or assign
a new one. Each policy preserves and discards different evidence. The ordinary
equations do not choose among them.

## 5. A point rating does not report estimation uncertainty

Outcome probability and rating uncertainty are different quantities.

If two rikishi have equal point ratings, ordinary Elo assigns their matchup a
50–50 probability whether each rating is supported by hundreds of bouts or one
has just entered with an assigned value. The probability expresses uncertainty
about the bout conditional on the point states; it does not say how precisely
those states are estimated.

This can make superficially identical comparisons evidentially very different.
A mature rating, a new entrant's prior and a stale returner's state may print
the same number without deserving the same confidence.

The absence of an uncertainty coordinate is a known limitation of ordinary
point-rating Elo. It is not yet an empirically measured defect of Elo-89
relative to an uncertainty-aware sumo model: the project has not run a
controlled production comparator of that kind. The importance of the omission
is therefore well motivated, but the size of the available improvement is
TBD.

## 6. Missing history cannot be inferred by the recurrence

Elo can process only represented results. If a career began before the data or
if bouts are missing within it, the update process cannot reconstruct those
outcomes from nothing.

This differs from ordinary uncertainty about a recorded upset. Missing history
removes edges from the comparison network and can leave a competitor's state
too dependent on its initial value or on a small, unrepresentative subset of
opponents.

Historical sumo makes this issue concrete. Makuuchi and Juryo records are
complete much earlier than the lower-division record. The project's audit also
shows that pre-1989 lower-division evidence is not simply absent: many basho
are complete and others are partially represented, with coverage improving at
different dates in different divisions. The resulting boundary is irregular,
not one clean moment at which all evidence changes from missing to complete.

That finding supports retaining genuinely learned information across a data
gap rather than automatically resetting it. It does not establish how stale a
persisted rating becomes, quantify the predictive harm caused by missing
results or identify one uniquely correct persistence policy.

The 1989 starting point used by Elo-89 is therefore a model and evidence
boundary chosen to obtain a sufficiently complete represented record. It is
not a claim that careers or competitive history began in January 1989.

## 7. Comparisons require a connected result network

Represent competitors as nodes and rated bouts as edges. Within a completely
disconnected component, every probability depends only on internal rating
differences. Adding a constant to all ratings in that component changes none
of its forecasts.

If two components have no cross-component bouts, their relative offset is
unidentified. Each can have internally meaningful differences without sharing
one empirically determined scale. This is a theorem, not merely a concern
about small samples.

Sparse bridge bouts can connect the components, but then the relative offset
may depend heavily on limited evidence. The existence of a path is not the
same as strong support for every comparison made through it.

The project's toy experiments demonstrate the distinction under controlled
conditions:

- disconnected synthetic divisions recover internal spacing but not their
  relative offset;
- artificial cross-division bridges can identify that offset in the tested
  worlds; and
- a bridge shaped by observed Makuuchi–Juryo scheduling was sufficient in the
  tested 42-plus-28-player toy setup.

Those results establish possibility under declared toy assumptions. They do
not prove that every historical division, period or individual rikishi is
connected strongly enough for every proposed comparison.

## 8. Unequal schedules remain selective evidence

Elo was attractive in Section 4 precisely because rikishi face unequal
opposition. Opponent sensitivity helps, but it does not turn a selective
schedule into a full round robin.

The model estimates states from the bouts which occurred. It does not observe
the outcomes of matchups which were never scheduled. In sumo, bouts are
predominantly local in rank and division, and the selection can change within
a basho. The exact torikumi formation policy has not been reconstructed by
this project.

Two limitations follow.

First, forecasts are best supported for matchup populations resembling the
observed network. Extending them to rarely connected ranks, divisions or eras
requires additional confidence in the scalar model.

Second, schedule and state may be related. Promotion changes opposition;
current results can affect later opponents; rank reflects earlier results. Elo
conditions on the scheduled pair but does not model this selection process.
Opponent adjustment is therefore not the same as eliminating every form of
schedule effect.

The empirical Basic Elo work reinforces the need for subgroup analysis. Its
aggregate predictive advantage over 50–50 was modest and varied materially
between sekitori and sub-sekitori populations and through historical time. A
single whole-population score concealed those differences.

## 9. A scalar cannot express persistent matchup cycles

Ordinary Elo imposes a transitive order of favourites. If real competition
contains persistent style relationships of the form A tends to beat B, B tends
to beat C, and C tends to beat A, one scalar cannot represent all three
pairwise tendencies simultaneously.

This is a structural limitation of the model. It is not currently an
established empirical finding about the size of style effects in sumo. The
project has not performed a systematic residual or interaction study capable
of showing whether a richer matchup model would improve out-of-sample
predictions.

The correct present claim is therefore conditional:

> If stable non-transitive or pairing-specific effects are material in sumo,
> ordinary one-dimensional Elo must compromise among them.

Names such as “oshi-zumo specialist” or a memorable head-to-head record are
not enough to quantify the effect. A serious test would need sufficient repeat
evidence, protection against retrospective selection and comparison on later
contests.

## 10. Cross-era equality is an additional claim

Printing ratings from different dates in one column does not itself establish
historical comparability.

Within one contemporaneous connected population, differences have the model
interpretation defined in Chapter 5. Across distant periods, the competitor
sets, schedule, evidence coverage, entry and departure flows and possibly the
relationship between rating difference and outcome may all have changed.

A population anchor can control one feature such as the overall mean. It
cannot by itself prove that the same printed rating denotes the same
competitive relationship at every chii, in every division or against a common
external population. Cross-era comparison therefore needs a declared anchor
and evidence appropriate to the claim being made.

This does not make historical ratings unusable. It makes their interpretation
conditional on the population model rather than a free consequence of using
the same formula throughout.

## What has been established, and what remains open

The problems above do not all have the same status.

| Issue | Present status |
| --- | --- |
| An initial state is required | Mathematical consequence |
| Equal initialisation creates equal initial probabilities | Mathematical consequence |
| Entry and departure can move the population mean | Mathematical consequence |
| Disconnected components have unidentified relative offsets | Mathematical consequence |
| Fixed-K individual ratings continue to fluctuate | Mathematical consequence supported by toy experiments |
| Sumo has irregular historical coverage and ranked-population gaps | Audited data finding |
| Basic Elo behaviour differs by sumo population and period | Empirical finding for the tested model |
| The observed Makuuchi–Juryo bridge can connect a toy scale | Conditional experimental finding |
| Individual uncertainty would materially improve the production model | Plausible, not yet tested comparatively |
| Stable style cycles materially damage scalar Elo in sumo | Open empirical question |
| One anchoring policy establishes unconditional cross-era equivalence | Not established |

Ordinary Elo nevertheless has demonstrated information about sumo results. A
specified post-1988 Basic Elo model performed better than a neutral 50–50
forecast over the represented history, including in a fair-coin simulation
comparison. That existential result matters: the difficulties in this chapter
do not make the model vacuous.

They do show why the ordinary equations are only a starting point. Applying
the Elo idea requires choices about initialisation, responsiveness,
uncertainty, population membership, scale, missing evidence and publication.
Different choices create different Elo-like systems.

That is the subject of the next chapter.

## Working sources

- `../../analysis/docs/story/06 Draft Standard Elo Account for the STEM Reader.md`
- `../../analysis/docs/story/17 Pre-1989 Bout-Data Completeness and Rating Persistence.md`
- `../../analysis/docs/story/22 Elo-89 Rating System Appraisal.md`
- `../../analysis/prediction/docs/A Defence of Elo for Sumo (Sketch).md`
- `../../analysis/prediction/docs/experiments/Findings.md`
- `../../analysis/toy_elo/README.md`
- `../../analysis/docs/2026 08 14 Elo Documentation Rummage.md`
