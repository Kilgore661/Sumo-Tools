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

SDDA now has an initial execution-slice layer. The base evidence is still conservative and import-reachability based, but the execution-aware reports distinguish direct product-slice concerns from imported helper noise.

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

Additional current reports include call-edge, execution-slice, and execution-aware review evidence. The exact call-edge counts vary as resolution rules improve.

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
  -> call edges
  -> execution call slice
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
  -> execution-aware review candidate report
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
call_edges.csv
execution_call_slice.csv
execution_review_candidates.csv
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

`review_candidates.csv` remains the conservative import-reachable triage report.

`execution_review_candidates.csv` is now the preferred product-slice triage report. It adds:

```text
execution_status
execution_depth
execution_reason
effective_review_priority
```

Rows outside the project execution slice are given `effective_review_priority: low`, while the base conservative priority is preserved.

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

The classifier is conservative. It avoids treating broad variable globs, deploy-only reads, non-root helper `main()` reads, unresolved parameters, unresolved locals, and object-field reads as definite source-distribution inputs unless a later provenance layer provides stronger evidence.

## Implemented value-flow and provenance improvements

### Dataclass and value facts

SDDA records class/dataclass definitions, dataclass fields, function parameter annotations, function return annotations, and selected local value facts from annotated calls.

An important correction was made to class/dataclass type facts: class rows now use the actual class full name rather than only the containing module name. This enabled constructor-return matching such as `MasterDataOutput(...)`.

### Field facts

SDDA resolves object field reads where the receiver has an inferred dataclass type. Examples include:

```text
producer_output.data_path
producer_output.report_path
build_output.root
build_output.file_count
```

### Producer output provenance

SDDA emits:

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

### Call edges and execution slice

SDDA now emits:

```text
call_edges.csv
execution_call_slice.csv
execution_review_candidates.csv
```

`call_edges.csv` records syntactic calls with resolved targets where possible. Current resolution categories include:

```text
from_import
same_module_definition
imported_attribute
current_class_method
builtin
external_from_import
external_imported_attribute
unresolved_name
unresolved_attribute
unresolved_dynamic
```

The first execution slice starts from:

```text
src.products.make_site2.__main__.<module>
src.products.make_site2.__main__.main
```

and follows project-resolved call edges. It does not follow builtin, external, or unresolved edges.

This layer proved that most remaining high-priority conservative rows were imported helper noise, while `load_bio_store()` was genuinely execution-reachable via:

```text
build_basho_results_data_output
  -> make_public_shikona
  -> load_bio_store
```

### Call argument bindings

SDDA emits:

```text
call_argument_bindings.csv
```

This connects call-site arguments to annotated callee parameters. For example, `main` passing `build_output` into deployment functions is visible:

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

SDDA emits:

```text
parameter_field_provenance.csv
```

This connects field reads inside a callee back to the caller-side argument source. The main useful case is:

```text
deploy_local/deploy_remote read build_output.root
```

SDDA distinguishes both branches:

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

SDDA emits:

```text
parameter_file_provenance.csv
```

This connects direct file-use parameters inside helper functions back to call-site arguments, local aliases, iterator families, or default parameter values.

Handled cases now include:

```text
parameter_from_path_expression
parameter_from_iterator_path_family
parameter_from_local_path_alias
parameter_from_default_path_expression
```

The direct path-expression case is handled for `copy_single_csv_chart_data_output:source_path`. Examples include:

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

Local-alias-derived parameter provenance is handled for deployment helper calls. For example:

```python
for source in build_output.root.rglob("*"):
    if source.is_file():
        copy_file(source, target)
```

SDDA records:

```text
copy_file:source <- build_output.root/**/*
```

and inherits the mode-dependent deployment-source classification:

```text
copy_file:source mode_dependent_deployment_source -> review, medium priority
```

Default-parameter provenance is handled for `load_bio_store(path: Path = OUTPUT_JSON)`. The execution-reachable read now resolves to:

```text
files/output/infra/get_bios/rikishi_bios.json
```

and is classified as a required distribution input rather than an unresolved high-priority parameter.

### Loop-variable aliasing

Simple literal filename tuples and loop variables from `zip(...)` are resolved.

The following former high-priority `name` rows have been collapsed:

```text
files/output/career_length/site/career_length_1958_01_to_2026_05/name
files/output/probability/matchups/site/win_probability_by_standing/name
```

Simple glob/rglob loop aliases are also resolved. This handles the browser runtime copy loop:

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

src.infra.get_bios.api:load_bio_store:path
  required_distribution_input
  include
  low effective review
  resolved via default parameter to files/output/infra/get_bios/rikishi_bios.json
```

As of the latest checked output, there are no effective high-priority review rows for the current `make_site2` execution slice.

Confirm with:

```powershell
Import-Csv files\output\sdda\src.products.make_site2.__main__\execution_review_candidates.csv |
  Where-Object { $_.effective_review_priority -eq "high" } |
  Select-Object family_pattern, review_priority, effective_review_priority, execution_status, classification_reason, first_module, first_scope |
  Format-Table -AutoSize
```

Expected result:

```text
no rows
```

The base conservative `review_candidates.csv` may still contain high-priority rows from import-reachable helper functions. In the execution-aware report these are marked:

```text
execution_status: not_in_execution_slice
effective_review_priority: low
```

Recently observed not-in-slice examples include:

```text
src.analysis.equelo.fixed_v2.api:load_day_end_ratings:path
src.analysis.equelo.fixed_v2.api:load_entrant_initial_ratings:path
src.analysis.equelo.fixed_v2.api:load_metadata:path
src.infra.get_bios.parser:main:path
src.infra.parser.parser2_margin:_parse_raw_marginalia:fn
src.infra.parser.parser_daily:_parse_daily_results:fn
```

## Known limitations

The execution slice is intentionally narrow. It follows project-resolved direct call edges, but it does not yet solve general dynamic dispatch or arbitrary object-method calls.

Unresolved method calls of the form:

```python
obj.method(...)
```

are still preserved in `unresolved.csv` and `call_edges.csv` rather than hidden. Some of these may eventually need receiver type resolution and method/call graph improvements.

The base conservative reports are still import-reachability based. The execution-aware reports should be used to distinguish direct product-slice concerns from imported helper noise.

## Current interpretation

Milestone 1, module and import evidence, is good enough for now.

Milestone 2, scope-level file-use evidence, is good enough for now.

Milestone 3, initial type/value/field facts, is useful and already feeding policy decisions.

Milestone 4, producer-output and parameter-provenance evidence, is working for the important direct `make_site2` build/deploy cases and the execution-reachable `load_bio_store` default-input case.

Milestone 5, file-family normalisation, classification, and distribution candidate reporting, is good enough for continued triage but should continue to consume stronger provenance facts as they are added.

Milestone 6, initial call-edge and execution-slice reporting, is now working well enough to clear the effective high-priority queue for the current `make_site2` slice.

The reports are not yet the final dependency answer. They are a conservative evidence layer from which later reports can derive candidate distribution inputs, generated outputs, caches, deployment assumptions, and review items.

## Recommended next steps

1. Treat `execution_review_candidates.csv` as the main triage view for product-slice work.
2. Keep `review_candidates.csv` as the conservative import-reachable evidence view.
3. Improve unresolved attribute calls by adding receiver type/method resolution where it materially affects the execution slice.
4. Consider deriving a final `source_distribution_inputs.csv` report from execution-aware classification, rather than expecting users to interpret the raw evidence reports directly.
5. Update documentation when the final source-distribution policy is chosen.

Do not prioritise further small alias cleanups unless they affect more than a handful of rows or block execution-slice/value-flow work.
