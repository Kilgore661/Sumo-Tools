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

SDDA is still not a full execution-slice analyser. It is currently an import-reachability based evidence pipeline with increasingly useful value-flow and provenance layers.

## Current run shape

Recent observed run against `src.products.make_site2.__main__`:

```text
Project modules indexed: 251
Reachable modules: 68
Import records: 646
Scopes: 560
Type facts: 1213
Value facts: 126
Field facts: 171
File uses: 120
File use resolutions: 2
Producer outputs: 2
Unresolved records: 168
```

The historic `Project modules indexed: 1104` count was caused by indexing `.venv`. That is no longer the expected shape after `.venv` was excluded.

## Implemented analysis pipeline

The current code implements this vertical slice:

```text
module index
  -> reachable import graph
  -> scope extraction
  -> type facts
  -> value facts
  -> field facts
  -> call argument bindings
  -> parameter field provenance
  -> parameter file provenance
  -> file-use resolution
  -> producer output provenance
  -> path-constant and local-alias normalisation
  -> file-family normalisation and grouping
  -> file-family classification
  -> distribution candidate decisions
  -> review candidate report
  -> unresolved-call evidence
  -> CSV and Markdown reports
```

The generated reports currently include:

```text
module_index.csv
imports.csv
module_graph.csv
scopes.csv
type_facts.csv
value_facts.csv
field_facts.csv
call_argument_bindings.csv
parameter_field_provenance.csv
parameter_file_provenance.csv
file_uses.csv
file_use_resolution.csv
producer_return_bindings.csv
producer_write_bindings.csv
producer_outputs.csv
file_families.csv
file_family_evidence.csv
file_family_classification.csv
distribution_candidates.csv
review_candidates.csv
unresolved.csv
summary.md
```

`review_candidates.csv` is now the main triage report. It joins distribution, classification, family, and first-evidence data into one view.

## What looks good

The module and import evidence is stable across recent runs.

The scope-level file-use evidence is useful enough for downstream analysis. It records common filesystem, URL, and environment operations, including:

```text
open(...)
Path.open(...)
Path.read_text(...)
Path.write_text(...)
Path.write_bytes(...)
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

Simple same-scope path aliases are resolved where the assignment is straightforward.

The classifier is conservative. It avoids treating broad variable globs, deploy-only reads, non-root helper `main()` reads, unresolved parameters, unresolved locals, and object-field reads as definite source-distribution inputs unless a later provenance layer provides stronger evidence.

## Implemented value-flow and provenance improvements

### Dataclass and value facts

SDDA now records class/dataclass definitions, dataclass fields, function parameter annotations, function return annotations, and selected local value facts from annotated calls.

An important correction was made to class/dataclass type facts: class rows now use the actual class full name rather than only the containing module name. This enabled constructor-return matching such as `MasterDataOutput(...)`.

### Field facts

SDDA now resolves object field reads where the receiver has an inferred dataclass type. Examples include:

```text
producer_output.data_path
producer_output.report_path
build_output.root
build_output.file_count
```

### Producer output provenance

SDDA now emits:

```text
producer_return_bindings.csv
producer_write_bindings.csv
producer_outputs.csv
```

This proves the important `write_master_data()` case:

```text
write_master_data()
  writes data_path/report_path
  returns MasterDataOutput(data_path=data_path, report_path=report_path)

build_career_comparisons_data_output()
  producer_output = write_master_data(...)
  reads producer_output.data_path/report_path
```

The resulting classification is:

```text
producer_output.data_path   generated_then_consumed -> exclude, low review
producer_output.report_path generated_then_consumed -> exclude, low review
```

### Call argument bindings

SDDA now emits:

```text
call_argument_bindings.csv
```

This connects call-site arguments to annotated callee parameters. For example, `main` passing `build_output` into deployment functions is now visible:

```text
main -> deploy_local(build_output, deployment_config)
main -> deploy_remote(build_output, deployment_config)
```

The `build_output` argument may come from both:

```text
src.products.make_site2.build.build_site
src.products.make_site2.deploy.build_output_from_existing
```

### Parameter field provenance

SDDA now emits:

```text
parameter_field_provenance.csv
```

This connects field reads inside a callee back to the caller-side argument source. The main useful case is:

```text
deploy_local/deploy_remote read build_output.root
```

SDDA now distinguishes both branches:

```text
build_output <- build_site(...)
  build_output.root is a generated output tree

build_output <- build_output_from_existing(args.output)
  build_output.root is an externally supplied existing output tree
