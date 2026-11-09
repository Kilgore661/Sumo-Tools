# 9. The Exact Elo-89 Model

## What the name denotes

**Elo-89**, written \(E_{89}\), is the selected numerical rating system for
rikishi on the banzuke from January 1989 onward.

The name denotes the complete contract in this chapter, not merely the Elo
probability equation. In particular it denotes:

- a January 1989 epoch and an eligible W/L result stream;
- one stored point rating for each previously rated rikishi;
- the \(q=400\) logistic expectation rule;
- a rank-level \(K\) schedule;
- first-rating initialisation from the fixed P89 table;
- no rating change while a rikishi is outside the active population;
- common start- and end-of-basho shifts which preserve a fixed active-
  population mean; and
- defined pre-bout, post-bout, day-end and basho-boundary observations.

It has no individual uncertainty coordinate, time decay, injury variable,
style interaction or explicit model of torikumi selection.

## Contract at a glance

| Component | Elo-89 rule |
| --- | --- |
| Model | Elo-89 / \(E_{89}\) |
| Epoch | January 1989 |
| End | The last basho in the particular calculation; not fixed by the model name |
| Rated result | Every recorded W/L result between rikishi on the basho banzuke |
| Excluded result | Paired fusen outcomes FS/FP; every other non-W/L outcome |
| Expectation scale | \(q=400\) |
| \(K\) | 10 for Yokozuna/Ozeki/Sekiwake/Komusubi; 15 for Maegashira; 25 for Juryo; 35 below Juryo |
| First rating | Fixed paired P89 value for the current chii |
| Active population | Banzuke members |
| Inactivity | A stored rating receives no bout update or population shift while its rikishi is outside the active population |
| Target mean | Raw mean of the first non-empty active population after P89 initialisation |
| Population operation | One common shift to the target before the basho and another after its bouts |
| Defined observations | Basho start, pre- and post-bout, day end, and normalised basho end |

The rest of the chapter makes each line precise.

## Inputs and time domain

An Elo-89 calculation requires:

1. banzuke and bout records beginning in January 1989;
2. an inclusive final basho determined by those records;
3. the paired P89 first-rating table; and
4. the fixed \(K\) schedule.

The model does not require one permanent final date: extending the record
through a later basho means applying the same model to a longer history. A
reproducible release must therefore record its data cut-off as well as the
model name.

Basho are processed in increasing date order. Within a basho, days are
processed in increasing order. In an ordinary torikumi, same-day bouts are
disjoint, so their relative processing order has no effect.

There is no update merely because calendar time passes. Only the explicit
population operations and eligible W/L results change ratings.

## The rated-result domain

For every recorded result between rikishi on the basho banzuke, Elo-89 examines
the pair of outcomes.

- Exactly one W and one L produces a rated bout.
- An FS/FP pair is counted as an excluded fusen and produces no update.
- Every other outcome combination is excluded as a non-binary result.

For either participant designated A, the score is

\[
s_A=
\begin{cases}
1,&\text{if A won},\\
0,&\text{if A lost}.
\end{cases}
\tag{9.1}
\]

## P89: the first-rating table

P89 answers a narrow question: what rating should Elo-89 assign before a
rikishi has ever had an Elo-89 rating? It is a table indexed by banzuke chii,
not a table of the current abilities of the rikishi occupying those chii. See
the [P89 production account](../../analysis/elo89/prior/README.md) and
[Appendix B](Appendix%20B%20-%20The%20Elo-89%20Entrant%20Prior.md) for the
exact values used. A rikishi who already has a stored rating is not assigned
another first rating.

Elo-89 uses a fixed **paired P89 table**. It does not estimate that table
again while calculating ratings. Literal cells are combined by direct support
weighting. East and west retain their observed support; every numbered Y, O,
S and K position present contributes to its rank-family value. Other ranks
retain their number while side and annotation are removed. This produces one
value for labels such as Y1, O1, S1, K1, M1, J1 and so on.

Every chii to which the model is applied must have a P89 value; a
neighbouring rank is not substituted for a missing value.

### How the table was obtained

P89 was estimated retrospectively from eligible results beginning in January
1989 by relating ratings to banzuke chii. Its purpose is to give a first rating
that is closer to the level indicated by the banzuke, thereby reducing
initialisation lag.

