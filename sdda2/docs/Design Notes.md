# SDDA2 Design Notes

## Product-First Framing

The old question was often phrased as:

```text
What does the `make_site2` module need?
```

The better question is:

```text
What does the local website product need, and what artifacts does it promise?
```

This distinction matters because code is machinery. The distribution target is the artifact set or target state delivered by that machinery.

## Why This Is Not Jervis

The Jervis line of thought asks whether a formal `free(S)` / `init(S)` analysis can be applied to Python-like programs.

That remains intellectually useful, but direct application to ordinary Python quickly becomes too expensive:

* loops may execute zero times;
* guarded loop outputs become conditional file families;
* `break` and `continue` require control-flow-sensitive treatment;
* useful precision tends toward abstract interpretation or symbolic execution.

SDDA2 should avoid that path.

The SDDA2 question is not:

```text
Can we prove the exact free set of this Python program?
```

It is:

```text
What file effects can we observe statically, how certain are they,
and how do they relate to a declared product?
```

## Useful Ideas To Keep

From the original SDDA work:

* scan file effects such as reads, writes, globs, copies, deletes, downloads, and environment reads;
* normalize file effects into file families;
* keep raw evidence separate from interpretation;
* classify evidence into reviewable policy buckets;
* report unresolved cases rather than hiding them;
* use execution slices as builder evidence where helpful.

From the Jervis discussion:

* be explicit about what can be known statically;
* distinguish guaranteed facts from possible or conditional facts;
* avoid pretending that arbitrary Python has a simple makefile semantics.

## New Center Of Gravity

SDDA2 should introduce product records before it introduces module analysis.

Candidate concepts:

```text
Product
Builder
Artifact family
Input family
External resource
Generated intermediate
Deployment target
Packaging policy
Evidence row
Review item
```

The report should answer product questions:

```text
For product P:
  what artifacts are promised?
  what source files/assets are required?
  what precomputed artifacts must be included or regenerated?
  what external resources are assumed?
  what generated intermediates are observed?
  what remains unresolved?
```

## Immediate Non-Goals

SDDA2 should not initially:

* infer every product from the repository;
* treat every module with a main guard as a product;
* derive a complete makefile;
* implement full Python control-flow semantics;
* prove exact file dependencies.

