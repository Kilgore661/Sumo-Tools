# SDDA Status Report

## Status

Working status report for the current SDDA implementation slice.

SDDA is implemented as a small package under the top-level `sdda` project. It is independent of `src/introspection` and is invoked through:

```powershell
python -m sdda src.products.make_site2.__main__ --import-root .
```

The current implementation writes generated reports under:

```text
files/output/sdda/src.products.make_site2.__main__/
```

These outputs are local generated evidence and are not normally committed.

## Purpose

The purpose of SDDA is to support a source distribution of the Sumo-Tools website product.

The exact set of runtime inputs needed by `make_site2` is not computable in general. The practical target is therefore a conservative static may-use account:

```text
Which file families, URL families, environment settings, and local assumptions may be needed by the website build/deploy product?
```

The current implementation does not yet answer that final distribution question. It now produces a useful evidence layer and a first normalised file-family layer from which classification can begin.

## Implemented slice

The current code implements this vertical slice:

```text
module index
  -> reachable import graph
  -> scope extraction
  -> raw file-use extraction
  -> file-family normalisation and grouping
  -> unresolved-call evidence
  -> CSV and Markdown reports
```

The generated reports currently include:

```text
module_index.csv
imports.csv
module_graph.csv
scopes.csv
file_uses.csv
file_families.csv
file_family_evidence.csv
unresolved.csv
summary.md
```

The latest run against `src.products.make_site2.__main__` produced:

```text
Project modules indexed: 1100
Reachable modules: 68
Import records: 646
Scopes: 560
File uses: 120
File families: 92
File family evidence rows: 120
Unresolved records: 168
```

## What looks good

The module and import evidence is stable across recent runs.

The scope-level file-use evidence is useful enough for downstream analysis. It records common filesystem, URL, and environment operations, including:

```text
open(...)
Path.open(...)
Path.read_text(...)
Path.write_text(...)
Path.exists(...)
Path.mkdir(...)
Path.glob(...)
Path.rglob(...)
glob.glob(...)
os.makedirs(...)
os.path.exists(...)
shutil.copy...
shutil.rmtree(...)
requests...
os.environ[...] and os.getenv(...)
```

Literal open modes are used to distinguish obvious reads from obvious writes.

Copy operations now produce separate source/read and destination/write evidence rows.

Path-style method calls now generally record the receiver expression rather than the method expression.

Simple local names in file-family patterns are scoped by module and scope to avoid collapsing unrelated variables such as `path` into one false family.

Directory-creation evidence is classified as `directory_family`.

The unresolved report has been reduced from broad call noise to a more useful review set. It now mostly represents the known limitation around object or project method dispatch.

## Known limitation

The major known limitation is unresolved method calls of the form:

```python
obj.method(...)
```

Such methods may hide important file uses.

Trying to solve object method dispatch in the abstract may be slower than first building downstream classification. The current evidence may already be sufficient to identify which file-family questions matter most, and that analysis may show which unresolved method calls actually block progress.

For now, method-call uncertainty is preserved in `unresolved.csv` rather than hidden.

## Current interpretation

Milestone 1, module and import evidence, is good enough for now.

Milestone 2, scope-level file-use evidence, is good enough for now.

The first part of Milestone 4, file-family normalisation and grouping, is also good enough to support the next downstream step.

The current reports are not the final dependency answer. They are an evidence layer from which later reports can derive candidate distribution inputs, generated outputs, caches, deployment assumptions, and review items.

## Next steps

The next step is first-pass file-family classification.

Implement a conservative classifier that reads the grouped file-family evidence and emits:

```text
file_family_classification.csv
```

The first classifier should use simple, reviewable labels such as:

```text
required_distribution_input
generated_output
possible_efficiency_cache
possible_state_or_control_file
directory_family
environment_setting
internet_source
unknown_review_needed
```

The initial rule should be conservative:

```text
families with only read or observe evidence are candidate inputs
families with only write/create/delete evidence are generated outputs or generated directories
families with both read/observe and write evidence are possible efficiency caches or possible state/control files
environment settings remain environment settings
URL families remain internet sources
low-confidence expression families remain unknown_review_needed
```

After the first classification report exists, review it against the source-distribution goal and use it to decide whether unresolved `obj.method(...)` calls need immediate attention.
