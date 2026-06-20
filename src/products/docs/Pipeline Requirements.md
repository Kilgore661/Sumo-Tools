# Product Pipeline Requirements

## Status

Placeholder product-level requirements note.

This document records the need for a coherent product pipeline above individual
products such as `make_site2`. It is intentionally small. It does not yet define
the final orchestration design.

---

## 1. Requirement

The product pipeline shall work.

That means the project shall have a reproducible way to prepare required
producer outputs, assemble public products from coherent inputs, and deploy or
stage the resulting outputs without relying on accidental stale files.

At minimum, the pipeline shall make clear:

- which producer steps are required for a full public refresh;
- which outputs each step produces;
- which later steps depend on those outputs;
- which data instance or live-store state the outputs represent;
- which artifacts are refreshed routinely when new data arrives;
- which artifacts are refreshed only by explicit analytical or public-scale
  decision;
- how a final deployment can be built from scratch at least once before release.

---

## 2. Current Implementation Evidence

The repository contains `_run.ps1`.

That script is legacy implementation evidence for a full refresh/deploy
workflow. It has worked in the past, but it is not yet an authoritative
pipeline contract derived from requirements and dependency analysis.

Until reviewed, `_run.ps1` should be treated as a provisional implementation
candidate, not as design truth.

---

## 3. Current Known Policy: Equelo Landmarks

The Equelo package distinguishes operational process ratings from public
rating landmarks.

Current Equelo policy is that ordinary new-data refreshes regenerate
operational fixed-supported process ratings when downstream pages need current
individual rikishi ratings. They do not automatically regenerate the public
`Typical Equelo Ratings` landmark bundle except as part of the accepted
fixed-supported refresh path.

Refreshing `Typical Equelo Ratings` is allowed, but it is an explicit
public-scale decision rather than an automatic consequence of a new basho or a
process-rating refresh.

---

## 4. Deferred Work

The full product pipeline still needs proper design.

That work should derive the implementation from requirements, producer
dependencies, data-flow analysis, freshness policy, validation/provenance needs,
and deployment requirements.
