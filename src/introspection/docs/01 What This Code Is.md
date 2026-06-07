# What This Code Is

## 1. Status

Draft.

This document is a reverse-engineered orientation note for the current `src.introspection` package.

It is not a complete requirements, specification, or design document. It records the current purpose and shape of the code well enough for someone cold on the project to understand why the package exists and where to look next.

## 2. Purpose

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

## 3. Immediate Problem

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

## 4. Current Implemented Tool

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

## 5. Output Reports

The tool currently writes four CSV reports.

Two reports are raw evidence:

```text
python_modules.csv
python_import_edges.csv
```

Two reports are smaller review surfaces:

```text
python_entry_candidates.csv
python_imported_main.csv
```

The raw reports should be treated as backing evidence. The smaller reports are intended to be read first by a human or LLM.

### 5.1 `python_modules.csv`

`python_modules.csv` has one row per discovered Python module.

It answers:

```text
What Python files exist under the scanned source roots?
Which dotted module name does each file correspond to?
Does the module expose a direct execution surface?
Is the module imported elsewhere in the project?
Which symbols are imported from it?
```

Current fields:

```text
module_path
module_name
has_main_guard
defines_main
parse_status
parse_error
imported_by_count
imported_by_modules
imported_symbols
main_imported_by_modules
non_main_imported_by_modules
```

Field meanings:

```text
module_path
  Repository-relative path to the Python file.

module_name
  Dotted project module name derived from the path.

has_main_guard
  True if the module has a top-level if __name__ == "__main__" guard.

  This means the module can be run directly. It does not prove that the module is a standalone program.

defines_main
  True if the module defines a top-level function named main.

parse_status
  ok if AST parsing succeeded; otherwise records a parse failure category.

parse_error
  Empty when parsing succeeds. Contains the syntax error text when parsing fails.

imported_by_count
  Number of discovered project modules that import this module.

imported_by_modules
  Semicolon-separated list of project modules that import this module.

imported_symbols
  Semicolon-separated list of symbols imported from this module by from-import syntax.

main_imported_by_modules
  Semicolon-separated list of project modules that import main from this module.

non_main_imported_by_modules
  Semicolon-separated list of project modules that import at least one non-main symbol from this module.
```

This report is the main summary table for distinguishing likely support modules from likely standalone modules.

### 5.2 `python_import_edges.csv`

`python_import_edges.csv` has one row per syntactic import edge.

It answers:

```text
Which module contains the import?
What exact module text appeared in the import statement?
Was the import absolute or relative?
Was the import an import statement or from-import statement?
Which project module/path did the import resolve to, if any?
```

Current fields:

```text
importer_path
importer_module
import_style
imported_module_text
imported_symbol
imported_alias
level
is_relative
resolved_module
resolved_path
resolved_symbol_module
resolved_symbol_path
resolution_status
```

Field meanings:

```text
importer_path
  Repository-relative path to the module containing the import.

importer_module
  Dotted project module name of the module containing the import.

import_style
  import for import x; from for from x import y.

imported_module_text
  The module text written in the import statement.

imported_symbol
  The imported symbol for from-import statements. Empty for plain import statements.

imported_alias
  The local alias if the import used as. Empty otherwise.

level
  Relative import level as reported by the AST. Zero means absolute import.

is_relative
  True when level is non-zero.

resolved_module
  Best-effort resolved dotted module name.

resolved_path
  Repository-relative path if resolved_module matches a discovered project module.

resolved_symbol_module
  For from-import statements, populated when the imported symbol itself resolves as a submodule.

resolved_symbol_path
  Repository-relative path for resolved_symbol_module, when known.

resolution_status
  Coarse resolution label: resolved_module, resolved_symbol_module, unresolved_project_module, or external_or_stdlib.
```

This is the raw backing evidence for the import graph. It may be large and is not expected to be the main review document.

### 5.3 `python_entry_candidates.csv`

