# SDDA Status Report

## Status

SDDA Dataflow is implemented under `sdda.dataflow`. It is independent of `src/introspection` and is invoked through:

```powershell
python -m sdda.dataflow --import-root . src.products.make_site2.__main__
```

The current implementation writes generated reports under:

```text
files/output/sdda/src.products.make_site2.__main__/
```

These outputs are local generated evidence and are not normally committed.

## Purpose

The purpose of SDDA is to support a source distribution of the Sumo-Tools website product.

The exact runtime input set for `make_site2` is not computable in general, so SDDA uses conservative static evidence plus an execution-slice overlay. The current goal is:

```text
Identify which file families, generated outputs, precomputed artifacts, source assets, deployment assumptions, and review items matter for the current make_site2 product slice.
```

The project has now moved beyond raw evidence reports. It emits a derived final report:

```text
source_distribution_inputs.csv
```

This is now the main source-distribution view.

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

Additional report counts vary as call and policy rules improve.

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
  -> source distribution input derivation
  -> unresolved-call evidence
  -> CSV and Markdown reports
```

Generated reports currently include:

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
source_distribution_inputs.csv
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

`execution_review_candidates.csv` is the product-slice triage report. It adds:

```text
execution_status
execution_depth
execution_reason
effective_review_priority
```

`source_distribution_inputs.csv` is the final derived source-distribution report. It combines distribution candidates with execution-aware status and source-distribution policy buckets.

## Current source_distribution_inputs.csv shape

Recent bucket counts:

```text
54 generated_or_intermediate_output
11 not_in_execution_slice
 8 precomputed_artifact_input
 4 unresolved_non_execution_parameter
 4 state_or_control_review
 3 repository_source_input
 2 pipeline_tree_review
 2 mode_dependent_review
 2 scoped_output_parameter
```

There is no generic `review` bucket in the latest checked output. The remaining non-final buckets are semantically named.

### Repository source inputs

These are concrete repository files/assets that should be included in a source distribution:

```text
src/analysis/standings/files/full_shiks.pkl
src/products/make_site2/runtime/site-refactor/**/*
src/products/make_site2/runtime/site.css
```

### Precomputed artifact inputs

These are required by the current `make_site2` product slice, but they live under `files/output/...`, so the policy decision is `include_or_regenerate` rather than unconditional source-control inclusion:

```text
files/output/bcr/data/banzuke_change_report.csv
files/output/bcr/site_config.json
files/output/career_length/site/career_length_1958_01_to_2026_05/{distribution.csv,pmf.csv,cdf.csv,survival.csv,longest.csv}
files/output/infra/get_bios/rikishi/*.html
files/output/misc/finish_by_chii_1958_2026_bottom_thresholds.csv
files/output/misc/finish_by_chii_1958_2026_top_thresholds.csv
files/output/probability/matchups/site/win_probability_by_standing/{observed_trace_points.csv,equelo_trace_points.csv}
files/output/standings/publisher/latest_data/site_config.json
```

### Mode-dependent deployment review

These rows represent deployment source-tree reads that are generated in normal build mode but externally supplied in `--no-build` mode:

```text
build_output.root/**/*
src.products.make_site2.deploy:copy_file:source
```

### State or control review

These rows are execution-reachable state/existence checks rather than source inputs:

```text
src.products.make_site2.build:count_output_files:path
src.products.make_site2.deploy:build_output_from_existing:entrypoint
src.products.make_site2.deploy:count_files:path
src.products.make_site2.deploy:deploy_remote:path
```

### Pipeline tree review

These are variable output-tree globs that are still worth understanding, but no longer appear as generic review noise:

```text
output_root/**/*
root/**/*
```

### Scoped output parameters

These are output-location parameters, not source-distribution inputs:

```text
src.analysis.sumo_history.basho_results.reports:write_index:output_root
src.products.make_site2.build:build_site:output_root
```

### Unresolved non-execution parameters

These are scoped parameter proxies that are not currently in the product execution slice or are not represented by concrete source-distribution families in the final report:

```text
src.analysis.equelo.expt1.params:load_divisional_k_fn:config_path
src.infra.get_bios.api:load_bio_store:path
src.products.make_site2.data_output:copy_single_csv_chart_data_output:source_path
src.products.make_site2.data_output:copy_standings_source_file:source_path
```

The concrete file/glob families produced from the important parameter provenance are represented elsewhere, for example under `precomputed_artifact_input` or `repository_source_input`.

## Important implemented improvements

### Dataclass and value facts

SDDA records class/dataclass definitions, dataclass fields, function parameter annotations, function return annotations, and selected local value facts from annotated calls.

Class/dataclass type facts use the actual class full name rather than only the containing module name. This enabled constructor-return matching such as `MasterDataOutput(...)`.

### Field facts

SDDA resolves object field reads where the receiver has an inferred dataclass type. Important examples include:

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

This proves the important generated-then-consumed case:

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
producer_output.data_path   generated_then_consumed -> exclude
producer_output.report_path generated_then_consumed -> exclude
```

