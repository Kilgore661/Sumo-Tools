# 2. A Base Model of Competition Over Time

*Part 2 of 5 — [Previous: What Is This About?](01-what-is-this-about.md) · [Next: Performance Measures and Schedule Strength](03-performance-measures-and-schedule-strength.md)*

## Purpose

This note specifies a minimal observational model of two-player, zero-one competition over time. Its purpose is to identify the important domain objects and the signatures of basic and derived functions. It is not intended as a development in universal algebra, nor does it attempt to reduce ordinary mathematical objects such as integers, Boolean values, sequences, or times to more primitive constructions.

Here and throughout this series, *minimal* is relative to the modelling purpose described in [Part 1](01-what-is-this-about.md). It is not a claim that these are the only concepts that can matter in a theory of competition.

The model deliberately introduces no notion of true skill. Ratings, measures of performance, schedule difficulty, predictions, and latent skill models are possible extensions of the base model, not parts of it.

## Background types

We take the following ordinary types for granted:

- `Bool`, for predicates;
- \(\mathbf 2=\{0,1\}\), for a loss or win;
- \(\mathbb N\), for indices and counts;
- finite or otherwise appropriate sequences;
- an ordered set \(\mathsf{Time}\).

## Domain types

The principal domain types are

\[
\mathsf{Player},\qquad
\mathsf{Bout},\qquad
\mathsf{Schedule},\qquad
\mathsf{History}.
\]

### Players

\(\mathsf{Player}\) is the type of competitors. A player may be represented in an implementation by an identifier; it need not necessarily be a class with substantial internal structure.

### Bouts

A bout records two distinct players, a time, and a zero-one result. One concrete representation is

\[
\mathsf{Bout}
=
\{(i,j,t,w)\in
\mathsf{Player}^2\times\mathsf{Time}\times\mathbf 2
:i\ne j\},
\]

where \(w=1\) means that the first player \(i\) won and \(w=0\) means that the first player lost.

An abstract implementation may instead provide accessors with signatures

\[
p_1,p_2:\mathsf{Bout}\to\mathsf{Player},
\]

\[
\operatorname{time}:\mathsf{Bout}\to\mathsf{Time},
\]

and

\[
\operatorname{outcome}:\mathsf{Bout}\to\mathbf 2.
\]

Useful derived functions include

\[
\operatorname{involves}:
\mathsf{Player}\times\mathsf{Bout}\to\mathsf{Bool},
\]

\[
\operatorname{opponent}:
\mathsf{Player}\times\mathsf{Bout}
\to\mathsf{Option}(\mathsf{Player}),
\]

and

\[
\operatorname{resultFor}:
\mathsf{Player}\times\mathsf{Bout}
\to\mathsf{Option}(\mathbf 2).
\]

The option type accounts for the case in which the supplied player did not participate in the bout.

### Schedules

A player schedule is an ordered sequence of opponent-time pairs:

\[
\mathsf{Schedule}
=
\operatorname{Seq}(\mathsf{Player}\times\mathsf{Time}).
\]

Thus, if \(s:\mathsf{Schedule}\), then

\[
s(n)=(j,t)
\]

means that the \(n\)-th bout on the schedule was against player \(j\) at time \(t\).

A schedule records whom a player faced and when. By this definition it does not itself record the result.

Common schedule-selection functions may include

\[
\operatorname{upTo}:
\mathsf{Time}\times\mathsf{Schedule}
\to\mathsf{Schedule},
\]

\[
\operatorname{between}:
\mathsf{Time}\times\mathsf{Time}\times\mathsf{Schedule}
\to\mathsf{Schedule},
\]

and

\[
\operatorname{last}:
\mathbb N\times\mathsf{Schedule}
\to\mathsf{Schedule}.
\]

These represent different choices about which observations are to count in a subsequent evaluation.

### Histories

A history is the global record of the competition. At minimum, it supplies each player's schedule and the result of each scheduled bout from that player's perspective.

This can be expressed by treating \(\mathsf{History}\) as a domain type equipped with accessors

\[
\operatorname{schedule}:
\mathsf{History}\times\mathsf{Player}
\to\mathsf{Schedule},
\]

