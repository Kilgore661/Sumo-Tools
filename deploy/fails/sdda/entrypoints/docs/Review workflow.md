# SDDA Entrypoint Review Workflow

This document describes how to use the output from `sdda.entrypoints`.

The tool produces machine classifications and a review form. The final decision about true entrypoints is made by a human reviewer.

## 1. Run the indexer

From the repository root:

```powershell
python -m sdda.entrypoints --import-root .
```

For a narrower folder:

```powershell
python -m sdda.entrypoints --import-root .\src\infra\get_bios\
```

Each import root writes to its own output folder:

```text
files/output/sdda/entrypoints/<import-root-name>/
```

## 2. Start with `summary.md`

Read the module type accounting first.

Example shape:

```text
total_modules: 12

library_modules: 3

programs: 9
  standalone_programs: 7
    command_like: 6
    weak_entrypoint_signal: 1
  imported_programs_needing_review: 2
    probable_library_modules: 1
    possible_entrypoints: 1
```

This is the partition of indexed modules used for review.

`standalone_programs` means programs with no observed inbound syntactic imports from other modules inside the import root. It does not mean confirmed entrypoints.

## 3. Check resolution notes and warnings

Open `warnings.csv` if the summary reports notes or warnings.

Severity `note` usually records an intentional resolution. For example, when a narrow import root is used, an absolute import such as:

```python
from src.infra.get_bios.parser import parse_top_fields
```

may be resolved to the local indexed module:

```text
parser
```

Severity `warning` means the machine saw something that may affect classification and needs review.

Do not record final conclusions until warnings have been considered.

## 4. Open `entrypoint_review_form.md`

The review form is the main working document.

It contains:

```text
machine-written context
overall human conclusion
standalone programs / probable entrypoint candidates
imported programs needing review
```

The form deliberately includes blank checkboxes and comment fields.

## 5. Review standalone programs

Standalone programs are probable entrypoint candidates.

The standalone-program classification is a statement about the import graph inside the import root:

```text
program with no observed inbound syntactic imports from other indexed modules
```

It is not a conclusion about intent.

Standalone programs have a command-shape subtype:

```text
command_like
weak_entrypoint_signal
```

`command_like` means the module is `__main__.py` or has a main guard.

`weak_entrypoint_signal` means the module is neither `__main__.py` nor guarded by `if __name__ == "__main__":`.

For each standalone program, decide whether it is:

```text
reviewed as true entrypoint
reviewed as not a true entrypoint
still unclear
```

Useful questions:

* Is this module intended to be run by a user or pipeline?
* Is it a package `__main__.py`?
* Does it have a main guard?
* Does it parse CLI arguments?
* Does it read or write durable data files?
* Is it only a probe, demonstration, or manual check?
* If it has weak entrypoint signal, is there other evidence that it is intentionally runnable?

A probe may still be a true entrypoint if it is deliberately runnable. The reviewer should decide whether the review is about all runnable commands or only production pipeline commands.

## 6. Review imported programs

Imported programs are executable modules that are imported by other indexed modules.

For each one, decide whether it is:

```text
reviewed as library-like module
reviewed as real entrypoint
reviewed as obsolete / ignore
still unclear
```

Useful questions:

* What imports this module?
* Is the imported functionality the main purpose of the file?
* Is the executable part only a test/demo/probe?
* Does the module have a `main` guard?
* Does it have top-level executable code after the final function?

Imported programs with subtype `probable_library` are likely to be library-like, but the subtype is only a hint.

## 7. Use CSVs when something is surprising

The form is a distillation of the CSV files, but the CSVs are useful for audit.

Use:

```text
module_references.csv
```

to inspect which import statements caused a module to be considered imported.

Use:

```text
program_evidence.csv
```

to see all non-declarative evidence, not just the first item shown in the form.

Use:

```text
module_index.csv
```

for sorting, filtering, or checking the complete partition.

## 8. Remember the scope assumptions

The import root is treated as the closed universe for reference analysis.

The tool does not look for inbound imports from outside the import root.

The tool does not detect dynamic imports.

The tool assumes relevant module relationships are expressed as ordinary syntactic imports:

```text
import ...
from ... import ...
```

## 9. Record the overall conclusion

After reviewing individual modules, complete the top section of the form:

```text
Conclusion
True entrypoints
Modules reviewed as library-like
Modules still unclear
```

The conclusion should state the import root and the reviewed result plainly.

For example:

```text
This folder has one true entrypoint: `__main__`.
The imported programs `classifier` and `module_index` were reviewed as library-like helper modules.
```

## 10. Preserve reviewed forms

Generated output under `files/output/...` is not durable source documentation.

If a reviewed form captures useful project knowledge, copy it into a checked-in documentation location, for example:

```text
sdda/entrypoints/docs/entrypoint_review_form_reviewed.md
```

or a package-specific docs folder near the reviewed code.

## 11. Re-run after code changes

The review is tied to the code at the time it was generated.

After code changes, re-run the tool and compare the new report against the reviewed form.

Pay particular attention to:

* new programs;
* programs that changed from standalone to imported;
* standalone programs that changed command-shape subtype;
* imported programs that changed subtype;
* new warnings;
* removed modules that were previously reviewed.
