# SDDA Entrypoint Index

This package builds a repository-wide index of Python modules to support human review of real entrypoints.

## Purpose

The objective is to make it easy to see which executable modules are likely to be real entrypoints and which executable modules are imported by other code and therefore need human review.

This package does not try to prove authorial intent.

## Terminology

A **library module** is a Python module whose module body is declarative only.

For the first implementation, declarative top-level statements are limited to:

```text
import
from ... import ...
def
async def
class
module docstring
pass
```

A **program** is any Python module whose module body contains any non-declarative statement.

Assignments are non-declarative. This is deliberately conservative: SDDA does not try to prove whether a top-level statement is semantically harmless.

A **standalone program** is a program that is not imported by any other indexed module.

An **imported program** is a program that is imported by at least one other indexed module. Imported programs are the main review queue: a human should decide whether they are real pipeline entrypoints or library-like modules with convenient executable code.

## Invocation

```powershell
python -m sdda.entrypoints --import-root .
```

By default reports are written to:

```text
files/output/sdda/entrypoints/
```

## Reports

```text
module_index.csv
programs.csv
standalone_programs.csv
imported_programs.csv
library_modules.csv
program_evidence.csv
module_references.csv
summary.md
```
