# SDDA Status Report

## Status

Working status report for the first SDDA implementation slice.

SDDA is now implemented as a small package under the top-level `sdda` project. It is independent of `src/introspection` and is invoked through:

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

The current implementation does not yet answer that final question. It produces the raw evidence needed to move toward it.

## Implemented slice

The current code implements this vertical slice:

```text
module index
  -> reachable import graph
  -> scope extraction
  -> raw file-use extraction
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
unresolved.csv
summary.md
```

The latest run against `src.products.make_site2.__main__` produced:

```text
Project modules indexed: 1099
Reachable modules: 68
Import records: 646
Scopes: 560
File uses: 106
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
glob.glob(...)
os.makedirs(...)
os.path.exists(...)
shutil.copy...
shutil.rmtree(...)
requests...
os.environ[...] and os.getenv(...)
```

Literal open modes are now used to distinguish obvious reads from obvious writes.

The unresolved report has been reduced from broad call noise to a more useful review set. It now mostly represents the known limitation around object or project method dispatch.

## Known limitation

The major known limitation is unresolved method calls of the form:

```python
obj.method(...)
```

Such methods may hide important file uses.

Trying to solve object method dispatch in the abstract may be slower than first building the downstream file-family analysis. The current evidence may already be sufficient to identify the file-family questions that matter most, and that analysis may show which unresolved method calls actually block progress.

For now, method-call uncertainty is preserved in `unresolved.csv` rather than hidden.

## Current interpretation

Milestone 1, module and import evidence, is good enough for now.

Milestone 2, scope-level file-use evidence, is also good enough for now.

The current reports are not the final dependency answer. They are an evidence layer from which later reports can derive file families, action groups, candidate distribution inputs, generated outputs, caches, and review items.

## Next steps

There are two candidate next steps.

The first candidate is to stop and resolve object method dispatch now.

The second candidate is to continue downstream from the current evidence and implement file-family normalisation and grouping, then return to object method dispatch where that downstream analysis shows it matters.

We will take the second candidate: continue downstream with file-family normalisation and grouping.
