# Process Deliverables

## Purpose

The audit should produce files that can be reviewed, diffed, sorted, regenerated and eventually used to create Makefile rules.

Graphs are useful views.

CSV-style inventories are the required process deliverables.

## Output Location

Generated audit data should be written under:

```text
files/output/makefile/
```

Suggested layout:

```text
files/output/makefile/
  csv/
  mermaid/
  html/
  reports/
```

## Required CSVs

### packages.csv

One row per package or sub-project scope under audit.

```csv
package_id,path,parent_package,status,notes
```

Example:

```csv
src.infra.get_bios,src/infra/get_bios,src.infra,reviewed,medium pipeline package
```

### modules.csv

One row per module, including isolated modules.

```csv
module_id,package_id,path,kind,has_main,is_entry_point,status,notes
```

Suggested `kind` values:

```text
module
package_init
script
docs
test
runtime_asset
```

### import_edges.csv

One row per import edge.

```csv
source_module,target_module,scope,import_form,evidence_file,evidence_line,notes
```

Suggested `scope` values:

```text
intra_package
package_external_exports
package_external_imports
installed_library_exports
```

The first audit pass may focus on `intra_package` edges.

### dataflow_edges.csv

One row per dataflow edge. Artifacts live on the edge.

```csv
source_id,source_type,target_id,target_type,artifact,edge_type,evidence_file,evidence_line,notes
```

During package-local audit, use `external` boundary nodes for artifact inputs and outputs unless the audited code directly connects producer and consumer.

Example:

```csv
source_id,source_type,target_id,target_type,artifact,edge_type,evidence_file,evidence_line,notes
src.infra.get_bios.__main__,module,external,external,OUTPUT_DIR/infra/rikishi/{rikid:05d}.html,output,src/infra/get_bios/__main__.py,84,writes raw bio HTML
external,external,src.infra.get_bios.parser,module,OUTPUT_DIR/infra/rikishi/*.html,input,src/infra/get_bios/parser.py,388,reads all HTML files in BIO_DIR
```

Do not join those rows during the package-local pass.

Suggested node types:

```text
module
entry_point
function
artifact
virtual_input
url
env_var
external
manual
browser_runtime
command
```

Suggested edge types:

```text
input
output
reads_existing
writes
copies
downloads
returns
diagnostic_output
manual_input
virtual_input
```

Use explicit path templates in `artifact` where possible:

```text
OUTPUT_DIR/infra/rikishi/{rikid}.html
files/output/HTML results/{year} {month}/{day}.html
files/output/misc/finish_by_chii_{start}_{end}_summary.csv
```

### entry_points.csv

One row per command, script, `main()` function, publisher, deploy step or build entry point.

```csv
entry_point_id,module_id,command,kind,inputs,outputs,network_access,notes
```

Suggested `kind` values:

```text
python_module
script
function
publisher
deployment
test_helper
manual_workflow
```

### output_families.csv

One row per output family, not per individual file unless individual files differ materially.

```csv
output_family_id,path_template,layer,producer_id,data_instance,regeneration_command,provenance_status,notes
```

### output_consumers.csv

One row per known consumer of an output family.

```csv
output_family_id,consumer_id,consumer_type,edge_type,evidence_file,evidence_line,status,notes
```

In a package-local audit, this table should include only consumers directly visible inside the audited scope. Cross-package consumers are added during global reconciliation or a repo-wide consumer-search phase.

Suggested `consumer_type` values:

```text
module
entry_point
test
site_builder
browser_runtime
deploy_step
manual
external
unknown
```

### output_classification.csv

One row per output family after review.

```csv
output_family_id,classification,layer,consumer_status,leaf_output,proposed_action,human_decision_needed,notes
```

### module_classification.csv

One row per module after review.

```csv
module_id,classification,produces_outputs,imported_by_nonlegacy,has_nonlegacy_dataflow,proposed_action,human_decision_needed,notes
```

## Optional CSVs

### reconciliation_edges.csv

Produced after multiple package-local audits exist.

```csv
producer_id,producer_artifact,consumer_id,consumer_artifact,match_type,confidence,evidence,notes
```

Suggested `match_type` values:

```text
exact
pattern_subset
pattern_superset
ambiguous
manual
incompatible
```

This is where compatible path templates are matched.

### execution_edges.csv

Use when commands have meaningful order.

```csv
source_command,target_command,edge_type,evidence_file,evidence_line,notes
```

### decisions.csv

Use for human decisions that should survive context loss.

```csv
decision_id,subject_id,subject_type,decision,rationale,decider,date,notes
```

### open_questions.csv

Use for unresolved audit questions.

```csv
question_id,subject_id,subject_type,question,blocked_action,priority,status,notes
```

## CSV Rules

- CSV is the canonical audit form.
- Every graph view should be generated from CSV or traceable back to CSV rows.
- Include isolated modules in `modules.csv`, even with no import/dataflow edges.
- Do not rely on graph layout as data.
- Use path templates rather than vague wildcards.
- Do not use blank edge labels in dataflow exports.
- Keep human decisions separate from mechanical evidence.
- Prefer stable IDs over display labels.

## Mermaid / HTML Output

Mermaid and HTML are generated views.

They are produced on demand. They are not required process deliverables unless a specific review task asks for them.

Suggested generated files:

```text
files/output/makefile/mermaid/{package_id}_imports.mmd
files/output/makefile/mermaid/{package_id}_dataflow.mmd
files/output/makefile/html/{package_id}_imports.html
files/output/makefile/html/{package_id}_dataflow.html
```

The graph view may use compressed labels. The CSV must retain full paths and evidence.

Do not commit generated chart/view files by default. If a chart becomes a retained review artifact, record why it is retained and where it is regenerated from.
