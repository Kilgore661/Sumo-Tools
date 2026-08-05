# 5. Mathematical Context for the Competition Framework

*Part 5 of 5 — [Previous: Player-Strength-Based Schedule Strength](04-player-strength-based-schedule-strength.md) · [Return to: What Is This About?](01-what-is-this-about.md)*

## Summary

The framework developed in the preceding notes already resembles established mathematics. It is not contained in one perfectly matching branch, but lies at the intersection of:

\[
\boxed{\text{temporal networks}}
\quad+\quad
\boxed{\text{generalized tournaments}}
\quad+\quad
\boxed{\text{axiomatic paired-comparison ranking}}
\quad+\quad
\boxed{\text{measurement theory}}.
\]

A suitable name for the present framework is:

> **An observational, temporal paired-comparison framework for axiomatic performance measurement.**

This description does not presuppose latent skill. Statistical latent-skill models can be introduced later as a distinct explanatory layer.

## The observational object

The base model contains players and time-stamped, zero-one bouts. A bout can be represented as

\[
(i,j,t,w),
\]

where players \(i\) and \(j\) compete at time \(t\), and \(w\in\{0,1\}\) records the result from \(i\)'s perspective.

If each player is represented by a vertex and a bout is represented by a directed edge from winner to loser, the competition becomes a directed comparison graph.

An ordinary graph-theoretic tournament has exactly one directed edge between every pair of vertices. The present framework is more general because:

- some pairs may never compete;
- some pairs may compete repeatedly;
- every bout has a time;
- different temporal windows may be selected for different measurements.

When time is ignored, the resulting object is naturally described as a **generalized tournament**, an **incomplete paired-comparison problem**, or a **directed comparison multigraph**.

