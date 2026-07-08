# Analysis

This folder contains a mixture of exploratory analysis, research prototypes,
supporting tools, and partly historical experiments. What belongs here, and
what should eventually graduate into a more stable product or data pipeline, is
still being worked out.

The common thread is not a single model. The common thread is a question:

```text
what is a rating, or what could a rating usefully be, in a domain where chii
are already rating-like labels in all but name?
```

Much of the work here grew out of Elo-style experiments, Equelo, probability
calibration, fixed-point constructions, banzuke comparison, and toy models of
rating behaviour. Some of those experiments rate rikishi. Some explore
rank/chii-derived initialisation or representation. The newer toy work asks
what happens if the object being estimated is not a rikishi at all, but an
ordered label or station.

## Epistemic Guardrail

The work in this folder should stay aware of the difference between:

```text
the epistemology of a formal model
```

and:

```text
a teleological story in which the system must be right in the following
respects ...
```

This matters because chii are already meaningful institutional labels. If a
model agrees with chii, it is tempting to say that the model has discovered
what chii really mean. If a model disagrees with chii, it is tempting to say
that the model has exposed the inadequacy or bias of the banzuke. Both moves
can be premature.

The aim is not to build a model flexible enough to explain chii after the fact.
The aim is to test whether deliberately constrained models produce stable,
interpretable signals, and to treat failure as information rather than as an
automatic invitation to add more mechanisms.

For the current version of this guardrail in the context of the toy Elo work,
see:

```text
src/analysis/toy_elo/docs/What Ratings Might Say About Grand Sumo.md
```

In particular, see the section:

```text
Anti-Teleology Guardrail
```

## Current State Of Play

The current toy Elo work supports a deliberately narrow claim:

```text
Under a correctly specified, stationary toy data-generating process, the Elo
implementation recovers the hidden skill-gap structure according to predefined
stability metrics.

In tested two-division cases, sparse boundary bridges are sufficient to make
the two division rating scales commensurate.
```

This should not be shortened to "Elo discovers true skill" without carrying
the conditions along. The model-level conditions currently include:

```text
fixed pool of players
fixed latent skill vector
linear hidden skill spacing
outcomes generated from the same logistic family used by the updater
uniform midpoint initial ratings
chosen q, rating span, and learning fraction
ensemble mean ratings across repeated stochastic runs
predefined RMSE, slope, window, and bridge-error stability criteria
```

The two-division claim is also conditional. The tested divisions are
skill-contiguous, and the bridges are particular tested bridge shapes, not a
proof that any limited inter-division matching is enough.

The evidence-aligned bridge work partially reduces the gap between the toy
model and sumo for one mechanism: interdivision matching is now represented by
scheduled-torikumi evidence and by distance from the division boundary, rather
than by an arbitrary bridge width or historically contingent absolute rank
labels. The broader toy-model caveats still pertain.

Important attack surfaces in the model are therefore:

```text
initialisation: mostly uniform midpoint ratings have been tested
stability: convergence means passing our chosen thresholds, not exact equality
event semantics: an event is full round robin in some toy runs and basho-like
                 in the evidence-aligned bridge run
bridge shape: bridge frequency and opponent-selection rules matter
correct specification: the hidden outcome process matches the Elo link
ensemble claim: clean convergence is about ensemble means, not every single run
```

The current robust wording is:

```text
Under a correctly specified, stationary toy data-generating process, our Elo
implementation recovers the hidden skill-gap structure according to predefined
stability metrics; and in tested two-division cases, sparse boundary bridges
are sufficient to make the two division scales commensurate.
```

## Current Status

This README is intentionally provisional. The folder still contains old notes,
active experiments, and research code whose status varies. Before treating any
analysis here as a stable claim, check the local README or docs for that
subfolder and inspect the run outputs or audit trail behind the claim.