and

\[
\operatorname{result}:
\mathsf{History}\times\mathsf{Player}\times\mathbb N
\to\mathsf{Option}(\mathbf 2).
\]

For a history \(h\), the notation

\[
h(i)
\]

may be used as shorthand for

\[
\operatorname{schedule}(h,i).
\]

Accordingly,

\[
h(i)(n)
\]

is the opponent-time pair for player \(i\)'s \(n\)-th bout, while

\[
\operatorname{result}(h,i,n)
\]

gives its result when the index is valid.

A valid history should satisfy consistency conditions. If player \(i\)'s schedule records a bout against \(j\) at time \(t\), player \(j\)'s record should contain the corresponding bout against \(i\), and the two results should be complementary. The precise handling of simultaneous bouts, duplicate records, and bout identity may be fixed when an implementation requires it.

## Performance measures

A performance measure is not part of the observational base model. It is a function added to that model.

Let \(V\) be an arbitrary value type. If ratings are to be comparable, \(V\) may be equipped with a relation

\[
\preceq_V:V\times V\to\mathsf{Bool}.
\]

Neither \(V\) nor its ordering is assumed to be numerical or total.

### Local measures

A measure that depends only on a player and a selected schedule has signature

\[
\Phi:
\mathsf{Player}\times\mathsf{Schedule}
\to V.
\]

Examples include a number of wins or a win proportion, provided the relevant results are carried with, or otherwise recoverable for, the selected schedule.

### History-dependent measures

If wider competitive context is required, the signature becomes

\[
\Phi:
\mathsf{Player}\times\mathsf{Schedule}\times\mathsf{History}
\to V.
\]

In

\[
\Phi(i,s,h),
\]

- \(i\) is the player being evaluated;
- \(s\) is the particular schedule, or selected part of a schedule, over which the evaluation is made;
- \(h\) is the global history supplying contextual information.

Typically \(s=h(i)\), or \(s\) is a selected subsequence of \(h(i)\), such as the most recent \(\ell\) bouts. Keeping \(s\) explicit permits several evaluation windows to be used with the same history.

The history argument is needed, for example, when the evidential significance of a result against an opponent depends on that opponent's record against other players. A measure that does not require this information should use the simpler signature.

There is no need at this stage to formulate one signature covering every possible performance functional. Dependencies should be exposed only when a particular measure requires them.

## Strength of schedule

Strength of schedule is also a derived notion. An elementary form first assigns opponents record-based values and then aggregates those values over a player's schedule. More general forms may depend directly on the player, the selected schedule, and the global history.

A local schedule descriptor might have signature

\[
D_0:\mathsf{Schedule}\to A,
\]

whereas a contextual schedule measure might have signature

\[
D:
\mathsf{Player}\times\mathsf{Schedule}\times\mathsf{History}
\to A.
\]

The latter permits the difficulty of a schedule to depend on opponents' other results or on player-opponent interactions. It does not require difficulty to be reducible to a single, opponent-independent player rating.

## Epistemological boundary

The base model contains observations:

\[
\text{players, bouts, times, schedules, histories, and results}.
\]

It does not contain an independently existing quantity called skill. A rating or performance value is a constructed summary:

\[
\text{observed history}
\longrightarrow
\text{selected schedule}
\longrightarrow
\text{performance value}.
\]

A latent-skill model is a further explanatory hypothesis. It introduces a separate skill carrier and claims that observed outcomes are generated from unobserved player states. Nothing in the base model or in the mere existence of a performance function requires that interpretation.

## Modelling stance

The specification is intentionally selective:

- ordinary mathematical infrastructure is treated as background;
- domain objects are made explicit where they carry conceptual weight;
- important dependencies are expressed by function signatures;
- derived notions are kept separate from observational primitives;
- fuller formalisation remains possible if a particular ambiguity or implementation requires it.

In Python, this naturally suggests classes for objects such as `Bout`, `Schedule`, and perhaps `History`, while using ordinary types for integers, Boolean results, times, sequences, and player identifiers where appropriate. The mathematical specification serves as a discipline for identifying concepts and dependencies, not as a requirement that every object belong to a specially developed algebra.
