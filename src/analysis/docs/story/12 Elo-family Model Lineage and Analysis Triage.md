# Elo-family Model Lineage and Analysis Triage

## Status

This document records the agreed conceptual route from Basic Elo to a finished
full-history Equelo model. It does not select the next model or prescribe the
pre-1989 completion policy.

It also establishes how the project's many analysis packages should eventually
be classified. That classification is necessary because the research record
contains production code, current evidence, reusable methods, superseded model
definitions and explorations of questions that are no longer central.

## The definitive Basic Elo baseline

The project has one definitive baseline model, denoted here by \(B\):

```text
history = represented results from 1989/01 onward
q = 400
k = constant 35
initialisation = the same rating for every newly encountered rikishi
update order = forecast, then process the observed result
rating identity = RikId
rating persistence = permanent
```

The common numerical starting value is only an origin when it is applied
consistently. The substantive baseline assumption is that every entrant starts
equal.

The values of \(q\), \(k\) and the epoch make \(B\) a specified model rather
than a reference to Elo systems in general. Earlier experiments using such
values as \(q=850\) or \(q=900\), or much larger update rates, are not variants
of this definitive baseline unless they are deliberately brought back into the
current programme.

## Selecting the post-1988 successor

The two model choices currently of interest are:

- the `k` policy: constant or divisional; and
- the entrant-initialisation policy: constant or informed priors.

Useful provisional notation is:

| Name | `k` policy | Initialisation |
|---|---|---|
| \(B\) | constant 35 | constant |
| \(B_k\) | divisional | constant |
| \(B_P\) | constant 35 | adopted post-1988 priors |
| \(B_{kP}\) | divisional | adopted post-1988 priors |

This notation identifies experimental contrasts; it does not assert that all
four must become maintained models. It also avoids implying that changing `k`
and changing the prior are sequential transformations whose order has already
been shown to be immaterial.