```

The resulting classification is:

```text
build_output.root/**/* mode_dependent_deployment_source -> review, medium priority
```

This is intentionally conservative because `--no-build` mode requires the output tree to already exist.

### Parameter file provenance

SDDA now emits:

```text
parameter_file_provenance.csv
```

This connects direct file-use parameters inside helper functions back to call-site arguments.

The direct path-expression case is now handled for `copy_single_csv_chart_data_output:source_path`. Examples include:

```text
DIVISION_STABILITY_SOURCE_ROOT / 'persistence.csv'
FIRST_CHII_APPEARANCE_SOURCE_ROOT / 'appearances.csv'
RANK_AT_RETIREMENT_SOURCE_ROOT / 'distribution.csv'
TYPICAL_EQUELO_VALUES_SOURCE_ROOT / 'typical_equelo_values.csv'
BANZUKE_DIVISION_BY_ERA_SOURCE_ROOT / 'divisions.csv'
MAKUUCHI_RANK_BY_ERA_SOURCE_ROOT / 'ranks.csv'
```

The resulting classification is:

```text
copy_single_csv_chart_data_output:source_path required_distribution_input -> low review
```

Iterator-derived parameter provenance is handled for `copy_standings_source_file:source_path`, from this source pattern:

```python
copy_standings_source_file(source_path, route_data_root)
for source_path in sorted(STANDINGS_SOURCE_ROOT.iterdir())
if source_path.name.startswith("multiple basho standings view ")
and source_path.suffix in {".csv", ".json"}
```

The current emitted iterator family is:

```text
files/output/standings/publisher/latest_data/**
```

The resulting classification is:

```text
copy_standings_source_file:source_path required_distribution_input -> low review
```

Local-alias-derived parameter provenance is also handled for deployment helper calls. For example:

```python
for source in build_output.root.rglob("*"):
    if source.is_file():
        copy_file(source, target)
```

SDDA now records:

```text
copy_file:source <- build_output.root/**/*
```

and inherits the mode-dependent deployment-source classification:

```text
copy_file:source mode_dependent_deployment_source -> review, medium priority
```

### Loop-variable aliasing

Simple literal filename tuples and loop variables from `zip(...)` are now resolved.

The following former high-priority `name` rows have been collapsed:

```text
files/output/career_length/site/career_length_1958_01_to_2026_05/name
files/output/probability/matchups/site/win_probability_by_standing/name
```

They no longer appear as high-priority unknown variable path segments.

Simple glob/rglob loop aliases are also now resolved. This handles the browser runtime copy loop:

```python
for source_path in RUNTIME_MODULE_SOURCE_ROOT.rglob("*"):
```

which now becomes:

```text
src/products/make_site2/runtime/site-refactor/**/* required_distribution_input -> low review
```

## Current make_site2 classification highlights

Closed or improved direct `make_site2` cases:

```text
producer_output.data_path
  generated_then_consumed
  exclude
  low review

producer_output.report_path
  generated_then_consumed
  exclude
  low review

build_output.root/**/*
  mode_dependent_deployment_source
  review
  medium review

copy_file:source
  mode_dependent_deployment_source
  review
  medium review

src/products/make_site2/runtime/site-refactor/**/*
  required_distribution_input
  include
  low review

copy_single_csv_chart_data_output:source_path
  required_distribution_input
  include
  low review

copy_standings_source_file:source_path
  required_distribution_input
  include
  low review
```

As of the latest checked output, there are no remaining high-priority review rows from direct `make_site2` build/deploy logic.

Confirm with:

```powershell
Import-Csv files\output\sdda\src.products.make_site2.__main__\review_candidates.csv |
  Where-Object { $_.review_priority -eq "high" } |
  Select-Object family_pattern, classification, classification_reason, first_module, first_scope, first_line, first_resolved_expression |
  Format-Table -AutoSize
```

The remaining high-priority rows should be imported helper/analysis APIs rather than direct `make_site2` build/deploy logic:

```text
src.analysis.equelo.expt1.params:load_divisional_k_fn:config_path
src.analysis.equelo.fixed_v2.api:load_day_end_ratings:path
src.analysis.equelo.fixed_v2.api:load_entrant_initial_ratings:path
src.analysis.equelo.fixed_v2.api:load_metadata:path
src.infra.get_bios.api:load_bio_store:path
src.infra.get_bios.parser:main:path
src.infra.parser.parser2_margin:_parse_raw_marginalia:fn
src.infra.parser.parser_daily:_parse_daily_results:fn
```

## Known limitations

The major architectural limitation is still that SDDA is import-reachability based, not full execution-slice based.

That means helper APIs imported into the reachable module set can still appear as high-priority review rows even when they may not actually be called by `make_site2` in the analysed run.

The remaining high-priority rows outside direct make_site2 work currently look like:

```text
src.analysis.equelo.expt1.params:load_divisional_k_fn:config_path
src.analysis.equelo.fixed_v2.api:load_day_end_ratings:path
src.analysis.equelo.fixed_v2.api:load_entrant_initial_ratings:path
src.analysis.equelo.fixed_v2.api:load_metadata:path
src.infra.get_bios.api:load_bio_store:path
src.infra.get_bios.parser:main:path
src.infra.parser.parser2_margin:_parse_raw_marginalia:fn
src.infra.parser.parser_daily:_parse_daily_results:fn
```

These should probably not be attacked with more ad hoc path-provenance rules. The better next step is to add call-edge reporting and then execution-slice filtering, or else classify unbound helper API parameters separately from direct product distribution inputs.

Unresolved method calls of the form:

```python
obj.method(...)
```

are still preserved in `unresolved.csv` rather than hidden. Some of these may eventually need method/call graph resolution.

## Current interpretation

Milestone 1, module and import evidence, is good enough for now.

Milestone 2, scope-level file-use evidence, is good enough for now.

Milestone 3, initial type/value/field facts, is useful and already feeding policy decisions.

Milestone 4, producer-output and parameter-provenance evidence, is now working for the important direct `make_site2` build/deploy cases.

Milestone 5, file-family normalisation, classification, and distribution candidate reporting, is good enough for continued triage but should continue to consume stronger provenance facts as they are added.

The reports are not yet the final dependency answer. They are a conservative evidence layer from which later reports can derive candidate distribution inputs, generated outputs, caches, deployment assumptions, and review items.

## Recommended next steps

1. Stop adding narrow path-provenance fixes for the remaining eight helper rows unless one is proven to be directly called by `make_site2`.
2. Add a `calls.csv` or `call_edges.csv` report with caller module/scope, call line, callee expression, resolved callee full name, and resolution kind.
3. Use the call-edge report to derive an execution-reachable call slice from `src.products.make_site2.__main__.main`.
4. Reclassify file-use families from imported-but-not-executed helper APIs as outside the direct `make_site2` execution slice, or as external helper API parameters.
5. Then revisit unresolved object-method calls with the call graph in place.

Do not prioritise further small alias cleanups unless they affect more than a handful of rows or block the call-graph/value-flow work.
