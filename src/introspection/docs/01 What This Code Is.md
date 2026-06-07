Here’s a draft for `src/introspection/docs/01 What This Code Is.md`.

# What This Code Is

## Status

Draft.

This document is a reverse-engineered orientation note for the current `src.introspection` package.

It is not a complete requirements, specification, or design document. It records the current purpose and shape of the code well enough for someone cold on the project to understand why the package exists and where to look next.

## Purpose

`src.introspection` exists to analyse the Sumo-Tools codebase.

The larger project goal is to make Sumo-Tools deployable elsewhere, starting with no generated data already present. To do that, the project needs to understand:

```text
what code exists
what code can be run
what code depends on what other code
what outputs are generated
what inputs those outputs need
what order the generation steps must run in
```

The intended deployment mechanism is `make`.

The eventual objective is to create a Makefile that can rebuild the necessary project outputs from source inputs and documented intermediate steps.

## Immediate Problem

The project contains many Python modules, many generated files, and many producer scripts. Much of the existing data flow is implicit rather than documented.

Before writing a Makefile, the project needs a mechanical inventory of the code structure.

The first narrow question is:

```text
What Python modules import what other Python modules or symbols?
```

This is useful because it helps distinguish:

```text
standalone runnable programs
runnable modules that are also support modules
ordinary support modules
orphan modules
modules that may be invoked only by external/manual workflows
```

That classification is not the final Makefile dependency graph. It is a prerequisite for deciding which modules are likely to be real entry points and which modules are dependencies of those entry points.

## Current Implemented Tool

The current implemented tool is:

```text
py -m src.introspection.python_import_graph
```

It performs static analysis of Python source files using Python's `ast` module.

By default, it scans:

```text
src/
tests/
```

and writes reports under:

```text
files/output/introspection/
```

The current reports are:

```text
python_modules.csv
python_import_edges.csv
python_entry_candidates.csv
python_imported_main.csv
```

## What the Tool Records

The tool records one row per discovered Python module, including:

```text
module path
module name
whether it has an if __name__ == "__main__" guard
whether it defines a top-level main function
whether parsing succeeded
which project modules import it
which symbols are imported from it
whether main is imported from it
whether non-main symbols are imported from it
```

It also records one row per syntactic import edge, including:

```text
importing module
imported module text
imported symbol
import style
relative import level
resolved project module, where known
resolved project path, where known
resolution status
```

The raw import-edge report may be large. The smaller review reports are intended to be the first human-facing outputs.

## Current Review Reports

### `python_entry_candidates.csv`

This report contains only modules with a `__main__` execution surface.

It is intended to help review likely runnable modules.

A module with a `__main__` guard is not automatically a standalone program. It may instead be a support module that can be run directly for testing, diagnostics, or development.

### `python_imported_main.csv`

This report contains only imports of the form:

```text
from x import main
```

This pattern needs review because `main` is often a poor name for a reusable API boundary.

Some cases are harmless or expected. For example:

```text
__main__.py imports main from cli.py
```

is usually just a package execution wrapper.

Other cases may represent orchestration, such as:

```text
publisher imports main from deploy
```

where `deploy` generally means copying web files to server targets.

The report exists to make those cases visible without reading the full import graph.

## Current Code Structure

The package is split into small modules:

```text
python_import_graph.py
python_import_model.py
python_module_discovery.py
python_import_parser.py
python_import_resolution.py
python_import_reports.py
```

### `python_import_graph.py`

Command-line entry point and orchestration.

It discovers Python files, parses them, extracts imports, writes reports, and prints summary counts.

### `python_import_model.py`

Data classes for the import graph.

Current model objects:

```text
PythonModule
ImportEdge
```

### `python_module_discovery.py`

Repository and module discovery helpers.

It finds Python files under configured source roots and converts file paths into dotted module names.

### `python_import_parser.py`

AST parsing and import extraction.

It detects:

```text
if __name__ == "__main__"
top-level main functions
import statements
from-import statements
```

### `python_import_resolution.py`

Import resolution helpers.

It resolves relative imports and matches resolved module names against discovered project modules where possible.

### `python_import_reports.py`

CSV report generation.

It writes the raw evidence reports and the smaller review reports.

## What This Code Does Not Yet Do

The current introspection code does not identify generated file inputs or outputs.

It does not yet know:

```text
which modules are producers
which files a producer reads
which files a producer writes
which generated files are canonical
which outputs are site-facing inputs
which outputs are legacy
which generated files should be deleted
which Makefile rules should exist
```

Those questions belong to later phases of the audit.

The current package only establishes a mechanical code-import map.

## Relationship to Existing Makefile Docs

The initial project documentation for this work currently lives under:

```text
src/docs/makefile/
```

Those documents describe the broader generated-output dependency audit: vocabulary, workflow, classification terms, review checklists, and current open issues.

The current open issue is that those docs should move under `src/introspection/docs`, with a small `src/docs/makefile/README.md` left behind to point readers to the new location.

For now, someone trying to understand the approach should read:

```text
src/introspection/README.md
src/introspection/docs/Open Issues.md
src/docs/makefile/
```

## Working Interpretation

This package is the first implementation step in a larger reverse-engineering effort.

The intended path is:

```text
1. identify Python module import structure
2. identify likely runnable entry points
3. inspect entry points for data inputs and generated outputs
4. build a producer/input/output graph
5. classify outputs and modules
6. write a Makefile that can rebuild the deployable project state
```

The current code only addresses step 1 and provides evidence for step 2.

