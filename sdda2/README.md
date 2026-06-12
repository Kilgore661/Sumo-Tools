# SDDA2

SDDA2 is the proposed artifact-first successor to the original `sdda` experiments.

The key correction is that a distribution is not primarily a distribution of a Python module. It is a distribution of a promised artifact set or target state.

Examples:

* local website files;
* remote website files;
* a generated build tree;
* a named family such as `foo-outputs`.

Python modules, functions, and commands are builders or evidence sources. They are not, by themselves, the thing being distributed.

## Relationship To Jervis

`jervis` records the formal `free(S)` / `init(S)` idea and the reasons why applying it directly to ordinary Python is likely too ambitious for this project.

SDDA2 is not intended to be a direct implementation of `free(S)`.

Instead, it carries forward a more practical idea:

```text
Find file effects, group them into file families, classify their certainty,
and compare them with declared products.
```

This means SDDA2 should be evidence-backed and conservative, but not a proof system for Python.

## Relationship To SDDA

The original `sdda` work contains useful machinery:

* Python module indexing;
* import reachability;
* scope extraction;
* file-use extraction;
* file-family normalisation;
* producer-output evidence;
* source-distribution bucket classification.

The weak point is conceptual: the workflow tends to start from a module or entrypoint and ask what distribution it implies.

SDDA2 should start from a product declaration and ask what evidence supports that product's required inputs, generated intermediates, final artifacts, and external assumptions.

## Intended Shape

A product declaration might eventually say:

```text
product:
  local-server-site

builder:
  src.products.make_site2.__main__

artifacts:
  local server file tree

external resources:
  internet access

policy:
  generated outputs are not source inputs
  precomputed artifacts must be included or regenerated
```

The analyser can then produce reports grouped by product rather than by module.

## First Goal

The first SDDA2 goal should be modest:

* define a product vocabulary;
* reuse or copy the useful SDDA file-effect scanning ideas;
* produce neutral evidence reports;
* avoid building a general Python abstract interpreter;
* avoid treating every runnable module as a distribution target.

