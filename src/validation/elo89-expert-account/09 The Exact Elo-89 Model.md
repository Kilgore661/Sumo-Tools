# 9. The Exact Elo-89 Model

> **Draft status:** First specification draft, checked against the retained
> producer, replay and production tests. It records two discrepancies in the
> surrounding documentation and artifact manifests rather than silently
> resolving them. Those are marked under “Contract issues exposed by this
> account”.

## What the name denotes

**Elo-89**, written (E_{89}), is the project's selected numerical rating
system for the sufficiently complete represented sumo record beginning in
January 1989.

The name denotes the complete contract in this chapter, not merely the Elo
probability equation. In particular it denotes:

- a January 1989 epoch and a chronological binary-result stream;
- one carried point rating for each active rikishi;
- the (q=400) logistic expectation rule;
- a rank-level K schedule;
- initialisation from the frozen P1 entrant-prior artifact;
- removal and reinitialisation across absence from the active population;
- common start- and end-of-basho shifts which preserve a fixed active-
  population mean; and
- defined pre-bout, post-bout, day-end and basho-boundary observations.

It has no individual uncertainty coordinate, time decay, injury variable,
style interaction or explicit model of torikumi selection.

## Contract at a glance

| Component | Elo-89 rule |
| --- | --- |
| Model identifier | `elo-89` / (E_{89}) |
| Epoch | The supplied history must begin at `1989/01` |
| End | The last basho in the particular production history; not fixed by the model name |
| Competitor identity | Stable `RikId`, not shikona |
| Rated result | Every represented result whose outcome pair is exactly W/L |
| Excluded result | Paired fusen outcomes FS/FP; every other non-W/L outcome |
| Expectation scale | (q=400) |
| K | 10 for Y/O/S/K; 15 for M; 25 for J; 35 below Juryo or when chii is absent |
| Entrant rating | Frozen paired P1 value for the current chii; the minimum P1 value when no chii exists |
| Active population | Banzuke members, plus participants in rated W/L results represented for that basho |
| Departure | Absence from the next active population discards the rating |
| Return | Treated as a new entrant and assigned P1 again |
| Target mean | Raw mean of the first non-empty active population after P1 initialisation |
| Population operation | One common shift to the target before the basho and another after its bouts |
| Bout chronology | Basho, then day, then canonical rikishi pair |
| Published internal observations | Basho start, pre- and post-bout, day end, and normalised basho end |

The rest of the chapter makes each line precise.

## Inputs and time domain

An Elo-89 production replay consumes:

1. a `History` whose first represented basho is January 1989;
2. an inclusive final basho determined by that history;
3. the paired P1 prior table; and
4. the fixed K configuration.

The producer rejects a history whose first sorted date is not `1989/01`. It
does not require one permanent final date: extending the site through a later
basho means running the same model over a longer history. A reproducible
release must therefore record its data cut-off as well as the model name.

Basho are processed in increasing date order. Within a basho, represented days
are processed in increasing day order. Within a day, eligible bouts are
ordered by the canonical pair of `RikId` values. In an ordinary torikumi,
same-day bouts are disjoint and their relative order has no effect. The
canonical ordering nevertheless makes the result deterministic if the data
ever contain multiple eligible appearances by one rikishi on one day.

There is no update merely because calendar time passes. Only the explicit
population operations and represented W/L results change ratings.

## The rated-result domain

For every represented result in the inclusive replay interval, Elo-89 examines
the pair of recorded outcomes.

- Exactly one W and one L produces a rated bout.
- An FS/FP pair is counted as an excluded fusen and produces no update.
- Every other outcome combination is excluded and currently reported under
  the implementation field `excluded_draw_count`. That field name is broader
  than the underlying category: it means “other non-binary result”, not
  necessarily a literal draw.

A known W/L result remains eligible when its kimarite or decision text is
blank. No result is inferred where the represented history has none.

The rated bout is put into canonical participant orientation. If the lower
`RikId` is designated A, its score is

\[
s_A=
\begin{cases}
1,&\text{if A won},\\
0,&\text{if A lost}.
\end{cases}
\tag{9.1}
\]

The orientation has no substantive effect; it provides deterministic bout
identity and output order.

## P1: the entrant-prior artifact

P1 answers a narrow question: what rating should Elo-89 assign before a
rikishi has an active carried rating? It is a table indexed by banzuke chii,
not a table of the current abilities of the rikishi occupying those chii.

The replay consumes a frozen **paired P1 table**. It does not estimate that
table again while calculating Elo-89. For a represented chii, annotations are
removed and east and west values belonging to the same rank pair are averaged
without support weights. Numbered positions above Maegashira are collapsed to
their level's first position by the retained rank-family policy. This produces
one value for labels such as Y, O, S, K, M1, J1 and so on.

If a rikishi has no chii, the replay uses the minimum value in the paired P1
table. If a non-null represented chii maps to no P1 entry, the replay fails;
it does not silently choose a neighbouring rank.

