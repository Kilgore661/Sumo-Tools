# SDDA Entrypoint Index

`SDDA Entrypoint Index` scans a Python import root and writes reports that help a human decide which modules are real entrypoints.

It is deliberately conservative. It does not try to prove author intent; it builds a review queue.

## Run

```powershell
python -m sdda.entrypoints --import-root .
```

For a narrower import root:

```powershell
python -m sdda.entrypoints --import-root .\src\infra\get_bios\
```

Reports are written under an import-root-specific output directory:

```text
files/output/sdda/entrypoints/<import-root-name>/
```

For example:

```text
files/output/sdda/entrypoints/src_infra_get_bios/
```

## Main outputs

```text
summary.md
entrypoint_review_form.md
module_index.csv
programs.csv
standalone_programs.csv
imported_programs.csv
library_modules.csv
dependency_atoms.csv
program_atoms.csv
library_atoms.csv
program_evidence.csv
module_references.csv
warnings.csv
```

Start with `summary.md`, then fill in `entrypoint_review_form.md` after human review.

The atom reports are quick graph leaves: indexed modules with no observed outgoing local module references. `program_atoms.csv` and `library_atoms.csv` split those leaves by module kind.

## Read next

The fuller design and review process are documented in:

```text
sdda/entrypoints/docs/Design.md
sdda/entrypoints/docs/Review workflow.md
```
