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

The current implementation does not yet answer that final distribution question. It produces a useful evidence layer, grouped file families, first-pass classifications, and conservative distribution candidate decisions.

## Implemented slice

The current code implements this vertical slice:

```text
module index
  -> reachable import graph
  -> scope extraction
  -> raw file-use extraction
  -> path-constant and local-alias normalisation
  -> file-family normalisation and grouping
  -> first-pass file-family classification
  -> first-pass distribution candidate decisions
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
file_family_classification.csv
distribution_candidates.csv
unresolved.csv
summary.md
```

The latest run against `src.products.make_site2.__main__` produced:

```text
Project modules indexed: 1104
Reachable modules: 68
Import records: 646
Scopes: 560
File uses: 120
File families: 92
File family evidence rows: 120
File family classifications: 92
Distribution candidates: 92
Unresolved records: 168
```

The latest distribution decision summary is:

```text
exclude: 54
review: 31
include: 7
```

The current include candidates are:

```text
files/output/bcr/data/banzuke_change_report.csv
files/output/bcr/site_config.json
files/output/misc/finish_by_chii_1958_2026_bottom_thresholds.csv
files/output/misc/finish_by_chii_1958_2026_top_thresholds.csv
files/output/standings/publisher/latest_data/site_config.json
src/analysis/standings/files/full_shiks.pkl
src/products/make_site2/runtime/site.css
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

Copy operations produce separate source/read and destination/write evidence rows.

Path-style method calls generally record the receiver expression rather than the method expression.

Simple local names in file-family patterns are scoped by module and scope to avoid collapsing unrelated variables such as `path` into one false family.

Path constants are resolved for common `Path(__file__).resolve().parent`-style constants and imported uppercase constants. This is enough to turn rows such as `LEGACY_QUALIFIED_SHIKONA` into concrete repository-relative paths.

Simple same-scope path aliases are resolved where the assignment is straightforward, such as `source_root = Path("files") / "output" / "misc"`.

The classifier is conservative. It now avoids treating broad variable globs, deploy-only reads, non-root helper `main()` reads, unresolved parameters, unresolved locals, and object-field reads as definite source-distribution inputs.

The `summary.md` report now gives enough information for first-pass review without opening the CSVs: counts, decision breakdowns, classification breakdowns, include candidates, and high-priority review candidates.

## Known limitations

The major known limitation is still unresolved method calls of the form:

```python
obj.method(...)
```

Such methods may hide important file uses. For now, method-call uncertainty is preserved in `unresolved.csv` rather than hidden.

The more immediate limitation exposed by the current reports is value flow. SDDA does not yet connect expressions such as:

```text
source_path
producer_output.data_path
output_root
BuildOutput.root
build_output.root
```

across function calls, return objects, and dataclass fields.

Because of that, some rows are correctly placed in review rather than include/exclude. Examples include parameter reads in helper functions, object-field reads, and deployment reads that probably consume build output.

Two attempted loop-alias changes intended to resolve `/name` rows were reverted because they had no visible effect and affected only two review rows. This is not a strategic blocker.

## Current interpretation

Milestone 1, module and import evidence, is good enough for now.

Milestone 2, scope-level file-use evidence, is good enough for now.

Milestone 4, file-family normalisation, classification, and first-pass distribution candidate reporting, is now good enough for this stage.

The current reports are not the final dependency answer. They are a conservative evidence layer from which later reports can derive candidate distribution inputs, generated outputs, caches, deployment assumptions, and review items.

The current break-point is reasonable because the remaining high-priority review rows mostly require a new analysis layer rather than more local classification tweaks.

## Next steps

The next major step is call-argument and value-flow matching.

The aim is to match producer and consumer expressions across the website pipeline, for example:

```text
build_site writes output_root
build_site returns BuildOutput(root=output_root)
__main__ passes build_output into deploy_local and deploy_remote
deploy reads build_output.root
```

This should allow SDDA to recognise pipeline intermediates more directly:

```text
generated_then_consumed / pipeline_intermediate
```

and avoid leaving those rows as high-priority review items.

Do not prioritise further small alias cleanups unless they affect more than a handful of rows or block the value-flow work.