### How the frozen source table was produced

The side-specific source for P1 was constructed by a separate iterative
procedure over the post-1988 history:

1. every chii in the producer's represented domain starts at 1,517;
2. the history is replayed with (q=400), the retained K schedule and the
   legacy departure-redistribution population rule;
3. basho-start ratings are pooled by chii and averaged to obtain a revised
   chii map;
4. enough correction mass to restore an unweighted map mean of 1,517 is
   allocated among chii in proportion to their observation counts; and
5. the revised map becomes the entrant table for the next pass.

The retained run stopped after 18 passes when the maximum change between
successive maps was 9.5748 points, below its ten-point stopping tolerance. It
contained 975 side-specific chii values. The stopping rule establishes what
artifact was produced; it is not a theorem of unique or exact convergence.

The prior producer uses its own Oracle-prepared history and legacy replay
eligibility, including exclusion of records whose decision is `blank`. The
Elo-89 replay itself instead rates every represented W/L result. P1 is also
future-informed: later history contributed to the table used to initialise
earlier entrants. These are properties of the fitted artifact's provenance,
not hidden steps in the Elo-89 recurrence.

The separation is essential. Feeding Elo-89's whole-population operator back
into the literal-chii fixed-point procedure produced unstable extreme values
at low-support chii. Elo-89 therefore holds externally produced P1 fixed.

## Active population and lifecycle

Let (A_t) be the active population for basho (t). In the retained replay,

\[
A_t={\text{rikishi on the basho banzuke}\}
\cup
\{\text{participants in its rated W/L bouts}\}.
\tag{9.2}
\]

The union matters to the formal implementation even though the current
production ledger contains no rated bout participant with a missing chii.

Before basho (t), every rikishi in (A_{t-1}\setminus A_t) loses his carried
rating. A rikishi in (A_t) without a carried rating is initialised from P1
using his chii for basho (t). Thus one-basho absence from the active set is a
departure, and later reappearance is a new initialisation. The previous rating
is not archived for restoration.

A banzuke member remains active even if he has no rated bout in that basho.
His rating participates in both population shifts but receives no bout update.

The rule models membership in the represented rating population. It should
not be paraphrased as a factual claim that the rikishi retired from sumo or
lost all underlying ability.

## The fixed target mean

After the first non-empty active population has been formed and every member
has been initialised from P1, Elo-89 calculates

\[
\mu^*=\frac{1}{|A_1|}\sum_{i\in A_1}R_i.
\tag{9.3}
\]

This becomes the target mean for the entire run. It is not the 1,517 mean used
inside the upstream P1 producer and it is not a separately chosen round
number. It depends on the first active population and the frozen paired prior.
The current production artifact records approximately 1,569.6961, but the
definition is Equation 9.3 rather than that rounded observation.

At the first basho, the raw active mean already equals the newly defined
target, so the first start adjustment is zero.

## Start-of-basho population operation

Once departures have been removed and entrants initialised, calculate the raw
active mean

\[
\bar R_t^{\mathrm{raw,start}}
=\frac{1}{|A_t|}\sum_{i\in A_t}R_i.
\tag{9.4}
\]

Every active rating then receives the same adjustment

\[
c_t^{\mathrm{start}}
=\mu^*-\bar R_t^{\mathrm{raw,start}},
\qquad
R_i\leftarrow R_i+c_t^{\mathrm{start}}
\quad(i\in A_t).
\tag{9.5}
\]

This restores the mean after changes in membership. Because it is a common
shift, it preserves every rating difference and every Elo probability among
the current active rikishi at that instant. It changes their shared coordinate
relative to the fixed P1 values from which future entrants will be initialised.

The resulting state is the **basho-start rating** observation.

## Forecast and bout update

Immediately before each rated bout between A and B, their current ratings give

\[
p_A=\frac{1}{1+10^{(R_B-R_A)/400}},
\qquad p_B=1-p_A.
\tag{9.6}
\]

The residual is

\[
e_A=s_A-p_A.
\tag{9.7}
\]

Each rikishi has a K determined by his chii on the current basho's banzuke:

| Chii level | K |
| --- | ---: |
| Yokozuna, Ozeki, Sekiwake or Komusubi | 10 |
| Maegashira | 15 |
| Juryo | 25 |
| Makushita, Sandanme, Jonidan or Jonokuchi | 35 |
| No represented chii | 35 |

The simultaneous update is

\[
R_A' = R_A+K_Ae_A,
\qquad
R_B' = R_B-K_Be_A.
\tag{9.8}
\]

The next eligible bout sees these updated ratings. K is based on the fixed
basho chii, not on a rank recalculated after each result.

When (K_A\ne K_B), the bout creates net rating mass

\[
\Delta(R_A+R_B)=(K_A-K_B)e_A.
\tag{9.9}
\]

Elo-89 does not alter Equation 9.8 to make such a bout zero-sum. The
end-of-basho population operation absorbs the resulting mean movement across
the active population.

