# Review Checklists

## Output Review Fields

Each generated output family should be reviewed with these fields:

```text
output_family_id:
example_paths:
path_template:
producer_entry_point:
producer_module:
generation_command:
layer:
output_subtype:
input_files:
input_virtual_data:
input_urls:
parameters:
data_instance:
known_consumers:
consumer_status:
leaf_output:
legacy_status:
provenance_present:
freshness_rule:
regeneration_command:
risk_if_stale_or_wrong:
classification:
proposed_action:
human_decision_needed:
notes:
```

## Module Review Fields

Each module should be reviewed with these fields:

```text
module:
package:
entry_points:
intra_package_imports:
external_imports:
imported_by:
produces_outputs:
generated_outputs:
reads_inputs:
network_access:
uses_live_store:
uses_history_zip:
uses_files_output:
tests:
docs:
replacement_or_successor:
module_classification:
proposed_action:
human_decision_needed:
notes:
```

## LLM Checklist

The LLM should fill mechanical and evidence-based fields.

For each package:

```text
- list modules
- identify command entry points
- build import graph, including isolated nodes
- build dataflow graph with labelled artifacts
- record files read
- record files written
- record directories written
- record URLs/network access
- record virtual inputs such as History
- record generated output families
- search for downstream consumers
- identify tests/docs that mention outputs
- record provenance/freshness clues
- record regeneration commands
```

The LLM should not decide human-intent questions such as:

```text
- whether an unused chart is still interesting
- whether a research result is worth retaining
- whether a manual workflow still matters
- whether a future use is plausible enough
```

When intent matters, mark:

```text
ASK_HUMAN
```

## Human Checklist

For each unused output:

```text
Would I deliberately regenerate this today?
Would I deliberately open this today?
Can I name a future task that needs this?
Is this output evidence for a recorded decision?
Is this merely something created during exploration?
If this disappeared, would I know how to recreate it?
If this disappeared, would anything non-legacy break?
If this stayed, could it mislead me later?
```

For each producer module:

```text
Is it an active producer?
Is it only a support module?
Is it a research module?
Is it redundant?
Should only its generated outputs be deleted?
Should the entry point be removed while support code remains?
Is a replacement already present?
```

For each retained output:

```text
What contract justifies keeping it?
What provenance should it carry?
What command regenerates it?
When is it stale?
Who is allowed to consume it?
```