One candidate will eventually be selected, if the evidence supports it. This
document calls the selected post-1988 model \(B'\). Until that selection has
been made, \(B'\) is a role in the argument rather than a model definition.

The first model-development question is:

> On the complete post-1988 record, is the proposed \(B'\) predictively more
> useful than \(B\), or at least no worse under a declared comparison?

The result must be allowed to answer *no*. A positive or defensible
non-inferiority result is a gate for adopting the changed model, not an outcome
to be manufactured by choosing a favourable account. The detailed validation
protocol remains to be settled, including the treatment of priors learned from
the same historical period.

## What Equelo has meant

`Equelo` has consistently named the project's rating system and the
full-history data product used by the website. What technically distinguished
it from simpler Elo-like systems has changed as the research has developed.

In the established production implementation, Equelo has a specific meaning:
it uses the fixed-supported initial-rating construction, includes represented
history from 1958 onward and supplies the ratings consumed by the website and
public API. That implementation is real production history and must remain
reproducible even if it is superseded.

At the time it was constructed, fixed-point chii priors were treated as an
important part of what made Equelo different from ordinary Elo. Subsequent
work showed that the fixed-point method is more properly understood as one way
to address *initialisation*. Initialisation is an issue for Elo-like systems
generally, not an operation that by itself defines Equelo.

The post-1988 period was used for the recent initial-rating work because it
provides the project's sufficiently complete bout record. Those experiments
therefore belong to the selection of an Elo-like \(B'\), even when their code
or artifacts currently live under `analysis/equelo`.

## The current boundary of Equelo

Once \(B'\) has been selected, the remaining distinctive Equelo construction
is its extension to the incomplete earlier history:

\[
B \longrightarrow B' \longrightarrow
\text{Equelo over the represented 1958--present history}.
\]

Equelo will be the named, fully specified historical application of the chosen
Elo-like model. Its distinctive contribution need not be a novel update
equation. It may instead lie in its explicit, reproducible policy for using
the incomplete 1958--1988 result record, historical banzuke information and
the ranks that do not occur in the post-1988 evidence.

This gives two separate evidential gates:

1. compare candidate \(B'\) with \(B\) on the post-1988 problem; then
2. compare the finished full-history Equelo construction with an appropriate
   ordinary-Elo comparator on the same declared prediction problem.

The second comparison cannot be specified completely until both \(B'\) and the
historical extension have been defined.

## The changed role of chii

The project no longer requires Elo-family ratings to follow chii
monotonically. Elo ratings are not chii. Some broad correlation is expected
because both contain information about performance, but disagreement is not
automatically a defect in the rating model.

Chii nevertheless remains relevant evidence:

- it is the JSA's ordinal assessment of rikishi;
- it can inform entrant initialisation;
- it may help compensate for missing early bout records; and
- it supplies a useful but imperfect external comparison with ratings.

Fixed-point or empirical chii maps must therefore be described as modelling
constructions conditional on data, representation and policy. They are not
measurements of a timeless numerical ability inherently belonging to each
literal chii.

## Consequence for the current story documents

The current STEM Equelo draft presents divisional `k`, normalisation and
informed initialisation as three changes made by Equelo. That was a reasonable
description of the earlier production conception, but it is now provisional.

The eventual story should instead distinguish:

1. the definition and demonstrated predictive value of \(B\);
2. the post-1988 experiments used to choose \(B'\);
3. the extension of \(B'\) to the incomplete pre-1989 record; and
4. the construction and validation of the resulting full-history Equelo.

The existing draft should not be rewritten as if \(B'\) were known before the
model-selection work has actually chosen it.

## Analysis-package triage policy

A package's directory name does not determine its current epistemic role.
In particular, work under `analysis/equelo` may concern the old production
model, a generic initialisation experiment, the proposed historical extension
or shared machinery. Individual producers and artifacts may therefore need
different classifications within the same package.

Every relevant analysis component should eventually be assigned one of these
statuses:

| Status | Meaning |
|---|---|
| **Canonical baseline** | Defines, produces or validates \(B\) |
| **Candidate model work** | Directly informs selection or validation of \(B'\) |
| **Equelo construction** | Directly implements or validates the pre-1989/full-history extension |
| **Production legacy** | Required to reproduce the existing fixed-supported Equelo and website data, but not presumed to define the successor |
| **Supporting method** | Supplies history, metrics, uncertainty, diagnostics or reusable infrastructure without defining a model |
| **Retained negative evidence** | Records a failed hypothesis or limitation that still constrains what may be claimed |
| **Tangential exploration** | Investigated a question no longer central to the current model route |
| **Unclassified** | Has not yet been audited against this lineage |

`Retained negative evidence` is not disposable work. For example, the failure
to establish literal-chii monotonicity explains why the project adopted its
current pragmatic position. `Tangential exploration` likewise does not mean
incorrect or worthless; it means that its parameters or objective should not
silently re-enter the definition of \(B\), \(B'\) or Equelo.

## Initial routing guide

The following is a high-level starting point, not yet the promised
producer-by-producer audit:

| Area | Present relevance |
|---|---|
| `analysis/prediction` | Primary definition and predictive evidence for \(B\); also contains post-1988 initialisation comparisons relevant to \(B'\) |
| `analysis/equelo` | Mixed: current fixed-supported production, recent candidate-prior work, prospective historical-extension work and shared machinery must be separated |
| `analysis/probability` | Earlier model and calibration investigation; its evaluation methods may remain useful, but its \(q=850\), divisional-`k`, 1958-onward model is not \(B\) |
| `analysis/clean_elo` and relevant `analysis/toy_elo` work | Evidence about chii/rating behaviour and mechanisms; important to the limitation record, but not definitions of \(B\) or \(B'\) |
| `analysis/sumo_history` and `analysis/common` | Supporting data and infrastructure whose contracts may affect every comparison |
| Website and public-rating producers | Consumers of the current production Equelo artifacts; migration targets rather than independent evidence for the successor model |

The full audit should record, for each germane producer or experiment:

- the model and parameters it actually runs;
- the historical epoch and eligible-result policy;
- whether it forecasts before updating;
- the artifacts it produces and the consumers of those artifacts;
- which question in the current lineage it answers;
- whether its findings remain affirmative, negative, superseded or merely
  tangential; and
- which methods or results can safely be reused without importing an obsolete
  model definition.

That audit will be the guide for deciding which packages are needed to finish
the full-history model and which belong only to the retained research history.
