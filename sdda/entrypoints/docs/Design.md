# SDDA Entrypoint Index Design

This document describes the design of `sdda.entrypoints`.

The tool is intended to support human review. It does not decide authorial intent. It scans Python modules, classifies them conservatively, records evidence, and generates reports that help a reviewer decide which programs are real entrypoints.

## Goal

Given an import root, produce an accounting of all Python modules under that root:

```text
all indexed modules
├── library modules
└── programs
    ├── standalone programs
    │   ├── command-like
    │   └── weak entrypoint signal
    └── imported programs needing review
        ├── probable library modules
        └── possible entrypoints
```

The output should make it easy to answer questions such as:

* How many modules are in this import root?
* Which modules are purely library-like?
* Which modules are executable programs?
* Which programs have no observed inbound syntactic imports from other indexed modules?
* Which standalone programs look command-like?
* Which standalone programs have weak entrypoint evidence?
* Which executable modules are imported by other modules and therefore need human review?
* After review, what are the true entrypoints for this import root?

## Scope assumptions

The import root is treated as the closed universe for reference analysis.

For example, if the command is:

```powershell
python -m sdda.entrypoints --import-root .\src
```

then the tool indexes modules under `src` and records references between those indexed modules.

The tool does not look for inbound imports from outside the import root.

The tool does not detect dynamic imports such as `importlib.import_module(...)`, string-based plugin loading, or shell commands that run `python -m ...`.

The analysis assumes relevant module relationships are expressed as ordinary syntactic imports:

```text
import ...
from ... import ...
```

## Terminology

### Library module

A library module is a Python module whose module body is declarative only.

The current implementation treats these top-level statements as declarative:

```text
import
from ... import ...
def
async def
class
module docstring
pass
```

### Program

A program is any Python module whose module body contains non-declarative top-level code.

Assignments are non-declarative. This is deliberate. The tool does not try to prove that a top-level assignment is semantically harmless.

For example, this is a program under the current rule:

```python
CONSTANT = 7

def f(x):
    return x + CONSTANT
```

That may be library-like after human review, but the machine classification remains conservative.

### Standalone program

A standalone program is a program with no inbound syntactic references from other indexed modules.

This is a topological statement about the indexed import graph. It does not mean the module is a confirmed command, and it does not prove that the module is not library-like.

In the generated review form, standalone programs are treated as probable entrypoint candidates.

### Command-like standalone program

A command-like standalone program is a standalone program that either:

* is `__main__.py`; or
* has a main guard such as `if __name__ == "__main__":`.

This is stronger evidence that the module is intentionally runnable, but it is still a review hint rather than proof.

### Weak-entrypoint-signal standalone program

A weak-entrypoint-signal standalone program is a standalone program that is neither `__main__.py` nor guarded by `if __name__ == "__main__":`.

It may still be a real entrypoint, but the machine has weaker evidence that it is intentionally runnable. It may also be old script code, dead code, or library-like code with top-level setup.

### Imported program

An imported program is a program that is imported by at least one other indexed module.

Imported programs need review because they may be:

* real entrypoints that are also imported by other code;
* library-like modules with constants or setup code;
* modules with a small `if __name__ == "__main__"` section for local testing;
* probes or obsolete scripts.

### Probable library module

An imported program with subtype `probable_library` has no non-declarative top-level code after its final top-level function.

This is a review hint only. It does not prove the module is a library.

### Possible entrypoint

An imported program counted as `possible_entrypoint` does not have the `probable_library` hint.

These modules are usually higher-priority review items because they have executable top-level code after their final function, or a shape that does not look like a simple library-like helper.

## Waterfall account of the implementation

### 1. Build the module index

The first stage walks the import root and indexes Python files.

Each indexed module records:

```text
module name
source path
whether it is __main__.py
```

The import root determines the local module names used by the report. For example, when running:

```powershell
python -m sdda.entrypoints --import-root .\src\infra\get_bios\
```

local module names include:

```text
__main__
parser
api
shikona_normalisation_probe
```

rather than fully qualified names such as:

```text
src.infra.get_bios.parser
```

### 2. Parse and classify each module body

Each Python file is parsed with `ast`.

The classifier examines the module body and records non-declarative top-level evidence.

If there is no evidence, the module is a `library_module`.

If there is evidence, the module is a `program`.

The evidence is written to `program_evidence.csv` and includes the line number, statement kind, and reason.

### 3. Extract references between indexed modules

The reference extractor walks imports and records references from one indexed module to another.

The main output is `module_references.csv`.

Reference extraction is intentionally limited to syntactic imports. It does not attempt to resolve dynamic imports, runtime plugin loading, string-based imports, or indirect execution.

### 4. Resolve imports for narrowed import roots

A common pattern in this repository is to run the tool on a narrow import root while source files still use absolute imports from the repository root.

For example, if the import root is:

```text
src\infra\get_bios
```

then the local module index may contain:

```text
shikona_normalisation_probe_intai
```

but the source code may say:

```python
from src.infra.get_bios.shikona_normalisation_probe_intai import try_fix_missing_intai
```

The resolver handles this by stripping the import-root package prefix when it can resolve the remaining local module name uniquely through the indexed module table.

These resolutions are written to `warnings.csv` with severity `note` and kind `import_root_relative_resolution`. They are audit notes, not errors.

If an import appears to start with the import-root package but cannot be resolved to an indexed local module, it is written with severity `warning`.

### 5. Classify programs by incoming references

After references are extracted, each program is classified as:

```text
standalone_program
imported_program
```

A program with no inbound references from other indexed modules is a `standalone_program`.

A program with at least one inbound reference is an `imported_program`.

This classification is relative to the import root. It does not consider imports from outside the import root and does not consider dynamic imports.

### 6. Add review hints

Standalone programs receive a command-shape subtype:

```text
command_like
weak_entrypoint_signal
```

`command_like` means the standalone program is either `__main__.py` or has a main guard.

`weak_entrypoint_signal` means the standalone program has neither signal.

Imported programs receive a subtype:

```text
probable_library
review
```

The generated reports present imported-program subtype `review` as `possible_entrypoints` in the accounting section.

All subtypes are based on syntax only. They are not proof of intent.

### 7. Write reports

The tool writes a small report bundle under:

```text
files/output/sdda/entrypoints/<import-root-name>/
```

The key files are:

```text
summary.md
entrypoint_review_form.md
module_index.csv
programs.csv
standalone_programs.csv
imported_programs.csv
library_modules.csv
program_evidence.csv
module_references.csv
warnings.csv
```

### 8. Human review records conclusions

The generated `entrypoint_review_form.md` is a working document.

A reviewer should inspect the probable entrypoints, imported programs, resolution notes, and source code as needed, then record conclusions in the form.

Reviewed forms that represent durable human judgement should be copied into `sdda/entrypoints/docs/` or another checked-in documentation location.

## What the tool does not do

The tool does not prove whether a module is intended to be run.

It does not detect every possible runtime relationship between modules.

It does not look outside the import root for inbound imports.

It does not detect dynamic imports.

It does not know whether a runnable probe is part of a production pipeline.

It does not know whether a `main` section exists for testing, demonstration, diagnostics, or production use.

These are human review decisions.

## Design principle

The tool should be conservative and explicit.

When it is unsure, it should generate review material rather than silently guessing.

When it performs a non-obvious resolution, such as resolving an absolute import inside a narrowed import root, it should record that fact in `warnings.csv` as a note or warning.