`python_entry_candidates.csv` has one row per module with a `__main__` execution surface.

It answers:

```text
Which modules can be run directly?
Are those modules imported elsewhere?
Are they imported through main or through non-main symbols?
What first-pass role does the import evidence suggest?
```

Current fields:

```text
module_path
module_name
defines_main
imported_by_count
imported_by_modules
main_imported_by_modules
non_main_imported_by_modules
candidate_role
needs_review
```

Field meanings:

```text
module_path
  Repository-relative path to the runnable module.

module_name
  Dotted project module name.

defines_main
  True if the module defines a top-level main function.

imported_by_count
  Number of discovered project modules that import this runnable module.

imported_by_modules
  Semicolon-separated list of project modules that import this runnable module.

main_imported_by_modules
  Semicolon-separated list of project modules that import main from this runnable module.

non_main_imported_by_modules
  Semicolon-separated list of project modules that import non-main symbols from this runnable module.

candidate_role
  First-pass role label derived from the import evidence.

needs_review
  True when the first-pass role is not mechanically safe enough to interpret without human inspection.
```

Current candidate role labels:

```text
standalone_entry_candidate
  The module has a __main__ guard and is not imported by other scanned project modules.

runnable_support_candidate
  The module has a __main__ guard and non-main symbols are imported elsewhere.

main_imported_needs_review
  The module has a __main__ guard and main is imported elsewhere.

runnable_imported_candidate
  The module has a __main__ guard and is imported elsewhere, but the evidence does not fit a narrower label.
```

This is the primary report for the current entry-point investigation.

### 5.4 `python_imported_main.csv`

`python_imported_main.csv` has one row per import of the form:

```text
from x import main
```

It answers:

```text
Where is main imported as a symbol?
Which module does that import resolve to?
Is this a package execution wrapper, deployment orchestration, or suspicious API boundary?
```

Current fields:

```text
importer_path
importer_module
imported_module_text
resolved_module
resolved_path
resolution_status
```

Field meanings:

```text
importer_path
  Repository-relative path to the module importing main.

importer_module
  Dotted project module name of the module importing main.

imported_module_text
  The module text written in the from-import statement.

resolved_module
  Best-effort resolved dotted module name that main was imported from.

resolved_path
  Repository-relative path for resolved_module, when it is a discovered project module.

resolution_status
  Coarse resolution label for the import.
```

This report exists because `main` is often an unhelpful API name. Importing it may be harmless, but it should be visible.

Expected harmless or low-concern cases include:

```text
__main__.py imports main from cli.py
```

Cases that need interpretation include:

```text
publisher imports main from deploy
```

where `deploy` generally means copying web files to server targets, and may be deliberate orchestration rather than a reusable API boundary.

## 6. What the Tool Records Internally

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

## 7. Current Code Structure

The package is split into small modules:

```text
python_import_graph.py
python_import_model.py
python_module_discovery.py
python_import_parser.py
python_import_resolution.py
python_import_reports.py
```

### 7.1 `python_import_graph.py`

Command-line entry point and orchestration.

It discovers Python files, parses them, extracts imports, writes reports, and prints summary counts.

### 7.2 `python_import_model.py`

Data classes for the import graph.

Current model objects:

```text
PythonModule
ImportEdge
```

### 7.3 `python_module_discovery.py`

Repository and module discovery helpers.

It finds Python files under configured source roots and converts file paths into dotted module names.

### 7.4 `python_import_parser.py`

AST parsing and import extraction.

It detects:

```text
if __name__ == "__main__"
top-level main functions
import statements
from-import statements
```

### 7.5 `python_import_resolution.py`

Import resolution helpers.

It resolves relative imports and matches resolved module names against discovered project modules where possible.

### 7.6 `python_import_reports.py`

CSV report generation.

It writes the raw evidence reports and the smaller review reports.

## 8. What This Code Does Not Yet Do

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

## 9. Relationship to Existing Makefile Docs

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

## 10. Working Interpretation

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
