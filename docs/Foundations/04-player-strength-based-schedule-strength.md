# 4. Player-Strength-Based Schedule Strength

*Part 4 of 5 — [Previous: Performance Measures and Schedule Strength](03-performance-measures-and-schedule-strength.md) · [Next: Mathematical Context](05-mathematical-context.md)*

## Purpose and relationship to the existing models

This note defines one particular class of schedule-strength measures over the framework developed in [*A Base Model of Competition Over Time*](02-base-model.md) and [*Performance Measures and Schedule Strength*](03-performance-measures-and-schedule-strength.md).

The base model supplies histories, players, times and schedules. A schedule is a sequence of opponent-time pairs:

\[
\mathsf{Schedule}
=
\operatorname{Seq}(\mathsf{Player}\times\mathsf{Time}).
\]

The schedule-strength model permits an abstract operation whose result lies in some schedule-strength carrier. This note specializes that abstract operation by making schedule strength depend only on the player-strength values of the opponents appearing in the schedule.

This is an extension of the previous models, not a revision of them. It does not claim that every conceivable schedule-strength measure must be based on player strength. Intrinsic properties such as schedule length, timing or repetition remain possible alternative bases for schedule strength.

## The Player Strength carrier

Introduce a new carrier

\[
S=\mathsf{PlayerStrength}.
\]

At this stage no further structure is assumed on \(S\). In particular, its elements are not assumed to be numbers, and no ordering, addition, averaging operation or interpretation is imposed.

Introduce the operation

\[
ps:
\mathsf{History}\times\mathsf{Player}
\rightharpoonup S,
\]

where

\[
ps(h,i)
\]

is player \(i\)'s strength after history \(h\). The operation is partial when player strength is defined only for players occurring in the history:

\[
ps(h,i)\text{ is defined iff }i\text{ occurs in }h.
\]

Nothing in this signature specifies how \(ps\) is calculated or what kind of quantity its value represents.

## Time-specific player strength

A finer-grained version is

\[
ps_t:
\mathsf{History}\times
\mathsf{Player}\times
\mathsf{Time}
\rightharpoonup S,
\]

where

\[
ps_t(h,i,t)
\]

is player \(i\)'s strength at time \(t\) in history \(h\). It is defined when \(i\) occurs in \(h\) before \(t\). Equivalently, its domain may be written explicitly as

\[
\left\{
(h,i,t):
i\text{ occurs in }h\text{ before }t
\right\}.
\]

The end-of-history operation \(ps\) and the time-specific operation \(ps_t\) are two available levels of granularity. No relationship between them is imposed here.

## Nonempty sequences of player strengths

Let

\[
S^+
=
\coprod_{n\geq1}S^n
\]

be the carrier of nonempty finite sequences of elements of \(S\). Thus an element of \(S^+\) belongs to \(S^n\) for some context-dependent positive length \(n\).

Because the base definition of \(\mathsf{Schedule}\) permits an empty sequence, write

\[
\mathsf{Schedule}^+
\]

for the derived subtype of nonempty schedules.

## Extracting opponent strengths from a schedule

Introduce the operation

\[
\operatorname{opponentStrengths}:
\mathsf{History}\times\mathsf{Schedule}^+
\rightharpoonup S^+.
\]

For a schedule

\[
sch=
((j_1,t_1),\ldots,(j_n,t_n)),
\]

define

\[
\operatorname{opponentStrengths}(h,sch)
=
\bigl(
ps(h,j_1),\ldots,ps(h,j_n)
\bigr).
\]

The operation is defined when each required player-strength value is defined. It preserves the length, order and multiplicity of the opponents in the schedule.

Using time-specific strength instead gives

\[
\operatorname{opponentStrengths}_t:
\mathsf{History}\times\mathsf{Schedule}^+
\rightharpoonup S^+,
\]

with

\[
\operatorname{opponentStrengths}_t(h,sch)
=
\bigl(
ps_t(h,j_1,t_1),\ldots,
ps_t(h,j_n,t_n)
\bigr).
\]

The first operation evaluates every opponent using an end-of-history player-strength value. The second uses the opponent's strength at the time recorded in the schedule.

## Aggregating opponent strengths

Let

\[
D=\mathsf{ScheduleStrength}
\]

be the schedule-strength carrier. It is distinct from \(S\) unless a particular model identifies them.

Introduce an abstract aggregation operation

\[
A:S^+\to D.
\]

Equivalently, this can be presented as a family of operations with a common codomain:

\[
A_n:S^n\to D,
\qquad n\geq1.
\]

No algebraic structure on \(S\) is required merely to state \(A\). In particular, calling \(A\) an aggregation operation does not assume that its inputs can be added or divided.

If schedule-strength values are to be compared, the carrier \(D\) may subsequently be equipped with a relation

\[
\preceq_D:D\times D\to\mathsf{Bool}.
\]

Whether this is a preorder, partial order or total order is a further choice.

## Player-strength-based schedule strength

Define

\[
\operatorname{strengthOf}:
\mathsf{History}\times\mathsf{Schedule}^+
\rightharpoonup D
\]

by

\[
\operatorname{strengthOf}(h,sch)
=
A\bigl(
\operatorname{opponentStrengths}(h,sch)
\bigr).
\]

The construction therefore factors as

\[
\mathsf{History}\times\mathsf{Schedule}^+
\xrightarrow{\ \operatorname{opponentStrengths}\ }
S^+
\xrightarrow{\ A\ }
D.
\]

The time-specific variant is

\[
\operatorname{strengthOf}_t(h,sch)
=
A\bigl(
\operatorname{opponentStrengths}_t(h,sch)
\bigr).
\]

In ordinary terms, the construction first assigns a strength value to every opponent in the schedule and then combines the resulting sequence into a schedule-strength value.

## Compatibility with the general schedule-strength signature

The earlier general contextual signature was

\[
D_{\mathrm{opponent}}:
\mathsf{Player}\times
\mathsf{Schedule}\times
\mathsf{History}
\to U.
\]

Here \(U\) is the same role now played by \(D\). The focal-player argument permits schedule difficulty to depend on the identity of the player whose schedule is being evaluated.

The construction in this note is based purely on the strengths of the opponents. It therefore does not use that focal-player argument. It fits the general signature by defining

\[
D_{\mathrm{PS}}(i,sch,h)
=
\operatorname{strengthOf}(h,sch).
\]

Thus the new operation is a specialization of the previously documented schedule-strength model: it is the case in which schedule strength factors through the sequence of player-strength values attached to the opponents.

The earlier placeholder

\[
Q:\mathsf{Player}\times\mathsf{History}\to X
\]

is likewise specialized here by taking \(X=S\) and, up to argument order, \(Q(i,h)=ps(h,i)\).

## What remains abstract

This extension deliberately leaves open:

- the nature of the carrier \(S\);
- the definition of \(ps\) or \(ps_t\);
- the nature of the carrier \(D\);
- the aggregation operation \(A\);
- whether \(D=S\);
- whether either carrier has an ordering or numerical structure;
- whether player strength has any particular observational, explanatory or ontological interpretation.

Consequently, this note defines a class of opponent-strength-based schedule measures without asserting that it is the only class of schedule-strength measures or selecting a particular numerical formula.