When time is retained, it is an **event-based temporal network**: players are nodes and bouts are time-stamped interaction events. Temporal-network theory explicitly studies systems whose elementary data are time-stamped events rather than permanent edges. See Petter Holme and Jari Saramäki, [“Temporal networks as a modeling framework”](https://arxiv.org/abs/2103.13586).

## Correspondence with existing terminology

| Present framework | Existing terminology |
|---|---|
| Player | Vertex, node, alternative or competitor |
| Bout \((i,j,t,w)\) | Time-stamped directed comparison event |
| History | Temporal directed multigraph or event stream |
| Player record | Incident-event sequence or ego history |
| Schedule | Projection of incident events to opponents and times |
| Direct measure | Local score or row-based statistic |
| Contextual measure | Global, recursive or graph-based score |
| Strength of schedule | Neighbour or opponent adjustment |

The term *sports scheduling* can be misleading in this context. That literature often studies how future fixtures should be arranged. Here a schedule is primarily an evidential projection of recorded bouts for a player.

## Paired-comparison ranking

The field most directly concerned with direct performance, contextual performance and opponent adjustment is **ranking from paired comparisons**.

A history is often compressed into matrices such as

\[
M=(m_{ij}),
\]

where \(m_{ij}\) records how many comparisons occurred between players \(i\) and \(j\), and

\[
A=(a_{ij}),
\]

where \(a_{ij}\) records the results obtained by \(i\) against \(j\).

This compression normally discards the temporal order preserved by the base model. After a temporal window has been selected, however, the selected history can always be reduced to this kind of comparison data.

Methods in this area exhibit the substance of the direct/contextual distinction:

- row sum or number of wins is direct;
- win percentage is direct;
- generalized row sum adjusts a direct score using opponent information;
- least-squares methods use the whole comparison graph;
- fair-bets and other recursive methods allow opponent values to depend on further opponents.

González-Díaz, Hendrickx and Lohmann study several such ranking methods axiomatically, including generalized row sum, least squares, fair bets and the Zermelo–Bradley–Terry method: [“Paired comparisons analysis: an axiomatic approach to ranking methods”](https://doi.org/10.1007/s00355-013-0726-2).

## Axiomatic ranking without latent skill

The literature most closely aligned with the present epistemological stance is **axiomatic ranking**.

It begins with observed comparison data and studies functions of the form

\[
F:
\mathsf{ComparisonData}
\to
\mathsf{RatingOrRanking}.
\]

Rather than first postulating a true skill, it asks which properties such a function should satisfy. Candidate requirements include:

- neutrality under renaming players;
- monotonicity when a player's result improves;
- consistency when bodies of results are combined;
- appropriate treatment of unequal schedules;
- independence from irrelevant matches;
- self-consistency relative to opponents.

Some attractive requirements cannot all be satisfied on a sufficiently general domain of incomplete and repeated comparisons. Relevant examples include László Csató's [“An impossibility theorem for paired comparisons”](https://arxiv.org/abs/1612.00186) and [“Some impossibilities of ranking in generalized tournaments”](https://arxiv.org/abs/1701.06539).

This programme closely matches the present approach:

1. specify the observational domain;
2. state the signature of the rating function;
3. propose axioms for that function;
4. determine which functions satisfy those axioms;
5. identify incompatibilities among apparently desirable requirements.

A related artificial-intelligence literature studies ranking systems where the objects being rated also supply relational evidence about one another. See Alon Altman and Moshe Tennenholtz, [“Axiomatic Foundations for Ranking Systems”](https://doi.org/10.1613/JAIR.2306).

## Tournament theory and social choice

Tournament theory treats directed pairwise dominance as a mathematical object in its own right. It studies score sequences, cycles, paths, dominant sets and methods for selecting distinguished competitors.

Computational social choice studies **tournament solutions** such as the Copeland rule, top cycle and uncovered set. These methods take pairwise dominance as given and need not assume an underlying real-valued quality. Cycles can be treated as genuine features of the relation rather than necessarily as noise around a latent ordering. See Brandt, Brill and Harrenstein, [“Tournament Solutions”](https://doi.org/10.1017/CBO9781107446984.004).

Tournament solutions often return a winner or a subset rather than a numerical rating. They therefore do not exactly solve the present measurement problem, but they share its observational-first philosophy.

## The statistical paired-comparison branch

Statistical paired-comparison modelling is a neighbouring but distinct development. Bradley–Terry, Thurstone–Mosteller, Elo and related systems generally introduce parameters intended to explain or predict comparison outcomes.

This is where a latent strength or skill carrier normally enters. A review of this statistical branch is Manuela Cattelan, [“Models for Paired Comparison Data: A Review with Emphasis on Dependent Data”](https://arxiv.org/abs/1210.1016).

The important separation is therefore

\[
\text{observed comparison events}
\longrightarrow
\text{selected records}
\longrightarrow
\text{rating function},
\]

followed, only if desired, by an explanatory model involving

\[
\text{latent player states}
\longrightarrow
\text{probabilistic outcome mechanism}.
\]

The first construction does not logically require the second.

## Measurement theory

The concern with the rating carrier \(V\), its ordering, and the meaning of numerical transformations belongs to **measurement theory**.

Measurement theory studies when an empirical or qualitative relational structure admits a numerical representation and which transformations preserve the meaning of that representation. It provides language for distinguishing:

- an arbitrary ordered carrier from \(\mathbb R\);
- ordinal scales from interval and ratio scales;
- partial orders from total orders;
- multidimensional values from scalar ratings;
- meaningful comparisons from artefacts of a chosen numerical representation.

Louis Narens' [*Abstract Measurement Theory*](https://mitpress.mit.edu/9780262140379/abstract-measurement-theory/) is a general reference for ordered relational structures and their numerical representations.

Measurement theory describes the codomain side of the rating functions. It does not by itself supply the competition history or the paired-comparison structure.

## Why game theory is not yet central

Game theory normally studies strategic choices, information, actions and payoffs. The present framework is concerned first with representing recorded competitive events and defining measurements over them.

Strategic models may later be added, but they are not necessary for:

- the player and bout types;
- schedules and histories;
- temporal selection;
- direct performance;
- contextual performance;
- opponent adjustment;
- axiomatic analysis of rating functions.

The nearest existing mathematics at this stage is therefore tournament and paired-comparison theory rather than strategic game theory.

## What is distinctive about the present framework

Classical ranking methods often begin after the match data have already been collapsed into totals or a comparison matrix. The present framework retains individual bouts and their times before deciding:

- which temporal window to use;
- whether to measure direct or contextual performance;
- whether schedule difficulty is intrinsic, focal-player-specific or opponent-based;
- whether to retain several dimensions or aggregate them;
- whether to introduce latent skill at all.

This makes the observational framework slightly more general than a conventional static tournament-ranking problem.

Once time and event identity are suppressed, it reduces naturally to the established mathematics of generalized tournaments and paired-comparison ranking. With time retained, temporal-network theory provides the corresponding event structure.

## Conclusion

The present framework is not an isolated reinvention. Its principal pieces already have established mathematical homes:

\[
\begin{aligned}
\text{time-stamped bouts} &\longleftrightarrow \text{temporal networks},\\
\text{binary competitive outcomes} &\longleftrightarrow \text{generalized tournaments},\\
\text{direct and contextual rating rules} &\longleftrightarrow \text{paired-comparison ranking},\\
\text{properties required of those rules} &\longleftrightarrow \text{axiomatic ranking},\\
\text{ordered rating carriers} &\longleftrightarrow \text{measurement theory}.
\end{aligned}
\]

The most promising existing branch from which to continue without latent skill is **axiomatic ranking from paired comparisons on generalized tournaments**. Temporal-network language can be used to preserve the event and time structure that static paired-comparison methods normally discard.