### Call edges and execution slice

SDDA emits:

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

The execution slice starts from:

```text
src.products.make_site2.__main__.<module>
src.products.make_site2.__main__.main
```

and follows project-resolved call edges. It does not follow builtin, external, or unresolved edges.

This layer proved that most high-priority conservative rows were imported helper noise, while `load_bio_store()` was genuinely execution-reachable via:

```text
build_basho_results_data_output
  -> make_public_shikona
  -> load_bio_store
```

### Parameter field provenance

SDDA emits:

```text
parameter_field_provenance.csv
```

This connects field reads inside a callee back to caller-side argument sources. The main useful case is:

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
build_output.root/**/* mode_dependent_deployment_source
```

### Parameter file provenance

SDDA emits:

```text
parameter_file_provenance.csv
```

This connects direct file-use parameters inside helper functions back to call-site arguments, local aliases, iterator families, or default parameter values.

Handled cases include:

```text
parameter_from_path_expression
parameter_from_iterator_path_family
parameter_from_local_path_alias
parameter_from_default_path_expression
```

Examples now handled include:

```text
copy_single_csv_chart_data_output:source_path
copy_standings_source_file:source_path
copy_file:source
load_bio_store(path: Path = OUTPUT_JSON)
```

The execution-reachable `load_bio_store` read resolves to:

```text
files/output/infra/get_bios/rikishi_bios.json
```

### Loop-variable aliasing

Simple literal filename tuples, `zip(...)` loop variables, and simple glob/rglob loop variables are resolved.

This collapsed former high-priority rows such as:

```text
files/output/career_length/site/career_length_1958_01_to_2026_05/name
files/output/probability/matchups/site/win_probability_by_standing/name
```

The browser runtime copy loop now becomes:

```text
src/products/make_site2/runtime/site-refactor/**/*
```

and is treated as a repository source input in `source_distribution_inputs.csv`.

## Known limitations

The execution slice is intentionally narrow. It follows project-resolved direct call edges, but it does not yet solve general dynamic dispatch or arbitrary object-method calls.

Unresolved method calls of the form:

```python
obj.method(...)
```

are still preserved in `unresolved.csv` and `call_edges.csv` rather than hidden. Some of these may eventually need receiver type resolution and method/call graph improvements.

The base conservative reports are still import-reachability based. The execution-aware and source-distribution reports should be used to distinguish direct product-slice concerns from imported helper noise.

The final source-distribution policy still treats `files/output/...` inputs as `include_or_regenerate`; a later product decision should decide which of those artifacts are committed, distributed separately, or regenerated as part of a full source build.

## Current interpretation

Milestone 1, module and import evidence, is good enough for now.

Milestone 2, scope-level file-use evidence, is good enough for now.

Milestone 3, type/value/field facts, is useful and feeding policy decisions.

Milestone 4, producer-output and parameter-provenance evidence, is working for the important direct `make_site2` cases.

Milestone 5, call-edge and execution-slice reporting, is working well enough to separate direct product-slice concerns from imported helper noise.

Milestone 6, `source_distribution_inputs.csv`, is now the main usable output. It provides semantically named buckets rather than raw review noise.

## Recommended next steps

1. Treat `source_distribution_inputs.csv` as the main source-distribution view.
2. Treat `execution_review_candidates.csv` as the main triage view when debugging product-slice analysis.
3. Keep `review_candidates.csv` as the conservative import-reachable evidence view.
4. Decide product policy for `precomputed_artifact_input`: include, regenerate, or package separately.
5. Investigate the two `pipeline_tree_review` rows if they matter: `output_root/**/*` and `root/**/*`.
6. Improve unresolved attribute calls by adding receiver type/method resolution only where it materially affects the final source-distribution report.

Do not prioritise further small alias cleanups unless they affect the final source-distribution buckets or block execution-slice/value-flow work.