The evidence boundary was fixed on **30 October 2026** using history through
the September 2026 basho. The final support-weighted aggregation was accepted
on 6 November, and the selected epsilon-8.5 source was promoted on 8 November;
those later provenance dates did not move the evidence boundary. Later
results do not alter the table, and a rikishi receiving his first rating after
the freeze date receives a value from this same table. Within the fitted
period P89 is future-informed: later career results contributed to values used
for earlier first ratings. Agreement between those ratings and chii during
that period is therefore not independent validation. From November 2026
onward, P89 acts as a fixed prior because subsequent results did not
contribute to its construction. A different fitting boundary would define a
different first-rating table.

The detailed fitting procedure and the fixed values are available in the
repository. They are inputs to Elo-89 rather than additional steps in its
recurrence.

## Active population and stored ratings

Let \(A_t\) be the active population for basho \(t\):

\[
A_t=\{\text{rikishi on the basho banzuke}\}.
\tag{9.2}
\]

At each basho, every member of \(A_t\) who already has a stored rating
continues from that rating. A member without a stored rating receives the
P89 value for his chii in basho \(t\). A stored rating belonging to a rikishi
outside \(A_t\) receives neither bout updates nor common population shifts.

A banzuke member remains active even if he has no rated bout in that basho.
His rating participates in both population shifts but receives no bout update.

The rule models absence of new contest information: without an eligible
result, there is no bout update. It does not claim that underlying
ability was literally constant, and Elo-89 does not model any growth in
uncertainty during inactivity.

## The fixed target mean

After the first non-empty active population has been formed and every member
has been initialised from P89, Elo-89 calculates

\[
\mu^*=\frac{1}{|A_1|}\sum_{i\in A_1}R_i.
\tag{9.3}
\]

This becomes the target mean for the entire calculation. It is not a
separately chosen round number. It depends on the first active population and
the fixed paired first-rating table, so its numerical value is a consequence
of the stated inputs.

At the first basho, the raw active mean already equals the newly defined
target, so the first start adjustment is zero.

## Start-of-basho population operation

Once \(A_t\) has been formed and members without stored ratings have been
initialised, calculate the raw active mean

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
relative to the fixed P89 values from which later first ratings will be
assigned.

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

Each rikishi has a \(K\) determined by his chii on the current basho's
banzuke:

| Chii level | \(K\) |
| --- | ---: |
| Yokozuna, Ozeki, Sekiwake or Komusubi | 10 |
| Maegashira | 15 |
| Juryo | 25 |
| Makushita, Sandanme, Jonidan or Jonokuchi | 35 |

The simultaneous update is

\[
R_A' = R_A+K_Ae_A,
\qquad
R_B' = R_B-K_Be_A.
\tag{9.8}
\]

The next eligible bout sees these updated ratings. \(K\) is based on the fixed
basho chii, not on a rank recalculated after each result.

When \(K_A\ne K_B\), the bout creates net rating mass

\[
\Delta(R_A+R_B)=(K_A-K_B)e_A.
\tag{9.9}
\]

Elo-89 does not alter Equation 9.8 to make such a bout zero-sum. The
end-of-basho population operation absorbs the resulting mean movement across
the active population.

## Day-end and end-of-basho states

After all eligible bouts on a day have been updated, the
calculation records a **day-end rating** for every active rikishi. There is no
population shift between days.

After the final day of the basho, calculate

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

1. Form the active population from the basho banzuke.
2. Continue each member from his stored rating, assigning P89 only where no
   stored rating exists.
3. At the first basho, set the target mean from this initial active
   population.
4. Apply the common start shift and record basho-start ratings.
5. Process days in order. For every eligible bout, record the
   forecast, update both ratings using their current-basho \(K\), and record
   the resulting ratings. Record the whole active population at day end.
6. Apply the common end shift and record normalised basho-end ratings.
7. Retain every stored rating for use in later basho. A rating outside the
   active population remains numerically unchanged.

These rules, the paired P89 values, the \(K\) table and the input records are
sufficient to reconstruct the rating states.

## Observation stages

A “rating at the start of the basho”, a probability offered before a bout, a
rating after day 15 and a normalised basho-end rating are not interchangeable.
A public label must identify which one it uses.

## Scope boundary

This chapter says what the Elo-89 contract calculates. It has not argued that
January 1989, P89, this \(K\) schedule or whole-population normalisation is
uniquely correct. Nor has it claimed that a fixed population mean establishes
stable rating meaning at every chii or across every historical period.

Those are questions about evidence and modelling judgement. Chapter 10 turns
to them explicitly.