## Day-end and end-of-basho states

After all eligible bouts on a represented day have been updated, the replay
records a **day-end rating** for every active rikishi. There is no population
shift between days.

After the final represented day of the basho, calculate

\[
\bar R_t^{\mathrm{raw,end}}
=\frac{1}{|A_t|}\sum_{i\in A_t}R_i
\tag{9.10}
\]

and apply

\[
c_t^{\mathrm{end}}
=\mu^*-\bar R_t^{\mathrm{raw,end}},
\qquad
R_i\leftarrow R_i+c_t^{\mathrm{end}}
\quad(i\in A_t).
\tag{9.11}
\]

The resulting state is the **normalised basho-end rating**. It is the state
carried toward the next basho.

Consequently, the final day's day-end value and the basho-end value need not
be equal. The former is after the day's bout updates but before Equation 9.11;
the latter is after the common end shift. Neither is an error or an alternative
model, provided the observation stage is named.

## One complete basho transition

The recurrence can be summarised as follows:

```text
form active set from banzuke members and rated-bout participants
discard ratings belonging to the previous active set but not this one
initialise every active rikishi without a rating from frozen paired P1
on the first non-empty basho, set the target to the resulting raw mean
shift every active rating by one common amount to restore the target mean
record basho-start ratings

for each represented day, in order:
    for each eligible W/L bout, in canonical-pair order:
        record the pre-bout forecast
        update both ratings with their own current-basho K
        record the post-bout ratings
    record day-end ratings for the whole active population

shift every active rating by one common amount to restore the target mean
record normalised basho-end ratings
carry those ratings forward for rikishi who remain active
```

This algorithm, the paired P1 values, the K table and the represented history
are sufficient to reconstruct the rating states.

## Production observations and artifacts

One production run writes:

| Artifact | Meaning |
| --- | --- |
| `prior.csv` | The paired P1 values actually consumed by the run |
| `basho_start_ratings.json` | State after membership changes, P1 initialisation and the start shift |
| `day_end_ratings.json` | State after each represented day's eligible bout updates, before the basho-end shift |
| `basho_end_ratings.json` | State after the end shift |
| `bout_ledger.csv` | Pre-bout ratings, probability, result, K values, deltas and immediate post-bout ratings |
| `basho_adjustments.csv` | Active counts, raw means and common start/end shifts |
| `manifest.json` | Model identifier, date interval, parameter paths, target mean, result counts and file names |

Different website tools may consume different observations. A “rating at the
start of the basho”, a probability offered before a bout, a rating after day
15 and a normalised basho-end rating are not interchangeable. A public label
must identify which one it uses.

## Contract issues exposed by this account

Two points require engineering or documentation resolution.

### 1. Off-banzuke result wording

The existing named-model table says that off-banzuke results are excluded and
reported. The retained Elo-89 selector does not perform that exclusion. It
rates every represented W/L result and the replay explicitly adds rated-bout
participants to the active population even when they are absent from the
banzuke. In that case they receive the unranked P1 fallback and K=35.

The current production ledger through September 2026 contains no such rated
participant, so the two descriptions happen to produce the same published
ratings for that artifact. They are not the same prospective contract. Until
the policy is deliberately settled, this chapter reports the implementation
rule rather than repeating the older prose claim.

### 2. Artifact identity in the manifest

The output bundle copies the exact paired prior values it consumed, so the
replay input is preserved. Its manifest does not currently record a SHA-256
for that copied prior, the K configuration, the source history or the replay
code. It records paths and a free-text history description instead.

That is weaker than the three-layer reproducibility standard in Chapter 8. A
release can still be audited from its copied inputs and ledger, but the
manifest should eventually bind the model contract, fitted artifact, K file,
history snapshot and code version with stable identities. Adding those
identities would strengthen provenance without changing the Elo-89 equations.

## Scope boundary

This chapter says what Elo-89 calculates. It has not argued that January 1989,
P1, this K schedule or whole-population preservation is uniquely correct. Nor
has it claimed that a fixed population mean establishes stable rating meaning
at every chii or across every historical period.

Those are questions about evidence and modelling judgement. Chapter 10 turns
to them explicitly.

## Working sources

- `../../analysis/elo89/model.py`
- `../../analysis/elo89/replay.py`
- `../../analysis/elo89/producer.py`
- `../../analysis/elo89/output.py`
- `../../analysis/prediction/bouts.py`
- `../../analysis/equelo_bkp1/README.md`
- `../../analysis/equelo_bkp1/solve.py`
- `../../analysis/equelo_bkp1/simulate.py`
- `../../analysis/equelo_bkp1/recenter.py`
- `../../analysis/equelo_population_policy/predict_candidate.py`
- `../../analysis/docs/story/15 Tranche 1 - Population Normalisation Policy.md`
- `../../analysis/docs/story/21 Elo-89 Website Production Handoff.md`
- `../../products/make_site89/docs/Documentation Handoff.md`
