# Introspection Docs

## Status

Draft.

This folder documents the `src.introspection` package.

## Purpose

`src.introspection` contains mechanical repository-inspection tools. These tools
produce evidence about the project structure; they do not decide final product,
module, or generated-output status.

The package was introduced to support the makefile/dependency-graph audit by
answering the first narrow question:

```text
What Python modules import what other Python modules or symbols?
```

## Current tool

The current implemented tool is:

```text
py -m src.introspection.python_import_graph
```

It scans Python files under `src/` and `tests/` by default and writes CSV reports
to:

```text
files/output/introspection/
```

The main reports are:

```text
python_modules.csv
python_import_edges.csv
python_entry_candidates.csv
python_imported_main.csv
```

`python_import_edges.csv` is raw evidence and may be large. The smaller review
surfaces are `python_entry_candidates.csv` and `python_imported_main.csv`.

## Relationship to makefile audit docs

The makefile audit docs live under:

```text
src/docs/makefile/
```

Those documents define the vocabulary and workflow for generated-output and
producer/consumer analysis. This package provides mechanical support for that
workflow, starting with Python import analysis.

The import graph is a pre-inventory step. It helps distinguish:

```text
standalone runnable modules
runnable support modules
ordinary support modules
orphan or externally-invoked modules
```

It does not yet identify generated file inputs, generated file outputs,
producers, consumers, freshness rules, or Makefile targets.

## Current boundary

This package should remain evidence-producing rather than decision-making.

A useful rule of thumb:

```text
src.introspection produces facts.
src/docs/makefile explains how to interpret those facts.
```
